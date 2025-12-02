# Minutes 36-45: Scale & Performance (Expanded)

## **Minute 36: Establish Scale Requirements (60 seconds)**

### **Opening the Scale Discussion**

*Transition from deep dives:*

“Now let’s talk about scale and performance. Let me first establish our target numbers based on the requirements we discussed.”

### **Back-of-the-Envelope Calculations**

*Write on whiteboard:*

```
GIVEN REQUIREMENTS:
- 100M daily active users (DAU)
- 10 notifications per user per day (average)
- Peak traffic: 3x average

CALCULATIONS:

Daily Volume:
- Total notifications/day = 100M users × 10 = 1 billion notifications/day

Average QPS (Queries Per Second):
- 1B notifications / 86,400 seconds = ~11,574 notifications/sec
- Round up: ~12K QPS average

Peak QPS:
- Peak = 3x average = 36K QPS
- Add buffer: Design for 50K QPS

Channel Distribution (assume):
- Push: 60% = 30K QPS peak
- Email: 30% = 15K QPS peak  
- SMS: 10% = 5K QPS peak

Storage Requirements:
- Per notification metadata: ~2KB
- Daily storage: 1B × 2KB = 2TB/day
- Monthly: 60TB/month
- Yearly: 720TB/year (with compression ~300TB)

Network Bandwidth:
- Average: 12K req/sec × 2KB = 24 MB/sec
- Peak: 50K req/sec × 2KB = 100 MB/sec
```

**Validation Check (15 seconds):**
“These numbers make sense? Any adjustments before we discuss how to handle this scale?”

-----

## **Minute 37-38: Horizontal Scaling Strategy (2 minutes)**

### **Scaling Each Component**

*Draw scaled architecture on whiteboard:*

```
                   [Global Load Balancer - DNS]
                             ↓
        ┌────────────────────┼────────────────────┐
        ↓                    ↓                    ↓
   [Region: US-EAST]   [Region: US-WEST]   [Region: EU]
        ↓                    ↓                    ↓
  [LB] → [API Gateway × N instances]
        ↓
  [LB] → [Notification Service × N instances]
        ↓
  [Kafka Cluster - Partitioned]
   - 50 partitions per topic
   - 3x replication
        ↓
  [Worker Pool - Auto-scaled]
   - Email Workers: 100-500 instances
   - SMS Workers: 50-200 instances
   - Push Workers: 200-1000 instances
```

### **Component Scaling Details (90 seconds)**

#### **1. API Gateway / Notification Service**

```yaml
Scaling Configuration:

API Gateway:
  - Stateless service (easy to scale)
  - Horizontal scaling: 50-100 instances
  - CPU: 2-4 cores per instance
  - Memory: 4-8 GB per instance
  - Each instance handles: 500-1000 QPS
  
Auto-scaling Rules:
  - Scale up if: CPU > 70% for 2 minutes
  - Scale up if: Request latency p99 > 500ms
  - Scale down if: CPU < 30% for 10 minutes
  - Min instances: 20 (always-on)
  - Max instances: 200

Notification Service:
  - Similar scaling as API Gateway
  - 30-50 instances baseline
  - Database connection pooling: 20 connections per instance
  - Total DB connections: 50 instances × 20 = 1000 connections
```

#### **2. Message Queue (Kafka) Scaling**

```yaml
Kafka Cluster Configuration:

Brokers: 12 nodes (minimum)
  - Distributed across 3 availability zones
  - 4 brokers per AZ
  
Partitions per Topic:
  - High priority: 50 partitions
  - Normal priority: 100 partitions
  - Low priority: 50 partitions
  
Why 50-100 partitions?
  - Allows 50-100 parallel consumers
  - Each partition: ~500-1000 QPS
  - Total throughput: 50K+ QPS
  
Replication:
  - Replication factor: 3
  - Min in-sync replicas: 2
  - Ensures durability even if 1 broker fails

Storage per Broker:
  - Retention: 7 days
  - Daily data: 2TB
  - Per broker: 2TB × 7 days / 12 brokers = ~1.2TB
  - Provision: 2TB SSD per broker (with headroom)
```

#### **3. Worker Pool Auto-Scaling**

*Draw worker scaling diagram:*

```
Queue Depth Monitoring → Auto-scaler → Worker Pool

If queue_depth > 10,000:
    target_workers = queue_depth / 100
    scale_to(min(target_workers, MAX_WORKERS))

If queue_depth < 1,000:
    target_workers = MAX(20, current_workers * 0.7)
    scale_to(target_workers)
```

**Worker Scaling Strategy:**

```python
class WorkerAutoScaler:
    def __init__(self, channel):
        self.channel = channel
        self.min_workers = CONFIG[channel]['min_workers']
        self.max_workers = CONFIG[channel]['max_workers']
    
    def calculate_desired_workers(self, metrics):
        queue_depth = metrics.queue_depth
        current_throughput = metrics.messages_per_second
        avg_processing_time = metrics.avg_processing_time_ms
        
        # Target: Keep queue depth < 5000 messages
        # Each worker processes ~10 messages/second
        
        if queue_depth > 5000:
            # Aggressive scale up
            desired = queue_depth / (10 * 60)  # Clear in 1 minute
            return min(desired, self.max_workers)
        
        elif queue_depth < 1000:
            # Scale down slowly
            return max(
                self.min_workers,
                current_throughput / 10  # 10 msg/sec per worker
            )
        
        else:
            # Maintain current level
            return metrics.current_workers

# Example configuration
CONFIG = {
    'email': {
        'min_workers': 50,
        'max_workers': 500,
        'target_msgs_per_worker': 10  # per second
    },
    'sms': {
        'min_workers': 20,
        'max_workers': 200,
        'target_msgs_per_worker': 15
    },
    'push': {
        'min_workers': 100,
        'max_workers': 1000,
        'target_msgs_per_worker': 20
    }
}
```

-----

## **Minute 39-40: Database Scaling (2 minutes)**

### **Database Sharding Strategy**

*Draw sharding architecture:*

```
                [Application Layer]
                        ↓
              [Shard Router/Proxy]
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   [Shard 0]       [Shard 1]       [Shard 2]
   Users:          Users:          Users:
   0-33M           34M-66M         67M-100M
   
   hash(user_id) % 3 = shard_id
```

#### **User Preferences DB Sharding (90 seconds)**

```sql
-- Sharding key: user_id
-- Sharding function: hash(user_id) % num_shards

Shard Configuration:
  - Total shards: 10 (start with 10, can grow to 100)
  - Users per shard: 10M users
  - Each shard: PostgreSQL instance
  - Replication: Primary + 2 read replicas per shard

Shard 0: users where hash(user_id) % 10 = 0
Shard 1: users where hash(user_id) % 10 = 1
...
Shard 9: users where hash(user_id) % 10 = 9

Query Routing:
def get_shard_for_user(user_id):
    shard_id = hash(user_id) % NUM_SHARDS
    return SHARD_CONNECTIONS[shard_id]

# Usage
user_id = "user_12345"
shard = get_shard_for_user(user_id)
preferences = shard.query(
    "SELECT * FROM user_preferences WHERE user_id = ?",
    user_id
)

Read/Write Split:
  - Writes → Primary
  - Reads → Load balanced across replicas
  - Eventual consistency acceptable (cache helps)

Storage per Shard:
  - 10M users × 5KB per user = 50GB
  - Indexes: ~20GB
  - Total: ~100GB per shard
  - Well within single PostgreSQL instance capacity
```

#### **Notification Logs Sharding (Cassandra)**

```sql
-- Cassandra naturally distributes data

Table: notification_logs
  Partition Key: user_id
  Clustering Key: sent_at (DESC)
  
Data Distribution:
  - Automatic across cluster nodes
  - Replication factor: 3
  - Consistency: LOCAL_QUORUM

Cluster Size:
  - Nodes: 20 (expandable)
  - Data per node: 60TB total / 3 replication / 20 nodes = ~1TB/node
  - Each node: 2TB SSD (50% capacity)

Query Performance:
  - Single partition queries (by user_id): <10ms
  - Range queries (time-based): <50ms
  - Write throughput: 50K+ writes/sec
```

-----

## **Minute 41-42: Caching Strategy (2 minutes)**

### **Multi-Layer Caching Architecture**

*Draw caching layers:*

```
[Application] → [L1: Local Cache] → [L2: Redis Cache] → [L3: Database]
                  (In-memory)         (Distributed)        (Source of Truth)
                  
Cache Hit Ratios (target):
  L1: 40% (avoid network call)
  L2: 55% (avoid DB query)
  L3: 5% (cache miss, query DB)
```

#### **Caching Implementation (90 seconds)**

**1. User Preferences Caching**

```python
class CachedPreferenceStore:
    def __init__(self):
        self.local_cache = TTLCache(maxsize=10000, ttl=60)  # L1: 1 min
        self.redis = RedisClient()  # L2: 5 min
        self.db = Database()  # L3: Source
    
    def get_preferences(self, user_id):
        # L1: Check local cache (in-process)
        if user_id in self.local_cache:
            metrics.incr('cache.l1.hit')
            return self.local_cache[user_id]
        
        # L2: Check Redis
        redis_key = f"prefs:{user_id}"
        cached = self.redis.get(redis_key)
        if cached:
            metrics.incr('cache.l2.hit')
            prefs = json.loads(cached)
            self.local_cache[user_id] = prefs  # Populate L1
            return prefs
        
        # L3: Query database
        metrics.incr('cache.miss')
        prefs = self.db.query(
            "SELECT * FROM user_preferences WHERE user_id = ?",
            user_id
        )
        
        if not prefs:
            prefs = self.get_default_preferences()
        
        # Populate caches
        self.redis.setex(redis_key, 300, json.dumps(prefs))  # 5 min
        self.local_cache[user_id] = prefs  # 1 min
        
        return prefs
    
    def invalidate(self, user_id):
        """Called when preferences updated"""
        # Invalidate all layers
        if user_id in self.local_cache:
            del self.local_cache[user_id]
        
        self.redis.delete(f"prefs:{user_id}")
        
        # Publish invalidation event for other instances
        self.redis.publish('cache.invalidate', json.dumps({
            'type': 'user_preferences',
            'user_id': user_id
        }))
```

**2. Template Caching**

```python
class TemplateCacheStrategy:
    """
    Templates change infrequently - aggressive caching
    """
    
    CACHE_TTL = 3600  # 1 hour
    
    def get_template(self, template_id, version):
        cache_key = f"template:{template_id}:v{version}"
        
        # Check Redis
        cached = redis.get(cache_key)
        if cached:
            return msgpack.unpackb(cached)  # Fast deserialization
        
        # Fetch from S3/DB
        template = s3.get_object(
            Bucket='templates',
            Key=f'{template_id}/v{version}.json'
        )
        
        # Cache with long TTL
        redis.setex(
            cache_key,
            self.CACHE_TTL,
            msgpack.packb(template)
        )
        
        return template
    
    def warm_cache(self, popular_templates):
        """Pre-populate cache with popular templates"""
        for template_id, version in popular_templates:
            self.get_template(template_id, version)
```

**3. Rate Limit State Caching**

```python
# Already covered in deep dive - Redis-based token bucket
# No additional cache needed (Redis IS the cache)

Cache Key Examples:
  - "rate:user:12345:email:2024-03-10" → token count
  - "rate:provider:sendgrid:2024-03-10:14:30" → requests in window
  - "idempotency:abc-123-def" → already processed flag
```

#### **Cache Sizing (30 seconds)**

```
Redis Cluster Configuration:

User Preferences Cache:
  - 100M users × 5KB per user = 500GB
  - Hit ratio: 95% (highly read-heavy)
  - Hot data (active users): 20M users = 100GB
  - Redis cluster: 6 nodes × 32GB = 192GB (sufficient)

Template Cache:
  - 1,000 active templates × 50KB = 50MB
  - Negligible

Rate Limit State:
  - Active users per day: 100M
  - State per user: 1KB
  - Total: 100GB (fits in same cluster)

Total Redis Memory: ~150GB → 6 nodes × 32GB = 192GB ✓
```

-----

## **Minute 43-44: Performance Optimizations (2 minutes)**

### **Optimization Strategies**

#### **1. Batch Processing (45 seconds)**

*Draw batching flow:*

```
Without Batching:
  Worker → [Send 1] → Provider (100ms)
  Worker → [Send 1] → Provider (100ms)  
  Worker → [Send 1] → Provider (100ms)
  Throughput: 10 requests/sec per worker

With Batching:
  Worker → [Batch 100] → Provider (200ms)
  Throughput: 500 requests/sec per worker
  50x improvement!
```

**Batch Processing Implementation:**

```python
class BatchProcessor:
    def __init__(self, provider, batch_size=100, max_wait_ms=1000):
        self.provider = provider
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.pending_batch = []
        self.last_flush = time.time()
    
    def add_to_batch(self, notification):
        self.pending_batch.append(notification)
        
        # Flush if batch full or max wait exceeded
        if (len(self.pending_batch) >= self.batch_size or 
            (time.time() - self.last_flush) * 1000 > self.max_wait_ms):
            self.flush()
    
    def flush(self):
        if not self.pending_batch:
            return
        
        # Send batch to provider
        try:
            # Many providers support batch APIs
            results = self.provider.send_batch(self.pending_batch)
            
            # Process results
            for notification, result in zip(self.pending_batch, results):
                if result.success:
                    self.mark_delivered(notification)
                else:
                    self.handle_failure(notification, result.error)
        
        finally:
            self.pending_batch = []
            self.last_flush = time.time()

# Provider batch API examples:
# - SendGrid: 1000 emails per API call
# - FCM: 500 push notifications per call
# - Twilio: 100 SMS per call (via messaging service)
```

#### **2. Connection Pooling (30 seconds)**

```python
# Reuse HTTP connections to providers

import urllib3

class ProviderClient:
    def __init__(self, provider_config):
        # Connection pool
        self.http = urllib3.PoolManager(
            maxsize=100,  # 100 persistent connections
            block=True,
            timeout=urllib3.Timeout(connect=2.0, read=5.0)
        )
        
        # Keep-alive connections reduce latency:
        # - New connection: ~100ms (TCP + TLS handshake)
        # - Pooled connection: ~2ms
        
        self.provider_url = provider_config.url
    
    def send(self, notification):
        # Reuses existing connection from pool
        response = self.http.request(
            'POST',
            f'{self.provider_url}/send',
            body=json.dumps(notification),
            headers={'Content-Type': 'application/json'}
        )
        return response
```

#### **3. Database Query Optimization (45 seconds)**

```sql
-- Inefficient: N+1 query problem
for user_id in user_ids:
    prefs = db.query("SELECT * FROM user_preferences WHERE user_id = ?", user_id)

-- Efficient: Batch query
user_ids = ['user_1', 'user_2', ..., 'user_100']
prefs_map = db.query("""
    SELECT * FROM user_preferences 
    WHERE user_id IN (?, ?, ..., ?)
""", *user_ids)

-- Use indexes
CREATE INDEX idx_user_channel ON user_preferences(user_id, channel);
CREATE INDEX idx_notification_status ON notification_logs(status, created_at);

-- Use read replicas for heavy queries
# Write to primary
primary_db.execute("UPDATE user_preferences SET ...")

# Read from replica (analytics, reports)
replica_db.query("SELECT COUNT(*) FROM notification_logs WHERE ...")
```

-----

## **Minute 45: Load Testing & Capacity Planning (60 seconds)**

### **Load Testing Strategy**

```python
# Load test script using Locust/K6

Scenarios to Test:

1. Steady State Load:
   - 12K QPS for 1 hour
   - Verify: p99 latency < 500ms
   - Verify: Error rate < 0.1%

2. Peak Load:
   - Ramp to 50K QPS over 5 minutes
   - Sustain for 30 minutes
   - Verify: System remains stable
   - Verify: Auto-scaling triggers correctly

3. Spike Test:
   - Instant jump: 5K → 50K QPS
   - Verify: Queue absorbs spike
   - Verify: No dropped requests
   - Verify: Workers scale up in <2 minutes

4. Endurance Test:
   - 15K QPS for 24 hours
   - Verify: No memory leaks
   - Verify: No connection pool exhaustion
   - Verify: Consistent performance

5. Provider Failure:
   - Simulate SendGrid outage
   - Verify: Failover to backup provider
   - Verify: Retry logic works
   - Verify: Circuit breaker activates
```

### **Capacity Planning Formula**

```
Current Capacity: 50K QPS peak
Current Usage: 36K QPS peak (72% utilization)

Growth Rate: 50% YoY

Year 1: 36K × 1.5 = 54K QPS (exceeds capacity!)
Year 2: 54K × 1.5 = 81K QPS

Action Plan:
- Now: Scale to 75K QPS capacity (50% headroom)
- Q3: Scale to 100K QPS capacity
- Continuous monitoring of growth trends

Cost Projections:
- Current: $50K/month infrastructure
- At 75K QPS: $80K/month (60% increase)
- At 100K QPS: $120K/month

Optimization opportunities to reduce costs:
1. Better batching → 30% reduction
2. Cheaper storage tier for old logs → 20% reduction
3. Reserved instances → 40% reduction
```

-----

## **Key Performance Metrics Dashboard**

### **What to Monitor**

```yaml
System Health Metrics:

1. Throughput:
   - Messages/second (by channel, priority)
   - Target: 50K QPS capacity, 36K QPS actual peak
   
2. Latency:
   - API response time: p50, p95, p99
   - End-to-end delivery time
   - Target: p99 < 10 seconds for critical notifications

3. Success Rate:
   - Delivery success rate by channel
   - Target: >99.5% for transactional, >95% for promotional
   
4. Queue Health:
   - Queue depth (messages waiting)
   - Queue processing lag (time in queue)
   - Target: Depth < 5000, Lag < 30 seconds

5. Resource Utilization:
   - Worker CPU/memory usage
   - Database connection pool usage
   - Cache hit ratios
   - Target: 70-80% utilization (buffer for spikes)

6. Error Rates:
   - 4xx errors (client errors)
   - 5xx errors (server errors)
   - Provider errors
   - Target: <0.1% error rate

7. Cost Metrics:
   - Cost per notification (by channel)
   - Provider costs
   - Infrastructure costs
```

-----

## **Summary: Scale & Performance**

### **What You’ve Covered:**

✅ **Capacity Calculations** (Minute 36)

- 100M users → 1B notifications/day → 50K QPS peak
- Storage: 2TB/day, 60TB/month
- Concrete numbers for each component

✅ **Horizontal Scaling** (Minutes 37-38)

- API Gateway: 50-100 instances
- Kafka: 12 brokers, 50-100 partitions
- Workers: 100-1000 instances with auto-scaling
- Multi-region deployment

✅ **Database Scaling** (Minutes 39-40)

- Sharding: 10 shards by user_id hash
- Cassandra for logs: 20-node cluster
- Read replicas for query distribution

✅ **Caching** (Minutes 41-42)

- Multi-layer: L1 (local) → L2 (Redis) → L3 (DB)
- 95%+ cache hit ratio for preferences
- 192GB Redis cluster

✅ **Performance Optimizations** (Minutes 43-44)

- Batching: 50x throughput improvement
- Connection pooling: 50x latency reduction
- Query optimization: N+1 → batch queries

✅ **Capacity Planning** (Minute 45)

- Load testing scenarios
- Growth projections
- Cost optimization strategies

-----

## **Common Interview Mistakes**

❌ **Vague scaling**: “We’ll just add more servers”  
✅ **Specific scaling**: “50-100 API instances, each handling 500-1000 QPS”

❌ **No numbers**: “We’ll use caching”  
✅ **Concrete numbers**: “192GB Redis cluster, 95% hit ratio, 100GB hot data”

❌ **Ignoring costs**: Only talking about technical solutions  
✅ **Cost-aware**: “This costs $80K/month, we can optimize with batching”

❌ **Over-engineering**: “Let’s use 1000 microservices”  
✅ **Right-sized**: “For 100M users, 10-shard database is sufficient”

-----

## **Transition to Next Section**

*At end of Minute 45:*

“We’ve covered how to scale the system to handle 100M users and 50K QPS. We have about 15 minutes left. Should we discuss:

1. **Failure scenarios** - What happens when providers go down?
1. **Monitoring & observability** - How do we know the system is healthy?
1. **Additional features** - Analytics, personalization, compliance?

What would you like to explore?”

You’re now ready to discuss failure handling and advanced topics! 🎯​​​​​​​​​​​​​​​​
