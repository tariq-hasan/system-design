# Minutes 51-55: Additional Considerations - Detailed Breakdown

This is your **finishing move** - demonstrating breadth of knowledge beyond the core design. Senior engineers think holistically about production systems.

-----

## **Minute 51: Monitoring & Observability**

### **Start with Impact Statement**

> “A system without observability is a black box. Let me show you how we’d monitor this at scale…”

**Write on board:**

```
OBSERVABILITY PILLARS
=====================
1. Metrics (What's happening?)
2. Logs (Why did it happen?)
3. Traces (Where did it happen?)
4. Alerts (When to act?)
```

### **Detailed Monitoring Strategy**

```python
# Comprehensive monitoring implementation

class FeedSystemObservability:
    """
    Complete observability for feed system
    """
    
    def __init__(self):
        self.metrics = PrometheusClient()
        self.logger = StructuredLogger()
        self.tracer = OpenTelemetryTracer()
        self.alertmanager = AlertManager()
    
    # ============================================
    # GOLDEN SIGNALS (Google SRE)
    # ============================================
    
    def track_latency(self, endpoint, duration_ms, user_id=None):
        """
        Latency: How long requests take
        Track p50, p90, p95, p99
        """
        self.metrics.histogram(
            'http_request_duration_milliseconds',
            duration_ms,
            labels={
                'endpoint': endpoint,
                'method': 'GET'
            }
        )
        
        # Alert on p99 > 500ms
        if duration_ms > 500:
            self.metrics.increment(
                'slow_requests_total',
                labels={'endpoint': endpoint}
            )
    
    def track_traffic(self, endpoint, status_code):
        """
        Traffic: How many requests
        """
        self.metrics.increment(
            'http_requests_total',
            labels={
                'endpoint': endpoint,
                'status': status_code
            }
        )
    
    def track_errors(self, endpoint, error_type, error_message):
        """
        Errors: Request failure rate
        """
        self.metrics.increment(
            'http_errors_total',
            labels={
                'endpoint': endpoint,
                'error_type': error_type
            }
        )
        
        # Structured logging for debugging
        self.logger.error({
            'event': 'request_error',
            'endpoint': endpoint,
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': time.time()
        })
        
        # Alert if error rate > 1%
        error_rate = self._calculate_error_rate(endpoint)
        if error_rate > 0.01:
            self.alertmanager.send(
                severity='critical',
                title=f'High error rate on {endpoint}',
                description=f'Error rate: {error_rate:.2%}'
            )
    
    def track_saturation(self):
        """
        Saturation: Resource utilization
        """
        metrics = {
            'redis_memory_usage': self._get_redis_memory_usage(),
            'database_connections': self._get_db_connection_count(),
            'kafka_consumer_lag': self._get_kafka_lag(),
            'cpu_usage': self._get_cpu_usage(),
            'disk_usage': self._get_disk_usage()
        }
        
        for metric_name, value in metrics.items():
            self.metrics.gauge(f'system_{metric_name}', value)
        
        # Alert on high saturation
        if metrics['redis_memory_usage'] > 0.85:
            self.alertmanager.send(
                severity='warning',
                title='Redis memory high',
                description=f"Usage: {metrics['redis_memory_usage']:.1%}"
            )
    
    # ============================================
    # BUSINESS METRICS
    # ============================================
    
    def track_feed_quality(self, user_id, feed_posts):
        """
        Track feed quality metrics
        """
        self.metrics.histogram(
            'feed_size',
            len(feed_posts),
            labels={'user_id': user_id}
        )
        
        # Track feed freshness (age of newest post)
        if feed_posts:
            newest_age = time.time() - feed_posts[0]['created_at']
            self.metrics.histogram(
                'feed_freshness_seconds',
                newest_age
            )
    
    def track_engagement(self, post_id, action):
        """
        Track user engagement
        """
        self.metrics.increment(
            'post_engagement_total',
            labels={
                'post_id': post_id,
                'action': action  # like, comment, share
            }
        )
    
    def track_cache_performance(self, cache_name, hit):
        """
        Track cache hit rates
        """
        self.metrics.increment(
            'cache_requests_total',
            labels={
                'cache': cache_name,
                'result': 'hit' if hit else 'miss'
            }
        )
    
    # ============================================
    # DISTRIBUTED TRACING
    # ============================================
    
    async def trace_feed_request(self, user_id):
        """
        End-to-end tracing for feed generation
        """
        with self.tracer.start_span('get_feed') as span:
            span.set_attribute('user_id', user_id)
            
            # Check cache
            with self.tracer.start_span('check_cache', parent=span):
                cached = await self.redis.get(f"feed:{user_id}")
            
            if not cached:
                # Generate feed
                with self.tracer.start_span('generate_feed', parent=span):
                    
                    # Get following
                    with self.tracer.start_span('get_following'):
                        following = await self.graph_db.get_following(user_id)
                    
                    # Get posts
                    with self.tracer.start_span('get_posts'):
                        posts = await self.post_db.get_posts(following)
                    
                    # Rank posts
                    with self.tracer.start_span('rank_posts'):
                        ranked = await self.ranking_service.rank(posts)
            
            return ranked

# Example trace output:
"""
get_feed (500ms)
├── check_cache (5ms) ✓
├── generate_feed (495ms)
│   ├── get_following (50ms)
│   ├── get_posts (400ms) ← SLOW!
│   └── rank_posts (45ms)
"""
```

### **Dashboard Configuration**

```
KEY DASHBOARDS
==============

1. System Health Dashboard
   • Request rate (QPS)
   • Error rate (%)
   • Latency (p50, p95, p99)
   • Resource utilization
   
2. Feed Performance Dashboard
   • Cache hit rate
   • Feed generation time
   • Fan-out lag
   • Feed freshness
   
3. Database Dashboard
   • Query latency
   • Connection pool usage
   • Slow queries (> 100ms)
   • Replication lag
   
4. Business Metrics Dashboard
   • Daily active users
   • Posts per day
   • Engagement rate
   • Feed scroll depth
```

**Alert Rules:**

```yaml
# Prometheus alert rules
groups:
- name: feed_system_alerts
  rules:
  
  # Critical: System down
  - alert: HighErrorRate
    expr: rate(http_errors_total[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"
  
  # Critical: Performance degraded
  - alert: HighLatency
    expr: histogram_quantile(0.99, rate(http_request_duration_milliseconds_bucket[5m])) > 500
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "P99 latency above 500ms"
  
  # Warning: Resource saturation
  - alert: RedisMemoryHigh
    expr: redis_memory_usage_ratio > 0.85
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "Redis memory usage high"
  
  # Warning: Queue lag
  - alert: KafkaLagHigh
    expr: kafka_consumer_lag > 1000000
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Kafka consumer lag > 1M messages"
  
  # Info: Cost anomaly
  - alert: CostSpike
    expr: rate(infrastructure_cost_dollars[1d]) > 1.2 * avg_over_time(infrastructure_cost_dollars[7d])
    labels:
      severity: info
    annotations:
      summary: "Infrastructure costs increased >20%"
```

-----

## **Minute 52: Security & Privacy**

### **Critical Security Considerations**

> “Security can’t be an afterthought. Here’s how we protect the system and users…”

**Write on board:**

```
SECURITY LAYERS
===============
1. Authentication & Authorization
2. Data Encryption
3. Rate Limiting & DDoS Protection
4. Input Validation & Sanitization
5. Privacy Controls
6. Audit Logging
```

### **Implementation Details**

```python
class SecurityLayer:
    """
    Comprehensive security implementation
    """
    
    # ============================================
    # AUTHENTICATION & AUTHORIZATION
    # ============================================
    
    def authenticate_request(self, request):
        """
        Verify user identity via JWT
        """
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            raise UnauthorizedError("No token provided")
        
        try:
            # Verify JWT signature and expiration
            payload = jwt.decode(
                token,
                PUBLIC_KEY,
                algorithms=['RS256']
            )
            
            user_id = payload['user_id']
            scopes = payload['scopes']
            
            # Check if token is revoked
            if self.token_blacklist.is_revoked(token):
                raise UnauthorizedError("Token revoked")
            
            return {
                'user_id': user_id,
                'scopes': scopes
            }
            
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("Invalid token")
    
    def authorize_action(self, user_id, action, resource):
        """
        Check if user can perform action on resource
        """
        # Example: Can user delete this post?
        if action == 'delete_post':
            post = self.post_db.get(resource['post_id'])
            
            # Only author can delete
            if post['user_id'] != user_id:
                raise ForbiddenError("Not authorized to delete this post")
        
        # Example: Can user view this feed?
        if action == 'view_feed':
            target_user_id = resource['user_id']
            target_user = self.user_db.get(target_user_id)
            
            # Check privacy settings
            if target_user['is_private']:
                # Must be following or self
                if user_id != target_user_id and not self.graph_db.is_following(user_id, target_user_id):
                    raise ForbiddenError("This account is private")
    
    # ============================================
    # DATA ENCRYPTION
    # ============================================
    
    def encrypt_sensitive_data(self, data):
        """
        Encrypt PII at rest
        """
        # Use AES-256-GCM
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        
        return {
            'ciphertext': b64encode(ciphertext).decode(),
            'nonce': b64encode(cipher.nonce).decode(),
            'tag': b64encode(tag).decode()
        }
    
    def setup_tls(self):
        """
        TLS configuration for data in transit
        """
        return {
            'min_tls_version': 'TLSv1.3',
            'ciphers': [
                'TLS_AES_256_GCM_SHA384',
                'TLS_CHACHA20_POLY1305_SHA256'
            ],
            'certificate': self.load_certificate(),
            'private_key': self.load_private_key()
        }
    
    # ============================================
    # RATE LIMITING & DDoS PROTECTION
    # ============================================
    
    async def check_rate_limit(self, user_id, action):
        """
        Token bucket rate limiting
        """
        # Different limits for different actions
        limits = {
            'post_create': (10, 3600),      # 10 posts per hour
            'feed_read': (1000, 3600),      # 1000 reads per hour
            'follow': (100, 3600),          # 100 follows per hour
            'like': (500, 3600)             # 500 likes per hour
        }
        
        max_requests, window = limits.get(action, (100, 60))
        
        # Redis-based rate limiting
        key = f"rate_limit:{user_id}:{action}"
        
        # Get current count
        current = await self.redis.get(key)
        
        if current and int(current) >= max_requests:
            # Rate limit exceeded
            raise RateLimitError(
                f"Rate limit exceeded. Max {max_requests} per {window}s"
            )
        
        # Increment counter
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        await pipe.execute()
    
    def ddos_protection(self, request):
        """
        DDoS mitigation strategies
        """
        ip = request.remote_addr
        
        # Check IP reputation
        if self.ip_blacklist.is_blocked(ip):
            raise BlockedError("IP blocked")
        
        # Challenge-response for suspicious traffic
        if self.is_suspicious_traffic(ip):
            return self.require_captcha(request)
        
        # Geographic filtering
        country = self.geoip.lookup(ip)
        if country in self.blocked_countries:
            raise BlockedError("Geographic restriction")
    
    # ============================================
    # INPUT VALIDATION
    # ============================================
    
    def sanitize_post_content(self, content):
        """
        Prevent XSS, SQL injection, etc.
        """
        # Strip HTML tags
        content = self.strip_html(content)
        
        # Escape special characters
        content = html.escape(content)
        
        # Check length
        if len(content) > 5000:
            raise ValidationError("Post too long")
        
        # Check for malicious patterns
        if self.contains_malicious_pattern(content):
            raise ValidationError("Invalid content")
        
        return content
    
    def validate_media_upload(self, file):
        """
        Validate uploaded media files
        """
        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if file.content_type not in allowed_types:
            raise ValidationError("Invalid file type")
        
        # Check file size
        max_size = 10 * 1024 * 1024  # 10 MB
        if file.size > max_size:
            raise ValidationError("File too large")
        
        # Scan for malware
        if self.malware_scanner.scan(file):
            raise ValidationError("File contains malware")
        
        # Strip EXIF data (privacy)
        return self.strip_exif(file)
    
    # ============================================
    # PRIVACY CONTROLS
    # ============================================
    
    def filter_feed_by_privacy(self, feed, viewer_id):
        """
        Filter feed based on privacy settings
        """
        filtered = []
        
        for post in feed:
            author = self.user_db.get(post['user_id'])
            
            # Check if viewer can see this post
            if self.can_view_post(viewer_id, post, author):
                filtered.append(post)
        
        return filtered
    
    def can_view_post(self, viewer_id, post, author):
        """
        Privacy logic
        """
        # Public posts: everyone can see
        if not author['is_private']:
            return True
        
        # Own posts: always visible
        if viewer_id == author['user_id']:
            return True
        
        # Private account: only followers can see
        if self.graph_db.is_following(viewer_id, author['user_id']):
            return True
        
        # Blocked users: cannot see
        if self.block_list.is_blocked(author['user_id'], viewer_id):
            return False
        
        return False
    
    # ============================================
    # AUDIT LOGGING
    # ============================================
    
    def audit_log(self, event_type, user_id, details):
        """
        Log security-relevant events
        """
        audit_entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': self.get_client_ip(),
            'user_agent': self.get_user_agent(),
            'details': details
        }
        
        # Write to immutable audit log
        self.audit_db.insert(audit_entry)
        
        # Examples of audited events:
        # - Login attempts (success/failure)
        # - Password changes
        # - Post deletions
        # - Account deletions
        # - Privacy setting changes
        # - Follow/unfollow actions
```

### **Security Best Practices Checklist**

```
SECURITY CHECKLIST
==================

✓ Authentication
  • JWT with short expiration (15 min access, 7 day refresh)
  • Token rotation on refresh
  • Secure token storage (httpOnly cookies)
  
✓ Authorization
  • Principle of least privilege
  • Resource-level permissions
  • Privacy settings enforcement
  
✓ Encryption
  • TLS 1.3 for data in transit
  • AES-256 for data at rest
  • Encrypted database backups
  
✓ Rate Limiting
  • Per-user limits
  • Per-IP limits
  • Exponential backoff
  
✓ Input Validation
  • Whitelist validation
  • Content sanitization
  • File type verification
  
✓ Secrets Management
  • Never commit secrets to git
  • Use AWS Secrets Manager / HashiCorp Vault
  • Rotate secrets regularly
  
✓ Compliance
  • GDPR (EU): Right to deletion, data export
  • CCPA (California): Opt-out of data selling
  • COPPA (US): No data from users under 13
```

-----

## **Minute 53: Content Moderation & Safety**

### **Content Moderation Pipeline**

> “At scale, we need automated content moderation with human review…”

```python
class ContentModerationSystem:
    """
    Multi-stage content moderation
    """
    
    def __init__(self):
        self.ml_classifier = MLContentClassifier()
        self.image_analyzer = ImageModerationAPI()  # AWS Rekognition, etc.
        self.text_analyzer = TextModerationAPI()
        self.review_queue = ReviewQueue()
    
    async def moderate_post(self, post):
        """
        Moderate post before publishing
        """
        moderation_result = {
            'post_id': post['id'],
            'status': 'pending',
            'flags': [],
            'confidence_scores': {}
        }
        
        # Stage 1: Text moderation
        text_result = await self.moderate_text(post['content'])
        moderation_result['flags'].extend(text_result['flags'])
        moderation_result['confidence_scores']['text'] = text_result['confidence']
        
        # Stage 2: Image moderation
        if post.get('media_urls'):
            for media_url in post['media_urls']:
                image_result = await self.moderate_image(media_url)
                moderation_result['flags'].extend(image_result['flags'])
        
        # Stage 3: Make decision
        decision = self.make_moderation_decision(moderation_result)
        
        if decision == 'approve':
            moderation_result['status'] = 'approved'
            return moderation_result
        
        elif decision == 'reject':
            moderation_result['status'] = 'rejected'
            await self.notify_user(post['user_id'], 'post_rejected', moderation_result)
            return moderation_result
        
        elif decision == 'review':
            moderation_result['status'] = 'needs_review'
            await self.review_queue.add(post, moderation_result)
            return moderation_result
    
    async def moderate_text(self, text):
        """
        Detect harmful text content
        """
        flags = []
        
        # Check against banned words list
        if self.contains_banned_words(text):
            flags.append('banned_words')
        
        # ML-based classification
        ml_result = await self.ml_classifier.classify(text)
        
        categories = {
            'hate_speech': ml_result['hate_speech_score'],
            'harassment': ml_result['harassment_score'],
            'violence': ml_result['violence_score'],
            'sexual_content': ml_result['sexual_content_score'],
            'spam': ml_result['spam_score']
        }
        
        # Flag if any category exceeds threshold
        for category, score in categories.items():
            if score > 0.7:  # High confidence
                flags.append(category)
        
        return {
            'flags': flags,
            'confidence': max(categories.values()) if categories else 0,
            'categories': categories
        }
    
    async def moderate_image(self, image_url):
        """
        Detect harmful image content
        """
        # Use AWS Rekognition or similar
        result = await self.image_analyzer.detect_moderation_labels(image_url)
        
        flags = []
        
        for label in result['ModerationLabels']:
            if label['Confidence'] > 80:
                # Map labels to our categories
                category = self.map_moderation_label(label['Name'])
                flags.append(category)
        
        return {
            'flags': flags,
            'labels': result['ModerationLabels']
        }
    
    def make_moderation_decision(self, moderation_result):
        """
        Decide: approve, reject, or human review
        """
        flags = moderation_result['flags']
        
        # Auto-reject severe violations
        severe_violations = ['child_safety', 'extreme_violence', 'terrorism']
        if any(flag in severe_violations for flag in flags):
            return 'reject'
        
        # Auto-approve clean content
        if not flags:
            return 'approve'
        
        # Medium confidence: human review
        max_confidence = max(moderation_result['confidence_scores'].values())
        if 0.5 < max_confidence < 0.8:
            return 'review'
        
        # High confidence violations: reject
        if max_confidence >= 0.8:
            return 'reject'
        
        # Low confidence: approve but monitor
        return 'approve'
    
    async def handle_user_report(self, report):
        """
        User-reported content
        """
        post = await self.post_db.get(report['post_id'])
        
        # Re-moderate with human review
        moderation_result = await self.moderate_post(post)
        moderation_result['user_reported'] = True
        moderation_result['report_reason'] = report['reason']
        
        # Prioritize in review queue
        await self.review_queue.add(post, moderation_result, priority='high')
        
        # Track reporter reputation
        await self.update_reporter_reputation(report['reporter_id'], report)
```

**Moderation Decision Tree:**

```
┌─────────────────────────────────────────┐
│         New Post Created                │
└───────────────┬─────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────┐
│  Automated Moderation (< 100ms)           │
│  • Text analysis (ML)                     │
│  • Image analysis (AWS Rekognition)       │
│  • Banned words check                     │
└───────────────┬───────────────────────────┘
                │
        ┌───────┴───────┬───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────┐
│   No Flags   │ │ Medium Conf  │ │ High Conf   │
│              │ │  (50-80%)    │ │  (>80%)     │
└──────┬───────┘ └──────┬───────┘ └──────┬──────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────┐
│  AUTO-       │ │  HUMAN       │ │  AUTO-      │
│  APPROVE     │ │  REVIEW      │ │  REJECT     │
│  Publish     │ │  Queue       │ │  Block      │
└──────────────┘ └──────────────┘ └─────────────┘
```

-----

## **Minute 54: Disaster Recovery & Business Continuity**

### **DR Strategy**

> “Let me cover our disaster recovery plan…”

**Write on board:**

```
DISASTER RECOVERY
=================

RTO (Recovery Time Objective): 1 hour
RPO (Recovery Point Objective): 5 minutes

Scenarios:
1. Single service failure
2. Database corruption
3. Data center outage
4. Regional disaster
5. Catastrophic failure
```

```python
class DisasterRecoverySystem:
    """
    Comprehensive DR implementation
    """
    
    # ============================================
    # BACKUP STRATEGY
    # ============================================
    
    def configure_backups(self):
        """
        Multi-layered backup strategy
        """
        backup_config = {
            # Database backups
            'database': {
                'full_backup': 'daily at 2am UTC',
                'incremental_backup': 'every 6 hours',
                'transaction_log_backup': 'every 5 minutes',
                'retention': '30 days',
                'location': 's3://backups-us-east-1 + s3://backups-us-west-2'
            },
            
            # Redis snapshots
            'cache': {
                'snapshot': 'every 1 hour',
                'aof': 'enabled',  # Append-only file
                'retention': '7 days',
                'location': 's3://redis-backups'
            },
            
            # Media files
            'media': {
                's3_versioning': 'enabled',
                'cross_region_replication': 'us-east-1 → eu-west-1',
                'glacier_archive': 'after 90 days'
            }
        }
        
        return backup_config
    
    async def restore_from_backup(self, component, timestamp):
        """
        Restore component from backup
        """
        if component == 'database':
            # Point-in-time recovery
            await self.restore_database(timestamp)
        
        elif component == 'cache':
            # Rebuild cache from database
            await self.rebuild_cache()
        
        elif component == 'media':
            # Restore from S3 versioning
            await self.restore_media_files(timestamp)
    
    # ============================================
    # MULTI-REGION FAILOVER
    # ============================================
    
    async def failover_to_region(self, target_region):
        """
        Failover to different region
        """
        print(f"Initiating failover to {target_region}")
        
        # Step 1: Update DNS (Route53)
        await self.update_dns_routing(target_region)
        # TTL: 60 seconds, so full cutover in 1-2 minutes
        
        # Step 2: Promote replica database to primary
        await self.promote_database_replica(target_region)
        
        # Step 3: Scale up services in target region
        await self.scale_services(target_region, scale_factor=3)
        
        # Step 4: Verify health
        health = await self.check_region_health(target_region)
        if not health['healthy']:
            raise FailoverError("Target region not healthy")
        
        # Step 5: Update monitoring
        await self.update_alerts(f"Failover to {target_region} complete")
        
        print(f"Failover complete. Now serving from {target_region}")
    
    def configure_multi_region(self):
        """
        Multi-region setup
        """
        regions = {
            'primary': {
                'region': 'us-east-1',
                'database': 'primary',
                'cache': 'primary',
                'traffic_percentage': 100
            },
            'secondary': {
                'region': 'us-west-2',
                'database': 'replica (async replication)',
                'cache': 'warm standby',
                'traffic_percentage': 0  # Standby only
            },
            'tertiary': {
                'region': 'eu-west-1',
                'database': 'replica (async replication)',
                'cache': 'warm standby',
                'traffic_percentage': 0
            }
        }
        
        return regions
    
    # ============================================
    # CHAOS ENGINEERING
    # ============================================
    
    async def run_disaster_drills(self):
        """
        Regular testing of DR procedures
        """
        drills = [
            {
                'name': 'Database Failover Drill',
                'frequency': 'monthly',
                'procedure': self.drill_database_failover
            },
            {
                'name': 'Regional Failover Drill',
                'frequency': 'quarterly',
                'procedure': self.drill_regional_failover
            },
            {
                'name': 'Cache Rebuild Drill',
                'frequency': 'monthly',
                'procedure': self.drill_cache_rebuild
            }
        ]
        
        for drill in drills:
            print(f"Running: {drill['name']}")
            try:
                await drill['procedure']()
                print(f"✓ {drill['name']} successful")
            except Exception as e:
                print(f"✗ {drill['name']} failed: {e}")
                # Alert on drill failure
                await self.alert_dr_failure(drill['name'], e)
```

**Failover Scenarios:**

```
SCENARIO 1: Database Primary Failure
=====================================
Impact: Write operations fail
Detection: Health check fails, replication lag infinite
Response Time: < 5 minutes

Automated Response:
1. Promote us-west-2 replica to primary (30 seconds)
2. Update application config (10 seconds)
3. Resume write operations (5 minutes total)

Data Loss: < 5 minutes (RPO)


SCENARIO 2: Full Regional Outage (us-east-1)
=============================================
Impact: All services unavailable in region
Detection: Multi-service failure, AWS status page
Response Time: < 1 hour

Manual Response (requires engineer approval):
1. Verify us-west-2 is healthy (5 min)
2. Promote databases (10 min)
3. Scale up services 3x (15 min)
4. Update Route53 DNS (5 min)
5. Wait for DNS propagation (30 min)
6. Verify traffic flowing (5 min)

Total: ~70 minutes (within RTO)
Data Loss: Last 5 min of writes (within RPO)


SCENARIO 3: Data Corruption
============================
Impact: Bad data propagated to replicas
Detection: Data integrity checks, user reports
Response Time: Varies by detection time

Manual Response:
1. Identify corruption timestamp
2. Stop replication to prevent spread
3. Restore from backup (point-in-time)
4. Replay transaction logs
5. Verify data integrity
6. Resume operations

Time: 2-4 hours depending on data volume
```

-----

## **Minute 55: A/B Testing & Feature Flags**

### **Experimentation Infrastructure**

> “We need to iterate quickly and safely. Here’s our experimentation framework…”

```python
class ExperimentationPlatform:
    """
    A/B testing and feature flag system
    """
    
    def __init__(self):
        self.experiment_config = ExperimentConfigStore()
        self.analytics = AnalyticsClient()
        self.feature_flags = FeatureFlagService()
    
    # ============================================
    # FEATURE FLAGS
    # ============================================
    
    def is_feature_enabled(self, feature_name, user_id, context=None):
        """
        Check if feature is enabled for user
        """
        # Get feature flag configuration
        flag = self.feature_flags.get(feature_name)
        
        if not flag:
            return False
        
        # Global killswitch
        if flag['enabled'] == False:
            return False
        
        # Percentage rollout
        if 'rollout_percentage' in flag:
            # Deterministic hash-based bucketing
            user_hash = self._hash_user(user_id, feature_name)
            if user_hash > flag['rollout_percentage']:
                return False
        
        # Whitelist/blacklist
        if user_id in flag.get('whitelist', []):
            return True
        if user_id in flag.get('blacklist', []):
            return False
        
        # Targeting rules
        if 'targeting' in flag:
            if not self._matches_targeting(user_id, flag['targeting'], context):
                return False
        
        return True
    
    def _hash_user(self, user_id, feature_name):
        """
        Consistent hash for user bucketing
        """
        hash_input = f"{user_id}:{feature_name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        return (hash_value % 100)  # 0-99
    
    def _matches_targeting(self, user_id, targeting, context):
        """
        Check if user matches targeting criteria
        """
        # Example: Target users in specific countries
        if 'countries' in targeting:
            user_country = context.get('country')
            if user_country not in targeting['countries']:
                return False
        
        # Example: Target users with specific attributes
        if 'user_segment' in targeting:
            user = self.user_service.get(user_id)
            if user['segment'] not in targeting['user_segment']:
                return False
        
        # Example: Target mobile vs desktop
        if 'platform' in targeting:
            if context.get('platform') not in targeting['platform']:
                return False
        
        return True
    
    # ============================================
    # A/B TESTING
    # ============================================
    
    def assign_experiment(self, experiment_name, user_id):
        """
        Assign user to experiment variant
        """
        experiment = self.experiment_config.get(experiment_name)
        
        if not experiment or experiment['status'] != 'active':
            return 'control'
        
        # Check if user is in experiment population
        if not self._in_experiment_population(user_id, experiment):
            return None
        
        # Assign to variant based on hash
        user_hash = self._hash_user(user_id, experiment_name)
        
        cumulative = 0
        for variant in experiment['variants']:
            cumulative += variant['percentage']
            if user_hash < cumulative:
                # Track assignment
                self.analytics.track({
                    'event': 'experiment_assigned',
                    'user_id': user_id,
                    'experiment': experiment_name,
                    'variant': variant['name']
                })
                return variant['name']
        
        return 'control'
    
    # ============================================
    # EXAMPLE: RANKING ALGORITHM EXPERIMENT
    # ============================================
    
    async def get_feed_with_experiment(self, user_id):
        """
        Serve different feed ranking algorithms via A/B test
        """
        # Assign to experiment
        variant = self.assign_experiment('feed_ranking_v2', user_id)
        
        # Get feed posts
        posts = await self.get_candidate_posts(user_id)
        
        # Apply ranking based on variant
        if variant == 'control':
            # Current algorithm (chronological + simple engagement)
            ranked_posts = self.ranking_v1.rank(posts, user_id)
        
        elif variant == 'ml_ranking':
            # New ML-based ranking
            ranked_posts = self.ranking_v2_ml.rank(posts, user_id)
        
        elif variant == 'hybrid':
            # Hybrid approach
            ranked_posts = self.ranking_v2_hybrid.rank(posts, user_id)
        
        else:
            # Default to control
            ranked_posts = self.ranking_v1.rank(posts, user_id)
        
        # Track which variant was served
        self.analytics.track({
            'event': 'feed_served',
            'user_id': user_id,
            'experiment': 'feed_ranking_v2',
            'variant': variant,
            'num_posts': len(ranked_posts)
        })
        
        return ranked_posts
    
    # ============================================
    # METRICS TRACKING
    # ============================================
    
    def track_experiment_metric(self, user_id, experiment_name, metric_name, value):
        """
        Track metrics for experiment analysis
        """
        variant = self.get_user_variant(user_id, experiment_name)
        
        if variant:
            self.analytics.track({
                'event': 'experiment_metric',
                'user_id': user_id,
                'experiment': experiment_name,
                'variant': variant,
                'metric': metric_name,
                'value': value,
                'timestamp': time.time()
            })
    
    async def analyze_experiment(self, experiment_name):
        """
        Statistical analysis of experiment results
        """
        experiment = self.experiment_config.get(experiment_name)
        
        # Get metrics for each variant
        results = {}
        for variant in experiment['variants']:
            metrics = await self.analytics.query(
                experiment=experiment_name,
                variant=variant['name'],
                time_range='7d'
            )
            results[variant['name']] = metrics
        
        # Calculate key metrics
        analysis = {
            'engagement_rate': {},
            'session_duration': {},
            'posts_viewed': {},
            'statistical_significance': {}
        }
        
        control = results['control']
        
        for variant_name, variant_metrics in results.items():
            if variant_name == 'control':
                continue
            
            # Calculate relative lift
            for metric in ['engagement_rate', 'session_duration', 'posts_viewed']:
                control_mean = control[metric]['mean']
                variant_mean = variant_metrics[metric]['mean']
                
                lift = ((variant_mean - control_mean) / control_mean) * 100
                
                # T-test for significance
                p_value = self._t_test(
                    control[metric]['values'],
                    variant_metrics[metric]['values']
                )
                
                analysis[metric][variant_name] = {
                    'control_mean': control_mean,
                    'variant_mean': variant_mean,
                    'lift': lift,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
        
        return analysis
    
    # ============================================
    # GRADUAL ROLLOUT
    # ============================================
    
    async def gradual_rollout(self, feature_name, stages):
        """
        Gradually increase feature rollout percentage
        
        Example stages:
        [
            {'percentage': 1, 'duration_hours': 24},   # 1% for 24h
            {'percentage': 5, 'duration_hours': 24},   # 5% for 24h
            {'percentage': 25, 'duration_hours': 48},  # 25% for 48h
            {'percentage': 50, 'duration_hours': 48},  # 50% for 48h
            {'percentage': 100, 'duration_hours': 0}   # Full rollout
        ]
        """
        for stage in stages:
            percentage = stage['percentage']
            duration = stage['duration_hours']
            
            # Update feature flag
            self.feature_flags.update(feature_name, {
                'rollout_percentage': percentage
            })
            
            print(f"Rolled out {feature_name} to {percentage}% of users")
            
            # Monitor for issues
            await self._monitor_rollout(feature_name, duration)
            
            # Check health metrics
            health = await self._check_rollout_health(feature_name)
            
            if not health['healthy']:
                # Rollback!
                print(f"Health check failed at {percentage}%. Rolling back.")
                await self.rollback_feature(feature_name)
                raise RolloutError(f"Rollback triggered: {health['reason']}")
            
            # Wait before next stage
            if duration > 0:
                await asyncio.sleep(duration * 3600)
    
    async def _check_rollout_health(self, feature_name):
        """
        Check if rollout is healthy
        """
        # Compare metrics for users with/without feature
        metrics_with = await self.get_metrics(feature_name, enabled=True)
        metrics_without = await self.get_metrics(feature_name, enabled=False)
        
        # Check error rates
        if metrics_with['error_rate'] > metrics_without['error_rate'] * 1.5:
            return {
                'healthy': False,
                'reason': f"Error rate increased by 50%"
            }
        
        # Check latency
        if metrics_with['p99_latency'] > metrics_without['p99_latency'] * 1.3:
            return {
                'healthy': False,
                'reason': f"P99 latency increased by 30%"
            }
        
        # Check engagement
        if metrics_with['engagement_rate'] < metrics_without['engagement_rate'] * 0.9:
            return {
                'healthy': False,
                'reason': f"Engagement dropped by 10%"
            }
        
        return {'healthy': True}
    
    async def rollback_feature(self, feature_name):
        """
        Emergency rollback
        """
        # Disable feature immediately
        self.feature_flags.update(feature_name, {
            'enabled': False
        })
        
        # Alert team
        self.alert_manager.send(
            severity='critical',
            title=f'Feature rollback: {feature_name}',
            description='Feature automatically disabled due to health check failure'
        )
        
        print(f"Feature {feature_name} rolled back")
```

### **Example Feature Flag Configurations**

```yaml
# feature_flags.yaml

new_feed_algorithm:
  enabled: true
  rollout_percentage: 10
  targeting:
    user_segment: ['power_users']
    countries: ['US', 'CA']
  created_at: '2025-10-20'
  owner: 'feed-team@company.com'

celebrity_pull_model:
  enabled: true
  rollout_percentage: 100
  targeting:
    follower_count_min: 10000
  created_at: '2025-09-15'
  
video_posts:
  enabled: true
  rollout_percentage: 50
  whitelist: [123, 456, 789]  # Beta testers
  created_at: '2025-10-22'

real_time_notifications:
  enabled: false  # Killswitch
  reason: 'High load on notification service'
  disabled_at: '2025-10-24'
  disabled_by: 'oncall-engineer'
```

### **A/B Test Example Configuration**

```yaml
# experiments.yaml

feed_ranking_v2:
  name: 'ML-based Feed Ranking'
  status: 'active'
  start_date: '2025-10-15'
  end_date: '2025-11-15'
  population_percentage: 20  # Only 20% of users in experiment
  
  variants:
    - name: 'control'
      percentage: 40  # 40% of experiment population
      description: 'Current chronological + engagement ranking'
    
    - name: 'ml_ranking'
      percentage: 30
      description: 'Full ML model (neural network)'
    
    - name: 'hybrid'
      percentage: 30
      description: 'ML + rule-based hybrid'
  
  success_metrics:
    primary: 'engagement_rate'
    secondary: ['session_duration', 'posts_viewed', 'return_rate']
  
  guardrail_metrics:
    - metric: 'error_rate'
      threshold: 0.01
      action: 'stop_experiment'
    
    - metric: 'p99_latency'
      threshold: 1000  # ms
      action: 'alert'
```

-----

## **Additional Topics (Quick Mentions)**

### **Performance Optimization**

```
PERFORMANCE BEST PRACTICES
==========================

✓ Database Query Optimization
  • Add indexes on frequently queried columns
  • Use EXPLAIN ANALYZE to find slow queries
  • Avoid N+1 queries (use batch loading)
  
✓ API Response Optimization
  • Pagination (limit 20-50 items per page)
  • Field filtering (only return needed fields)
  • Compression (gzip responses)
  
✓ Image Optimization
  • Lazy loading
  • WebP format (30% smaller than JPEG)
  • Responsive images (multiple sizes)
  • Progressive JPEG (loads incrementally)
  
✓ Client-Side Caching
  • Service workers for offline support
  • Local storage for user preferences
  • ETags for cache validation
```

### **Legal & Compliance**

```
COMPLIANCE REQUIREMENTS
=======================

GDPR (EU):
  ✓ Right to access (data export)
  ✓ Right to erasure (delete account)
  ✓ Right to portability (JSON export)
  ✓ Consent management
  ✓ Data processing agreements
  
CCPA (California):
  ✓ Opt-out of data selling
  ✓ Disclosure of data collection
  
COPPA (US < 13 years):
  ✓ Parental consent required
  ✓ Age verification
  ✓ Limited data collection
  
Accessibility:
  ✓ WCAG 2.1 AA compliance
  ✓ Screen reader support
  ✓ Keyboard navigation
```

### **Internationalization**

```
i18n CONSIDERATIONS
===================

✓ Multi-language Support
  • Translation service for UI
  • Content translation (optional)
  • RTL support (Arabic, Hebrew)
  
✓ Regional Differences
  • Date/time formats
  • Currency handling
  • Legal requirements per region
  
✓ CDN Edge Locations
  • Deploy close to users globally
  • Reduce latency for international users
```

### **Mobile Optimization**

```
MOBILE CONSIDERATIONS
=====================

✓ Bandwidth Optimization
  • Smaller image sizes for mobile
  • Reduce API payload size
  • Delta updates (only changed data)
  
✓ Offline Support
  • Cache posts for offline viewing
  • Queue actions for when online
  • Sync when connectivity restored
  
✓ Battery Optimization
  • Batch network requests
  • Reduce background polling
  • Efficient image decoding
```

-----

## **Minute 55: Wrap-up & Summary**

### **Create Executive Summary**

> “Let me summarize the key aspects of our design…”

**Write on board:**

```
╔══════════════════════════════════════════════════════════╗
║           NEWS FEED SYSTEM - EXECUTIVE SUMMARY           ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║ SCALE                                                    ║
║   • 200M DAU, 100M posts/day                             ║
║   • 35K read QPS, 1.2K write QPS                         ║
║   • 12 TB/day storage, 5 PB total                        ║
║                                                          ║
║ KEY DESIGN DECISIONS                                     ║
║   • Hybrid fan-out (push for regular, pull for celebs)   ║
║   • Eventual consistency (AP in CAP)                     ║
║   • Aggressive caching (Redis + CDN)                     ║
║   • Async processing (Kafka)                             ║
║                                                          ║
║ ARCHITECTURE                                             ║
║   • 5 core services (Post, Feed, User, Fanout, Rank)     ║
║   • Cassandra for posts, MySQL for graph, Redis cache    ║
║   • Multi-region with failover (RTO: 1h, RPO: 5min)      ║
║                                                          ║
║ TRADE-OFFS                                               ║
║   • Latency vs consistency: Chose latency                ║
║   • Cost vs performance: 80/20 caching                   ║
║   • Complexity vs scalability: Chose scalability         ║
║                                                          ║
║ PRODUCTION-READY FEATURES                                ║
║   • Monitoring (Prometheus + Grafana)                    ║
║   • Security (TLS, JWT, rate limiting)                   ║
║   • Content moderation (ML + human review)               ║
║   • A/B testing & feature flags                          ║
║   • Disaster recovery & backups                          ║
║                                                          ║
║ COST: ~$180K/month (~$2.2M/year)                         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### **Areas Not Covered (Be Honest)**

> “Given time constraints, here are areas we didn’t deep dive but would be important…”

```
OUT OF SCOPE (But Important)
=============================

✓ Mentioned but not detailed:
  • Recommendation engine details
  • Video streaming infrastructure
  • Real-time notifications (WebSocket/SSE)
  • Search and discovery
  • Analytics pipeline
  • ML model training infrastructure
  • Mobile app architecture
  • DevOps/CI/CD pipeline

✓ Would address in follow-up:
  • Detailed cost optimization
  • Capacity planning models
  • Incident response procedures
  • Team structure and ownership
  • Migration strategy (brownfield vs greenfield)
```

-----

## **Final Thoughts: What Makes This Section Strong**

### **Senior-Level Signals in “Additional Considerations”:**

1. **Holistic thinking**: Not just architecture, but security, compliance, DR
1. **Production awareness**: Monitoring, rollback procedures, chaos engineering
1. **Business context**: Cost analysis, legal requirements, A/B testing
1. **Risk management**: What could go wrong and how to handle it
1. **Continuous improvement**: Feature flags for safe iteration

### **Time Management:**

- **1 minute per topic** (monitoring, security, DR, A/B testing)
- **Quick, high-level overview** (not deep implementation)
- **Connect back to main design** (“This monitoring supports our SLA goals”)
- **Show you’ve built production systems** (reference real tools, real problems)

### **How to Pivot Based on Interviewer Interest:**

**If interviewer asks about specific topic:**

> “Let me dive deeper into [topic]…”
> → Expand with implementation details

**If interviewer looks at clock:**

> “I can touch on these briefly or we can move to Q&A…”
> → Respect their time

**If interviewer seems satisfied:**

> “That covers the additional considerations. What questions do you have?”
> → Transition smoothly

-----

## **Transition to Q&A (Minute 56+)**

**At minute 55, conclude with:**

> “That covers the core design, trade-offs, and production considerations. We’ve designed a system that:
> 
> ✓ Scales to 200M DAU
> ✓ Delivers feeds in <500ms
> ✓ Handles celebrity posts efficiently
> ✓ Is observable, secure, and recoverable
> ✓ Can iterate safely with A/B tests
> 
> We have about 5 minutes left. What aspects would you like to explore further, or what questions do you have?”

**This shows:**

- You managed your time well (finished with buffer)
- You covered breadth AND depth
- You’re confident in your design
- You’re open to feedback and discussion

The “Additional Considerations” section demonstrates you think beyond just making the system work—you think about making it **production-ready, maintainable, and evolvable**. This is what distinguishes senior engineers from mid-level engineers in interviews.​​​​​​​​​​​​​​​​
