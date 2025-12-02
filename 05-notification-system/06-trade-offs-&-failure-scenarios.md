# Minutes 46-52: Trade-offs & Failure Scenarios (Expanded)

## **Minute 46: Opening Trade-offs Discussion (60 seconds)**

### **Frame the Conversation**

*Transition statement:*

“Now let’s discuss the key trade-offs we’ve made in this design and how the system handles failures. Every architectural decision involves trade-offs, and I want to be explicit about what we’re optimizing for and what we’re sacrificing.”

### **Major Trade-offs Overview**

*Write on whiteboard:*

```
KEY TRADE-OFFS IN OUR DESIGN:

1. At-least-once vs Exactly-once delivery
   ↓
   Chose: At-least-once (simpler, faster, cheaper)

2. Latency vs Cost (batching)
   ↓
   Chose: Low-priority can wait (save 50% on costs)

3. Consistency vs Availability
   ↓
   Chose: Availability (eventual consistency for preferences)

4. Vendor lock-in vs Complexity
   ↓
   Chose: Multi-provider (resilience over simplicity)

5. Build vs Buy
   ↓
   Chose: Buy (Kafka, SendGrid, Twilio vs custom)
```

-----

## **Minute 47-48: Deep Dive on Critical Trade-offs (2 minutes)**

### **Trade-off 1: At-Least-Once vs Exactly-Once Delivery (45 seconds)**

*Draw comparison table:*

```
┌─────────────────────┬──────────────────────┬──────────────────────┐
│                     │   AT-LEAST-ONCE      │   EXACTLY-ONCE       │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Guarantee           │ May get duplicates   │ Never duplicates     │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Complexity          │ Simple               │ Complex              │
│                     │ - Basic retry        │ - Distributed txns   │
│                     │ - Idempotency keys   │ - 2-phase commit     │
│                     │                      │ - Deduplication logic│
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Performance         │ Fast                 │ Slower               │
│                     │ - No coordination    │ - Coordination needed│
│                     │ - No state locking   │ - Must track state   │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Cost                │ Lower                │ Higher               │
│                     │ - Less storage       │ - 2x storage needed  │
│                     │ - Simpler infra      │ - More DB writes     │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Availability        │ Higher               │ Lower                │
│                     │ - Keep retrying      │ - Must maintain state│
│                     │                      │ - Failure = stuck    │
└─────────────────────┴──────────────────────┴──────────────────────┘

OUR CHOICE: At-least-once

WHY:
✓ Duplicate notifications are annoying but acceptable
  - User sees "Order confirmed" twice → minor UX issue
  - User misses notification completely → major problem
  
✓ Providers often deduplicate for us
  - FCM: message_id deduplication
  - SendGrid: X-Message-Id header
  
✓ We add idempotency keys for client protection
  - Prevents our service from creating duplicates
  - Provider-side duplicates still possible but rare

WHEN EXACTLY-ONCE MATTERS:
✗ Financial transactions (charges, payments)
✗ Account state changes (password resets)
→ For these: Use transactional outbox pattern
```

**Transactional Outbox (if interviewer asks):**

```python
# For critical notifications requiring exactly-once

@transaction
def process_payment(payment):
    # 1. Update payment in DB
    db.payments.update(payment.id, status='completed')
    
    # 2. Write notification to outbox table in SAME transaction
    db.notification_outbox.insert({
        'id': uuid.uuid4(),
        'user_id': payment.user_id,
        'type': 'payment_confirmation',
        'payload': payment.to_dict(),
        'status': 'pending',
        'created_at': now()
    })
    # Both succeed or both fail - atomic

# Separate process reads outbox and sends notifications
def outbox_processor():
    while True:
        pending = db.notification_outbox.get_pending(limit=100)
        
        for notification in pending:
            if send_notification(notification):
                db.notification_outbox.update(
                    notification.id,
                    status='sent'
                )
```

-----

### **Trade-off 2: Latency vs Cost (Batching) (45 seconds)**

```
┌──────────────────┬─────────────────┬─────────────────┐
│                  │  NO BATCHING    │  WITH BATCHING  │
├──────────────────┼─────────────────┼─────────────────┤
│ Latency          │ ~100ms          │ ~1-5 seconds    │
│                  │ (immediate)     │ (wait for batch)│
├──────────────────┼─────────────────┼─────────────────┤
│ Throughput       │ 10 msg/sec      │ 500 msg/sec     │
│ (per worker)     │                 │                 │
├──────────────────┼─────────────────┼─────────────────┤
│ Cost             │ High            │ Low             │
│                  │ - More workers  │ - Fewer workers │
│                  │ - More API calls│ - Batch discounts│
├──────────────────┼─────────────────┼─────────────────┤
│ Provider Costs   │ $0.001/email    │ $0.0005/email   │
│                  │ (individual)    │ (bulk pricing)  │
└──────────────────┴─────────────────┴─────────────────┘

OUR APPROACH: Hybrid - Batch by priority

Critical Priority:
  - No batching
  - Max latency: 1 second
  - Cost: Higher, but acceptable
  - Use cases: OTP, security alerts, fraud warnings

Normal Priority:
  - Small batches (10-20)
  - Max wait: 5 seconds
  - Cost: Balanced
  - Use cases: Order confirmations, friend requests

Low Priority:
  - Large batches (100-500)
  - Max wait: 60 seconds
  - Cost: Optimized (50% savings)
  - Use cases: Newsletters, digests, suggestions

COST IMPACT:
  Without batching: 1B notifications × $0.001 = $1M/day
  With batching: 1B notifications × $0.0005 = $500K/day
  Savings: $500K/day = $15M/month!
```

-----

### **Trade-off 3: Consistency vs Availability (30 seconds)**

```
SCENARIO: User opts out of email notifications

┌──────────────────────────────────────────────────┐
│  STRONG CONSISTENCY (sacrifice availability)     │
├──────────────────────────────────────────────────┤
│  1. User clicks "unsubscribe"                    │
│  2. Write to primary DB with lock                │
│  3. Wait for all replicas to confirm             │
│  4. Invalidate ALL caches (wait for ACK)         │
│  5. Confirm to user                              │
│                                                   │
│  Problem: If any step fails, system unavailable  │
│  Latency: 500ms - 2 seconds                      │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  EVENTUAL CONSISTENCY (our choice)               │
├──────────────────────────────────────────────────┤
│  1. User clicks "unsubscribe"                    │
│  2. Write to primary DB (async replication)      │
│  3. Invalidate cache (best effort)               │
│  4. Confirm to user immediately                  │
│                                                   │
│  Benefit: Always available, fast response        │
│  Trade-off: User might get 1-2 more emails       │
│            in next 30 seconds (acceptable)       │
│  Latency: <50ms                                  │
└──────────────────────────────────────────────────┘

WHY EVENTUAL CONSISTENCY WORKS HERE:
- Notification preferences aren't mission-critical
- Brief inconsistency window (seconds, not hours)
- Worst case: 1 extra unwanted email (annoying but not harmful)
- System remains available even during DB issues
```

-----

## **Minute 49-50: Failure Scenarios & Mitigations (2 minutes)**

### **Failure Scenario 1: Provider Outage (45 seconds)**

*Draw failure flow:*

```
SCENARIO: SendGrid goes down

                [Notification Service]
                        ↓
                  [Email Queue]
                        ↓
                [Email Workers] ──→ [SendGrid] ✗ DOWN
                                         ↓
                                  503 Service Unavailable
```

**Detection & Response:**

```python
class ProviderCircuitBreaker:
    """
    Circuit breaker pattern to detect and handle provider failures
    """
    def __init__(self, provider_name):
        self.provider_name = provider_name
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.failure_threshold = 5
        self.timeout = 60  # seconds
        self.last_failure_time = None
    
    def call(self, func, *args):
        if self.state == 'OPEN':
            # Check if timeout elapsed
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                # Circuit open - fail fast
                raise CircuitBreakerOpen(f"{self.provider_name} circuit open")
        
        try:
            result = func(*args)
            
            if self.state == 'HALF_OPEN':
                # Success - close circuit
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info(f"{self.provider_name} circuit closed")
            
            return result
            
        except ProviderError as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(f"{self.provider_name} circuit opened!")
                
                # Trigger alerts
                alert_oncall(f"{self.provider_name} is down")
                
                # Enable fallback provider
                self.enable_fallback()
            
            raise

# Multi-provider fallback
class EmailSender:
    def __init__(self):
        self.primary = SendGridClient()
        self.fallback = MailgunClient()
        self.circuit_breaker = ProviderCircuitBreaker('sendgrid')
    
    def send_email(self, email):
        try:
            # Try primary provider
            return self.circuit_breaker.call(
                self.primary.send,
                email
            )
        except CircuitBreakerOpen:
            # Primary is down - use fallback
            logger.warning("Using fallback email provider")
            return self.fallback.send(email)
```

**Mitigation Strategy:**

```
Step 1: Circuit Breaker Opens (after 5 failures in 10 sec)
  ↓
Step 2: Switch to Fallback Provider (Mailgun)
  ↓
Step 3: Alert On-call Engineer
  ↓
Step 4: Monitor SendGrid Status Page
  ↓
Step 5: Circuit Breaker Half-Open (test after 60 sec)
  ↓
Step 6: If success → Close circuit, back to primary
        If failure → Keep circuit open, stay on fallback

Metrics:
- Time to detect: <10 seconds
- Time to failover: <1 second
- Notifications lost: 0 (queued during transition)
- Notifications delayed: ~5-10 seconds
```

-----

### **Failure Scenario 2: Database Outage (45 seconds)**

```
SCENARIO: User Preferences DB (Primary) goes down

[Notification Service] → [Preferences DB Primary] ✗ DOWN
                              ↓
                        [Read Replica 1] ✓ Available
                        [Read Replica 2] ✓ Available
```

**Response Strategy:**

```python
class DatabaseFailover:
    def __init__(self):
        self.primary = PrimaryDB()
        self.replicas = [ReplicaDB1(), ReplicaDB2()]
        self.current_primary_healthy = True
    
    def get_connection(self, operation='read'):
        if operation == 'write':
            try:
                # Try primary
                conn = self.primary.connect(timeout=1)
                return conn
            except ConnectionError:
                self.current_primary_healthy = False
                
                # CRITICAL: Can't write preferences
                # Fail gracefully - use cached/default values
                logger.critical("Primary DB down - using defaults")
                
                # Alert immediately
                page_oncall("Primary DB unavailable")
                
                # Return None - caller must handle
                return None
        
        else:  # read operation
            if self.current_primary_healthy:
                try:
                    return self.primary.connect(timeout=1)
                except ConnectionError:
                    pass  # Fall through to replicas
            
            # Try replicas
            for replica in self.replicas:
                try:
                    return replica.connect(timeout=1)
                except ConnectionError:
                    continue
            
            raise AllDatabasesDown()

# Usage in notification service
def get_user_preferences(user_id):
    try:
        db = database_failover.get_connection(operation='read')
        return db.query("SELECT * FROM user_preferences WHERE user_id = ?", user_id)
    except AllDatabasesDown:
        # All DBs down - use cached or default
        cached = cache.get(f"prefs:{user_id}")
        if cached:
            return cached
        
        # Return safe defaults (opt-in for critical, opt-out for marketing)
        return DEFAULT_PREFERENCES
```

**Impact Analysis:**

```
Primary DB Down:
├─ Reads: Continue from replicas (no impact)
├─ Writes (preference updates): FAIL
│   └─ Mitigation: Show error to user, retry later
└─ Cached preferences: Continue working (95% hit rate)

All DBs Down (extreme case):
├─ Use default preferences
├─ Allow critical notifications
├─ Block marketing notifications (safety)
└─ Queue preference writes for later

Recovery Time Objective (RTO): 5 minutes
Recovery Point Objective (RPO): 0 (no data loss with replication)
```

-----

### **Failure Scenario 3: Kafka Cluster Partial Failure (30 seconds)**

```
SCENARIO: 4 out of 12 Kafka brokers crash

Kafka Cluster (12 brokers, replication factor 3):
  Broker 1-4: ✗ DOWN
  Broker 5-12: ✓ UP

Impact:
- Some partitions unavailable (leader on down broker)
- Automatic leader election to alive brokers
- Short unavailability: 10-30 seconds
- No data loss (min-in-sync-replicas = 2)

Response:
1. Kafka automatically rebalances
2. Producers retry failed writes (built-in retry)
3. Consumers rebalance partitions
4. Alert SRE team (not paging - auto-recovery)
5. Manual intervention only if >50% brokers down
```

-----

## **Minute 51: Cascading Failures & Defense (60 seconds)**

### **Cascading Failure Scenario**

*Draw cascade diagram:*

```
CASCADING FAILURE EXAMPLE:

Step 1: High Load Event (Black Friday traffic spike)
         ↓
Step 2: Workers overwhelmed → slow processing
         ↓
Step 3: Queue depth grows → memory pressure
         ↓
Step 4: Database connection pool exhausted
         ↓
Step 5: API Gateway times out
         ↓
Step 6: Clients retry → amplifies load 10x
         ↓
Step 7: TOTAL SYSTEM FAILURE
```

**Defense Mechanisms:**

```python
# 1. BULKHEAD PATTERN - Isolate failures

class BulkheadIsolation:
    """
    Separate connection pools per channel
    If email workers fail, SMS/Push unaffected
    """
    connection_pools = {
        'email': ConnectionPool(max_connections=100),
        'sms': ConnectionPool(max_connections=50),
        'push': ConnectionPool(max_connections=200)
    }
    
    def get_connection(self, channel):
        return self.connection_pools[channel].get()
    
    # Email DB issues don't affect SMS workers

# 2. BACKPRESSURE - Reject load when overwhelmed

class LoadShedding:
    def should_accept_request(self, priority):
        cpu_usage = get_cpu_usage()
        queue_depth = get_queue_depth()
        
        if cpu_usage > 90:
            # Shed low priority traffic
            if priority == 'low':
                return False, "503 Service Overloaded"
        
        if queue_depth > 100000:
            # Only accept critical
            if priority != 'critical':
                return False, "503 Queue Full"
        
        return True, "OK"

# 3. RATE LIMITING - Prevent client retry storms

class AdaptiveRateLimit:
    def __init__(self):
        self.normal_limit = 1000  # req/min per client
        self.degraded_limit = 100  # during issues
    
    def get_limit(self):
        if system_health.is_degraded():
            # Reduce limits during incidents
            return self.degraded_limit
        return self.normal_limit

# 4. TIMEOUT CONFIGURATION - Fail fast

TIMEOUTS = {
    'api_request': 5000,      # 5 seconds
    'database_query': 1000,   # 1 second
    'cache_lookup': 100,      # 100ms
    'provider_api': 10000     # 10 seconds
}

# Don't let slow operations block the system

# 5. GRACEFUL DEGRADATION

def send_notification_with_degradation(notification):
    try:
        # Try full feature set
        preferences = get_user_preferences(notification.user_id)
        template = get_template(notification.template_id)
        rendered = render_template(template, notification.data)
        send(rendered)
    except DatabaseTimeout:
        # Degrade: Skip preference check, use defaults
        template = get_cached_template(notification.template_id)
        rendered = render_template(template, notification.data)
        send(rendered)
    except TemplateServiceDown:
        # Degrade further: Use plain text
        send_plain_text(notification.message)
    except ProviderDown:
        # Last resort: Queue for later
        queue_for_retry(notification)
```

**Defense Summary:**

```
Layer 1: Request Validation
  ├─ Rate limiting
  ├─ Input validation
  └─ Authentication

Layer 2: Load Shedding
  ├─ Priority-based acceptance
  ├─ Queue depth monitoring
  └─ Adaptive rate limits

Layer 3: Isolation
  ├─ Bulkhead pattern (separate pools)
  ├─ Circuit breakers
  └─ Timeout enforcement

Layer 4: Graceful Degradation
  ├─ Fallback to cached data
  ├─ Default configurations
  └─ Simplified processing

Layer 5: Monitoring & Alerts
  ├─ Real-time metrics
  ├─ Automated alerting
  └─ Runbooks for incidents
```

-----

## **Minute 52: Data Loss Prevention (60 seconds)**

### **Critical: Never Lose Notifications**

```
DATA DURABILITY STRATEGY:

1. Write-Ahead Logging (WAL)
   ├─ Before enqueuing, write to durable storage
   ├─ If queue fails, recover from WAL
   └─ Retention: 7 days

2. Queue Persistence
   ├─ Kafka: Replicated to 3 brokers
   ├─ Data persisted to disk
   └─ Survives broker restarts

3. Audit Trail
   ├─ Every notification logged to Cassandra
   ├─ Can replay from logs if needed
   └─ Retention: 90 days

4. Dead Letter Queue
   ├─ Failed notifications never discarded
   ├─ Stored indefinitely
   └─ Manual review and replay

5. Backup Strategy
   ├─ Database: Continuous replication + daily snapshots
   ├─ Kafka: Cross-region replication
   └─ Recovery time: <1 hour
```

**Recovery Procedures:**

```python
# Scenario: Queue data corrupted, need to recover

class DisasterRecovery:
    def recover_lost_notifications(self, time_range):
        """
        Recover notifications from audit logs
        """
        # 1. Query audit logs for undelivered notifications
        lost_notifications = cassandra.query("""
            SELECT * FROM notification_logs
            WHERE status = 'queued'
              AND sent_at > ?
              AND sent_at < ?
        """, time_range.start, time_range.end)
        
        # 2. De-duplicate (check if already delivered)
        for notif in lost_notifications:
            if not self.was_delivered(notif.id):
                # 3. Re-enqueue
                queue.send(notif)
                logger.info(f"Recovered notification {notif.id}")
        
        return len(lost_notifications)
    
    def was_delivered(self, notification_id):
        # Check delivery logs
        return cassandra.query("""
            SELECT 1 FROM notification_logs
            WHERE notification_id = ?
              AND status IN ('delivered', 'opened')
            LIMIT 1
        """, notification_id) is not None
```

-----

## **Summary: Trade-offs & Failure Handling**

### **Key Trade-offs Made:**

|Decision              |Choice        |Rationale               |Trade-off           |
|----------------------|--------------|------------------------|--------------------|
|**Delivery Guarantee**|At-least-once |Simpler, faster, cheaper|Possible duplicates |
|**Batching**          |Priority-based|Balance latency and cost|Low-priority delayed|
|**Consistency**       |Eventual      |High availability       |Brief inconsistency |
|**Providers**         |Multi-provider|Resilience              |Added complexity    |
|**Caching**           |Aggressive    |Performance             |Stale data possible |

### **Failure Scenarios Covered:**

✅ Provider outage → Circuit breaker + fallback provider  
✅ Database outage → Read replicas + cached defaults  
✅ Kafka failure → Automatic rebalancing + replication  
✅ Cascading failures → Bulkheads + load shedding + timeouts  
✅ Data loss → WAL + audit logs + recovery procedures

### **Reliability Metrics:**

```
Target SLA: 99.95% availability
  = 21.6 minutes downtime/month
  = ~4 hours downtime/year

Achieved through:
  ✓ Multi-region deployment
  ✓ Automatic failover (< 30 seconds)
  ✓ No single point of failure
  ✓ Graceful degradation
  ✓ Comprehensive monitoring
```

-----

## **Transition to Final Section**

*At end of Minute 52:*

“We’ve covered the major trade-offs and how the system handles various failure scenarios. We have about 8 minutes remaining. Would you like to discuss:

1. **Monitoring & Observability** - Dashboards, alerts, metrics
1. **Security & Compliance** - GDPR, data privacy, authentication
1. **Future Enhancements** - AI-powered optimization, advanced features
1. **Cost Optimization** - Further reducing operational costs

What interests you most?”

You’re now prepared to wrap up with observability, security, or advanced topics! 🎯​​​​​​​​​​​​​​​​
