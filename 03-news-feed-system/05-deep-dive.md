# Minutes 26-40: Deep Dive - Detailed Breakdown

This is where you demonstrate **senior-level depth**. The interviewer will typically pick 2-3 areas to explore. Be ready to dive deep into any component.

-----

## **Strategy for This Phase**

### **Listen for Signals**

- If interviewer asks: “How would you handle X?” → Deep dive into X
- If they say: “This looks good, what about scalability?” → Focus on scaling
- If they’re quiet: Offer 3-4 options and let them choose

### **Common Deep Dive Topics**

1. Feed Generation & Ranking Algorithm
1. Scalability & Sharding Strategies
1. The Celebrity/Hot User Problem
1. Cache Invalidation & Consistency
1. Database Schema & Indexing
1. Fault Tolerance & Failure Handling

Let me expand on each:

-----

## **Deep Dive Option 1: Feed Generation & Ranking Algorithm (Minutes 26-31)**

### **Minute 26: Ranking Signals**

> “Let me break down how we’d build an intelligent feed ranking system…”

**Write on board:**

```
RANKING SIGNALS (Features)
===========================
Time-based:
  • Recency: How old is the post?
  • Time decay function: score = 1 / (age_hours + 2)^1.5
  
Engagement-based:
  • Likes count (normalized by follower count)
  • Comments count (higher weight than likes)
  • Shares/retweets (highest weight)
  • Click-through rate (CTR)
  • Dwell time (how long user looked at post)
  
User affinity:
  • Historical interaction frequency with author
  • Similarity in interests (content categories)
  • Network distance (friend of friend?)
  
Content features:
  • Has media (images/videos rank higher)
  • Content length (not too short, not too long)
  • Hashtags/mentions
  • Content category (news, sports, entertainment)
  
Context:
  • Time of day (trending topics vary)
  • User's current location
  • Device type (mobile vs desktop)
```

### **Minute 27-28: Scoring Function**

**Detail the algorithm:**

```python
class FeedRanker:
    def __init__(self):
        self.model = self.load_ml_model()  # Pre-trained ML model
        self.weights = {
            'recency': 0.25,
            'engagement': 0.30,
            'affinity': 0.25,
            'content': 0.15,
            'context': 0.05
        }
    
    def calculate_score(self, post, user, context):
        """
        Multi-signal ranking with learned weights
        """
        features = self.extract_features(post, user, context)
        
        # Traditional scoring
        recency_score = self._recency_score(post.created_at)
        engagement_score = self._engagement_score(post)
        affinity_score = self._affinity_score(user.id, post.user_id)
        content_score = self._content_score(post)
        context_score = self._context_score(post, context)
        
        # Weighted combination
        base_score = (
            self.weights['recency'] * recency_score +
            self.weights['engagement'] * engagement_score +
            self.weights['affinity'] * affinity_score +
            self.weights['content'] * content_score +
            self.weights['context'] * context_score
        )
        
        # ML boost (if we have trained model)
        ml_boost = self.model.predict(features) if self.model else 0
        
        final_score = base_score + 0.1 * ml_boost
        
        return final_score
    
    def _recency_score(self, created_at):
        """
        Time decay function - newer posts score higher
        """
        age_hours = (datetime.now() - created_at).total_seconds() / 3600
        # Logarithmic decay
        return 1.0 / (1.0 + age_hours / 24.0)
    
    def _engagement_score(self, post):
        """
        Normalize engagement by author's follower count
        Prevents celebrity posts from always dominating
        """
        author_followers = post.author.follower_count or 1
        
        # Weighted engagement
        engagement = (
            1.0 * post.likes_count +
            3.0 * post.comments_count +  # Comments worth more
            5.0 * post.shares_count      # Shares worth most
        )
        
        # Normalize by follower count
        normalized = engagement / math.sqrt(author_followers)
        
        # Cap at 100 to prevent outliers
        return min(normalized, 100) / 100.0
    
    def _affinity_score(self, user_id, author_id):
        """
        How much does this user interact with this author?
        """
        # Get from cache or compute
        cache_key = f"affinity:{user_id}:{author_id}"
        cached = redis.get(cache_key)
        
        if cached:
            return float(cached)
        
        # Compute based on historical interactions
        last_30_days = datetime.now() - timedelta(days=30)
        interactions = db.query("""
            SELECT COUNT(*) FROM interactions
            WHERE user_id = ? AND author_id = ?
            AND created_at > ?
        """, user_id, author_id, last_30_days)
        
        # Logarithmic scale
        score = math.log(interactions + 1) / math.log(100)
        
        # Cache for 1 hour
        redis.setex(cache_key, 3600, score)
        
        return min(score, 1.0)
    
    def _content_score(self, post):
        """
        Content quality signals
        """
        score = 0.5  # Base score
        
        # Has media
        if post.media_urls:
            score += 0.3
        
        # Text length (sweet spot: 100-500 chars)
        text_len = len(post.content)
        if 100 <= text_len <= 500:
            score += 0.2
        elif text_len < 50:
            score -= 0.1  # Too short
        
        return min(score, 1.0)
    
    def _context_score(self, post, context):
        """
        Contextual relevance
        """
        score = 0.5
        
        # Trending topics
        if self._is_trending(post.hashtags, context.time):
            score += 0.3
        
        # Location relevance
        if post.location and context.user_location:
            distance = self._geo_distance(
                post.location, 
                context.user_location
            )
            if distance < 50:  # Within 50km
                score += 0.2
        
        return min(score, 1.0)
```

### **Minute 29: ML-Based Ranking (Advanced)**

> “For a production system, we’d use machine learning…”

**Draw ML Pipeline:**

```
Historical Data Collection
         ↓
┌─────────────────────────┐
│ Training Data:          │
│ - User viewed post      │
│ - User liked post       │
│ - User commented        │
│ - User shared           │
│ - Dwell time            │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Feature Engineering     │
│ - Extract signals       │
│ - Normalize values      │
│ - Create embeddings     │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Model Training          │
│ - Algorithm: GBDT       │
│   (LightGBM/XGBoost)    │
│ - Or: Neural Network    │
│ - Objective: Maximize   │
│   engagement probability│
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Model Serving           │
│ - Deploy to prediction  │
│   service               │
│ - Real-time scoring     │
│ - A/B testing           │
└─────────────────────────┘
```

**Model Architecture:**

```python
# Simplified ML approach

class MLRankingModel:
    """
    Two-tower neural network for feed ranking
    """
    def __init__(self):
        self.user_tower = self._build_user_tower()
        self.post_tower = self._build_post_tower()
        self.interaction_layer = self._build_interaction()
    
    def predict(self, user_features, post_features):
        """
        Predict engagement probability
        """
        # User embedding
        user_embedding = self.user_tower(user_features)
        # Shape: (embedding_dim,)
        
        # Post embedding  
        post_embedding = self.post_tower(post_features)
        # Shape: (embedding_dim,)
        
        # Interaction features
        interaction = self.interaction_layer(
            user_embedding, 
            post_embedding
        )
        
        # Final prediction: probability of engagement
        engagement_prob = sigmoid(interaction)
        
        return engagement_prob
    
    def _build_user_tower(self):
        """
        Neural network for user representation
        Inputs: user_id, follower_count, following_count,
                historical_interactions, user_interests
        Output: dense embedding
        """
        return NeuralNetwork([256, 128, 64])
    
    def _build_post_tower(self):
        """
        Neural network for post representation
        Inputs: author_id, content_embedding, media_type,
                engagement_stats, recency
        Output: dense embedding
        """
        return NeuralNetwork([256, 128, 64])
```

### **Minute 30-31: Ranking at Scale**

**Address performance concerns:**

```
RANKING SCALABILITY CHALLENGES
===============================
Problem 1: Can't score all posts in real-time
  → Too many posts from followed users
  
Solution: Two-stage ranking
  ┌─────────────────────────────┐
  │ Stage 1: Candidate Selection│
  │ - Quick filtering           │
  │ - Fetch top 500 posts       │
  │ - Basic signals only        │
  │ - Fast (< 50ms)             │
  └──────────┬──────────────────┘
             ↓
  ┌─────────────────────────────┐
  │ Stage 2: Heavy Ranking      │
  │ - ML model scoring          │
  │ - Complex features          │
  │ - Score top 500 → 20        │
  │ - Medium speed (< 200ms)    │
  └─────────────────────────────┘

Problem 2: Model serving latency
  
Solution: Pre-compute embeddings
  • User embeddings: Compute daily, cache
  • Post embeddings: Compute at creation
  • Only compute interaction score real-time
```

**Pre-computation Strategy:**

```python
# Offline job (runs daily)
def precompute_user_embeddings():
    """
    Generate embeddings for all active users
    """
    users = db.get_active_users()  # Users active in last 30 days
    
    for user in users:
        features = extract_user_features(user)
        embedding = model.user_tower(features)
        
        # Store in Redis
        redis.setex(
            f"user_embedding:{user.id}",
            86400,  # 24 hour TTL
            embedding.tobytes()
        )

# At post creation
def precompute_post_embedding(post):
    """
    Generate embedding when post is created
    """
    features = extract_post_features(post)
    embedding = model.post_tower(features)
    
    # Store with post in database
    db.update(
        "posts",
        {"post_id": post.id},
        {"embedding": embedding.tobytes()}
    )

# At serving time (fast)
def score_post_for_user(user_id, post_id):
    """
    Fast scoring using pre-computed embeddings
    """
    user_emb = redis.get(f"user_embedding:{user_id}")
    post_emb = db.get_post_embedding(post_id)
    
    # Only compute dot product (very fast)
    score = dot_product(user_emb, post_emb)
    return score
```

-----

## **Deep Dive Option 2: Scalability & Sharding (Minutes 26-31)**

### **Minute 26-27: Database Sharding Strategy**

> “Let’s talk about how we partition data to scale horizontally…”

**Post Database Sharding:**

```
SHARDING STRATEGIES
===================

Option 1: Shard by User ID
┌─────────────────────┐
│ Shard 1 (Users 0-1M)│
│ - All posts by      │
│   these users       │
└─────────────────────┘
┌─────────────────────┐
│ Shard 2 (1M-2M)     │
└─────────────────────┘
┌─────────────────────┐
│ Shard 3 (2M-3M)     │
└─────────────────────┘

Pros:
  ✓ Simple routing: hash(user_id) % num_shards
  ✓ Easy to fetch user's own posts
  ✓ User data locality

Cons:
  ✗ Hot users create hot shards
  ✗ Feed generation requires multi-shard queries

Option 2: Shard by Post ID
┌─────────────────────┐
│ Shard 1 (Posts 0-1B)│
└─────────────────────┘
┌─────────────────────┐
│ Shard 2 (1B-2B)     │
└─────────────────────┘

Pros:
  ✓ Uniform distribution
  ✓ Time-based partitioning (newer posts in newer shards)

Cons:
  ✗ Fetching user's posts requires index
  ✗ More complex routing

RECOMMENDATION: Shard by Post ID
  • More uniform distribution
  • Better for read-heavy workload
  • Can add secondary index on user_id
```

**Implementation:**

```python
class PostDBSharding:
    def __init__(self, num_shards=32):
        self.num_shards = num_shards
        self.shards = [
            connect_to_db(f"post_db_shard_{i}") 
            for i in range(num_shards)
        ]
    
    def get_shard(self, post_id):
        """
        Determine which shard holds this post
        """
        shard_id = post_id % self.num_shards
        return self.shards[shard_id]
    
    def write_post(self, post):
        """
        Write post to appropriate shard
        """
        shard = self.get_shard(post.post_id)
        shard.insert("posts", post)
        
        # Also update secondary index for user_id
        self._update_user_post_index(post.user_id, post.post_id)
    
    def get_post(self, post_id):
        """
        Fetch post from appropriate shard
        """
        shard = self.get_shard(post_id)
        return shard.query(
            "SELECT * FROM posts WHERE post_id = ?", 
            post_id
        )
    
    def get_user_posts(self, user_id, limit=20):
        """
        Fetch user's posts (requires scatter-gather)
        """
        # Option 1: Scatter-gather across all shards (slow)
        results = []
        for shard in self.shards:
            posts = shard.query(
                "SELECT * FROM posts WHERE user_id = ? LIMIT ?",
                user_id, limit
            )
            results.extend(posts)
        
        # Merge and sort
        results.sort(key=lambda p: p.created_at, reverse=True)
        return results[:limit]
        
        # Option 2: Use secondary index (better)
        post_ids = self.user_post_index.get(user_id, limit)
        return [self.get_post(pid) for pid in post_ids]
```

### **Minute 28: Graph Database Sharding**

**Social Graph Partitioning:**

```
GRAPH SHARDING
==============

Challenge: Social graph is highly interconnected
  • Can't easily partition without edge cuts

Strategy 1: Shard by User ID
┌──────────────────────────┐
│ Shard 1: Users 0-1M      │
│ Stores all followers/    │
│ following for these users│
└──────────────────────────┘

Implementation:
CREATE TABLE followers_shard_1 (
    follower_id BIGINT,    -- Must be in range [0, 1M]
    followee_id BIGINT,    -- Can be any user
    created_at TIMESTAMP,
    PRIMARY KEY (follower_id, followee_id)
);

Query: "Who does Alice follow?"
  → Go to Alice's shard
  → SELECT followee_id WHERE follower_id = alice_id

Query: "Who follows Bob?"
  → Scatter-gather across ALL shards
  → SELECT follower_id WHERE followee_id = bob_id
  → This is expensive!

Optimization: Dual Storage
  • followers_by_follower (sharded by follower_id)
  • followers_by_followee (sharded by followee_id)
  • Write to both, read from appropriate one
```

**Code:**

```python
class GraphDBSharding:
    def __init__(self):
        self.followers_by_follower = ShardedDB(shard_key='follower_id')
        self.followers_by_followee = ShardedDB(shard_key='followee_id')
    
    def follow(self, follower_id, followee_id):
        """
        User A follows User B
        Write to both tables for efficient reads
        """
        # Table 1: Optimize for "who does A follow?"
        self.followers_by_follower.insert({
            'follower_id': follower_id,
            'followee_id': followee_id,
            'created_at': datetime.now()
        })
        
        # Table 2: Optimize for "who follows B?"
        self.followers_by_followee.insert({
            'followee_id': followee_id,
            'follower_id': follower_id,
            'created_at': datetime.now()
        })
    
    def get_following(self, user_id):
        """
        Who does this user follow?
        Single shard lookup
        """
        return self.followers_by_follower.query(
            user_id,  # Shard key
            "SELECT followee_id FROM followers WHERE follower_id = ?",
            user_id
        )
    
    def get_followers(self, user_id):
        """
        Who follows this user?
        Single shard lookup (thanks to dual storage)
        """
        return self.followers_by_followee.query(
            user_id,  # Shard key
            "SELECT follower_id FROM followers WHERE followee_id = ?",
            user_id
        )
```

### **Minute 29: Cache Sharding**

**Redis Cluster Setup:**

```
CACHE SHARDING (Redis Cluster)
===============================

Setup: 6 nodes (3 master, 3 replica)
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Master 1   │  │ Master 2   │  │ Master 3   │
│ Slots:     │  │ Slots:     │  │ Slots:     │
│ 0-5460     │  │ 5461-10922 │  │ 10923-16383│
└──────┬─────┘  └──────┬─────┘  └──────┬─────┘
       │                │                │
┌──────▼─────┐  ┌──────▼─────┐  ┌──────▼─────┐
│ Replica 1  │  │ Replica 2  │  │ Replica 3  │
└────────────┘  └────────────┘  └────────────┘

Consistent Hashing:
  key = "feed:12345"
  slot = CRC16(key) % 16384
  node = slot_to_node_mapping[slot]

Advantages:
  ✓ Horizontal scaling (add more nodes)
  ✓ Automatic failover (replica promotion)
  ✓ Data partitioning

Implementation:
```

```python
from rediscluster import RedisCluster

class FeedCache:
    def __init__(self):
        # Redis Cluster handles sharding automatically
        self.redis = RedisCluster(
            startup_nodes=[
                {"host": "redis-1", "port": 6379},
                {"host": "redis-2", "port": 6379},
                {"host": "redis-3", "port": 6379}
            ],
            decode_responses=True
        )
    
    def add_to_feed(self, user_id, post_id, score=None):
        """
        Add post to user's feed
        Redis Cluster automatically routes to correct node
        """
        key = f"feed:{user_id}"
        score = score or time.time()
        
        # ZADD automatically goes to the right shard
        self.redis.zadd(key, {post_id: score})
        
        # Keep only recent 1000 posts
        self.redis.zremrangebyrank(key, 0, -1001)
        
        # Set TTL
        self.redis.expire(key, 300)  # 5 minutes
    
    def get_feed(self, user_id, limit=20):
        """
        Get user's feed
        """
        key = f"feed:{user_id}"
        
        # ZREVRANGE automatically routes to correct node
        post_ids = self.redis.zrevrange(key, 0, limit - 1)
        
        return post_ids
```

### **Minute 30-31: Service Scaling**

**Horizontal Scaling Strategy:**

```
SERVICE SCALING
===============

Stateless Services (Easy to scale):
┌──────────────────────────────────┐
│        Load Balancer (Nginx)     │
└───────────┬──────────────────────┘
            │
    ┌───────┼───────┬───────┬──────────┐
    ▼       ▼       ▼       ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐  ┌────────┐
│Post    │ │Post    │ │Post    │  │Post    │
│Service │ │Service │ │Service │  │Service │
│Instance│ │Instance│ │Instance│  │Instance│
│   1    │ │   2    │ │   3    │  │   N    │
└────────┘ └────────┘ └────────┘  └────────┘

Auto-scaling triggers:
  • CPU > 70% for 5 minutes → scale up
  • QPS > 10K per instance → scale up
  • Error rate > 1% → investigate, maybe scale
  • CPU < 30% for 30 minutes → scale down

Stateful Services (More complex):
  • Fan-out Workers: Scale based on queue depth
  • Ranking Service: Scale based on latency p99
```

**Auto-scaling Configuration:**

```yaml
# Kubernetes HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: post-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: post-service
  minReplicas: 10
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "10000"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 2
        periodSeconds: 120
```

-----

## **Deep Dive Option 3: The Celebrity Problem (Minutes 26-31)**

### **Minute 26-27: Problem Definition**

> “Let me detail the celebrity/hot user problem and our solution…”

**Write on board:**

```
THE CELEBRITY PROBLEM
=====================

Scenario: Taylor Swift posts (100M followers)

Naive fan-out on write:
  1. Taylor posts
  2. System tries to write to 100M feeds
  3. 100M cache writes
  4. Takes minutes to hours
  5. Overwhelms the system
  6. Other users see delays

Impact:
  • Write amplification: 1 write → 100M writes
  • Cache pollution: Celebrity posts push out others
  • Uneven load: Celebrity post creates traffic spike
  • Latency: Regular users wait for celebrity fan-out
```

### **Minute 28: Hybrid Solution Deep Dive**

**Detailed Hybrid Strategy:**

```python
class HybridFanoutService:
    """
    Intelligent fan-out based on follower count
    """
    # Thresholds
    SMALL_USER_THRESHOLD = 1000      # Full fan-out
    MEDIUM_USER_THRESHOLD = 100000   # Partial fan-out
    # Above 100K: Pull model only
    
    def __init__(self):
        self.kafka_producer = KafkaProducer()
        self.redis = Redis()
        self.graph_db = GraphDB()
        self.post_db = PostDB()
    
    async def fanout_post(self, post):
        """
        Decide fan-out strategy based on author's follower count
        """
        author_id = post.user_id
        follower_count = await self._get_follower_count(author_id)
        
        if follower_count < self.SMALL_USER_THRESHOLD:
            # SMALL USER: Full push model
            await self._full_fanout(post)
            
        elif follower_count < self.MEDIUM_USER_THRESHOLD:
            # MEDIUM USER: Hybrid approach
            await self._partial_fanout(post)
            
        else:
            # CELEBRITY: Pure pull model
            await self._celebrity_fanout(post)
    
    async def _full_fanout(self, post):
        """
        Push to all followers' feeds
        Fast for small user base
        """
        followers = await self.graph_db.get_followers(post.user_id)
        
        # Batch writes for efficiency
        pipeline = self.redis.pipeline()
        for follower_id in followers:
            key = f"feed:{follower_id}"
            pipeline.zadd(key, {post.post_id: post.created_at.timestamp()})
            pipeline.expire(key, 300)  # 5 min TTL
        
        await pipeline.execute()
        
        print(f"Fanned out to {len(followers)} users (push model)")
    
    async def _partial_fanout(self, post):
        """
        Push only to active followers
        Others will pull on demand
        """
        # Get recently active followers (logged in last 24h)
        active_followers = await self.graph_db.get_active_followers(
            post.user_id,
            since=datetime.now() - timedelta(days=1)
        )
        
        # Push to active followers (maybe 10-20% of total)
        pipeline = self.redis.pipeline()
        for follower_id in active_followers:
            key = f"feed:{follower_id}"
            pipeline.zadd(key, {post.post_id: post.created_at.timestamp()})
            pipeline.expire(key, 300)
        await pipeline.execute()
        
        # Add to celebrity post cache for others to pull
        await self.redis.zadd(
            f"celebrity_posts:{post.user_id}",
            {post.post_id: post.created_at.timestamp()}
        )
        await self.redis.expire(f"celebrity_posts:{post.user_id}", 3600)
        
        print(f"Partial fanout: {len(active_followers)} active users")
    
    async def _celebrity_fanout(self, post):
        """
        NO fan-out to followers
        Just index for pull-time retrieval
        """
        # Add to celebrity's recent posts (sorted by time)
        await self.redis.zadd(
            f"celebrity_posts:{post.user_id}",
            {post.post_id: post.created_at.timestamp()}
        )
        await self.redis.expire(f"celebrity_posts:{post.user_id}", 3600)
        
        # Optionally: pre-warm cache for top content
        if await self._is_likely_viral(post):
            await self.redis.set(
                f"post:{post.post_id}",
                json.dumps(post.to_dict()),
                ex=3600
            )
        
        print(f"Celebrity post indexed (pull model)")
    
    async def _get_follower_count(self, user_id):
        """
        Get follower count (cached)
        """
        cache_key = f"follower_count:{user_id}"
        count = await self.redis.get(cache_key)
        
        if count is None:
            count = await self.graph_db.count_followers(user_id)
            await self.redis.setex(cache_key, 3600, count)
        
        return int(count)
```

### **Minute 29: Read-time Merging for Celebrities**

**Feed generation with celebrity content:**

```python
class FeedGenerator:
    async def generate_feed(self, user_id, limit=20):
        """
        Generate feed with celebrity content merged in
        """
        # Get users this person follows
        following = await self.graph_db.get_following(user_id)
        
        # Separate into regular and celebrity
        regular_users = []
        celebrities = []
        
        for followed_user in following:
            if followed_user.follower_count < 100000:
                regular_users.append(followed_user.id)
            else:
                celebrities.append(followed_user.id)
        
        # Strategy 1: Get pre-fanned out posts (push model)
        pushed_posts = await self.redis.zrevrange(
            f"feed:{user_id}",
            0,
            limit * 2  # Get more for merging
        )
        
        # Strategy 2: Get celebrity posts (pull model)
        celebrity_posts = []
        for celebrity_id in celebrities:
            posts = await self.redis.zrevrange(
                f"celebrity_posts:{celebrity_id}",
                0,
                10  # Get recent 10 from each celebrity
            )
            celebrity_posts.extend(posts)
        
        # Merge and sort by timestamp
        all_post_ids = pushed_posts + celebrity_posts
        
        # Hydrate posts (get full post data)
        posts = await self.post_db.get_posts(all_post_ids)
        
        # Sort by creation time (or ranking score)
        posts.sort(key=lambda p: p.created_at, reverse=True)
        
        # Rank and return top N
        ranked_posts = await self.ranking_service.rank(posts, user_id)
        return ranked_posts[:limit]
```












### **Minute 30: Hot Partition Mitigation**

**Addressing the hot partition problem:**

```
HOT PARTITION PROBLEM
=====================

Issue: Celebrity posts create hot keys in cache
  • Key: celebrity_posts:taylor_swift
  • Gets millions of reads per second
  • Single Redis node can't handle it
  • Becomes bottleneck

Solutions:
```

**1. Replication of Hot Keys**

```python
class HotKeyReplicator:
    """
    Replicate frequently accessed keys across multiple cache nodes
    """
    def __init__(self, num_replicas=5):
        self.num_replicas = num_replicas
        self.redis_nodes = [
            Redis(host=f"redis-{i}") 
            for i in range(num_replicas)
        ]
        self.hot_key_detector = HotKeyDetector()
    
    async def get(self, key):
        """
        Get value, load balance across replicas for hot keys
        """
        if self.hot_key_detector.is_hot(key):
            # Route to random replica to spread load
            node_idx = random.randint(0, self.num_replicas - 1)
            return await self.redis_nodes[node_idx].get(key)
        else:
            # Normal key, use primary
            return await self.redis_nodes[0].get(key)
    
    async def set(self, key, value, ttl=None):
        """
        Write to all replicas if hot key
        """
        if self.hot_key_detector.is_hot(key):
            # Write to all replicas
            tasks = [
                node.setex(key, ttl, value) if ttl else node.set(key, value)
                for node in self.redis_nodes
            ]
            await asyncio.gather(*tasks)
        else:
            # Normal key, write to primary only
            if ttl:
                await self.redis_nodes[0].setex(key, ttl, value)
            else:
                await self.redis_nodes[0].set(key, value)

class HotKeyDetector:
    """
    Detect hot keys using sliding window counter
    """
    def __init__(self, threshold=10000):
        self.threshold = threshold  # Requests per minute
        self.counters = {}  # key -> deque of timestamps
        self.window = 60  # seconds
    
    def is_hot(self, key):
        """
        Check if key is hot (high request rate)
        """
        now = time.time()
        
        if key not in self.counters:
            self.counters[key] = deque()
        
        # Add current access
        self.counters[key].append(now)
        
        # Remove old accesses outside window
        while self.counters[key] and self.counters[key][0] < now - self.window:
            self.counters[key].popleft()
        
        # Check if exceeds threshold
        return len(self.counters[key]) > self.threshold
```

**2. Client-Side Caching**

```python
class ClientCache:
    """
    Cache celebrity posts on client side
    Reduces load on backend
    """
    def __init__(self):
        self.local_cache = LRUCache(maxsize=1000)
        self.cache_ttl = 60  # 1 minute for celebrity posts
    
    async def get_celebrity_posts(self, celebrity_id):
        """
        Check local cache first
        """
        cache_key = f"celebrity_posts:{celebrity_id}"
        
        # Check local cache
        cached = self.local_cache.get(cache_key)
        if cached and not self._is_expired(cached):
            return cached['data']
        
        # Cache miss, fetch from backend
        posts = await self.backend.get_celebrity_posts(celebrity_id)
        
        # Store in local cache
        self.local_cache[cache_key] = {
            'data': posts,
            'timestamp': time.time()
        }
        
        return posts
    
    def _is_expired(self, cached_item):
        age = time.time() - cached_item['timestamp']
        return age > self.cache_ttl
```

**3. Request Coalescing**

```python
class RequestCoalescer:
    """
    Batch multiple identical requests into one backend call
    """
    def __init__(self):
        self.in_flight = {}  # key -> Future
        self.lock = asyncio.Lock()
    
    async def get(self, key, fetch_func):
        """
        Coalesce concurrent requests for same key
        """
        async with self.lock:
            # Check if request already in flight
            if key in self.in_flight:
                # Wait for existing request
                return await self.in_flight[key]
            
            # Create new request
            future = asyncio.create_task(fetch_func(key))
            self.in_flight[key] = future
        
        try:
            # Execute and get result
            result = await future
            return result
        finally:
            # Clean up
            async with self.lock:
                del self.in_flight[key]

# Usage
coalescer = RequestCoalescer()

async def get_celebrity_posts(celebrity_id):
    """
    Get celebrity posts with request coalescing
    """
    key = f"celebrity_posts:{celebrity_id}"
    
    async def fetch(k):
        return await redis.zrevrange(k, 0, 10)
    
    return await coalescer.get(key, fetch)
```

### **Minute 31: Celebrity Write Path Optimization**

**Async processing with backpressure:**

```python
class CelebrityPostProcessor:
    """
    Process celebrity posts with rate limiting and backpressure
    """
    def __init__(self):
        self.kafka = KafkaProducer()
        self.rate_limiter = RateLimiter(max_posts_per_hour=100)
        self.priority_queue = PriorityQueue()
    
    async def process_celebrity_post(self, post, author):
        """
        Handle celebrity post with special processing
        """
        # Check rate limit (prevent spam)
        if not self.rate_limiter.allow(author.id):
            raise RateLimitError("Too many posts")
        
        # Save post to database (immediate)
        await self.post_db.save(post)
        
        # Queue for async processing (lower priority than regular posts)
        await self.priority_queue.put({
            'post': post,
            'priority': 'low',  # Celebrity posts are lower priority
            'follower_count': author.follower_count
        })
        
        # Publish event (non-blocking)
        self.kafka.produce(
            topic='celebrity-posts',
            key=str(author.id),
            value=json.dumps(post.to_dict())
        )
        
        # Pre-compute trending signals
        await self._compute_trending_score(post)
        
        # Return immediately (don't wait for fan-out)
        return {'post_id': post.id, 'status': 'processing'}
    
    async def _compute_trending_score(self, post):
        """
        Pre-compute signals that help with ranking
        """
        # Calculate initial engagement prediction
        author_avg_engagement = await self._get_author_avg_engagement(
            post.user_id
        )
        
        # Store prediction
        await self.redis.setex(
            f"post_prediction:{post.id}",
            3600,
            json.dumps({
                'expected_likes': author_avg_engagement['likes'],
                'expected_shares': author_avg_engagement['shares'],
                'trending_score': self._calculate_trending_score(post)
            })
        )
```

-----

## **Deep Dive Option 4: Cache Invalidation & Consistency (Minutes 26-31)**

### **Minute 26-27: Cache Invalidation Strategies**

> “Cache invalidation is notoriously hard. Let me show you how we handle it…”

**Write on board:**

```
CACHE INVALIDATION CHALLENGES
==============================

Problem 1: Post updated/deleted
  → Need to remove from all followers' feeds
  
Problem 2: User unfollows someone
  → Need to remove that user's posts from feed
  
Problem 3: New follower
  → Need to populate their feed with followed users' posts
  
Problem 4: Stale data
  → Feed shows old like counts, comment counts
```

### **Cache Invalidation Patterns:**

```python
class CacheInvalidationService:
    """
    Handle various cache invalidation scenarios
    """
    def __init__(self):
        self.redis = Redis()
        self.kafka = KafkaProducer()
        self.graph_db = GraphDB()
    
    async def on_post_deleted(self, post_id, author_id):
        """
        Post was deleted - remove from all caches
        """
        # Strategy 1: Lazy deletion (mark as deleted)
        await self.post_db.update(
            post_id, 
            {'is_deleted': True, 'deleted_at': datetime.now()}
        )
        
        # Strategy 2: Active invalidation for small users
        follower_count = await self._get_follower_count(author_id)
        
        if follower_count < 10000:
            # Small user: actively remove from feeds
            followers = await self.graph_db.get_followers(author_id)
            
            pipeline = self.redis.pipeline()
            for follower_id in followers:
                feed_key = f"feed:{follower_id}"
                pipeline.zrem(feed_key, post_id)
            
            await pipeline.execute()
        else:
            # Celebrity: just mark deleted, filter on read
            # Too expensive to invalidate millions of caches
            await self.redis.setex(
                f"deleted_post:{post_id}",
                86400,  # 24 hours
                '1'
            )
        
        # Invalidate post cache
        await self.redis.delete(f"post:{post_id}")
        
        print(f"Post {post_id} deleted and caches invalidated")
    
    async def on_post_updated(self, post_id, updates):
        """
        Post content updated
        """
        # Update database
        await self.post_db.update(post_id, updates)
        
        # Invalidate cached post data
        await self.redis.delete(f"post:{post_id}")
        
        # Feed entries are just IDs, so no need to update
        # They'll fetch fresh data on hydration
        
        # Update search index if content changed
        if 'content' in updates:
            await self.search_index.update(post_id, updates['content'])
    
    async def on_user_unfollow(self, follower_id, followee_id):
        """
        User A unfollows User B
        Remove B's posts from A's feed
        """
        # Update graph database
        await self.graph_db.remove_follow(follower_id, followee_id)
        
        # Strategy 1: Immediate removal (simple but expensive)
        # Get all posts from unfollowed user
        followee_posts = await self.redis.zrevrange(
            f"celebrity_posts:{followee_id}",
            0, -1
        )
        
        # Remove from follower's feed
        if followee_posts:
            await self.redis.zrem(
                f"feed:{follower_id}",
                *followee_posts
            )
        
        # Strategy 2: Lazy removal (better performance)
        # Just invalidate the feed cache entirely
        await self.redis.delete(f"feed:{follower_id}")
        
        # Feed will be regenerated on next request
        # with updated following list
    
    async def on_new_follow(self, follower_id, followee_id):
        """
        User A follows User B
        Add B's recent posts to A's feed
        """
        # Update graph database
        await self.graph_db.add_follow(follower_id, followee_id)
        
        # Check if followee is celebrity
        follower_count = await self._get_follower_count(followee_id)
        
        if follower_count < 1000:
            # Regular user: add their recent posts to new follower's feed
            recent_posts = await self.post_db.get_user_recent_posts(
                followee_id,
                limit=50
            )
            
            pipeline = self.redis.pipeline()
            feed_key = f"feed:{follower_id}"
            
            for post in recent_posts:
                pipeline.zadd(
                    feed_key,
                    {post.id: post.created_at.timestamp()}
                )
            
            await pipeline.execute()
        else:
            # Celebrity: just invalidate follower's feed
            # They'll pull celebrity posts on next feed request
            await self.redis.delete(f"feed:{follower_id}")
        
        # Increment follower count cache
        await self.redis.incr(f"follower_count:{followee_id}")
    
    async def on_engagement_update(self, post_id, engagement_type):
        """
        Post got liked/commented/shared
        Update cached engagement counts
        """
        # Update database
        await self.post_db.increment_engagement(post_id, engagement_type)
        
        # Invalidate cached post (will fetch fresh data next time)
        await self.redis.delete(f"post:{post_id}")
        
        # Could also update incrementally:
        # await self.redis.hincrby(f"post:{post_id}", f"{engagement_type}_count", 1)
        # But this requires more complex logic to handle race conditions
```

### **Minute 28-29: Consistency Guarantees**

**Trade-offs between consistency and availability:**

```
CONSISTENCY LEVELS
==================

Level 1: Eventual Consistency (What we use)
┌──────────────────────────────────────────┐
│ User posts → Database written            │
│           → Kafka event published        │
│           → Fan-out happens async        │
│ Timeline:                                │
│  t=0ms:  Post saved to DB                │
│  t=5ms:  Event in Kafka                  │
│  t=50ms: Fan-out starts                  │
│  t=500ms: Most feeds updated             │
│  t=5s:   All feeds updated               │
└──────────────────────────────────────────┘

Implications:
  ✓ Fast writes (user gets immediate response)
  ✓ High throughput
  ✗ Followers may not see post immediately
  ✗ Possible race conditions

Level 2: Strong Consistency (Too slow for us)
┌──────────────────────────────────────────┐
│ User posts → Database written            │
│           → Wait for all fan-outs        │
│           → Return success               │
│ Timeline:                                │
│  t=0ms:  Post saved to DB                │
│  t=5s:   All feeds updated               │
│  t=5s:   User gets response              │
└──────────────────────────────────────────┘

Why we don't use this:
  ✗ 5 second latency for user
  ✗ Blocks on slow followers
  ✗ Can't scale to celebrity posts
```

**Handling race conditions:**

```python
class ConsistencyHandler:
    """
    Handle race conditions in distributed system
    """
    
    async def ensure_timeline_consistency(self, user_id):
        """
        Ensure user's feed is consistent when reading
        """
        # Get feed from cache
        cached_feed = await self.redis.zrevrange(
            f"feed:{user_id}", 
            0, 20
        )
        
        if not cached_feed:
            # Cache miss - generate fresh feed
            return await self.generate_fresh_feed(user_id)
        
        # Cache hit - but check for recent follows
        last_feed_update = await self.redis.get(
            f"feed_timestamp:{user_id}"
        )
        
        if last_feed_update:
            last_update_time = float(last_feed_update)
            now = time.time()
            
            # If feed is older than 5 minutes, regenerate
            if now - last_update_time > 300:
                return await self.generate_fresh_feed(user_id)
        
        # Feed is fresh, return cached version
        return cached_feed
    
    async def handle_concurrent_writes(self, post_id, field, increment):
        """
        Handle concurrent engagement updates (likes, comments)
        Use atomic operations
        """
        # Option 1: Use Redis INCR (atomic)
        await self.redis.hincrby(f"post:{post_id}", field, increment)
        
        # Option 2: Use database with optimistic locking
        max_retries = 5
        for attempt in range(max_retries):
            try:
                post = await self.post_db.get(post_id)
                version = post['version']
                
                # Update with version check
                success = await self.post_db.update_with_version(
                    post_id,
                    {field: post[field] + increment},
                    expected_version=version,
                    new_version=version + 1
                )
                
                if success:
                    break
            except VersionMismatchError:
                # Retry
                await asyncio.sleep(0.01 * (2 ** attempt))
                continue
        
        return success
    
    async def ensure_read_your_writes(self, user_id, post_id):
        """
        Ensure user can see their own post immediately after writing
        """
        # After user creates post, explicitly add to their feed cache
        await self.redis.zadd(
            f"feed:{user_id}",
            {post_id: time.time()}
        )
        
        # Also add to their profile cache
        await self.redis.zadd(
            f"user_posts:{user_id}",
            {post_id: time.time()}
        )
        
        # Set flag that this user has pending writes
        await self.redis.setex(
            f"pending_write:{user_id}:{post_id}",
            10,  # 10 seconds
            '1'
        )
```

### **Minute 30-31: Cache Stampede Prevention**

**Handling thundering herd:**

```python
class CacheStampedeProtection:
    """
    Prevent cache stampede when popular keys expire
    """
    
    def __init__(self):
        self.redis = Redis()
        self.locks = {}  # In-memory locks per process
    
    async def get_with_lock(self, key, fetch_func, ttl=300):
        """
        Get value with distributed lock to prevent stampede
        
        Scenario: Taylor Swift's feed expires
        1000 concurrent requests try to regenerate it
        Without lock: 1000 database queries
        With lock: 1 database query, 999 wait
        """
        # Try to get from cache
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        
        # Cache miss - acquire lock
        lock_key = f"lock:{key}"
        lock_acquired = await self.redis.set(
            lock_key,
            '1',
            nx=True,  # Only set if not exists
            ex=10     # Lock expires in 10 seconds
        )
        
        if lock_acquired:
            try:
                # We got the lock - fetch data
                value = await fetch_func()
                
                # Store in cache
                await self.redis.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                
                return value
            finally:
                # Release lock
                await self.redis.delete(lock_key)
        else:
            # Someone else is fetching - wait and retry
            for _ in range(50):  # Wait up to 5 seconds
                await asyncio.sleep(0.1)
                
                value = await self.redis.get(key)
                if value:
                    return json.loads(value)
            
            # Timeout - fetch anyway (fallback)
            return await fetch_func()
    
    async def probabilistic_early_expiration(self, key, fetch_func, ttl=300):
        """
        Prevent stampede by refreshing cache before it expires
        XFetch algorithm
        """
        # Get value and TTL
        value = await self.redis.get(key)
        remaining_ttl = await self.redis.ttl(key)
        
        if value is None:
            # Cache miss - fetch normally
            value = await fetch_func()
            await self.redis.setex(key, ttl, json.dumps(value))
            return value
        
        # Calculate refresh probability
        # Higher probability as TTL approaches 0
        delta = ttl - remaining_ttl
        beta = 1.0  # Tuning parameter
        
        refresh_probability = delta * beta * math.log(random.random()) / ttl
        
        if refresh_probability < -1:
            # Refresh cache early
            fresh_value = await fetch_func()
            await self.redis.setex(key, ttl, json.dumps(fresh_value))
            return fresh_value
        
        # Return cached value
        return json.loads(value)
    
    async def cache_with_stale_while_revalidate(self, key, fetch_func, ttl=300):
        """
        Serve stale data while refreshing in background
        """
        value = await self.redis.get(key)
        remaining_ttl = await self.redis.ttl(key)
        
        if value is None:
            # Cache miss - fetch normally
            value = await fetch_func()
            await self.redis.setex(key, ttl, json.dumps(value))
            return json.loads(value)
        
        if remaining_ttl < 60:  # Less than 1 minute left
            # Serve stale data
            stale_data = json.loads(value)
            
            # Refresh in background (don't wait)
            asyncio.create_task(self._refresh_cache(key, fetch_func, ttl))
            
            return stale_data
        
        return json.loads(value)
    
    async def _refresh_cache(self, key, fetch_func, ttl):
        """
        Background task to refresh cache
        """
        try:
            fresh_value = await fetch_func()
            await self.redis.setex(key, ttl, json.dumps(fresh_value))
        except Exception as e:
            # Log error but don't crash
            print(f"Error refreshing cache for {key}: {e}")
```

**Multi-level caching:**

```python
class MultiLevelCache:
    """
    L1: Application memory (fastest, smallest)
    L2: Redis (fast, medium)
    L3: Database (slow, largest)
    """
    
    def __init__(self):
        self.l1_cache = LRUCache(maxsize=1000)  # In-memory
        self.l2_cache = Redis()                  # Redis
        self.l3_store = Database()               # Database
    
    async def get(self, key):
        """
        Try L1 → L2 → L3
        """
        # L1: Application memory
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # L2: Redis
        value = await self.l2_cache.get(key)
        if value:
            # Populate L1
            self.l1_cache[key] = value
            return value
        
        # L3: Database
        value = await self.l3_store.get(key)
        if value:
            # Populate L2 and L1
            await self.l2_cache.setex(key, 300, value)
            self.l1_cache[key] = value
            return value
        
        return None
    
    async def set(self, key, value, ttl=300):
        """
        Write through all levels
        """
        # Write to database (source of truth)
        await self.l3_store.set(key, value)
        
        # Populate caches
        await self.l2_cache.setex(key, ttl, value)
        self.l1_cache[key] = value
    
    async def invalidate(self, key):
        """
        Invalidate all levels
        """
        # Remove from L1
        if key in self.l1_cache:
            del self.l1_cache[key]
        
        # Remove from L2
        await self.l2_cache.delete(key)
        
        # L3 (database) keeps the value
```

-----

## **How to Navigate the Deep Dive Phase**

### **Reading the Interviewer**

**Positive signals (keep going):**

- Nodding, taking notes
- Asking follow-up questions
- “Interesting, tell me more about…”
- Leaning forward, engaged

**Negative signals (change topic):**

- Looking at clock frequently
- Glazed eyes, disengaged
- “OK, what about…” (redirecting)
- Interrupting to move on

### **Transitioning Between Topics**

**After covering a topic:**

> “That covers [topic]. Are there any questions on this, or should we move to [next topic]?”

**If running short on time:**

> “I see we have 10 minutes left. Would you like me to continue here, or should we discuss trade-offs and failure scenarios?”

**If interviewer is quiet:**

> “I can go deeper into [A], [B], or [C]. Which would be most valuable?”

-----

## **Key Takeaways for Deep Dive Phase**

### **What Makes a Strong Deep Dive:**

1. **Specificity**: Actual code, not hand-waving
1. **Trade-offs**: Explain why you chose this approach
1. **Numbers**: Reference your capacity calculations
1. **Real-world awareness**: Mention production challenges
1. **Alternatives**: Show you know multiple solutions

### **Common Mistakes:**

❌ **Going too shallow**: “We’d use Redis” (not enough)
❌ **Going too deep too fast**: Diving into TCP handshakes
❌ **Ignoring interviewer**: Talking for 10 minutes straight
❌ **Not connecting to requirements**: Solving problems you don’t have
❌ **Being dogmatic**: “We MUST use Kafka” (why not Kinesis/RabbitMQ?)

### **Time Management:**

- **5 minutes per deep dive topic** is ideal
- **Cover 2-3 topics** in 14 minutes
- **Save 1-2 minutes** for transition to next phase
- **Watch the clock** - glance every 2-3 minutes

-----

**At Minute 40, transition to trade-offs:**

> “We’ve covered [topics]. Now let me discuss the key trade-offs in this design and how we’d handle failures…”

This positions you perfectly for the final critical phase where you demonstrate senior-level judgment about real-world constraints.​​​​​​​​​​​​​​​​
