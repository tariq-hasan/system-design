# Minutes 16-35: Deep Dive into Core Components (Expanded)

## **Pre-Deep Dive: Prioritization (30 seconds)**

*After showing high-level design, ask:*

“We have about 20 minutes for deep dives. Based on your priorities, which areas should we focus on? I can go deep on:

1. **Message Queue & Reliability** - retry logic, exactly-once delivery, dead letter queues
1. **Priority & Rate Limiting** - token bucket, backpressure, provider quotas
1. **Template Management** - versioning, localization, A/B testing
1. **User Preferences** - schema design, real-time updates, do-not-disturb
1. **Scaling & Performance** - horizontal scaling, partitioning, caching

What’s most critical?”

*Adapt based on interviewer’s answer. Below covers all areas - use what’s relevant.*

-----

## **DEEP DIVE 1: Message Queue & Reliability (6-7 minutes)**

### **Minute 16-17: Queue Architecture Details (2 min)**

#### **Queue Topology Design**

*Draw detailed queue structure:*

```
                [Notification Service]
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   [Critical]      [Normal]         [Low]
    Priority       Priority       Priority
        ↓               ↓               ↓
  ┌────┼────┐    ┌────┼────┐    ┌────┼────┐
  ↓    ↓    ↓    ↓    ↓    ↓    ↓    ↓    ↓
Email SMS Push Email SMS Push Email SMS Push

Each queue partitioned by: hash(userId) % num_partitions
```

**Explain partitioning strategy (60 seconds):**

“Why partition by userId?”

- **Ordering**: All notifications for user_123 go to same partition
- **Even distribution**: Hash function spreads load evenly
- **Parallelism**: Different partitions processed by different workers
- **Scalability**: Add partitions to increase throughput

**Example:**

```
100M users, 10 partitions per queue
userId "user_12345" → hash → 7 → always goes to partition 7
All that user's notifications processed in order
```

**Queue Configuration (30 seconds):**

```yaml
Email Queue:
  - Partitions: 10
  - Retention: 7 days
  - Max message size: 256KB
  - Visibility timeout: 30 seconds
  
SMS Queue:
  - Partitions: 5 (lower volume)
  - Retention: 3 days
  
Push Queue:
  - Partitions: 20 (highest volume)
  - Retention: 3 days
```

-----

### **Minute 18-19: Reliability & Delivery Guarantees (2 min)**

#### **At-Least-Once Delivery Pattern**

*Write on whiteboard:*

**Producer Side (Notification Service):**

```python
def enqueue_notification(notification):
    # 1. Generate idempotency key (client-provided or generated)
    idempotency_key = notification.metadata.idempotency_key
    
    # 2. Check if already processed
    if redis.exists(f"processed:{idempotency_key}"):
        return {"status": "duplicate", "message": "already sent"}
    
    # 3. Write to database FIRST (for audit/recovery)
    db.notifications.insert({
        "id": notification.id,
        "idempotency_key": idempotency_key,
        "status": "pending",
        "created_at": now(),
        "payload": notification
    })
    
    # 4. Publish to queue
    kafka.produce(
        topic=get_topic(notification.channel, notification.priority),
        key=notification.user_id,  # for partitioning
        value=notification,
        callback=on_delivery_report
    )
    
    # 5. Mark as enqueued
    redis.setex(f"processed:{idempotency_key}", 86400, "1")
    
    return {"status": "queued", "notification_id": notification.id}
```

**Consumer Side (Workers):**

```python
def process_notification(message):
    notification = parse(message.value)
    
    # 1. Check if already delivered (idempotency check)
    delivery_key = f"delivered:{notification.id}"
    if redis.exists(delivery_key):
        message.ack()  # Already sent, acknowledge and skip
        return
    
    try:
        # 2. Attempt delivery
        result = send_via_provider(notification)
        
        # 3. Record success
        db.delivery_logs.insert({
            "notification_id": notification.id,
            "status": "delivered",
            "provider_response": result,
            "delivered_at": now()
        })
        
        # 4. Mark as delivered (prevent duplicates)
        redis.setex(delivery_key, 7*86400, "1")  # 7 days
        
        # 5. Acknowledge message (remove from queue)
        message.ack()
        
    except TemporaryError as e:
        # Transient failure - will retry via visibility timeout
        # Don't ack, message becomes visible again
        log.warning(f"Temporary failure: {e}")
        
    except PermanentError as e:
        # Permanent failure - send to DLQ
        dlq.send(message)
        message.ack()
```

**Key Points (30 seconds):**

- ✅ **Database write before queue**: Can recover if queue fails
- ✅ **Idempotency keys**: Prevent duplicate sends
- ✅ **Redis cache**: Fast duplicate detection
- ✅ **No ack on failure**: Message redelivered automatically

-----

### **Minute 20-21: Retry Logic & Exponential Backoff (2 min)**

#### **Retry Strategy**

*Draw retry timeline:*

```
Attempt 1: Immediate
    ↓ (fails)
Attempt 2: Wait 1 second
    ↓ (fails)
Attempt 3: Wait 2 seconds
    ↓ (fails)
Attempt 4: Wait 4 seconds
    ↓ (fails)
Attempt 5: Wait 8 seconds
    ↓ (fails)
After 5 attempts → Dead Letter Queue
```

**Implementation (90 seconds):**

```python
class RetryHandler:
    MAX_ATTEMPTS = 5
    BASE_DELAY = 1  # second
    MAX_DELAY = 300  # 5 minutes
    
    def calculate_backoff(self, attempt):
        """Exponential backoff with jitter"""
        delay = min(self.BASE_DELAY * (2 ** attempt), self.MAX_DELAY)
        jitter = random.uniform(0, delay * 0.1)  # +/- 10% jitter
        return delay + jitter
    
    def should_retry(self, error, attempt):
        """Determine if error is retryable"""
        # Temporary errors - retry
        if isinstance(error, (TimeoutError, ConnectionError, 
                             RateLimitError, ServiceUnavailable)):
            return attempt < self.MAX_ATTEMPTS
        
        # Permanent errors - don't retry
        if isinstance(error, (InvalidToken, UserOptedOut, 
                             InvalidPhoneNumber, BadRequest)):
            return False
        
        # Unknown errors - retry conservatively
        return attempt < 2

def process_with_retry(notification):
    attempt = notification.metadata.get('attempt', 0)
    
    try:
        send_notification(notification)
    except Exception as e:
        if retry_handler.should_retry(e, attempt):
            # Calculate delay
            delay = retry_handler.calculate_backoff(attempt)
            
            # Re-enqueue with delay
            notification.metadata['attempt'] = attempt + 1
            notification.metadata['scheduled_time'] = now() + delay
            
            delayed_queue.send(notification, delay=delay)
        else:
            # Move to DLQ
            dead_letter_queue.send({
                'notification': notification,
                'error': str(e),
                'attempts': attempt,
                'final_attempt_time': now()
            })
```

**Why Exponential Backoff? (30 seconds)**

- Prevents overwhelming failing service
- Gives time for transient issues to resolve
- Jitter prevents thundering herd (all retries at same time)

-----

### **Minute 22: Dead Letter Queue (DLQ) Strategy (60 seconds)**

#### **DLQ Architecture**

```
[Main Queue] → (max retries exceeded) → [Dead Letter Queue]
                                              ↓
                                    [Alert/Monitoring System]
                                              ↓
                                    [Manual Review Dashboard]
                                              ↓
                                    [Replay Mechanism]
```

**DLQ Message Schema:**

```json
{
  "original_notification": { /* full notification payload */ },
  "failure_reason": "Invalid device token",
  "error_details": "APNs returned BadDeviceToken",
  "attempt_count": 5,
  "first_attempt": "2024-03-10T10:00:00Z",
  "last_attempt": "2024-03-10T10:15:23Z",
  "dlq_timestamp": "2024-03-10T10:15:23Z",
  "classification": "permanent_error"
}
```

**DLQ Handling (30 seconds):**

1. **Alert on spike**: If DLQ messages > threshold, page on-call
1. **Classification**: Categorize errors (invalid tokens, provider outage, etc.)
1. **Auto-remediation**:

- Invalid tokens → Remove from user profile
- Rate limit errors → Slow down that channel

1. **Manual replay**: Dashboard to resend after fixing root cause

-----

## **DEEP DIVE 2: Priority & Rate Limiting (5-6 minutes)**

### **Minute 23-24: Priority Queue Implementation (2 min)**

#### **Multi-Level Priority System**

*Draw priority architecture:*

```
Priority Levels:
┌─────────────┬──────────────────┬─────────────┐
│   CRITICAL  │     NORMAL       │     LOW     │
├─────────────┼──────────────────┼─────────────┤
│ Security    │ Order confirm    │ Newsletter  │
│ alerts      │ Password reset   │ Marketing   │
│ OTP codes   │ Friend requests  │ Digest      │
│ Fraud       │ Comments         │ Suggestions │
└─────────────┴──────────────────┴─────────────┘
     ↓                ↓                 ↓
  Process         Process           Process
  immediately     within 10s        when idle
```

**Worker Resource Allocation (60 seconds):**

```python
# Worker pool configuration
WORKER_ALLOCATION = {
    'critical': {
        'workers': 50,      # Most workers
        'poll_interval': 100,  # Poll every 100ms
        'batch_size': 10
    },
    'normal': {
        'workers': 30,
        'poll_interval': 500,  # Poll every 500ms
        'batch_size': 50
    },
    'low': {
        'workers': 10,       # Fewest workers
        'poll_interval': 2000, # Poll every 2s
        'batch_size': 100    # Larger batches for efficiency
    }
}

# Dynamic scaling based on queue depth
def auto_scale_workers(queue_name, depth):
    if depth > 10000 and queue_name == 'critical':
        scale_up(queue_name, target_workers=100)
    elif depth < 1000:
        scale_down(queue_name, target_workers=20)
```

**Priority Starvation Prevention (30 seconds):**

```
Problem: Low priority queue never processed if high priority busy

Solution: Weighted round-robin
- Critical: 70% of worker time
- Normal: 20% of worker time
- Low: 10% of worker time (guaranteed minimum)
```

-----

### **Minute 25-26: Rate Limiting (Token Bucket) (2 min)**

#### **Multi-Layer Rate Limiting**

*Draw rate limiting layers:*

```
Layer 1: API Gateway
  └─ Per-client: 1000 requests/minute

Layer 2: Per-user sending limits
  └─ User can receive max 50 notifications/hour

Layer 3: Per-channel limits
  └─ Email: 20/day, SMS: 10/day, Push: 100/day

Layer 4: Provider limits
  └─ Twilio: 1000 SMS/second globally
```

**Token Bucket Algorithm Implementation (90 seconds):**

```python
class TokenBucket:
    """
    Distributed token bucket using Redis
    """
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def allow_request(self, key, max_tokens, refill_rate, 
                      refill_period=60):
        """
        key: "rate_limit:user:12345:email"
        max_tokens: 20 (max emails per period)
        refill_rate: 20 tokens
        refill_period: 86400 seconds (daily)
        """
        now = time.time()
        
        # Lua script for atomic operation
        script = """
        local key = KEYS[1]
        local max_tokens = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local refill_period = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or max_tokens
        local last_refill = tonumber(bucket[2]) or now
        
        -- Calculate refill
        local time_passed = now - last_refill
        local refills = math.floor(time_passed / refill_period)
        tokens = math.min(max_tokens, tokens + (refills * refill_rate))
        
        -- Try to consume token
        if tokens >= 1 then
            tokens = tokens - 1
            redis.call('HMSET', key, 
                      'tokens', tokens, 
                      'last_refill', now)
            redis.call('EXPIRE', key, refill_period * 2)
            return {1, tokens}  -- allowed, remaining tokens
        else
            return {0, tokens}  -- denied, remaining tokens
        end
        """
        
        result = self.redis.eval(script, 1, key, 
                                max_tokens, refill_rate, 
                                refill_period, now)
        
        return {
            'allowed': bool(result[0]),
            'remaining': result[1],
            'retry_after': refill_period if not result[0] else None
        }

# Usage in worker
def send_notification(notification):
    user_id = notification.user_id
    channel = notification.channel
    
    # Check user-level rate limit
    limit_key = f"rate_limit:user:{user_id}:{channel}"
    result = token_bucket.allow_request(
        key=limit_key,
        max_tokens=get_limit(channel),  # email: 20, sms: 10
        refill_rate=get_limit(channel),
        refill_period=86400  # daily
    )
    
    if not result['allowed']:
        # Rate limited - delay or drop
        if notification.priority == 'critical':
            # Critical notifications bypass user limits (but not provider limits)
            pass
        else:
            # Re-queue for later
            delay_notification(notification, result['retry_after'])
            return
    
    # Proceed with sending
    provider.send(notification)
```

-----

### **Minute 27-28: Provider Rate Limiting & Backpressure (2 min)**

#### **Provider-Level Rate Limiting**

**Challenge:**

- SendGrid: 10,000 emails/second
- Twilio: 1,000 SMS/second
- FCM: 5,000 requests/second

**Solution: Global Rate Limiter (90 seconds)**

```python
class GlobalProviderRateLimiter:
    """
    Centralized rate limiting for providers
    Uses Redis sorted sets for sliding window
    """
    
    def check_provider_limit(self, provider, limit_per_second):
        """
        Sliding window rate limiter
        """
        now = time.time()
        window_start = now - 1  # 1 second window
        
        key = f"provider_rate:{provider}"
        
        pipe = redis.pipeline()
        
        # Remove old entries outside window
        pipe.zremrangebyscore(key, '-inf', window_start)
        
        # Count requests in current window
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {uuid.uuid4().hex: now})
        
        # Set expiry
        pipe.expire(key, 2)
        
        results = pipe.execute()
        current_count = results[1]
        
        if current_count >= limit_per_second:
            return False, limit_per_second - current_count
        
        return True, limit_per_second - current_count - 1

# Worker implementation with backpressure
class NotificationWorker:
    def process_batch(self, messages):
        provider = self.get_provider()  # SendGrid, Twilio, etc.
        
        for msg in messages:
            # Check provider rate limit
            allowed, remaining = rate_limiter.check_provider_limit(
                provider.name, 
                provider.rate_limit
            )
            
            if not allowed:
                # Backpressure: slow down consumption
                time.sleep(0.1)  # Wait 100ms
                
                # Re-queue message
                self.queue.send(msg, delay=1)
                continue
            
            # Send notification
            try:
                provider.send(msg)
            except RateLimitError:
                # Provider returned 429
                # Exponential backoff
                self.backoff_delay *= 2
                time.sleep(self.backoff_delay)
                self.queue.send(msg, delay=self.backoff_delay)
```

**Backpressure Mechanisms (30 seconds):**

```
When overwhelmed:
1. Slow down queue consumption (increase poll interval)
2. Reduce worker batch size
3. Implement circuit breaker (stop completely if failure rate > 50%)
4. Auto-scale workers down to reduce load
5. Drop low-priority notifications (with user consent)
```

-----

## **DEEP DIVE 3: Template Management (3-4 minutes)**

### **Minute 29-30: Template Service Architecture (2 min)**

#### **Template Storage & Versioning**

*Draw template service:*

```
[Template Service]
        ↓
┌──────────────────┐
│  Template Store  │
│  (Database/S3)   │
└──────────────────┘
        ↓
  Template Schema:
  ├─ ID: "order_confirmation_v3"
  ├─ Version: 3
  ├─ Channel: email
  ├─ Language: en_US
  ├─ Subject: "Order {{orderId}} confirmed!"
  ├─ Body: HTML template
  ├─ Variables: [orderId, amount, deliveryDate]
  ├─ Created: timestamp
  └─ Active: true
```

**Template Schema Design (60 seconds):**

```json
{
  "templateId": "order_confirmation",
  "version": 3,
  "channel": "email",
  "variants": [
    {
      "language": "en_US",
      "subject": "Order {{orderId}} confirmed!",
      "htmlBody": "<html>...</html>",
      "textBody": "Your order {{orderId}}...",
      "requiredVariables": ["orderId", "amount", "estimatedDelivery"],
      "previewData": {
        "orderId": "ORD-123",
        "amount": "$99.99"
      }
    },
    {
      "language": "es_ES",
      "subject": "¡Pedido {{orderId}} confirmado!",
      "htmlBody": "<html>...</html>",
      "textBody": "Tu pedido {{orderId}}...",
      "requiredVariables": ["orderId", "amount", "estimatedDelivery"]
    }
  ],
  "metadata": {
    "createdBy": "user@example.com",
    "createdAt": "2024-03-01T10:00:00Z",
    "status": "active",
    "abTest": {
      "enabled": true,
      "variant_split": {"v2": 0.3, "v3": 0.7}
    }
  }
}
```

**Template Rendering (60 seconds):**

```python
class TemplateRenderer:
    def __init__(self, cache, template_store):
        self.cache = cache  # Redis
        self.store = template_store
    
    def render(self, template_id, user_data, user_locale):
        # 1. Fetch template (with caching)
        cache_key = f"template:{template_id}:v{self.get_version(template_id)}"
        
        template = self.cache.get(cache_key)
        if not template:
            template = self.store.get(template_id)
            self.cache.setex(cache_key, 3600, template)  # Cache 1 hour
        
        # 2. Select variant based on A/B test
        if template.ab_test.enabled:
            variant = self.select_ab_variant(
                template.ab_test.variant_split,
                user_data.user_id
            )
            template = template.variants[variant]
        
        # 3. Select language
        localized = self.get_localized_version(template, user_locale)
        
        # 4. Validate variables
        missing = set(localized.required_variables) - set(user_data.keys())
        if missing:
            raise MissingVariablesError(f"Missing: {missing}")
        
        # 5. Render with Jinja2/Handlebars
        rendered_subject = jinja2.render(localized.subject, user_data)
        rendered_body = jinja2.render(localized.html_body, user_data)
        
        return {
            'subject': rendered_subject,
            'html': rendered_body,
            'text': jinja2.render(localized.text_body, user_data)
        }
    
    def select_ab_variant(self, split, user_id):
        """Consistent hash for A/B testing"""
        hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        percentile = (hash_val % 100) / 100.0
        
        cumulative = 0
        for variant, percentage in split.items():
            cumulative += percentage
            if percentile < cumulative:
                return variant
        
        return list(split.keys())[0]  # Default
```

-----

### **Minute 31: A/B Testing & Analytics (60 seconds)**

#### **A/B Test Implementation**

**Use Case:** Testing two email subject lines

```json
Template A/B Configuration:
{
  "templateId": "promotional_email",
  "abTest": {
    "enabled": true,
    "testName": "subject_line_test_march_2024",
    "variants": {
      "control": {
        "percentage": 0.5,
        "subject": "50% off everything!",
        "version": "v2"
      },
      "variant_a": {
        "percentage": 0.5,
        "subject": "Exclusive: Half price sale today",
        "version": "v3"
      }
    },
    "metrics_to_track": ["open_rate", "click_rate", "conversion_rate"],
    "duration_days": 7
  }
}
```

**Analytics Tracking:**

```python
def track_notification_event(notification_id, event_type, metadata):
    """
    event_type: 'sent', 'delivered', 'opened', 'clicked', 'converted'
    """
    analytics_db.insert({
        'notification_id': notification_id,
        'user_id': metadata.user_id,
        'template_id': metadata.template_id,
        'template_version': metadata.template_version,
        'ab_variant': metadata.ab_variant,
        'event_type': event_type,
        'timestamp': now(),
        'metadata': metadata
    })
    
    # Update real-time metrics
    redis.hincrby(
        f"metrics:{metadata.template_id}:{metadata.ab_variant}",
        event_type,
        1
    )
```

-----

## **DEEP DIVE 4: User Preferences (3-4 minutes)**

### **Minute 32-33: Preference Schema & Storage (2 min)**

#### **User Preferences Database Design**

```sql
-- User Preferences Table
CREATE TABLE user_notification_preferences (
    user_id VARCHAR(255) PRIMARY KEY,
    
    -- Global settings
    global_enabled BOOLEAN DEFAULT true,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en_US',
    
    -- Do Not Disturb
    dnd_enabled BOOLEAN DEFAULT false,
    dnd_start_time TIME,  -- e.g., '22:00:00'
    dnd_end_time TIME,    -- e.g., '08:00:00'
    dnd_days JSON,        -- ['MON', 'TUE', 'WED', 'THU', 'FRI']
    
    -- Channel preferences (JSON for flexibility)
    channel_preferences JSON,
    -- Example: {
    --   "email": {"enabled": true, "frequency_cap": 20},
    --   "sms": {"enabled": false},
    --   "push": {"enabled": true, "frequency_cap": 100}
    -- }
    
    -- Category preferences
    category_preferences JSON,
    -- Example: {
    --   "transactional": {"email": true, "sms": true, "push": true},
    --   "marketing": {"email": true, "sms": false, "push": false},
    --   "social": {"email": false, "sms": false, "push": true}
    -- }
    
    -- Frequency caps (per day)
    daily_cap_email INTEGER DEFAULT 20,
    daily_cap_sms INTEGER DEFAULT 10,
    daily_cap_push INTEGER DEFAULT 100,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_user_id (user_id)
);

-- Opt-out history (audit trail)
CREATE TABLE notification_opt_outs (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    channel VARCHAR(50),
    category VARCHAR(100),
    opted_out_at TIMESTAMP,
    reason TEXT,
    
    INDEX idx_user_channel (user_id, channel)
);
```

**Preference Checking Logic (90 seconds):**

```python
class PreferenceChecker:
    def __init__(self, db, cache):
        self.db = db
        self.cache = cache  # Redis
    
    def should_send(self, user_id, notification):
        # 1. Fetch preferences (cached)
        prefs = self.get_user_preferences(user_id)
        
        if not prefs.global_enabled:
            return False, "User disabled all notifications"
        
        # 2. Check channel opt-out
        channel = notification.channel
        if not prefs.channel_preferences.get(channel, {}).get('enabled', True):
            return False, f"User opted out of {channel}"
        
        # 3. Check category opt-out
        category = notification.category  # 'transactional', 'marketing', etc.
        if not prefs.category_preferences.get(category, {}).get(channel, True):
            return False, f"User opted out of {category} on {channel}"
        
        # 4. Check Do Not Disturb
        if self.is_dnd_active(prefs, notification):
            if notification.priority != 'critical':
                return False, "Do Not Disturb active"
        
        # 5. Check frequency cap
        if not self.check_frequency_cap(user_id, channel, prefs):
            if notification.priority != 'critical':
                return False, "Frequency cap exceeded"
        
        return True, "OK"
    
    def is_dnd_active(self, prefs, notification):
        if not prefs.dnd_enabled:
            return False
        
        # Convert notification time to user's timezone
        user_tz = pytz.timezone(prefs.timezone)
        current_time = datetime.now(user_tz).time()
        current_day = datetime.now(user_tz).strftime('%a').upper()
        
        # Check if current day is in DND days
        if current_day not in prefs.dnd_days:
            return False
        
        # Check if current time is in DND window
        if prefs.dnd_start_time <= current_time <= prefs.dnd_end_time:
            return True
        
        return False
    
    def check_frequency_cap(self, user_id, channel, prefs):
        # Count notifications sent today
        key = f"freq_cap:{user_id}:{channel}:{date.today()}"
        count = self.cache.get(key) or 0
        
        cap = getattr(prefs, f'daily_cap_{channel}', float('inf'))
        
        if count >= cap:
            return False
        
        # Increment counter
        self.cache.incr(key)
        self.cache.expire(key, 86400)  # Expire after 24 hours
        
        return True
    
    def get_user_preferences(self, user_id):
        # Try cache first
        cache_key = f"user_prefs:{user_id}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Fetch from DB
        prefs = self.db.query(
            "SELECT * FROM user_notification_preferences WHERE user_id = ?",
            user_id
        )
        
        if not prefs:
            # Return defaults
            prefs = self.get_default_preferences()
        
        # Cache for 5 minutes
        self.cache.setex(cache_key, 300, json.dumps(prefs))
        
        return prefs
```

-----

### **Minute 34: Real-time Preference Updates (60 seconds)**

#### **Handling Preference Changes**

**Challenge:** User updates preferences, notifications in queue must respect new settings

**Solution: Cache Invalidation + Re-check**

```python
# API endpoint for updating preferences
@app.post("/api/v1/users/{user_id}/preferences")
def update_preferences(user_id, new_preferences):
    # 1. Validate preferences
    validate_preferences(new_preferences)
    
    # 2. Update database
    db.update_user_preferences(user_id, new_preferences)
    
    # 3. Invalidate cache immediately
    cache.delete(f"user_prefs:{user_id}")
    
    # 4. Publish preference change event
    event_bus.publish("user.preferences.updated", {
        "user_id": user_id,
        "timestamp": now(),
        "changes": new_preferences
    })
    
    return {"status": "updated"}

# Workers listen for preference change events
def on_preference_update(event):
    user_id = event.user_id
    
    # Re-check all pending notifications for this user
    pending = queue.get_pending_for_user(user_id)
    
    for notification in pending:
        should_send, reason = preference_checker.should_send(
            user_id, 
            notification
        )
        
        if not should_send:
            # Remove from queue or mark as cancelled
            queue.cancel(notification.id)
            
            # Log cancellation
            db.notification_logs.insert({
                'notification_id': notification.id,
                'user_id': user_id,
                'status': 'cancelled',
                'reason': reason,
                'cancelled_at': now()
            })
```

**Edge Case: Opt-out Links (30 seconds)**

```python
# Email contains: https://api.example.com/unsubscribe?token=xyz

@app.get("/unsubscribe")
def unsubscribe(token):
    # Decode token (contains user_id, channel, category)
    data = jwt.decode(token)
    
    # Update preferences
    update_preferences(data.user_id, {
        'channel_preferences': {
            data.channel: {'enabled': False}
        }
    })
    
    # Honor immediately - invalidate cache
    cache.delete(f"user_prefs:{data.user_id}")
    
    return "You've been unsubscribed"
```

-----

## **DEEP DIVE 5: Database & Data Model (Bonus - 2-3 minutes if time permits)**

### **Minute 35: Data Storage Strategy (Optional)**

#### **Database Choices by Use Case**

*Draw database architecture:*

```
┌─────────────────────────────────────────┐
│         Data Storage Layer              │
├─────────────────────────────────────────┤
│                                         │
│  [PostgreSQL - User Preferences]        │
│   - Strong consistency                  │
│   - ACID transactions                   │
│   - ~100M rows                          │
│                                         │
│  [Cassandra - Notification Logs]        │
│   - High write throughput               │
│   - Time-series data                    │
│   - Billions of records                 │
│   - Partition by: (user_id, timestamp)  │
│                                         │
│  [Redis - Caching & Rate Limiting]      │
│   - User preferences cache              │
│   - Token buckets                       │
│   - Idempotency keys                    │
│   - Real-time counters                  │
│                                         │
│  [S3 - Templates & Archives]            │
│   - Template HTML/images                │
│   - Old notification archives           │
│   - Cost-efficient long-term storage    │
│                                         │
└─────────────────────────────────────────┘
```

**Notification Logs Schema (Cassandra):**

```sql
CREATE TABLE notification_logs (
    user_id TEXT,
    notification_id UUID,
    sent_at TIMESTAMP,
    
    -- Partition key: user_id
    -- Clustering key: sent_at (DESC) for time-ordered queries
    
    channel TEXT,
    category TEXT,
    priority TEXT,
    
    status TEXT,  -- 'queued', 'sent', 'delivered', 'failed', 'opened', 'clicked'
    
    template_id TEXT,
    template_version INT,
    
    provider TEXT,  -- 'sendgrid', 'twilio', 'fcm'
    provider_message_id TEXT,
    
    error_message TEXT,
    retry_count INT,
    
    metadata MAP<TEXT, TEXT>,
    
    PRIMARY KEY (user_id, sent_at, notification_id)
) WITH CLUSTERING ORDER BY (sent_at DESC);

-- Query examples:
-- Get user's recent notifications:
SELECT * FROM notification_logs 
WHERE user_id = 'user_123' 
LIMIT 50;

-- Get notifications in time range:
SELECT * FROM notification_logs 
WHERE user_id = 'user_123' 
  AND sent_at > '2024-03-01' 
  AND sent_at < '2024-03-31';
```

**Why these choices? (30 seconds)**

|Database      |Use Case            |Reason                                     |
|--------------|--------------------|-------------------------------------------|
|**PostgreSQL**|User preferences    |Need ACID, complex queries, joins          |
|**Cassandra** |Notification logs   |High write volume, time-series, scalable   |
|**Redis**     |Cache, rate limiting|Sub-millisecond latency, atomic operations |
|**S3**        |Templates, archives |Cost-effective, durability, CDN integration|

-----

## **Key Takeaways from Deep Dives**

### **What You Should Have Covered:**

✅ **Message Queue & Reliability (6-7 min)**

- Partitioning strategy (userId hashing)
- At-least-once delivery with idempotency
- Retry logic with exponential backoff
- Dead letter queue handling

✅ **Priority & Rate Limiting (5-6 min)**

- Multi-level priority queues
- Token bucket algorithm implementation
- Provider-level rate limiting
- Backpressure mechanisms

✅ **Template Management (3-4 min)**

- Template storage and versioning
- Multi-language support
- A/B testing framework
- Rendering with caching

✅ **User Preferences (3-4 min)**

- Preference schema design
- Do-not-disturb implementation
- Frequency capping
- Real-time preference updates

-----

## **Interviewer Signal Reading**

**Watch for these cues to adjust:**

|Interviewer Reaction               |Your Response                                                        |
|-----------------------------------|---------------------------------------------------------------------|
|“Tell me more about X”             |Deep dive further into that area                                     |
|“That makes sense, what about Y?”  |Move to next topic quickly                                           |
|Checking watch                     |Speed up, summarize remaining points                                 |
|Taking lots of notes               |Good sign - continue at current pace                                 |
|“How would you handle Z edge case?”|Address it, but don’t rabbit hole                                    |
|Silence                            |Ask: “Should I continue or would you like to explore something else?”|

-----

## **Common Deep Dive Mistakes**

❌ **Going too deep too early**: Don’t explain every line of code unless asked  
❌ **Ignoring trade-offs**: Always mention “We could also do X, but Y is better because…”  
❌ **Over-engineering**: Keep it practical for the stated scale  
❌ **Missing the “why”**: Always explain reasoning behind choices  
❌ **Not using concrete examples**: Abstract explanations are hard to follow  
❌ **Forgetting failure scenarios**: Always discuss what happens when things break

-----

## **Deep Dive Success Checklist**

After each deep dive, you should have covered:

- [ ] **What** - What is this component/mechanism?
- [ ] **Why** - Why is it needed? What problem does it solve?
- [ ] **How** - How does it work? (pseudo-code level detail)
- [ ] **Trade-offs** - What are alternatives? Why this choice?
- [ ] **Failure modes** - What happens when it breaks?
- [ ] **Scale** - How does it handle growth?
- [ ] **Monitoring** - How do we know it’s working?

-----

## **Transition to Next Section**

*At the end of Minute 35, transition with:*

“We’ve covered the core components in detail. We have about 25 minutes left. Should we discuss:

1. **Scaling strategies** - How to handle 10x growth
1. **Failure scenarios** - Provider outages, cascading failures
1. **Monitoring & observability** - What metrics matter
1. **Additional features** - Analytics, personalization, multi-tenancy

What would be most valuable?”

**This shows:**

- ✅ Time awareness
- ✅ Structured thinking
- ✅ Collaboration with interviewer
- ✅ Understanding there’s more depth available

-----

## **Pro Tips for Deep Dives**

💡 **Use analogies**: “Token bucket is like a water bucket with a hole - water drips in steadily, requests drain it”

💡 **Draw timelines**: Show sequence of events over time for retry logic

💡 **Use real numbers**: “At 12K QPS, with 100ms latency, we need X workers”

💡 **Reference real systems**: “This is similar to how Kafka handles…” (shows you know production systems)

💡 **Code when helpful**: Pseudo-code clarifies complex logic, but don’t over-code

💡 **Layer your explanation**: Start high-level, then go deeper if interviewer wants more

💡 **Connect back to requirements**: “Remember we said 99.9% availability? This retry logic helps us achieve that”

-----

You’re now equipped to handle deep technical discussions on any component the interviewer wants to explore! 🚀​​​​​​​​​​​​​​​​
