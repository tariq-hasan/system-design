# 60-Minute Structure for Chat Messaging System Design

Here’s how I’d structure this interview to maximize impact and demonstrate senior-level thinking:

## **Minutes 0-5: Requirements Clarification (5 min)**

**Functional Requirements:**

- 1-on-1 messaging vs group chat (focus on both)
- Message types: text, images, files, reactions
- Online status and typing indicators
- Read receipts
- Message history and search
- Push notifications

**Non-Functional Requirements:**

- Scale: 500M DAU, 100M concurrent users
- Low latency: <100ms message delivery
- High availability: 99.99%
- Message durability: no message loss
- Eventual consistency acceptable for some features

**Out of Scope:**

- Voice/video calls
- End-to-end encryption details
- Payment features

**Key Clarifying Questions:**

- What’s more important: delivery speed or guaranteed ordering?
- Do we need message edit/delete?
- How long to retain message history?

## **Minutes 5-15: High-Level Design (10 min)**

**Core Components Overview:**

1. **Client Applications** (web, mobile)
1. **API Gateway** (REST for HTTP, WebSocket Gateway for real-time)
1. **Chat Service** (message handling, routing)
1. **Presence Service** (online/offline, typing)
1. **Message Storage** (Cassandra/ScyllaDB)
1. **Media Storage** (S3/CDN)
1. **Notification Service** (push notifications)
1. **User Service** (profiles, contacts)

**Basic Flow:**

- User A sends message → WebSocket → Chat Service → Message Queue → WebSocket → User B
- Draw simple box diagram showing main services and data flow

**Key Design Decision to Highlight:**
WebSocket for real-time bidirectional communication vs polling (show why WebSocket wins)

## **Minutes 15-35: Deep Dive & Detailed Design (20 min)**

### **1. Real-Time Message Delivery (8 min)**

**WebSocket Connection Management:**

- Long-lived persistent connections
- Connection pooling across multiple WebSocket servers
- Session mapping: UserID → WebSocket Server (stored in Redis)

**Message Flow:**

```
Sender → WebSocket Server A → Chat Service → 
Message Queue (Kafka) → Chat Service → 
WebSocket Server B → Recipient
```

**Handling Offline Users:**

- Store undelivered messages in queue
- Fetch on reconnection
- Use push notifications as fallback

### **2. Message Storage Strategy (6 min)**

**Write Pattern:**

- Partition by conversation_id (1-on-1) or channel_id (group)
- Use Cassandra for horizontal scalability
- Schema: `(conversation_id, timestamp, message_id) → message_data`

**Read Pattern:**

- Recent messages: fetch from cache (Redis)
- Older messages: query Cassandra with pagination
- Cache warming on user login

**Group Chat Optimization:**

- Fanout-on-write vs fanout-on-read tradeoff
- For large groups (>50): single message copy, read-time fanout
- For small groups: write to each user’s inbox (faster reads)

### **3. Scaling WebSocket Connections (6 min)**

**Challenge:** 100M concurrent connections

**Solution:**

- Distribute across 10,000 WebSocket servers (10K connections each)
- Service discovery: clients find available WS servers via API Gateway
- Load balancing: consistent hashing based on UserID
- Heartbeat mechanism to detect dead connections

**State Synchronization:**

- Redis cluster maintains UserID → WebSocket Server mapping
- Pub/sub pattern for cross-server message routing

## **Minutes 35-45: Addressing Bottlenecks & Scaling (10 min)**

### **Identified Bottlenecks:**

**1. Message Ordering in Group Chats:**

- Use Lamport timestamps or vector clocks
- Sequence numbers per conversation
- Handle network delays and out-of-order delivery

**2. Hot Partitions:**

- Very active group chats create write hotspots
- Solution: Further partition by time window + conversation_id
- Implement rate limiting per group

**3. Media Upload/Download:**

- Direct upload to S3 via pre-signed URLs
- CDN for global distribution
- Thumbnail generation via async workers

**4. Database Scaling:**

- Cassandra replication factor: 3
- Read/write quorum for consistency
- Separate clusters for different regions

### **Additional Optimizations:**

**Read Receipts & Typing Indicators:**

- Ephemeral, non-persistent events
- Use Redis pub/sub (don’t write to database)
- Batch typing indicators to reduce traffic

**Search Functionality:**

- Elasticsearch for full-text message search
- Async indexing pipeline from Cassandra
- Trade-off: slight delay in searchability vs real-time

## **Minutes 45-55: Edge Cases & Monitoring (10 min)**

### **Edge Cases:**

1. **Network Partitions:**

- Client reconnection with exponential backoff
- Message deduplication using message_id

1. **Split-Brain Scenarios:**

- Use distributed consensus (Raft/Paxos) for critical metadata
- Accept eventual consistency for message delivery

1. **Message Size Limits:**

- Enforce 64KB for text messages
- Large files: direct S3 upload with metadata in message

1. **Delete/Edit Message:**

- Soft delete with tombstone markers
- Propagate delete/edit events through same message pipeline

### **Monitoring & Observability:**

**Key Metrics:**

- Message delivery latency (p50, p99, p999)
- WebSocket connection count and churn rate
- Message throughput (messages/sec)
- Failed message delivery rate

**Alerts:**

- Latency spike >200ms
- Connection failures >1%
- Database write failures
- Kafka lag increasing

## **Minutes 55-60: Trade-offs & Wrap-up (5 min)**

### **Key Trade-offs Made:**

1. **Consistency vs Availability:**

- Chose AP in CAP theorem
- Eventual consistency acceptable for message ordering

1. **Fanout Strategy:**

- Hybrid approach based on group size
- Optimized for common case (small groups)

1. **Storage Cost vs Performance:**

- Hot data in Redis (expensive but fast)
- Cold data in Cassandra (cheaper, slower)

### **Questions I’d Ask Back:**

- “Would you like me to dive deeper into any component?”
- “Should we discuss the data model schema in detail?”
- “Want to explore the multi-region deployment strategy?”

-----

## **Key Senior-Level Signals to Demonstrate:**

1. **Quantitative Reasoning:** Mention actual numbers (100M users, 10K servers, latency targets)
1. **Production Experience:** Reference real technologies (Cassandra, Kafka, Redis)
1. **Trade-off Analysis:** Explicitly state why you chose one approach over another
1. **Failure Handling:** Proactively discuss edge cases and monitoring
1. **Structured Communication:** Clear transitions between sections, summarize before deep-diving

This structure ensures you cover breadth early, demonstrate depth in critical areas, and leave time for discussion—all while showing you can ship production systems at scale.​​​​​​​​​​​​​​​​
