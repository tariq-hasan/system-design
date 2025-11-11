# Minutes 6-10: Back-of-Envelope Calculations - Detailed Breakdown

This phase demonstrates your ability to **reason quantitatively** about distributed systems. Senior engineers must validate their designs with numbers, not just intuition.

-----

## **Minute 6: Traffic & Load Estimates**

### Start With User Activity

**Say this out loud as you write:**

> “Let me start by estimating our traffic patterns to understand what we’re dealing with…”

### **Daily Active Users (DAU) Analysis**

**Given:** 500M total users, 200M DAU

```
DAU = 200M users
Average sessions per user per day = 5 sessions
Average feed refreshes per session = 3 refreshes

Total feed requests/day = 200M × 5 × 3 = 3 billion requests/day
```

### **Convert to Requests Per Second (QPS)**

```
Seconds in a day = 86,400 seconds

Average QPS = 3B / 86,400 ≈ 35,000 requests/sec

Peak QPS (assume 3x average) = 105,000 requests/sec
```

**Write on whiteboard:**

```
TRAFFIC ESTIMATES
=================
Feed reads: ~35K QPS average, ~105K QPS peak
```

### **Post Creation (Write Traffic)**

```
Posts per day = 100M posts/day
Posts per second = 100M / 86,400 ≈ 1,200 writes/sec
Peak writes (3x) = 3,600 writes/sec
```

**Add to whiteboard:**

```
Post writes: ~1.2K QPS average, ~3.6K QPS peak
Read:Write ratio = 35K:1.2K ≈ 30:1
```

### **What You’re Demonstrating:**

- You can convert business requirements into engineering metrics
- You understand traffic patterns aren’t uniform (peak hours matter)
- You recognize read-heavy vs write-heavy systems require different designs

-----

## **Minute 7: Storage Calculations**

### **Post Storage Requirements**

**Think aloud:**

> “Now let’s figure out how much storage we need, starting with post metadata…”

### **Text Posts**

```
Average post size:
- Post ID: 8 bytes (64-bit integer)
- User ID: 8 bytes
- Content: 500 bytes (avg text)
- Timestamp: 8 bytes
- Metadata (likes count, comments count, etc.): 100 bytes
- Total per post: ~624 bytes ≈ 1 KB (round up for overhead)

Daily storage = 100M posts × 1 KB = 100 GB/day
Annual storage = 100 GB × 365 ≈ 36 TB/year
5-year storage = 180 TB
```

### **Media Storage (Images/Videos)**

**Ask/Clarify:** “Should we estimate media storage? Let’s assume 60% of posts have images.”

```
Posts with images per day = 100M × 0.6 = 60M images
Average image size (after compression) = 200 KB

Daily image storage = 60M × 200 KB = 12 TB/day
Annual image storage = 12 TB × 365 ≈ 4.4 PB/year
```

**Write on whiteboard:**

```
STORAGE ESTIMATES
=================
Post metadata: 100 GB/day, 36 TB/year
Media (images): 12 TB/day, 4.4 PB/year
Total: ~12 TB/day
```

### **Senior Insight to Mention:**

> “Media dominates our storage costs. We’ll definitely need a CDN and object storage like S3. We might also want to consider image compression pipelines and multiple resolutions for different devices.”

-----

## **Minute 8: Feed Cache & Memory Requirements**

### **Feed Cache Sizing (Critical Calculation)**

**Explain your reasoning:**

> “Feed generation is expensive, so we’ll cache pre-computed feeds. Let me estimate cache size…”

### **Approach 1: Cache Recent Posts Per User**

```
Active users = 200M DAU
Posts to cache per user = 1,000 recent posts in feed
Post ID size = 8 bytes

Cache size = 200M users × 1,000 posts × 8 bytes
           = 1,600 GB = 1.6 TB

With metadata (timestamps, scores): ~2-3 TB
```

### **Approach 2: Cache Top Active Users Only**

```
Cache only 20% of most active users = 40M users
Cache size = 40M × 1,000 × 8 bytes = 320 GB

With metadata: ~500 GB (more manageable)
```

**Write on whiteboard:**

```
CACHE ESTIMATES
===============
Full cache (200M users): ~2-3 TB
Partial cache (20% users): ~500 GB
Strategy: Cache active users + LRU eviction
```

### **Memory for Hot Data**

```
User metadata in memory:
- User ID, follower count, following count
- 100 bytes per user × 200M = 20 GB

Graph data (follow relationships):
- User ID (8 bytes) + Follower ID (8 bytes) = 16 bytes
- Average 500 followers per user
- 200M × 500 × 16 bytes = 1.6 TB

Note: Too large for memory, needs persistent store
```

**Senior Insight:**

> “The social graph is too large to fit in memory. We’ll need a distributed graph database like Neo4j or a sharded SQL solution. We can cache frequently accessed paths in Redis.”

-----

## **Minute 9: Bandwidth Calculations**

### **Outgoing Bandwidth (Feed Delivery)**

```
Feed request size:
- 20 posts per feed load
- Each post: 1 KB metadata + thumbnail (50 KB average)
- Total per request: 20 × 51 KB ≈ 1 MB

Bandwidth = 35,000 requests/sec × 1 MB = 35 GB/sec
Peak bandwidth = 105 GB/sec
```

### **Incoming Bandwidth (Post Creation)**

```
Post uploads:
- 1,200 posts/sec
- Average post with image: 200 KB

Bandwidth = 1,200 × 200 KB = 240 MB/sec
Peak: 720 MB/sec
```

**Write on whiteboard:**

```
BANDWIDTH
=========
Outbound: 35 GB/s avg, 105 GB/s peak
Inbound: 240 MB/s avg, 720 MB/s peak
Outbound >> Inbound (read-heavy confirmed)
```

-----

## **Minute 10: Fan-out Calculations (Critical for Design)**

### **The Key Calculation That Drives Architecture**

> “This is crucial: when someone posts, how many feed updates do we need to push?”

### **Fan-out on Write Estimation**

```
Average followers per user = 500
Posts per day = 100M

Fan-out operations/day = 100M posts × 500 followers
                       = 50 billion writes/day
                       = 50B / 86,400 ≈ 580K writes/sec

This is 580x our original write traffic!
```

### **Celebrity Problem**

```
Top 1% of users = 2M users with 1M+ followers each
If celebrity posts once/day:
- Fan-out for one celebrity post = 1M writes
- If 2M celebrities post 1x/day = 2B writes just for celebrities
```

**Write on whiteboard:**

```
FAN-OUT ANALYSIS
================
Avg user (500 followers): Manageable with fan-out on write
Celebrity (1M+ followers): Fan-out on write is too expensive
Strategy: Hybrid approach
  - Push model (<1000 followers)
  - Pull model (>1000 followers)
```

### **Senior Insight to Share:**

> “Pure fan-out on write explodes our write load by 500x. We need a hybrid model: pre-compute feeds for normal users, but merge celebrity content on-demand during read. This is what Twitter does.”

-----

## **Summary Table for Whiteboard**

Create a clean summary box:

```
═══════════════════════════════════════════════════
CAPACITY ESTIMATES SUMMARY
═══════════════════════════════════════════════════
TRAFFIC
  • Feed reads: 35K QPS (105K peak)
  • Post writes: 1.2K QPS (3.6K peak)
  • Read:Write ratio: 30:1

STORAGE
  • Post metadata: 100 GB/day
  • Media: 12 TB/day
  • 5-year total: ~22 PB

MEMORY/CACHE
  • Feed cache: 500 GB - 3 TB (depending on strategy)
  • Hot user metadata: 20 GB
  • Social graph: 1.6 TB (disk-backed)

BANDWIDTH
  • Outbound: 35 GB/s (105 GB/s peak)
  • Inbound: 240 MB/s (720 MB/s peak)

FAN-OUT
  • Avg user: 500 followers → manageable
  • Celebrity: 1M+ followers → requires pull model
  • Strategy: Hybrid push/pull
═══════════════════════════════════════════════════
```

-----

## **Key Techniques for This Phase**

### **1. Rounding & Approximation**

- **Do:** Round to make math easy (86,400 ≈ 100K, 1024 ≈ 1000)
- **Say:** “I’m rounding for simplicity—we can be more precise later”
- **Example:** “3 billion divided by 100K is about 30,000”

### **2. Show Your Work**

- Write calculations on the whiteboard as you speak
- Don’t just announce answers; show the logic
- Use consistent units (convert KB → GB → TB → PB clearly)

### **3. State Assumptions**

- “Assuming 3x traffic during peak hours…”
- “If average post size is 1 KB…”
- “Let’s say 60% of posts include images…”

### **4. Sanity Checks**

- “Does 105K QPS seem reasonable for 200M users? That’s about 1 request per user every 2,000 seconds, or roughly every 30 minutes. That seems low actually—users probably check more often. Let me adjust…”

-----

## **Common Mistakes to Avoid**

### ❌ **Don’t:**

1. **Skip this section** - “We can figure out numbers later” (No! Numbers inform design)
1. **Get bogged down in precision** - Don’t spend 3 minutes calculating exactly 1,157.407 writes/sec
1. **Forget units** - Always label: MB, GB, TB, QPS, etc.
1. **Ignore the implications** - Calculate AND interpret (“This means we need sharding”)
1. **Use unrealistic numbers** - Don’t say “1 billion QPS” for 200M DAU

### ✅ **Do:**

1. **Use powers of 10** - 1K = 10³, 1M = 10⁶, 1B = 10⁹
1. **Round aggressively** - 86,400 → 100K, 365 → 400
1. **Verbalize as you calculate** - Helps interviewer follow your logic
1. **Connect to design decisions** - “This fan-out number tells us we need a hybrid approach”
1. **Keep it visible** - Don’t erase; you’ll reference these numbers later

-----

## **Transitioning to Architecture**

**At the 10-minute mark:**

> “Okay, so we’re looking at 35K read QPS, 1.2K write QPS, 12 TB of storage per day, and a challenging fan-out problem for high-follower users. These numbers will guide our architecture. Let me now sketch the high-level system design. Should take about 15 minutes.”

**What you’ve accomplished:**

- ✅ Validated the system is truly large-scale (not a toy problem)
- ✅ Identified the read-heavy nature (caching is critical)
- ✅ Discovered the fan-out bottleneck (drives architecture choice)
- ✅ Sized storage, memory, and bandwidth (guides infrastructure)
- ✅ Demonstrated quantitative thinking (senior signal)

-----

## **Pro Tips**

### **Memory Aids for Common Conversions:**

```
1 KB = 1,000 bytes (10³)
1 MB = 1,000 KB (10⁶ bytes)
1 GB = 1,000 MB (10⁹ bytes)
1 TB = 1,000 GB (10¹² bytes)
1 PB = 1,000 TB (10¹⁵ bytes)

1 day = ~100K seconds (86,400)
1 year = ~30M seconds (31.5M)
1 month = ~2.5M seconds
```

### **Quick Mental Math Tricks:**

- **Dividing by 86,400**: Divide by 100K instead (15% error, acceptable)
- **Multiplying by 365**: Use 400 (10% error, easier)
- **Peak traffic**: 2-3x average is standard assumption

### **Body Language:**

- Write on the board while talking (shows confidence)
- Make eye contact when stating key insights
- Use hand gestures to emphasize the fan-out explosion
- Pause briefly after calculations to let them sink in

-----

**This phase separates senior engineers from junior ones. Juniors jump to Redis/Kafka/MongoDB. Seniors do the math first, then choose technologies based on actual requirements.**
