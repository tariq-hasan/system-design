# Minutes 5-15: High-Level Design (10 min)

This phase is about demonstrating **architectural thinking** and **system-level judgment**. You’re painting the big picture before diving into details. Senior engineers excel here by showing they understand how components fit together and why certain architectural patterns work.

-----

## **Minute 5-6: Transition & Approach Statement (1 min)**

### **Your Transition:**

*“Now that we’ve aligned on requirements, let me start with a high-level architecture. I’ll sketch out the main components first, then walk through the core data flows. After that, I’ll identify the critical paths we should deep dive on.”*

**Why this works:**

- Sets expectations for this phase
- Shows structured thinking
- Signals you’ll prioritize after laying groundwork

### **Start Drawing (Immediately):**

**Draw a simple box diagram with:**

- Clients at the top
- Services in the middle
- Data stores at the bottom

*“Let me start from the client perspective and work backward…”*

-----

## **Minute 6-8: Core Components (2 min)**

### **Draw and Explain Each Component:**

**As you draw, explain the “why” not just the “what”:**

#### **1. Client Applications**

```
[Mobile Apps] [Web Clients] [Desktop Apps]
```

*“Users interact through various clients. These maintain persistent connections for real-time updates. Key consideration: we need to handle offline mode and reconnection logic at this layer.”*

#### **2. API Gateway Layer**

```
[Load Balancer] → [API Gateway]
```

*“This is our entry point. It handles:*

- *Authentication/authorization*
- *Rate limiting per user*
- *Request routing to appropriate services*
- *SSL termination*

*For REST APIs, traditional HTTP works. But for real-time messaging, we need something better.”*

#### **3. WebSocket Gateway (Critical Component)**

```
[WebSocket Gateway Cluster]
    ↕
[Connection Manager]
```

*“This is the heart of our real-time system. Some key points:*

- *Maintains long-lived, bidirectional connections with clients*
- *We’ll need thousands of these servers to handle 100M concurrent connections*
- *Each server handles ~10-20K connections*
- *Uses persistent TCP connections, not HTTP polling*

*Why WebSockets over alternatives?*

- *Long polling: Too much overhead, 3-5 sec latency*
- *Server-Sent Events (SSE): Unidirectional, need separate channel for uploads*
- *HTTP/2 Server Push: Complex, not widely supported*
- *WebSockets: Perfect for bidirectional, low-latency messaging”*

**Draw this decision on the side:**

```
WebSocket vs Long Polling
━━━━━━━━━━━━━━━━━━━━━━
WS: <100ms latency, persistent connection
LP: 3-5s latency, constant polling overhead
→ WebSocket wins for chat
```

#### **4. Chat Service (Core Business Logic)**

```
[Chat Service Cluster]
```

*“This handles all message-related business logic:*

- *Message validation*
- *Spam detection*
- *Message routing decisions*
- *Fanout logic for group chats*
- *Stateless so we can scale horizontally*

*It doesn’t maintain connections—that’s the WebSocket layer’s job. Separation of concerns.”*

#### **5. Presence Service**

```
[Presence Service]
```

*“Manages online/offline status and typing indicators:*

- *Very high write throughput (every heartbeat)*
- *Ephemeral data—doesn’t need durability*
- *We’ll use in-memory cache (Redis) here*
- *Separate service because its characteristics are so different from message storage”*

#### **6. Message Storage**

```
[Message Queue: Kafka]
    ↓
[Message DB: Cassandra/ScyllaDB]
```

*“For storage, we need:*

- *High write throughput: 290K messages/sec*
- *Horizontal scalability*
- *Fast range queries by conversation_id + timestamp*

*Cassandra is perfect here:*

- *Wide-column store, great for time-series data*
- *No single point of failure*
- *Tunable consistency*

*Kafka sits in front for:*

- *Buffering during spikes*
- *Decoupling producers from consumers*
- *Enabling multiple consumers (analytics, search indexing)”*

**Why not alternatives:**

```
Why not MySQL/Postgres?
- Hard to shard beyond a point
- Vertical scaling limits
- Joins not needed here

Why not MongoDB?
- Could work, but Cassandra better for time-series
- Cassandra's replication model better for global scale
```

#### **7. Media Storage**

```
[Object Storage: S3]
    ↓
[CDN: CloudFront]
```

*“For images/videos/files:*

- *Blob storage (S3) for durability*
- *CDN for fast global access*
- *Direct client-to-S3 uploads using pre-signed URLs*
- *This keeps media traffic off our core message path”*

#### **8. User Service**

```
[User Service]
    ↓
[User DB: PostgreSQL]
```

*“Manages user profiles, contacts, group memberships:*

- *Lower throughput than messages*
- *Needs transactions (e.g., atomic group member updates)*
- *Relational DB works fine here—Postgres*
- *Can cache heavily in Redis since this data changes rarely”*

#### **9. Notification Service**

```
[Notification Service]
    ↓
[APNs] [FCM] [Email]
```

*“For offline users:*

- *Push notifications via Apple/Google services*
- *Batching and prioritization*
- *Separate service to isolate third-party dependencies”*

#### **10. Cache Layer**

```
[Redis Cluster]
```

*“Used throughout for:*

- *Session data (UserID → WebSocket server mapping)*
- *Presence information*
- *Recent message cache*
- *User profile cache*
- *Hot group chat data”*

-----

## **Minute 8-9: Draw the Complete Architecture (1 min)**

### **Your Whiteboard Should Look Like This:**

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTS                             │
│   [Mobile Apps]    [Web Clients]    [Desktop Apps]          │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ├────────────────────────────────┤
             │                                │
        ┌────▼────┐                      ┌────▼────┐
        │   LB    │                      │   CDN   │
        └────┬────┘                      └────┬────┘
             │                                │
    ┌────────▼────────────┐                   │
    │   API Gateway       │                   │
    └────────┬────────────┘                   │
             │                                │
    ┌────────▼────────────────────────────────▼──────┐
    │         WebSocket Gateway Cluster              │
    │    [WS-1] [WS-2] ... [WS-10000]                │
    └────────┬───────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────────┐
    │              SERVICE LAYER                      │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
    │  │   Chat   │  │ Presence │  │   User   │       │
    │  │ Service  │  │ Service  │  │ Service  │       │
    │  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
    └───────┼─────────────┼─────────────┼─────────────┘
            │             │             │
    ┌───────▼─────────────▼─────────────▼─────────────┐
    │                CACHE LAYER                      │
    │            [Redis Cluster]                      │
    └──────────────────────┬──────────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────┐
    │              STORAGE LAYER                      │
    │  ┌────────┐  ┌──────────┐  ┌────────┐           │
    │  │ Kafka  │→ │Cassandra │  │Postgres│  [S3]     │
    │  │ Queue  │  │(Messages)│  │(Users) │           │
    │  └────────┘  └──────────┘  └────────┘           │
    └─────────────────────────────────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────┐
    │         NOTIFICATION SERVICE                    │
    │    [APNs]  [FCM]  [Email Workers]               │
    └─────────────────────────────────────────────────┘
```

**As you draw, narrate:**

*“So we have three main layers:*

1. *Connection layer (WebSocket gateways) - handles connections*
2. *Service layer (stateless logic) - handles business rules*
3. *Storage layer (persistent data) - handles durability*

*This separation lets us scale each layer independently based on bottlenecks.”*

-----

## **Minute 9-12: Core Data Flows (3 min)**

### **Flow 1: Sending a Message (1-on-1 Chat)**

*“Let me walk through the most critical path—sending a message:”*

**Draw the flow with numbered steps:**

```
1. User A types message in mobile app
   ↓
2. Message sent over existing WebSocket connection
   ↓
3. WebSocket Gateway (WS-1) receives message
   ↓
4. Gateway forwards to Chat Service
   ↓
5. Chat Service:
   - Validates message
   - Generates message_id (UUID)
   - Adds timestamp
   - Publishes to Kafka
   ↓
6. Message written to Cassandra (async)
   ↓
7. Chat Service checks User B's status in Redis:
   - Online? → Send to User B's WebSocket server
   - Offline? → Queue for Notification Service
   ↓
8. If online: Lookup User B's connection
   - Redis: UserB_ID → WS-Server-5
   ↓
9. Route message to WS-Server-5
   ↓
10. WS-Server-5 pushes message to User B
    ↓
11. User B receives message (<200ms total)
    ↓
12. User B sends ACK back through same path
```

**Key Points to Highlight:**

*“Notice a few things:*

- *Write to Kafka immediately for durability*
- *Cassandra write happens asynchronously—doesn’t block message delivery*
- *We need a mapping service (Redis) to know which WebSocket server has User B*
- *If User B is offline, we defer to push notifications*
- *This is write-through caching: write to durable storage, deliver from cache”*

### **Flow 2: Sending a Message (Group Chat)**

*“Group chats are more interesting because of fanout:”*

```
1. User A sends message to Group (500 members)
   ↓
2. Message arrives at Chat Service
   ↓
3. Chat Service decides fanout strategy:
   
   OPTION A: Fanout-on-Write (for small groups <50)
   ├─→ Write 500 copies to Cassandra
   ├─→ Each user has their own inbox
   └─→ Faster reads, slower writes
   
   OPTION B: Fanout-on-Read (for large groups >50)
   ├─→ Write 1 copy to Cassandra
   ├─→ Store in group's shared channel
   └─→ Faster writes, slower reads
   
   [We'll use OPTION B for 500 members]
   ↓
4. Write message once to Cassandra:
   Key: (group_id, timestamp, message_id)
   ↓
5. For online members:
   - Query Redis for all online users in group
   - Route to respective WebSocket servers
   - Parallel delivery to all online users
   ↓
6. For offline members:
   - Batch notification job
   - "You have 5 new messages in Group X"
```

**Explain the Trade-off:**

*“The fanout decision is critical:*

**Fanout-on-Write:**

- ✅ Faster reads (each user queries their own inbox)
- ❌ Slower writes (write N copies for N members)
- ❌ Storage amplification (500 members = 500 copies)
- 👍 Good for small groups (<50)

**Fanout-on-Read:**

- ✅ Faster writes (one write regardless of size)
- ✅ Less storage (single copy)
- ❌ Slower reads (must aggregate from group channel)
- 👍 Good for large groups (>50)

*We’ll use a hybrid: small groups use write fanout, large groups use read fanout.”*

### **Flow 3: User Coming Online**

*“When a user opens the app:”*

```
1. Client initiates WebSocket connection
   ↓
2. Connection established with WS-Server-X
   ↓
3. Client sends authentication token
   ↓
4. Gateway validates token with User Service
   ↓
5. Upon success:
   - Update Redis: UserID → WS-Server-X
   - Update Presence Service: UserID = ONLINE
   ↓
6. Fetch undelivered messages:
   - Query Kafka for pending messages
   - Query Cassandra for messages since last_seen_timestamp
   ↓
7. Push all unread messages to client
   ↓
8. Broadcast online status to user's contacts
   (via Presence Service pub/sub)
```

### **Flow 4: Typing Indicators & Read Receipts**

*“These are ephemeral events, handled differently:”*

```
TYPING INDICATOR:
User A starts typing → WebSocket → Presence Service
    ↓
Presence Service (Redis pub/sub):
    - Does NOT write to database
    - Broadcasts to User B only
    - TTL: 3 seconds (auto-expires)
    ↓
User B sees "User A is typing..."

READ RECEIPT:
User B reads message → WebSocket → Chat Service
    ↓
Update in Cassandra:
    - message_read_by: [UserB_ID, timestamp]
    ↓
Notify User A via WebSocket
    - "Message read by User B"
```

**Highlight the difference:**

*“Typing indicators don’t need durability—if the system crashes, it’s fine to lose them. So we use Redis pub/sub, not Cassandra. Read receipts need persistence, so they go through the full path.”*

-----

## **Minute 12-14: Critical Design Decisions (2 min)**

### **Decision 1: Why WebSocket Over HTTP/2 or Long Polling?**

Create a comparison table:

```
┌─────────────────┬──────────┬────────────┬─────────┐
│                 │WebSocket │Long Polling│ HTTP/2  │
├─────────────────┼──────────┼────────────┼─────────┤
│Latency          │ <100ms   │  3-5 sec   │ <100ms  │
│Overhead         │ Minimal  │  High      │ Medium  │
│Bidirectional    │ Yes      │  No        │ Limited │
│Connection Count │ Low      │  Very High │ Medium  │
│Battery Impact   │ Low      │  High      │ Low     │
└─────────────────┴──────────┴────────────┴─────────┘

→ WebSocket is the clear winner for real-time chat
```

### **Decision 2: Why Cassandra Over Relational DB?**

*“For message storage, I chose Cassandra because:*

1. **Write-heavy workload**: 290K writes/sec

- Cassandra’s log-structured merge tree optimized for writes
- Postgres would struggle without heavy sharding

2. **Time-series data pattern**: Messages naturally ordered by time

- Cassandra’s wide-column model perfect for (conversation_id, timestamp) queries
- No joins needed

3. **Horizontal scalability**: Can add nodes seamlessly

- Postgres sharding is manual and painful
- Cassandra handles it automatically

4. **Multi-region**: Built-in replication

- Critical for global deployment

*Trade-off: We lose ACID transactions, but we don’t need them for messages.”*

### **Decision 3: Why Kafka for Message Queue?**

*“Kafka provides:*

- **Durability**: Messages persisted to disk immediately
- **Replay**: Can reprocess messages for analytics, search indexing
- **Ordering**: Per-partition ordering guarantees
- **Multiple consumers**: Message storage, notifications, analytics can all consume

*Alternative like RabbitMQ would work but lacks replay capability.”*

-----

## **Minute 14-15: Identify Deep Dive Areas (1 min)**

### **Transition to Next Phase:**

*“So that’s the high-level architecture. Now, there are several areas we should dive deeper into to make this production-ready:*

1. **WebSocket Connection Management**: How do we scale to 100M concurrent connections?
2. **Message Storage Schema**: Exactly how do we model data in Cassandra?
3. **Ensuring Message Ordering**: Especially in group chats with network delays
4. **Handling Failures**: What happens when WebSocket servers crash?
5. **Geographic Distribution**: Multi-region considerations

*Which of these would you like me to focus on first, or should I cover them in this order?”*

**Why ask this:**

- Shows you have a plan
- Lets interviewer guide priorities
- Demonstrates you’re thinking beyond just “making it work”

-----

## **What Your Whiteboard Looks Like After 10 Minutes:**

```
┌─────────────────────────────────────────────────────┐
│  HIGH-LEVEL ARCHITECTURE                            │
│  [Full component diagram drawn]                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  KEY DATA FLOWS                                     │
│  1. Send Message (1-on-1) [arrows & steps]          │
│  2. Send Message (Group)  [fanout options]          │
│  3. User Online           [connection flow]         │
│  4. Typing/Read Receipts  [ephemeral events]        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  KEY DECISIONS                                      │
│  • WebSocket > Long Polling (latency)               │
│  • Cassandra > RDBMS (write throughput)             │
│  • Kafka for durability + replay                    │
│  • Hybrid fanout (small=write, large=read)          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  DEEP DIVE AREAS                                    │
│  → WebSocket scaling                                │
│  → Data modeling                                    │
│  → Message ordering                                 │
│  → Failure handling                                 │
└─────────────────────────────────────────────────────┘
```

-----

## **Common Mistakes to Avoid:**

- ❌ **Drawing too detailed too soon**: Don’t show DB schemas or API contracts yet
- ❌ **Not explaining why**: Every component needs justification
- ❌ **Forgetting data flows**: Architecture without flows is incomplete
- ❌ **Ignoring alternatives**: Show you considered other options
- ❌ **Going past 10 minutes**: You need time for deep dives
- ❌ **Not using the whiteboard**: Draw as you talk, don’t just narrate

-----

## **Signals You’re Giving as a Senior Engineer:**

- ✅ **Systems Thinking**: You see how components interact, not just individual pieces
- ✅ **Trade-off Analysis**: Every decision has pros/cons, and you articulate them
- ✅ **Technology Choices**: You know when to use Cassandra vs Postgres
- ✅ **Scalability Awareness**: You think about bottlenecks proactively
- ✅ **Communication**: Clear structure, good pacing, uses visuals effectively

**You’re now 15 minutes in and perfectly positioned to go deep on the critical areas.**
