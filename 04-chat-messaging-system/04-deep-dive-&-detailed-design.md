# Minutes 15-35: Deep Dive & Detailed Design (20 min)

This is where **senior engineers separate themselves from mid-level candidates**. You’re demonstrating deep technical expertise, production-level thinking, and the ability to solve complex distributed systems problems. This phase should feel like you’re designing a system that could actually ship.

-----

## **Minute 15-16: Transition & Prioritization (1 min)**

### **Your Transition Statement:**

*“Now let’s dive deep into the critical components. Based on our requirements—100M concurrent connections and <200ms delivery latency—I want to focus on three areas that will make or break this system:*

1. *Real-time message delivery architecture*
1. *Message storage and data modeling*
1. *Scaling WebSocket connections*

*I’ll spend about 6-7 minutes on each, and we can adjust if you want to go deeper on any particular area.”*

**Why this works:**

- Shows time management
- Prioritizes the hardest problems
- Invites collaboration

-----

## **DEEP DIVE 1: Real-Time Message Delivery (Minutes 16-23, ~7 min)**

### **Minute 16-17: WebSocket Architecture Detail (1 min)**

*“Let’s start with how we actually deliver messages in real-time. The WebSocket layer is the most critical piece.”*

#### **Draw the Detailed WebSocket Architecture:**

```
    ┌─────────────────────────────────────────────────────┐
    │                     CLIENT LAYER                    │
    │  [Mobile App]  [Web Client]  [Desktop App]          │
    └──────┬──────────────┬────────────────┬──────────────┘
           │              │                │
           │    ┌─────────▼────────────────▼───────┐
           │    │   Load Balancer (Layer 4)        │
           │    │   - Consistent hashing by UserID │
           │    │   - Sticky sessions              │
           │    └─────────┬────────────────────────┘
           │              │
    ┌──────▼──────────────▼──────────────────────────────┐
    │         WebSocket Gateway Cluster                  │
    │                                                    │
    │  ┌──────────┐  ┌──────────┐       ┌──────────┐     │
    │  │  WS-1    │  │  WS-2    │  ...  │ WS-10000 │     │
    │  │10K conns │  │10K conns │       │10K conns │     │
    │  └────┬─────┘  └────┬─────┘       └──────┬───┘     │
    │       │             │                    │         │
    └───────┼─────────────┼────────────────────┼─────────┘
            │             │                    │
            └─────────────┼────────────────────┘
                          │
    ┌─────────────────────▼──────────────────────────────┐
    │         Connection Registry (Redis Cluster)        │
    │                                                    │
    │  UserID → Server mapping                           │
    │  user:12345 → ws-server-42                         │
    │  user:67890 → ws-server-103                        │
    │                                                    │
    │  Server → Active Connections                       │
    │  ws-server-42 → [user:12345, user:54321, ...]      │
    └────────────────────────────────────────────────────┘
```

**Explain the Flow:**

*“Here’s what happens when User A sends a message to User B:*

1. *User A’s client sends message via established WebSocket on WS-Server-42*
2. *WS-Server-42 forwards to Chat Service*
3. *Chat Service needs to deliver to User B*
4. *Query Redis: ‘Where is User B connected?’*
5. *Redis returns: ‘WS-Server-103’*
6. *Chat Service routes message to WS-Server-103*
7. *WS-Server-103 pushes to User B over existing WebSocket*

*The key insight: WebSocket servers are just connection managers. They don’t know routing logic—that’s in Redis.”*

-----

### **Minute 17-19: Connection State Management (2 min)**

#### **Problem Statement:**

*“With 100M concurrent connections across 10,000 servers, how do we maintain connection state?”*

#### **Solution: Multi-Level State Management**

**Draw this architecture:**

```
┌─────────────────────────────────────────────────────────┐
│  LEVEL 1: Local Server State (In-Memory)                │
│                                                         │
│  Each WS Server maintains:                              │
│  ┌────────────────────────────────────┐                 │
│  │ connectionId → WebSocket object    │                 │
│  │ userId → connectionId              │                 │
│  │ heartbeat timestamps               │                 │
│  └────────────────────────────────────┘                 │
│                                                         │
│  Data Structure:                                        │
│  HashMap<UserId, WebSocketConnection>                   │
│                                                         │
│  Why local? → O(1) lookup for message delivery          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LEVEL 2: Global State (Redis Cluster)                  │
│                                                         │
│  Redis maintains:                                       │
│  ┌────────────────────────────────────┐                 │
│  │ user:{userId} → ws-server-id       │                 │
│  │ TTL: 65 seconds                    │                 │
│  │                                    │                 │
│  │ server:{serverId} → [userIds]      │                 │
│  │ (Set data structure)               │                 │
│  └────────────────────────────────────┘                 │
│                                                         │
│  Why Redis?                                             │
│  • Fast lookups (sub-millisecond)                       │
│  • Distributed across all chat servers                  │
│  • TTL for automatic cleanup                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  HEARTBEAT MECHANISM                                    │
│                                                         │
│  Client → Server: Ping every 30 seconds                 │
│  Server → Redis: Refresh TTL every 30 seconds           │
│                                                         │
│  If TTL expires → Connection considered dead            │
│  Server cleanup: Remove from local state                │
│  Presence Service: Mark user offline                    │
└─────────────────────────────────────────────────────────┘
```

#### **Explain the Design:**

*“We use a two-tier state management approach:*

**Local State (WS Server):**

- *Fast lookups when delivering to users on THIS server*
- *No network round-trip*
- *Handles 99% of operations*

**Global State (Redis):**

- *Routing between servers*
- *Allows any Chat Service instance to find any user*
- *TTL-based expiration for automatic cleanup when connections die*

**Heartbeat Protocol:**

```
Every 30 seconds:
├─ Client sends: {type: 'ping', timestamp: 1234567890}
├─ Server responds: {type: 'pong', timestamp: 1234567890}
└─ Server refreshes Redis TTL

If 2 missed heartbeats (60 sec):
├─ Server closes connection
├─ Redis key expires (65 sec TTL)
└─ Presence Service marks user offline
```

*This handles zombie connections—clients that crashed without closing WebSocket properly.”*

-----

### **Minute 19-21: Message Routing & Delivery Guarantees (2 min)**

#### **Problem: How do we ensure messages aren’t lost?**

**Draw the detailed message flow:**

```
┌─────────────────────────────────────────────────────────┐
│  MESSAGE DELIVERY PIPELINE                              │
│                                                         │
│  Step 1: ACCEPTANCE                                     │
│  ┌──────────────────────────────────┐                   │
│  │ Client sends message             │                   │
│  │ WS Server assigns temp_id        │                   │
│  │ Immediately ACK to client        │                   │
│  │ Status: "SENT"                   │                   │
│  └──────────────────────────────────┘                   │
│                  │                                      │
│  Step 2: PERSISTENCE                                    │
│  ┌───────────────▼──────────────────┐                   │
│  │ Chat Service writes to Kafka     │                   │
│  │ Kafka ACKs                       │                   │
│  │ Generate permanent message_id    │                   │
│  │ Update client: temp_id→msg_id    │                   │
│  │ Status: "DELIVERED"              │                   │
│  └──────────────────────────────────┘                   │
│                  │                                      │
│  Step 3: DELIVERY TO RECIPIENT                          │
│  ┌───────────────▼──────────────────┐                   │
│  │ Lookup recipient in Redis        │                   │
│  │ Route to recipient's WS Server   │                   │
│  │ Push to recipient                │                   │
│  └──────────────────────────────────┘                   │
│                  │                                      │
│  Step 4: CONFIRMATION                                   │
│  ┌───────────────▼──────────────────┐                   │
│  │ Recipient sends ACK              │                   │
│  │ Update sender: "SEEN"            │                   │
│  │ Store in Cassandra (async)       │                   │
│  └──────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

#### **Message States:**

*“Every message goes through these states:”*

```
SENT → DELIVERED → SEEN

SENT:     Client sent, server received
DELIVERED: Written to Kafka, routed to recipient
SEEN:     Recipient ACKed receipt
```

#### **Handling Failures:**

*“Let’s talk about what happens when things go wrong:”*

**Scenario 1: Recipient is Offline**

```
Chat Service checks Redis → User not found
    ↓
Store in pending messages queue (Kafka topic)
    ├─ Topic: pending-messages-{userId}
    ├─ When user comes online, drain queue
    └─ Also trigger push notification
```

**Scenario 2: Message Delivery Fails**

```
WS Server can't deliver (connection broken)
    ↓
Return NACK to Chat Service
    ↓
Chat Service:
    ├─ Remove user from Redis (connection dead)
    ├─ Add to pending queue
    └─ Update Presence Service (user offline)
```

**Scenario 3: Network Partition**

```
Client doesn't receive ACK within 5 seconds
    ↓
Client retries with same temp_id
    ↓
Chat Service deduplicates:
    ├─ Check if temp_id already processed
    ├─ If yes, return existing message_id
    └─ If no, process as new message

Deduplication window: 60 seconds (in Redis)
```

-----

### **Minute 21-23: Group Chat Message Delivery (2 min)**

#### **The Fanout Challenge:**

*“Group chats with 500 members create a fanout problem. Let’s optimize this.”*

**Draw the fanout architecture:**

```
┌─────────────────────────────────────────────────────────┐
│  GROUP MESSAGE FANOUT STRATEGY                          │
│                                                         │
│  User A sends message to Group G (500 members)          │
│                                                         │
│  Step 1: WRITE TO STORAGE (Single Write)                │
│  ┌──────────────────────────────────┐                   │
│  │ Write once to Cassandra:         │                   │
│  │ Key: (group_id, timestamp)       │                   │
│  │ Value: {msg_id, user_id, text}   │                   │
│  └──────────────────────────────────┘                   │
│                  │                                      │
│  Step 2: ONLINE USER FANOUT                             │
│  ┌───────────────▼──────────────────┐                   │
│  │ Query Redis:                     │                   │
│  │ Get all online members of Group G│                   │
│  │                                  │                   │
│  │ SMEMBERS group:G:online          │                   │
│  │ Returns: [user:10, user:15, ...] │                   │
│  │ (Say 200 out of 500 are online)  │                   │
│  └──────────────────────────────────┘                   │
│                  │                                      │
│  Step 3: BATCH BY SERVER                                │
│  ┌───────────────▼──────────────────┐                   │
│  │ Group users by WS Server:        │                   │
│  │                                  │                   │
│  │ ws-server-1: [user:10, user:23]  │                   │
│  │ ws-server-5: [user:15, user:67]  │                   │
│  │ ws-server-8: [user:42, user:91]  │                   │
│  │                                  │                   │
│  │ Send ONE message per server      │                   │
│  │ with list of target users        │                   │
│  └──────────────────────────────────┘                   │
│                  │                                      │
│  Step 4: SERVER-SIDE FANOUT                             │
│  ┌──────────────▼───────────────────┐                   │
│  │ Each WS Server:                  │                   │
│  │ Receives message + user list     │                   │
│  │ Fans out to local connections    │                   │
│  │ (All in-memory, very fast)       │                   │
│  └──────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────┘

OPTIMIZATION:
Instead of 200 network calls (Chat Service → 200 WS Servers),
we make ~20 calls (200 users distributed across ~20 servers)
```

#### **The Math:**

*“Let’s calculate the savings:”*

```
Naive approach:
- 500 members
- 200 online
- 200 separate messages from Chat Service → WS Servers
- Network overhead: 200 RPCs

Optimized approach:
- Group by server (assume ~10 users per server on average)
- 200 users / 10 = 20 servers
- 20 RPCs from Chat Service
- Each WS Server does local fanout

Savings: 200 → 20 RPCs (10x reduction)
```

#### **Handling Offline Users:**

*“For the 300 offline users:”*

```
Notification Service batches:
├─ Wait 5 minutes for more messages
├─ Bundle into digest: "15 new messages in Group G"
└─ Send one push notification

Avoids push notification spam
```

-----

## **DEEP DIVE 2: Message Storage & Data Modeling (Minutes 23-30, ~7 min)**

### **Minute 23-25: Cassandra Data Model (2 min)**

*“Now let’s design the exact data model in Cassandra. This is critical for performance.”*

#### **Schema Design:**

**Draw the tables:**

```
┌─────────────────────────────────────────────────────────┐
│  TABLE: messages_by_conversation (1-on-1 Chat)          │
│                                                         │
│  PRIMARY KEY: ((conversation_id), timestamp, message_id)│
│                                                         │
│  Partition Key: conversation_id                         │
│  Clustering Keys: timestamp DESC, message_id            │
│                                                         │
│  ┌───────────────┬──────────┬────────────┬──────────┐   │
│  │conversation_id│timestamp │ message_id │  data    │   │
│  ├───────────────┼──────────┼────────────┼──────────┤   │
│  │ conv_123      │ ...456   │ msg_abc    │ {...}    │   │
│  │ conv_123      │ ...455   │ msg_xyz    │ {...}    │   │
│  │ conv_123      │ ...454   │ msg_def    │ {...}    │   │
│  └───────────────┴──────────┴────────────┴──────────┘   │
│                                                         │
│  conversation_id: UUID (derived from sorted user IDs)   │
│  timestamp: Unix timestamp (milliseconds)               │
│  message_id: UUID v1 (time-based)                       │
│  data: {sender_id, text, media_url, status, ...}        │
│                                                         │
│  Why this design?                                       │
│  • All messages for a conversation in same partition    │
│  • Time-ordered (newest first with DESC)                │
│  • Efficient range queries: "last 50 messages"          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  TABLE: messages_by_group                               │
│                                                         │
│  PRIMARY KEY: ((group_id), timestamp, message_id)       │
│                                                         │
│  ┌──────────┬──────────┬────────────┬──────────────┐    │
│  │ group_id │timestamp │ message_id │     data     │    │
│  ├──────────┼──────────┼────────────┼──────────────┤    │
│  │ grp_456  │ ...789   │ msg_111    │ {...}        │    │
│  │ grp_456  │ ...788   │ msg_222    │ {...}        │    │
│  └──────────┴──────────┴────────────┴──────────────┘    │
│                                                         │
│  Single partition for entire group = fanout-on-read     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  TABLE: user_conversations                              │
│                                                         │
│  PRIMARY KEY: ((user_id), last_message_time, conv_id)   │
│                                                         │
│  ┌─────────┬────────────────┬─────────┬──────────────┐  │
│  │ user_id │last_msg_time   │ conv_id │ metadata     │  │
│  ├─────────┼────────────────┼─────────┼──────────────┤  │
│  │ user_10 │ ...999         │ conv_5  │{unread:3...} │  │
│  │ user_10 │ ...998         │ conv_8  │{unread:0...} │  │
│  └─────────┴────────────────┴─────────┴──────────────┘  │
│                                                         │
│  Purpose: Fetch user's conversation list quickly        │
│  Sorted by most recent activity                         │
└─────────────────────────────────────────────────────────┘
```

#### **Key Design Decisions:**

*“Let me explain the partition key choice:”*

**Conversation ID as Partition Key:**

```
✅ GOOD:
- All messages for a conversation co-located
- Single partition read for "last 50 messages"
- Sequential writes to same partition

❌ POTENTIAL ISSUE:
- Very active conversations → hot partitions
- Partition size limit (~100GB in Cassandra)

MITIGATION:
- Monitor partition sizes
- For super-active groups, split by time:
  conversation_id = hash(group_id + month)
```

**Timestamp as Clustering Key:**

```
✅ GOOD:
- Natural sort order for messages
- Range queries efficient
- DESC means latest messages first (common query)

Queries we can efficiently support:
1. "Get last 50 messages" → LIMIT 50
2. "Get messages after timestamp T" → WHERE timestamp > T
3. "Get messages in time range" → WHERE timestamp > T1 AND timestamp < T2
```

-----

### **Minute 25-27: Query Patterns & Optimization (2 min)**

#### **Common Query Patterns:**

*“Let’s walk through how we handle actual queries:”*

**Query 1: Load Recent Messages (Cold Start)**

```sql
-- User opens conversation for first time
SELECT * FROM messages_by_conversation
WHERE conversation_id = 'conv_123'
ORDER BY timestamp DESC
LIMIT 50;

-- Cassandra Performance:
- Single partition scan
- Time complexity: O(log N + 50) with SSTable index
- Latency: ~10-20ms
```

**Query 2: Fetch Older Messages (Pagination)**

```sql
-- User scrolls up to see history
SELECT * FROM messages_by_conversation
WHERE conversation_id = 'conv_123'
  AND timestamp < 1699999999000
ORDER BY timestamp DESC
LIMIT 50;

-- Uses clustering key range scan
-- Latency: ~10-20ms
```

**Query 3: Fetch New Messages (Incremental)**

```sql
-- User reconnects after being offline
SELECT * FROM messages_by_conversation
WHERE conversation_id = 'conv_123'
  AND timestamp > 1699999999000
ORDER BY timestamp ASC;  -- Note: ASC for chronological

-- Returns all messages since last_seen_timestamp
```

#### **Caching Strategy:**

*“We add caching to avoid hitting Cassandra for hot conversations:”*

```
┌─────────────────────────────────────────────────────────┐
│  CACHING LAYERS                                         │
│                                                         │
│  Layer 1: Redis (Recent Messages)                       │
│  ┌──────────────────────────────────┐                   │
│  │ Key: conv:{conv_id}:recent       │                   │
│  │ Type: Sorted Set (by timestamp)  │                   │
│  │ Size: Last 100 messages          │                   │
│  │ TTL: 24 hours                    │                   │
│  └──────────────────────────────────┘                   │
│                                                         │
│  Layer 2: Application Cache (Server-side)               │
│  ┌──────────────────────────────────┐                   │
│  │ LRU cache in Chat Service        │                   │
│  │ Size: 10,000 conversations       │                   │
│  │ Hit rate: ~60-70%                │                   │
│  └──────────────────────────────────┘                   │
│                                                         │
│  Layer 3: Cassandra (Source of Truth)                   │
│  └──────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────┘

Read Path:
1. Check Redis → Cache hit (70% of requests)
2. If miss, check Cassandra
3. Populate Redis asynchronously
4. Return to client

Write Path:
1. Write to Kafka (durability)
2. Write to Cassandra (async)
3. Update Redis (sync, for immediate reads)
4. Deliver to online users
```

-----

### **Minute 27-30: Handling Scale & Hot Partitions (3 min)**

#### **Problem: Very Active Group Chats**

*“What if we have a group with 100K members and 1000 messages/sec?”*

**Draw the hot partition problem:**

```
┌─────────────────────────────────────────────────────────┐
│  PROBLEM: Hot Partition                                 │
│                                                         │
│  Large Group (100K members, 1000 msg/sec)               │
│         │                                               │
│         ▼                                               │
│  All writes go to ONE partition                         │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                       │
│  │ Node 5 in    │  ← Overloaded!                        │
│  │ Cassandra    │                                       │
│  │ Cluster      │                                       │
│  └──────────────┘                                       │
│                                                         │
│  Symptoms:                                              │
│  • Write latency increases (>100ms)                     │
│  • Compaction lag                                       │
│  • Memory pressure                                      │
│  • Read latency affected                                │
└─────────────────────────────────────────────────────────┘
```

#### **Solution 1: Time-Based Partitioning**

```
┌─────────────────────────────────────────────────────────┐
│  SOLUTION: Composite Partition Key                      │
│                                                         │
│  Change partition key from:                             │
│    (group_id)                                           │
│  To:                                                    │
│    (group_id, time_bucket)                              │
│                                                         │
│  where time_bucket = timestamp / (24 * 3600 * 1000)     │
│  (i.e., day-based bucketing)                            │
│                                                         │
│  PRIMARY KEY: ((group_id, time_bucket), timestamp, ...) │
│                                                         │
│  Effect:                                                │
│  • Messages for same group spread across partitions     │
│  • Each day gets new partition                          │
│  • Max partition size bounded                           │
│                                                         │
│  Trade-off:                                             │
│  ✅ Prevents hot partitions                             │
│  ❌ Range queries across days need multiple partitions  │
│  ❌ "Last 50 messages" might need 2 queries             │
└─────────────────────────────────────────────────────────┘
```

**Show the query change:**

```sql
-- Old (single partition):
SELECT * FROM messages_by_group
WHERE group_id = 'grp_456'
ORDER BY timestamp DESC
LIMIT 50;

-- New (might need multiple partitions):
SELECT * FROM messages_by_group
WHERE group_id = 'grp_456'
  AND time_bucket IN ('2024-11-14', '2024-11-15')
ORDER BY timestamp DESC
LIMIT 50;

-- Application logic:
1. Calculate current time_bucket
2. Fetch from current bucket
3. If < 50 messages, fetch from previous bucket
4. Merge and sort
```

#### **Solution 2: Read Replicas & Materialized Views**

*“For very large groups, we can also optimize reads:”*

```
┌─────────────────────────────────────────────────────────┐
│  MATERIALIZED VIEW: User's Group Messages               │
│                                                         │
│  CREATE MATERIALIZED VIEW messages_by_user_and_group AS │
│  SELECT * FROM messages_by_group                        │
│  WHERE user_id IS NOT NULL                              │
│    AND group_id IS NOT NULL                             │
│  PRIMARY KEY ((user_id, group_id), timestamp, msg_id)   │
│                                                         │
│  Purpose:                                               │
│  • Each user has their own partition for each group     │
│  • Fanout-on-write for reads                            │
│  • Trade storage for read performance                   │
│                                                         │
│  When to use:                                           │
│  • Groups with < 1000 members                           │
│  • Where read performance critical                      │
│  • Storage cost acceptable                              │
└─────────────────────────────────────────────────────────┘
```

#### **Monitoring & Alerting:**

*“We need to detect hot partitions proactively:”*

```
METRICS TO TRACK:

1. Partition Size:
   - Alert if partition > 80GB
   - Split partition before hitting 100GB limit

2. Write Throughput per Partition:
   - Alert if > 5000 writes/sec to single partition
   - Consider time-bucketing

3. Compaction Lag:
   - Alert if lag > 2 hours
   - Indicates partition under stress

4. Read Latency (p99):
   - Alert if p99 > 100ms
   - May indicate hot partition affecting reads

AUTOMATED REMEDIATION:
- Automatically enable time-bucketing for groups > 10K members
- Pre-create partitions for known large groups
- Monitor and rebalance Cassandra cluster
```

-----

## **DEEP DIVE 3: Scaling WebSocket Connections (Minutes 30-35, ~5 min)**

### **Minute 30-32: Connection Distribution Strategy (2 min)**

*“Let’s tackle the elephant in the room: 100 million concurrent WebSocket connections. How do we actually build this?”*

#### **The Math:**

```
┌─────────────────────────────────────────────────────────────┐
│  CONNECTION SCALING CALCULATION                             │
│                                                             │
│  Target: 100M concurrent connections                        │
│                                                             │
│  Per-server capacity:                                       │
│  • c5.2xlarge (AWS): 8 vCPUs, 16GB RAM                      │
│  • Theoretical max: ~65K connections (file descriptor limit)│
│  • Practical limit: ~10K connections                        │
│    - Account for CPU, memory, network bandwidth             │
│    - Leave headroom for spikes                              │
│                                                             │
│  Servers needed: 100M / 10K = 10,000 servers                │
│                                                             │
│  Cost estimate:                                             │
│  • c5.2xlarge: $0.34/hour                                   │
│  • 10,000 servers × $0.34 = $3,400/hour                     │
│  • Monthly: ~$2.5M (for connections alone!)                 │
└─────────────────────────────────────────────────────────────┘
```

**Draw the distribution architecture:**

```
┌─────────────────────────────────────────────────────────┐
│  WEBSOCKET SERVER DISTRIBUTION                          │
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │         DNS Load Balancing                     │     │
│  │  ws1.chat.com, ws2.chat.com, ... ws10.chat.com │     │
│  └───────────────────┬────────────────────────────┘     │
│                      │                                  │
│  ┌───────────────────▼────────────────────────────┐     │
│  │       Layer 4 Load Balancer per Region         │     │
│  │       (1,000 servers per LB pool)              │     │
│  └───────────────────┬────────────────────────────┘     │
│                      │                                  │
│  ┌───────────────────▼────────────────────────────┐     │
│  │      WebSocket Server Pool (Region 1)          │     │
│  │                                                │     │
│  │   [WS-0001]  [WS-0002]  ...  [WS-3333]         │     │
│  │   10K conn   10K conn        10K conn          │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
│  Repeat for Region 2, Region 3                          │
└─────────────────────────────────────────────────────────┘

CLIENT CONNECTION FLOW:
1. Client resolves ws.chat.com via DNS
   → Returns LB IP based on geolocation
2. Client connects to LB
3. LB uses consistent hashing on user_id
   → Routes to same WS server (sticky sessions)
4. WebSocket handshake completes
5. Server registers connection in Redis
```

-----

### **Minute 32-34: Handling Server Failures (2 min)**

*“With 10,000 servers, failures are not exceptional—they’re constant. We need graceful degradation.”*

#### **Failure Scenarios & Solutions:**

**Scenario 1: WebSocket Server Crashes**

```
┌─────────────────────────────────────────────────────────┐
│  SERVER CRASH HANDLING                                  │
│                                                         │
│  WS-Server-42 crashes (10K connections lost)            │
│         │                                               │
│         ▼                                               │
│  Health Check Fails (within 5 seconds)                  │
│         │                                               │
│         ▼                                               │
│  Load Balancer removes server from pool                 │
│         │                                               │
│         ▼                                               │
│  Redis TTLs expire (65 seconds)                         │
│  ├─ user:{id} → ws-server-42 entries expire             │
│  └─ Presence Service marks users offline                │
│         │                                               │
│         ▼                                               │
│  Client Reconnection:                                   │
│  ├─ Clients detect connection loss (ping timeout)       │
│  ├─ Exponential backoff: 1s, 2s, 4s, 8s, ...            │
│  ├─ Connect to different WS server                      │
│  └─ Request missed messages since last_timestamp        │
└─────────────────────────────────────────────────────────┘
```

**Client Reconnection Logic:**

```javascript
class WebSocketClient {
  reconnectAttempts = 0;
  maxBackoff = 60000; // 60 seconds
  
  async reconnect() {
    const backoff = Math.min(
      1000 * Math.pow(2, this.reconnectAttempts),
      this.maxBackoff
    );
    
    await sleep(backoff + randomJitter());
    
    try {
      await this.connect();
      // Fetch missed messages
      const missedMsgs = await this.fetchMissedMessages(
        this.lastSeenTimestamp
      );
      this.reconnectAttempts = 0;
    } catch (error) {
      this.reconnectAttempts++;
      this.reconnect();
    }
  }
}
```

**Scenario 2: Partial Network Partition**

```
Region 1 loses connectivity to Redis
    │
    ├─ Can't update user→server mappings
    ├─ Can't route messages between servers
    │
    ▼
Graceful Degradation:
    ├─ Keep existing connections alive
    ├─ Local delivery works (same server)
    ├─ Cross-server delivery fails temporarily
    │
    ▼
When Redis reconnects:
    ├─ Reconcile state
    ├─ Re-register all connections
    └─ Resume cross-server routing
```

-----

### **Minute 34-35: Optimizations & Resource Management (1 min)**

#### **Connection Pooling & Resource Limits:**

*“Each connection consumes resources. Let’s optimize:”*

```
┌─────────────────────────────────────────────────────────┐
│  PER-CONNECTION RESOURCE USAGE                          │
│                                                         │
│  File Descriptors:  1 FD per connection                 │
│  Memory:            ~4KB per connection (buffers)       │
│  CPU:               Minimal (event-driven I/O)          │
│                                                         │
│  10K connections per server:                            │
│  • FDs: 10,000                                          │
│  • Memory: ~40MB for connection buffers                 │
│  • OS tuning required:                                  │
│    ulimit -n 65535  (increase FD limit)                 │
│    net.core.somaxconn = 4096                            │
│    net.ipv4.tcp_max_syn_backlog = 4096                  │
└─────────────────────────────────────────────────────────┘
```

#### **Compression & Protocol Optimization:**

```
┌─────────────────────────────────────────────────────────┐
│  BANDWIDTH OPTIMIZATION                                 │
│                                                         │
│  Enable WebSocket Per-Message Deflate:                  │
│  ├─ Compress messages before sending                    │
│  ├─ ~60% reduction for text messages                    │
│  └─ CPU trade-off: +5% CPU for -60% bandwidth           │
│                                                         │
│  Binary Protocol (optional):                            │
│  ├─ Use Protocol Buffers instead of JSON                │
│  ├─ Smaller message size                                │
│  └─ Faster serialization/deserialization                │
│                                                         │
│  Example:                                               │
│  JSON:  {"type":"msg","id":"123","text":"hi"} = 42 bytes│
│  Protobuf:  [binary] = ~12 bytes                        │
│  Savings: 70%                                           │
└─────────────────────────────────────────────────────────┘
```

-----

## **Minute 35: Transition to Next Phase**

*“Excellent! We’ve now covered the three most critical components in depth:*

1. *✅ Real-time message delivery with WebSocket architecture*
1. *✅ Message storage and Cassandra data modeling*
1. *✅ Scaling to 100M connections with failure handling*

*These form the core of our chat system. Now let’s discuss potential bottlenecks, edge cases, and how we’d monitor this in production. Should we move on to that?”*

-----

## **What Your Whiteboard Looks Like After 20 Minutes:**

```
┌──────────────────── DEEP DIVES ─────────────────────┐
│                                                     │
│ 1. REAL-TIME DELIVERY                               │
│    • WebSocket Gateway Architecture (detailed)      │
│    • Connection State (local + Redis)               │
│    • Message delivery guarantees (SENT→DELIVERED)   │
│    • Group fanout optimization (batch by server)    │
│                                                     │
│ 2. STORAGE                                          │
│    • Cassandra schema (3 tables, keys explained)    │
│    • Query patterns (w/ SQL examples)               │
│    • Caching layers (Redis + app cache)             │
│    • Hot partition solutions (time-bucketing)       │
│                                                     │
│ 3. CONNECTION SCALING                               │
│    • 10K servers calculation                        │
│    • Failure handling (server crash, partitions)    │
│    • Resource optimization (compression, FD limits) │
│                                                     │
└─────────────────────────────────────────────────────┘
```

-----

## **Senior-Level Signals You’re Demonstrating:**

- ✅ **Production Experience**: Specific technologies (Cassandra, Redis, Kafka), not just abstract concepts
- ✅ **Quantitative Reasoning**: Exact calculations (10K servers, 290K msg/sec, partition sizes)
- ✅ **Failure Handling**: Proactively discuss crash scenarios, not waiting to be asked
- ✅ **Trade-off Analysis**: Every decision justified with pros/cons
- ✅ **Optimization Thinking**: Caching, batching, compression—shows you’ve built real systems
- ✅ **Monitoring Awareness**: Mention metrics and alerts, not just design

**You’re now perfectly positioned to discuss bottlenecks, edge cases, and wrap up strongly.**
