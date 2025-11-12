# Minutes 11-25: High-Level Architecture - Detailed Breakdown

This is the **core deliverable** of your interview. You need to design a complete, coherent system while explaining your reasoning. This section will make or break your performance.

-----

## **Minute 11-12: Set Up the Canvas & Component Overview**

### **Start with a Clear Statement**

> “Based on our requirements and calculations, I’m going to design a system with these major components. Let me start with a high-level view, then we’ll drill into each part.”

### **Draw the Basic Layout First**

Set up your whiteboard with clear zones:

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  [CLIENT LAYER]                                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [API GATEWAY / LOAD BALANCERS]                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [APPLICATION SERVICES]                                 │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [DATA STORES]                                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### **List Core Components**

**Write on the side:**

```
MAJOR COMPONENTS
================
1. API Gateway & Load Balancers
2. Post Service (write path)
3. Feed Service (read path)
4. Fan-out Service
5. User Service
6. Graph Service (followers/following)
7. Post Database
8. Graph Database
9. Feed Cache (Redis)
10. CDN (for media)
11. Object Storage (S3)
12. Message Queue (Kafka)
```

**Say:** “These are the key pieces. I’ll show how they interact for both posting and reading feeds.”

-----

## **Minute 12-15: Write Path (Post Creation Flow)**

### **Draw the Write Path**

> “Let’s start with what happens when a user creates a post…”

```
┌──────────┐
│  Mobile  │
│  Client  │
└────┬─────┘
     │ 1. POST /api/posts
     │    {userId, content, mediaIds}
     ▼
┌─────────────┐
│API Gateway/ │
│Load Balancer│
└─────┬───────┘
      │ 2. Route to Post Service
      ▼
┌──────────────┐
│ Post Service │◄────┐
└──────┬───────┘     │ 3a. Validate user
       │             │     Get user info
       │        ┌────┴───────┐
       │        │User Service│
       │        └────────────┘
       │
       │ 3b. Generate Post ID
       │     Save post
       ▼
┌──────────────┐
│  Post DB     │
│  (Cassandra/ │
│   MySQL)     │
└──────┬───────┘
       │
       │ 4. Publish PostCreated event
       ▼
┌──────────────┐
│Message Queue │
│   (Kafka)    │
└──────┬───────┘
       │
       │ 5. Fan-out Service consumes
       ▼
┌──────────────┐
│ Fan-out      │
│ Service      │
└──────┬───────┘
       │
       │ 6a. Get followers    6b. Write to feeds
       │                           ▼
       ▼                     ┌─────────────┐
┌──────────────┐             │ Feed Cache  │
│  Graph DB    │             │  (Redis)    │
│  (Neo4j/     │             │             │
│   MySQL)     │             └─────────────┘
└──────────────┘
```

### **Narrate Each Step**

**1. Client Request**

```
POST /api/v1/posts
{
  "userId": 12345,
  "content": "Hello world!",
  "mediaIds": ["img_001", "img_002"],
  "timestamp": "2025-10-24T10:30:00Z"
}
```

**2. API Gateway**

- Authenticate user (JWT validation)
- Rate limiting (prevent spam)
- Route to appropriate service

**3. Post Service**

```python
# Pseudo-code
def createPost(userId, content, mediaIds):
    # Validate user exists and is active
    user = userService.getUser(userId)
    
    # Generate unique post ID (Snowflake ID or UUID)
    postId = generatePostId()
    
    # Save to database
    post = {
        'postId': postId,
        'userId': userId,
        'content': content,
        'mediaUrls': getMediaUrls(mediaIds),
        'createdAt': now(),
        'likesCount': 0,
        'commentsCount': 0
    }
    postDB.save(post)
    
    # Publish event for async processing
    kafka.publish('post-created', post)
    
    return postId
```

**4. Message Queue (Kafka)**

- Decouples post creation from fan-out
- Allows async processing
- Provides durability and replay capability

**5. Fan-out Service (Critical Component)**

> “This is where our hybrid approach comes in…”

```python
def fanOutPost(post):
    userId = post.userId
    
    # Get user's follower count
    followerCount = graphService.getFollowerCount(userId)
    
    if followerCount < 1000:
        # PUSH MODEL: Fan-out on write
        followers = graphService.getFollowers(userId)
        for followerId in followers:
            feedCache.addToFeed(followerId, post.postId)
    else:
        # PULL MODEL: Fan-out on read
        # Just mark that this celebrity posted
        # We'll fetch during read time
        celebrityPostCache.add(userId, post.postId)
```

### **Key Design Decision - Explain the Hybrid Approach**

**Write on board:**

```
FAN-OUT STRATEGY (HYBRID)
=========================
Regular Users (<1K followers):
  ✓ Push Model (fan-out on write)
  ✓ Pre-compute feeds
  ✓ Fast reads, more writes
  
Celebrities (>1K followers):
  ✓ Pull Model (fan-out on read)  
  ✓ Compute feeds on-demand
  ✓ Slower reads, fewer writes
  
Why? 1M followers × 1 post = 1M writes
     Too expensive to fan-out!
```

-----

## **Minute 15-18: Read Path (Feed Generation Flow)**

### **Draw the Read Path**

> “Now let’s look at how we generate a user’s feed…”

```
┌──────────┐
│  Mobile  │
│  Client  │
└────┬─────┘
     │ 1. GET /api/feed?userId=123
     ▼
┌─────────────┐
│API Gateway/ │
│Load Balancer│
└─────┬───────┘
      │ 2. Route to Feed Service
      ▼
┌──────────────┐
│ Feed Service │
└──────┬───────┘
       │ 3. Check cache
       ▼
┌──────────────┐      Cache Hit
│ Feed Cache   │────────────────┐
│   (Redis)    │                │
└──────┬───────┘                │
       │ Cache Miss             │
       │                        │
       │ 4. Fetch following     │
       ▼                        │
┌──────────────┐                │
│  Graph DB    │                │
│              │                │
└──────┬───────┘                │
       │                        │
       │ 5. Get posts from      │
       │    followed users      │
       ▼                        │
┌──────────────┐                │
│  Post DB     │                │
│              │                │
└──────┬───────┘                │
       │                        │
       │ 6. Merge & rank        │
       ▼                        ▼
┌───────────────────────────────┐
│   Ranking Service             │
│   (ML-based scoring)          │
└──────┬────────────────────────┘
       │ 7. Hydrate full posts
       ▼
┌──────────────┐
│  Post DB     │
│              │
└──────┬───────┘
       │ 8. Return to client
       ▼
  [Feed JSON]
```

### **Detailed Feed Service Logic**

```python
def getFeed(userId, page=1, pageSize=20):
    cacheKey = f"feed:{userId}"
    
    # Step 1: Check cache
    cachedFeed = redis.get(cacheKey)
    if cachedFeed:
        postIds = cachedFeed[page*pageSize:(page+1)*pageSize]
        return hydratePosts(postIds)
    
    # Step 2: Cache miss - generate feed
    feed = generateFeed(userId, pageSize * 10)  # Get extra for ranking
    
    # Step 3: Cache the result (TTL = 5 minutes)
    redis.setex(cacheKey, 300, feed)
    
    return hydratePosts(feed[:pageSize])

def generateFeed(userId, limit):
    # Get users this person follows
    following = graphService.getFollowing(userId)
    
    # Separate regular users from celebrities
    regularUsers = [u for u in following if u.followerCount < 1000]
    celebrities = [u for u in following if u.followerCount >= 1000]
    
    # For regular users: posts already in their feed cache
    regularPosts = []
    for followedUser in regularUsers:
        posts = feedCache.getRecentPosts(userId, followedUser)
        regularPosts.extend(posts)
    
    # For celebrities: fetch recent posts on-demand
    celebrityPosts = []
    for celebrity in celebrities:
        posts = postDB.getRecentPosts(celebrity.id, limit=10)
        celebrityPosts.extend(posts)
    
    # Merge and rank
    allPosts = regularPosts + celebrityPosts
    rankedPosts = rankingService.rank(allPosts, userId)
    
    return rankedPosts[:limit]
```

### **Explain the Cache Strategy**

**Write on board:**

```
FEED CACHE STRUCTURE (Redis)
=============================
Key: feed:{userId}
Value: Sorted Set of post IDs
Score: Timestamp (for chronological) or 
       Ranking score (for algorithmic)

Example:
feed:12345 → [
  {postId: 999, score: 1729756800},
  {postId: 998, score: 1729753200},
  {postId: 997, score: 1729749600},
  ...
]

TTL: 5-10 minutes (keeps cache fresh)
Max size: 1000 posts per user
Eviction: Keep only recent posts
```

-----

## **Minute 18-21: Data Models & Databases**

### **Post Database Schema**

> “Let me show you the key data models…”

**Post Table (Cassandra or MySQL with sharding)**

```sql
CREATE TABLE posts (
    post_id         BIGINT PRIMARY KEY,    -- Snowflake ID
    user_id         BIGINT NOT NULL,
    content         TEXT,
    media_urls      JSON,                   -- Array of CDN URLs
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP,
    likes_count     INT DEFAULT 0,
    comments_count  INT DEFAULT 0,
    shares_count    INT DEFAULT 0,
    is_deleted      BOOLEAN DEFAULT FALSE,
    
    INDEX idx_user_time (user_id, created_at DESC)
);
```

**Why this design:**

- `post_id` as primary key enables sharding by post ID
- `user_id` index for fetching user’s own posts
- Denormalized counts (likes, comments) for fast reads
- `created_at` for time-range queries

### **Graph Database Schema**

**Follower Relationship (MySQL or Neo4j)**

**Option 1: SQL (for smaller scale)**

```sql
CREATE TABLE followers (
    follower_id   BIGINT NOT NULL,    -- User who follows
    followee_id   BIGINT NOT NULL,    -- User being followed
    created_at    TIMESTAMP NOT NULL,
    
    PRIMARY KEY (follower_id, followee_id),
    INDEX idx_followee (followee_id, created_at DESC)
);

-- For "Who does Alice follow?"
SELECT followee_id FROM followers 
WHERE follower_id = alice_id;

-- For "Who follows Alice?"
SELECT follower_id FROM followers 
WHERE followee_id = alice_id;
```

**Option 2: Graph DB (for complex queries)**

```cypher
// Neo4j
(user1:User)-[:FOLLOWS]->(user2:User)

// Query: Get Alice's feed sources
MATCH (alice:User {id: 12345})-[:FOLLOWS]->(followed:User)
RETURN followed.id

// Query: Mutual followers
MATCH (alice:User)-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(bob:User)
RETURN mutual
```

### **User Table**

```sql
CREATE TABLE users (
    user_id         BIGINT PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE,
    profile_pic_url VARCHAR(500),
    bio             TEXT,
    follower_count  INT DEFAULT 0,
    following_count INT DEFAULT 0,
    created_at      TIMESTAMP NOT NULL,
    is_verified     BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    
    INDEX idx_username (username)
);
```

### **Feed Cache Structure (Redis)**

```python
# Redis data structures

# User's feed (sorted set by timestamp)
ZADD feed:12345 1729756800 999  # postId 999 at timestamp
ZADD feed:12345 1729753200 998
ZADD feed:12345 1729749600 997

# Get user's feed (most recent 20)
ZREVRANGE feed:12345 0 19

# Celebrity's recent posts (for pull model)
ZADD celebrity_posts:67890 1729756800 888
ZADD celebrity_posts:67890 1729753200 887

# Follower count cache
SET user:12345:follower_count 1500
EXPIRE user:12345:follower_count 3600  # 1 hour TTL
```

### **Database Choice Rationale**

**Write on board:**

```
DATABASE DECISIONS
==================
Post Storage: Cassandra or MySQL (sharded)
  Why? High write throughput, time-series data
  Sharding: By user_id or post_id
  
Graph Storage: MySQL (simple) or Neo4j (complex)
  Why? Relationship queries (followers/following)
  Sharding: By user_id
  
Feed Cache: Redis
  Why? Fast reads, TTL support, sorted sets
  
Media Storage: S3 + CloudFront CDN
  Why? Cheap, scalable, global distribution
  
User Data: MySQL/PostgreSQL
  Why? ACID transactions, structured data
```

-----

## **Minute 21-23: Supporting Services & Infrastructure**

### **Ranking Service**

> “Feeds aren’t just chronological anymore. Let’s add intelligent ranking…”

```python
class RankingService:
    def rank(self, posts, userId):
        """
        Rank posts using multiple signals
        """
        userPreferences = self.getUserPreferences(userId)
        
        scoredPosts = []
        for post in posts:
            score = self.calculateScore(post, userId, userPreferences)
            scoredPosts.append((post, score))
        
        # Sort by score descending
        scoredPosts.sort(key=lambda x: x[1], reverse=True)
        return [post for post, score in scoredPosts]
    
    def calculateScore(self, post, userId, preferences):
        """
        Scoring factors:
        - Recency (time decay)
        - Engagement (likes, comments, shares)
        - User affinity (how often user interacts with author)
        - Content type preference (images vs text)
        - Historical CTR for similar posts
        """
        recencyScore = self.timeDecay(post.createdAt)
        engagementScore = self.normalizeEngagement(
            post.likesCount, 
            post.commentsCount, 
            post.sharesCount
        )
        affinityScore = self.userAffinity(userId, post.userId)
        contentScore = self.contentTypeScore(post, preferences)
        
        # Weighted combination
        finalScore = (
            0.3 * recencyScore +
            0.3 * engagementScore +
            0.25 * affinityScore +
            0.15 * contentScore
        )
        
        return finalScore
```

### **Media Service**

```
┌──────────┐
│  Client  │
└────┬─────┘
     │ 1. POST /api/media/upload
     ▼
┌──────────────┐
│Media Service │
└──────┬───────┘
       │ 2. Resize/compress image
       │    Generate thumbnails
       ▼
┌──────────────┐
│  S3 Bucket   │
│              │
└──────┬───────┘
       │ 3. Return CDN URL
       ▼
┌──────────────┐
│  CloudFront  │
│     CDN      │
└──────────────┘
```

**Image Processing Pipeline:**

```python
def uploadMedia(file, userId):
    # Validate file
    if not isValidImage(file):
        raise InvalidFileError
    
    # Generate unique ID
    mediaId = generateMediaId()
    
    # Process image
    original = file
    large = resize(file, 1200, 1200)      # Full size
    medium = resize(file, 600, 600)       # Preview
    thumbnail = resize(file, 150, 150)    # Thumbnail
    
    # Upload to S3
    s3.upload(f"media/{userId}/{mediaId}/original.jpg", original)
    s3.upload(f"media/{userId}/{mediaId}/large.jpg", large)
    s3.upload(f"media/{userId}/{mediaId}/medium.jpg", medium)
    s3.upload(f"media/{userId}/{mediaId}/thumb.jpg", thumbnail)
    
    # Return CDN URLs
    return {
        'mediaId': mediaId,
        'urls': {
            'original': f"https://cdn.example.com/media/{userId}/{mediaId}/original.jpg",
            'large': f"https://cdn.example.com/media/{userId}/{mediaId}/large.jpg",
            'medium': f"https://cdn.example.com/media/{userId}/{mediaId}/medium.jpg",
            'thumbnail': f"https://cdn.example.com/media/{userId}/{mediaId}/thumb.jpg"
        }
    }
```

-----

## **Minute 23-25: Complete System Diagram**

### **Draw the Full Architecture**

> “Let me now put it all together in one comprehensive diagram…”

```
                         ┌─────────────────┐
                         │  Mobile/Web     │
                         │    Clients      │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │   CDN (Static   │
                         │  Assets/Media)  │
                         └────────┬────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │     API Gateway            │
                    │  (Auth, Rate Limit, Route) │
                    └─────────────┬──────────────┘
                                  │
        ┌─────────────────────────┼────────────────────────┐
        │                         │                        │
┌───────▼────────┐    ┌───────────▼─────────┐    ┌─────────▼────────┐
│  Post Service  │    │   Feed Service      │    │  User Service    │
│   (Write)      │    │     (Read)          │    │                  │
└───────┬────────┘    └───────────┬─────────┘    └─────────┬────────┘
        │                         │                        │
        │              ┌──────────▼─────────┐              │
        │              │  Ranking Service   │              │
        │              │  (ML-based score)  │              │
        │              └──────────┬─────────┘              │
        │                         │                        │
        ▼                         ▼                        ▼
┌────────────────┐       ┌─────────────────┐      ┌──────────────────┐
│   Post DB      │       │  Feed Cache     │      │    User DB       │
│  (Cassandra)   │       │    (Redis)      │      │  (PostgreSQL)    │
└───────┬────────┘       └─────────────────┘      └──────────────────┘
        │
        │ PostCreated Event
        ▼
┌────────────────────┐
│   Kafka Cluster    │
│  (Message Queue)   │
└────────┬───────────┘
         │
         ▼
┌─────────────────────┐
│  Fan-out Service    │
│  (Async Workers)    │
└────────┬────────────┘
         │
         ├────────────────┐
         ▼                ▼
┌─────────────┐  ┌─────────────────┐
│  Graph DB   │  │  Feed Cache     │
│  (Neo4j/    │  │    (Redis)      │
│   MySQL)    │  │  Write feeds    │
└─────────────┘  └─────────────────┘

        ┌──────────────────┐
        │  Object Storage  │
        │   (S3 + CDN)     │
        │  Media files     │
        └──────────────────┘
```

### **Data Flow Summary**

**Write Path:**

```
Client → API Gateway → Post Service → Post DB
                                    → Kafka
                                    → Fan-out Service
                                    → Feed Cache + Graph DB
```

**Read Path:**

```
Client → API Gateway → Feed Service → Feed Cache (hit) → Return
                                    → Feed Cache (miss)
                                    → Graph DB (get following)
                                    → Post DB (get posts)
                                    → Ranking Service
                                    → Return
```

-----

## **Key Points to Emphasize**

### **1. Separation of Concerns**

- **Post Service**: Handles writes
- **Feed Service**: Handles reads
- **Fan-out Service**: Async background processing
- **Each service can scale independently**

### **2. Async Processing**

- Kafka decouples post creation from fan-out
- User gets immediate response
- Fan-out happens in background
- Provides fault tolerance and replay

### **3. Hybrid Fan-out Strategy**

- **Push for regular users** (fast reads)
- **Pull for celebrities** (efficient writes)
- **Threshold-based decision** (1K followers)

### **4. Caching Strategy**

- **Redis for feed cache** (hot data)
- **CDN for media** (static content)
- **Database for cold data** (persistent storage)

### **5. Scalability**

- **Horizontal scaling**: Add more service instances
- **Database sharding**: Partition by user_id or post_id
- **Cache partitioning**: Consistent hashing
- **Async workers**: Scale fan-out independently

-----

## **Common Questions & Answers**

**Q: “Why Cassandra for posts?”**

> “Cassandra excels at time-series data with high write throughput. Posts are append-mostly with reads by time range—perfect for Cassandra. We could also use MySQL with sharding, but Cassandra gives us better write scaling and automatic replication.”

**Q: “Why not cache everything?”**

> “Storage cost vs benefit. We calculated 2-3 TB for full cache. More economical to cache just the 20% most active users (Pareto principle) and generate feeds on-demand for inactive users.”

**Q: “What if Redis goes down?”**

> “Feed cache is not source of truth—just for performance. If Redis fails, we fall back to generating feeds from Post DB and Graph DB. It’s slower but functional. We’d use Redis Sentinel or Redis Cluster for high availability.”

**Q: “How do you handle hot partitions?”**

> “Celebrity posts create hot keys in cache. We can: (1) Replicate hot keys across multiple cache nodes, (2) Use consistent hashing with virtual nodes, (3) Add a separate cache tier for celebrities.”

-----

## **Transition to Deep Dive**

**At minute 25:**

> “So that’s the high-level architecture. We have a scalable, performant system that handles both regular users and celebrities efficiently. The write path is async and non-blocking. The read path is cached and fast.
> 
> Which component would you like me to deep dive into? We could explore:
> 
> - The ranking algorithm in more detail
> - Sharding strategies for the databases
> - How we handle the celebrity problem
> - Cache invalidation and consistency
> 
> What interests you most?”

**This shows:**

- ✅ You’ve completed a full design
- ✅ You’re ready to go deeper
- ✅ You’re letting the interviewer guide the discussion
- ✅ You understand there are multiple interesting areas to explore

-----

## **Whiteboard Management Tips**

### **Use Space Wisely**

- Top 1/3: Write path
- Middle 1/3: Read path
- Bottom 1/3: Data models
- Side: Key metrics and decisions

### **Color Coding (if available)**

- Black: Main components
- Blue: Data flow
- Red: Cache/hot path
- Green: Async processes

### **Keep It Clean**

- Don’t overcrowd
- Use arrows consistently
- Label everything
- Erase obsolete iterations

### **Reference Your Calculations**

- Point back to your capacity estimates
- “Remember we calculated 105K QPS? That’s why we need this cache.”
- Shows you’re designing based on actual requirements

-----

This architecture phase is where you demonstrate **system design maturity**. You’re not just listing technologies—you’re building a coherent system that solves real problems at scale.​​​​​​​​​​​​​​​​