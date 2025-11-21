# Minutes 45-55: Edge Cases & Monitoring (10 min)

This phase demonstrates **production maturity**. Senior engineers don’t just build systems—they anticipate what goes wrong in the real world and build observability to detect and diagnose issues. This is where you show you’ve been on-call and debugged production incidents.

-----

## **Minute 45-46: Transition & Framework (1 min)**

### **Your Transition Statement:**

*“Now let’s discuss how this system behaves when things go wrong—because in distributed systems, failures are guaranteed, not exceptional. I’ll organize this into:*

1. *Critical edge cases and failure scenarios*
1. *Data consistency and conflict resolution*
1. *Security and abuse prevention*
1. *Observability and monitoring strategy*

*For each, I’ll explain the problem, impact radius, detection method, and mitigation.”*

**Why this works:**

- Shows you’ve debugged production systems
- Demonstrates defensive programming mindset
- Proves you think about operational burden

-----

## **EDGE CASE 1: Network Partitions & Split-Brain Scenarios (Minutes 46-49, ~3 min)**

### **Minute 46-47: The Split-Brain Problem (1 min)**

*“One of the most insidious problems in distributed systems: what happens when our infrastructure splits into isolated islands?”*

#### **Draw the Scenario:**

```
┌─────────────────────────────────────────────────────────┐
│  NETWORK PARTITION SCENARIO                             │
│                                                         │
│  Normal State:                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Region: US-EAST                                 │   │
│  │  ┌───────────┐    ┌──────────┐    ┌──────────┐   │   │
│  │  │ WS Servers│────│Chat Svc  │────│ Cassandra│   │   │
│  │  └───────────┘    └──────────┘    └──────────┘   │   │
│  │       │               │                │         │   │
│  │       └───────────────┼────────────────┘         │   │
│  │                       │                          │   │
│  │                  ┌────▼────┐                     │   │
│  │                  │  Redis  │                     │   │
│  │                  │ Cluster │                     │   │
│  │                  └─────────┘                     │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  Network Partition Occurs:                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Island A              │        Island B          │  │
│  │                        │                          │  │
│  │  ┌──────────┐          │         ┌──────────┐     │  │
│  │  │WS-1 to   │          │         │WS-5001 to│     │  │
│  │  │WS-5000   │          ╳         │WS-10000  │     │  │
│  │  └──────────┘          │         └──────────┘     │  │
│  │       │                │              │           │  │
│  │  ┌────▼────┐           │         ┌────▼────┐      │  │
│  │  │Redis    │           │         │Redis    │      │  │
│  │  │Primary  │           │         │Replica  │      │  │
│  │  └─────────┘           │         └─────────┘      │  │
│  │                        │                          │  │
│  │  Can't talk to ────────╳──────── Can't talk to    │  │
│  │  Island B              │         Island A         │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  PROBLEMS:                                              │
│  1. Both islands think they're authoritative            │
│  2. Same user might connect to both islands             │
│  3. Messages sent in Island A invisible in Island B     │
│  4. Sequence numbers diverge                            │
│  5. When partition heals, conflicts everywhere          │
└─────────────────────────────────────────────────────────┘
```

**Explain the severity:**

*“This isn’t theoretical—this happens during:*

- *Data center network failures*
- *BGP routing issues*
- *Undersea cable cuts*
- *Cloud provider regional outages*
- *Misconfigured firewalls*

*And it can last minutes to hours. We need to handle it gracefully.”*

-----

### **Minute 47-49: Solutions for Network Partitions (2 min)**

#### **Solution 1: Quorum-Based Consistency for Critical Operations**

```
┌─────────────────────────────────────────────────────────┐
│  QUORUM CONSENSUS FOR WRITES                            │
│                                                         │
│  Critical operations that MUST be consistent:           │
│  • User registration                                    │
│  • Group creation                                       │
│  • Admin actions (kick user, delete group)              │
│                                                         │
│  Implementation:                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Cassandra consistency level: QUORUM               │  │
│  │                                                   │  │
│  │ Replication Factor (RF) = 3                       │  │
│  │ Write Quorum = (RF / 2) + 1 = 2                   │  │
│  │ Read Quorum = 2                                   │  │
│  │                                                   │  │
│  │ For write to succeed:                             │  │
│  │ ✅ Must receive ACK from 2 out of 3 replicas      │  │
│  │                                                   │  │
│  │ During partition:                                 │  │
│  │ Island A: Has 2 replicas → writes succeed ✅      │  │
│  │ Island B: Has 1 replica → writes fail ❌          │  │
│  │                                                   │  │
│  │ Result: At most one partition accepts writes      │  │
│  │ (The partition with majority)                     │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Trade-off:                                             │
│  ✅ Strong consistency (no split-brain)                 │
│  ❌ Availability reduced (minority partition fails)     │
│  ❌ Higher latency (wait for 2 ACKs)                    │
└─────────────────────────────────────────────────────────┘
```

#### **Solution 2: AP Mode for Regular Messages (Eventual Consistency)**

```
┌─────────────────────────────────────────────────────────┐
│  EVENTUAL CONSISTENCY FOR MESSAGES                      │
│                                                         │
│  Philosophy: Better to let users send messages and      │
│  reconcile later than block all communication           │
│                                                         │
│  During Partition:                                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Island A:                                         │  │
│  │ • Users can send messages                         │  │
│  │ • Messages written to local Cassandra             │  │
│  │ • Sequence numbers: 1, 2, 3, 4, ...               │  │
│  │                                                   │  │
│  │ Island B:                                         │  │
│  │ • Different users can also send messages          │  │
│  │ • Messages written to different Cassandra nodes   │  │
│  │ • Sequence numbers: 1, 2, 3, 4, ... (CONFLICT!)   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  When Partition Heals:                                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 1. Detect conflict: Same sequence numbers exist   │  │
│  │                                                   │  │
│  │ 2. Conflict resolution strategy:                  │  │
│  │    Use vector clocks or Lamport timestamps        │  │
│  │                                                   │  │
│  │ 3. For each conflicting message:                  │  │
│  │    New sequence = (original_seq, island_id, ts)   │  │
│  │                                                   │  │
│  │    Island A messages:                             │  │
│  │    (1, 'A', 1699999900) → becomes seq 1.A         │  │
│  │    (2, 'A', 1699999905) → becomes seq 2.A         │  │
│  │                                                   │  │
│  │    Island B messages:                             │  │
│  │    (1, 'B', 1699999902) → becomes seq 1.B         │  │
│  │    (2, 'B', 1699999908) → becomes seq 2.B         │  │
│  │                                                   │  │
│  │ 4. Merge sort by timestamp:                       │  │
│  │    Final order: 1.A, 1.B, 2.A, 2.B                │  │
│  │                                                   │  │
│  │ 5. Broadcast merge notification to all clients    │  │
│  │    "Messages reordered due to network issue"      │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

#### **Solution 3: Partition Detection & Graceful Degradation**

```
┌─────────────────────────────────────────────────────────┐
│  AUTOMATIC PARTITION DETECTION                          │
│                                                         │
│  Health Check System:                                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Every WS Server runs continuous health checks:    │  │
│  │                                                   │  │
│  │ Every 5 seconds:                                  │  │
│  │ ├─ Ping Redis (expect <10ms)                      │  │
│  │ ├─ Ping Cassandra (expect <20ms)                  │  │
│  │ ├─ Ping Kafka (expect <15ms)                      │  │
│  │ └─ Ping 3 peer WS servers in cluster              │  │
│  │                                                   │  │
│  │ If failures > threshold (3 consecutive):          │  │
│  │ ├─ Set server status = DEGRADED                   │  │
│  │ ├─ Emit alert to ops team                         │  │
│  │ └─ Activate degraded mode behavior                │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Degraded Mode Behavior:                                │
│  ┌───────────────────────────────────────────────────┐  │
│  │ • Accept messages but buffer locally              │  │
│  │ • Show warning to users: "Limited connectivity"   │  │
│  │ • Disable features requiring coordination:        │  │
│  │   - Group member additions                        │  │
│  │   - Message editing/deletion                      │  │
│  │   - Admin actions                                 │  │
│  │ • Allow read-only operations                      │  │
│  │ • Retry failed writes with exponential backoff    │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  User Experience:                                       │
│  "You're offline or experiencing connectivity issues.   │
│   Messages will be delivered when connection restores." │
└─────────────────────────────────────────────────────────┘
```

-----

## **EDGE CASE 2: Message Deduplication & Idempotency (Minutes 49-51, ~2 min)**

### **Minute 49-50: The Duplicate Message Problem (1 min)**

*“Another critical edge case: ensuring exactly-once delivery in an at-least-once world.”*

#### **Draw the Scenario:**

```
┌─────────────────────────────────────────────────────────┐
│  DUPLICATE MESSAGE SCENARIO                             │
│                                                         │
│  User sends: "Hello"                                    │
│      │                                                  │
│      ▼                                                  │
│  WS Server receives message                             │
│      │                                                  │
│      ├─────► Chat Service                               │
│      │           │                                      │
│      │           ├─► Write to Kafka ✅                  │
│      │           │                                      │
│      │           ├─► ACK back to WS Server              │
│      │           │                                      │
│      │       ⚡ Network glitch! ACK lost                 │
│      │                                                  │
│  WS Server timeout (no ACK received after 5s)           │
│      │                                                  │
│      ├─────► Chat Service (RETRY with same message)     │
│                  │                                      │
│                  ├─► Write to Kafka ✅ (DUPLICATE!)     │
│                                                         │
│  Result: "Hello" appears twice in recipient's chat      │
│                                                         │
│  Other scenarios causing duplicates:                    │
│  • Client retries on timeout                            │
│  • Server crashes mid-processing                        │
│  • Message queue redelivery                             │
│  • Network packet duplication (rare but possible)       │
└─────────────────────────────────────────────────────────┘
```

-----

### **Minute 50-51: Deduplication Strategy (1 min)**

#### **Solution: Idempotency with Client-Generated IDs**

```
┌─────────────────────────────────────────────────────────┐
│  IDEMPOTENT MESSAGE PROCESSING                          │
│                                                         │
│  Step 1: Client generates unique ID                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │ When user sends message, client creates:          │  │
│  │                                                   │  │
│  │ client_message_id = UUID.v4()                     │  │
│  │   // e.g., "550e8400-e29b-41d4-a716-446655440000" │  │
│  │                                                   │  │
│  │ Message payload:                                  │  │
│  │ {                                                 │  │
│  │   client_msg_id: "550e8400-...",                  │  │
│  │   sender_id: "user_123",                          │  │
│  │   conversation_id: "conv_456",                    │  │
│  │   text: "Hello",                                  │  │
│  │   timestamp: 1699999999                           │  │
│  │ }                                                 │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Step 2: Server-side deduplication                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Chat Service receives message:                    │  │
│  │                                                   │  │
│  │ 1. Check Redis dedup cache:                       │  │
│  │    key = f"dedup:{client_msg_id}"                 │  │
│  │    ttl = 300 seconds (5 minutes)                  │  │
│  │                                                   │  │
│  │ 2. If key exists:                                 │  │
│  │    ├─ Retrieve server_message_id                  │  │
│  │    ├─ Return cached response (idempotent!)        │  │
│  │    └─ Log: "Duplicate detected, skipping"         │  │
│  │                                                   │  │
│  │ 3. If key doesn't exist:                          │  │
│  │    ├─ Process message normally                    │  │
│  │    ├─ Generate server_message_id                  │  │
│  │    ├─ Write to Kafka/Cassandra                    │  │
│  │    └─ Cache mapping:                              │  │
│  │       SET dedup:{client_msg_id}                   │  │
│  │           {server_msg_id: "msg_789"}              │  │
│  │           EX 300                                  │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Step 3: Client-side deduplication (defense in depth)   │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Client maintains local cache:                     │  │
│  │ Map<client_msg_id, display_state>                 │  │
│  │                                                   │  │
│  │ If same client_msg_id received twice:             │  │
│  │ ├─ Ignore duplicate                               │  │
│  │ └─ Update UI state only once                      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Why 5-minute TTL?                                      │
│  • Covers typical retry windows                         │
│  • Balances memory usage vs safety                      │
│  • After 5 min, extremely unlikely to be duplicate      │
└─────────────────────────────────────────────────────────┘
```

#### **Handling Edge Cases in Deduplication:**

```
┌─────────────────────────────────────────────────────────┐
│  DEDUPLICATION EDGE CASES                               │
│                                                         │
│  Case 1: Redis cache miss on retry                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Scenario: Redis evicts entry before retry         │  │
│  │                                                   │  │
│  │ Solution: Secondary check in Cassandra            │  │
│  │ Query: Does message with client_msg_id exist?     │  │
│  │                                                   │  │
│  │ SELECT server_msg_id FROM messages                │  │
│  │ WHERE conversation_id = ? AND                     │  │
│  │       client_msg_id = ?                           │  │
│  │ LIMIT 1                                           │  │
│  │                                                   │  │
│  │ If found: Return existing, don't create duplicate │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Case 2: Client sends same message twice (intentional)  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ User clicks "Send" twice rapidly                  │  │
│  │                                                   │  │
│  │ Client behavior:                                  │  │
│  │ • Disable send button on first click              │  │
│  │ • Only re-enable after server ACK                 │  │
│  │ • If user really wants duplicate, generate new ID │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Case 3: Same text, different instances                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ User sends "OK" at t=0, then "OK" again at t=10   │  │
│  │                                                   │  │
│  │ These are DIFFERENT messages (different IDs):     │  │
│  │ Message 1: {id: "uuid-1", text: "OK", t: 0}       │  │
│  │ Message 2: {id: "uuid-2", text: "OK", t: 10}      │  │
│  │                                                   │  │
│  │ Not duplicates! Both should be delivered.         │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

-----

## **EDGE CASE 3: Security & Abuse Prevention (Minutes 51-53, ~2 min)**

### **Minute 51-52: Attack Vectors (1 min)**

*“Chat systems are prime targets for abuse. Let me show you the attack vectors we need to defend against:”*

```
┌─────────────────────────────────────────────────────────┐
│  SECURITY THREATS                                       │
│                                                         │
│  1. MESSAGE SPAM                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Attack: Bot sends 10K messages/sec to flood chat  │  │
│  │ Impact: System overload, user experience ruined   │  │
│  │ Detection: Spike in message rate from single user │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  2. CONNECTION EXHAUSTION                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Attack: Open millions of connections, never close │  │
│  │ Impact: Exhaust file descriptors, block real users│  │
│  │ Detection: Connections with no activity           │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  3. LARGE MESSAGE ATTACKS                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Attack: Send 100MB messages to crash servers      │  │
│  │ Impact: Memory exhaustion, bandwidth saturation   │  │
│  │ Detection: Message size > threshold               │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  4. UNAUTHORIZED ACCESS                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Attack: Access others' messages without permission│  │
│  │ Impact: Privacy breach, data leak                 │  │
│  │ Detection: Authorization failures, unusual access │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  5. MEDIA STORAGE ABUSE                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Attack: Upload illegal/malicious files            │  │
│  │ Impact: Legal liability, malware distribution     │  │
│  │ Detection: Content scanning, file type validation │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

-----

### **Minute 52-53: Defense Mechanisms (1 min)**

```
┌─────────────────────────────────────────────────────────┐
│  DEFENSE IN DEPTH STRATEGY                              │
│                                                         │
│  Layer 1: Rate Limiting (Multiple Tiers)                │
│  ┌───────────────────────────────────────────────────┐  │
│  │ PER USER:                                         │  │
│  │ ├─ Messages: 100/min, 1000/hour                   │  │
│  │ ├─ Connections: 5 devices max                     │  │
│  │ ├─ Media uploads: 10/hour                         │  │
│  │ └─ Group creations: 5/day                         │  │
│  │                                                   │  │
│  │ PER CONVERSATION:                                 │  │
│  │ ├─ Message rate: 10K/min (prevent flood)          │  │
│  │ └─ Member additions: 50/hour                      │  │
│  │                                                   │  │
│  │ PER IP ADDRESS:                                   │  │
│  │ ├─ Connection attempts: 100/min                   │  │
│  │ └─ Failed auth: 10/min → temp ban                 │  │
│  │                                                   │  │
│  │ Implementation: Token bucket in Redis             │  │
│  │ ┌─────────────────────────────────────────┐       │  │
│  │ │ key = f"rate:{user_id}:msg"             │       │  │
│  │ │                                         │       │  │
│  │ │ current = INCR key                      │       │  │
│  │ │ if current == 1:                        │       │  │
│  │ │   EXPIRE key 60  # 1 minute window      │       │  │
│  │ │                                         │       │  │
│  │ │ if current > 100:                       │       │  │
│  │ │   return HTTP 429 Too Many Requests     │       │  │
│  │ └─────────────────────────────────────────┘       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Layer 2: Message Size Limits                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Enforced at WebSocket Gateway:                    │  │
│  │ ├─ Text message: 64 KB max                        │  │
│  │ ├─ Media reference: 10 MB max                     │  │
│  │ ├─ WebSocket frame: 1 MB max                      │  │
│  │ └─ Reject oversized messages immediately          │  │
│  │                                                   │  │
│  │ Prevents:                                         │  │
│  │ • Memory exhaustion                               │  │
│  │ • Slowloris-style attacks                         │  │
│  │ • Bandwidth saturation                            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Layer 3: Content Validation                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Text Messages:                                    │  │
│  │ ├─ UTF-8 validation                               │  │
│  │ ├─ Remove null bytes                              │  │
│  │ ├─ Check for control characters                   │  │
│  │ └─ Basic profanity filter (optional)              │  │
│  │                                                   │  │
│  │ Media Files:                                      │  │
│  │ ├─ Verify MIME type matches extension             │  │
│  │ ├─ Virus scan (ClamAV integration)                │  │
│  │ ├─ Image: Check for exploits (ImageMagick bypass) │  │
│  │ ├─ Reject executables (.exe, .sh, .bat)           │  │
│  │ └─ Async scanning (don't block upload)            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Layer 4: Authentication & Authorization                │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Every message checks:                             │  │
│  │ ├─ Is sender authenticated? (JWT validation)      │  │
│  │ ├─ Is sender member of conversation?              │  │
│  │ ├─ Is sender allowed to send? (not banned/muted)  │  │
│  │ └─ Is conversation still active? (not deleted)    │  │
│  │                                                   │  │
│  │ Fail closed: Deny if any check fails              │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Layer 5: Anomaly Detection (ML-based)                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Real-time anomaly scoring:                        │  │
│  │ ├─ Sudden spike in message rate                   │  │
│  │ ├─ Messages sent at unusual times (3 AM local)    │  │
│  │ ├─ Repetitive content (copy-paste spam)           │  │
│  │ ├─ Connections from unusual geolocations          │  │
│  │ └─ Messages with suspicious URLs                  │  │
│  │                                                   │  │
│  │ Anomaly score > threshold:                        │  │
│  │ ├─ Trigger CAPTCHA challenge                      │  │
│  │ ├─ Require re-authentication                      │  │
│  │ ├─ Flag for manual review                         │  │
│  │ └─ Temporary rate limit reduction                 │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

-----

## **MONITORING & OBSERVABILITY (Minutes 53-55, ~2 min)**

### **Minute 53-54: Metrics & Alerting Strategy (1 min)**

*“Finally, let’s talk about how we know the system is healthy and detect issues before users do.”*

```
┌─────────────────────────────────────────────────────────┐
│  OBSERVABILITY STRATEGY (The Four Golden Signals)       │
│                                                         │
│  1. LATENCY METRICS                                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │ message_delivery_latency_ms                       │  │
│  │ ├─ p50:  < 50ms   (median)                        │  │
│  │ ├─ p95:  < 100ms                                  │  │
│  │ ├─ p99:  < 200ms  ⚠️  Alert if > 200ms            │  │
│  │ └─ p999: < 500ms  🚨 Alert if > 500ms             │  │
│  │                                                   │  │
│  │ websocket_connection_time_ms                      │  │
│  │ ├─ p99: < 1000ms                                  │  │
│  │ └─ Alert if > 2000ms                              │  │
│  │                                                   │  │
│  │ cassandra_write_latency_ms                        │  │
│  │ ├─ p99: < 50ms                                    │  │
│  │ └─ Alert if > 100ms (indicates hot partition)     │  │
│  │                                                   │  │
│  │ redis_operation_latency_ms                        │  │
│  │ ├─ p99: < 5ms                                     │  │
│  │ └─ Alert if > 20ms (indicates overload)           │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  2. TRAFFIC METRICS                                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │ messages_per_second                               │  │
│  │ ├─ Track globally and per conversation            │  │
│  │ ├─ Alert on sudden 10x spike (potential attack)   │  │
│  │ └─ Alert on sudden drop to 0 (outage)             │  │
│  │                                                   │  │
│  │ active_connections                                │  │
│  │ ├─ Current: ~100M                                 │  │
│  │ ├─ Alert if drops > 20% in 5 min                  │  │
│  │ └─ Alert if exceeds capacity (110M)               │  │
│  │                                                   │  │
│  │ connection_churn_rate                             │  │
│  │ ├─ connects_per_second                            │  │
│  │ ├─ disconnects_per_second                         │  │
│  │ └─ Alert if churn > 50K/sec (thundering herd)     │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  3. ERROR METRICS                                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │ message_delivery_failures                         │  │
│  │ ├─ Rate: < 0.1% acceptable                        │  │
│  │ └─ Alert if > 1%                                  │  │
│  │                                                   │  │
│  │ websocket_connection_failures                     │  │
│  │ ├─ Track by reason (timeout, auth, refused)       │  │
│  │ └─ Alert if rate > 5%                             │  │
│  │                                                   │  │
│  │ kafka_consumer_lag                                │  │
│  │ ├─ Ideal: < 1000 messages                         │  │
│  │ ├─ Warning: > 10K messages                        │  │
│  │ └─ Critical: > 100K messages                      │  │
│  │                                                   │  │
│  │ cassandra_write_failures                          │  │
│  │ └─ Alert if > 0.01% (write path critical)         │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  4. SATURATION METRICS                                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ websocket_server_cpu_usage                        │  │
│  │ ├─ Warning: > 70%                                 │  │
│  │ └─ Critical: > 85% → trigger auto-scaling         │  │
│  │                                                   │  │
│  │ redis_memory_usage                                │  │
│  │ ├─ Warning: > 80%                                 │  │
│  │ └─ Critical: > 90% → eviction starts              │  │
│  │                                                   │  │
│  │ cassandra_disk_usage                              │  │
│  │ ├─ Warning: > 70%                                 │  │
│  │ └─ Critical: > 85% → add nodes                    │  │
│  │                                                   │  │
│  │ kafka_queue_depth                                 │  │
│  │ ├─ Normal: < 10K                                  │  │
│  │ └─ Alert: > 100K (consumers falling behind)       │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

-----

### **Minute 54-55: Logging, Tracing & Debugging (1 min)**

```
┌─────────────────────────────────────────────────────────┐
│  DISTRIBUTED TRACING                                    │
│                                                         │
│  Every message gets a trace_id:                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ trace_id = uuid.v4()  // Generated at client      │  │
│  │                                                   │  │
│  │ Propagated through entire flow:                   │  │
│  │ Client → WS Gateway → Chat Service → Kafka        │  │
│  │   → Cassandra → Recipient WS → Client             │  │
│  │                                                   │  │
│  │ Each component logs with trace_id:                │  │
│  │ {                                                 │  │
│  │   "trace_id": "abc-123",                          │  │
│  │   "component": "chat_service",                    │  │
│  │   "event": "message_received",                    │  │
│  │   "timestamp": 1699999999,                        │  │
│  │   "latency_ms": 45,                               │  │
│  │   "user_id": "user_123"                           │  │
│  │ }                                                 │  │
│  │                                                   │  │
│  │ Enables:                                          │  │
│  │ ✅ End-to-end message tracking                    │  │
│  │ ✅ Identify bottlenecks in delivery path          │  │
│  │ ✅ Debug "message not delivered" issues           │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Example trace visualization:                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Client send          [0ms]                        │  │
│  │ ├─ WS receive        [5ms]    +5ms                │  │
│  │ ├─ Chat Service      [15ms]   +10ms               │  │
│  │ ├─ Kafka write       [35ms]   +20ms ⚠️ slow       │  │
│  │ ├─ Redis lookup      [40ms]   +5ms                │  │
│  │ ├─ Route to WS       [45ms]   +5ms                │  │
│  │ └─ Recipient recv    [50ms]   +5ms                │  │
│  │                                                   │  │
│  │ Total: 50ms (meets SLA ✅)                        │  │
│  │ Bottleneck: Kafka write (20ms) → investigate      │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  STRUCTURED LOGGING STRATEGY                            │
│                                                         │
│  Log Levels:                                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │ DEBUG: Message routing decisions                  │  │
│  │ INFO:  Message sent/received (sampled 1%)         │  │
│  │ WARN:  Retry attempts, degraded mode              │  │
│  │ ERROR: Failed delivery, auth failures             │  │
│  │ FATAL: Service crash, data corruption             │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Critical logs to capture:                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ • Every message delivery (sampled)                │  │
│  │ • Every failed delivery (100%)                    │  │
│  │ • Authentication failures                         │  │
│  │ • Rate limit hits                                 │  │
│  │ • Partition events (split/heal)                   │  │
│  │ • Auto-scaling events                             │  │
│  │ • Configuration changes                           │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Log aggregation: ELK Stack or Datadog                  │
│  Retention: 30 days hot, 1 year cold storage            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  DASHBOARDS & ON-CALL RUNBOOKS                          │
│                                                         │
│  Primary Dashboard:                                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │ • Overall system health (RED/GREEN)               │  │
│  │ • Message delivery p99 latency (line chart)       │  │
│  │ • Active connections (gauge)                      │  │
│  │ • Messages/sec (line chart)                       │  │
│  │ • Error rate by component (heatmap)               │  │
│  │ • Top 10 hot conversations (table)                │  │
│  │ • Infrastructure saturation (bars)                │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Runbooks for common incidents:                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ "High message delivery latency"                   │  │
│  │ ├─ Check Kafka consumer lag                       │  │
│  │ ├─ Check Cassandra write latency                  │  │
│  │ ├─ Identify hot partitions                        │  │
│  │ ├─ Scale consumers if lag > 100K                  │  │
│  │ └─ Enable auto-sharding for hot conversations     │  │
│  │                                                   │  │
│  │ "Connection storm"                                │  │
│  │ ├─ Check if network partition just healed         │  │
│  │ ├─ Verify rate limiting is active                 │  │
│  │ ├─ Scale WebSocket servers if needed              │  │
│  │ └─ Monitor for DDoS patterns                      │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

-----

## **Minute 55: Summary & Transition**

*“Let me quickly summarize the edge cases and monitoring we’ve covered:”*

```
┌─────────────────────────────────────────────────────────┐
│  EDGE CASES & MONITORING SUMMARY                        │
│                                                         │
│  EDGE CASES HANDLED:                                    │
│  ✅ Network partitions → Quorum writes + reconciliation │
│  ✅ Duplicate messages → Client IDs + Redis dedup       │
│  ✅ Security attacks → Multi-layer rate limiting        │
│  ✅ Content abuse → Validation + anomaly detection      │
│                                                         │
│  OBSERVABILITY:                                         │
│  ✅ Latency: p99 < 200ms                                │
│  ✅ Traffic: 290K msg/sec baseline                      │
│  ✅ Errors: < 0.1% failure rate                         │
│  ✅ Saturation: Auto-scaling at 70% CPU                 │
│  ✅ Tracing: End-to-end message tracking                │
│                                                         │
│  ON-CALL READINESS:                                     │
│  ✅ Automated alerts with clear thresholds              │
│  ✅ Runbooks for common incidents                       │
│  ✅ Dashboards for quick diagnosis                      │
│  ✅ Distributed tracing for deep debugging              │
└─────────────────────────────────────────────────────────┘
```

-----

## **What Your Whiteboard Looks Like After 10 Minutes:**

```
┌──────────── EDGE CASES & MONITORING ─────────────┐
│                                                  │
│ EDGE CASES:                                      │
│ 1. Network Partitions                            │
│    [Split-brain diagram]                         │
│    → Quorum writes + conflict resolution         │
│                                                  │
│ 2. Duplicate Messages                            │
│    [Retry scenario diagram]                      │
│    → Client IDs + Redis dedup cache (5min TTL)   │
│                                                  │
│ 3. Security                                      │
│    [Defense layers: rate limit → validation →    │
│     auth → anomaly detection]                    │
│                                                  │
│ MONITORING:                                      │
│ • Latency: p99 < 200ms                           │
│ • Traffic: 290K msg/sec                          │
│ • Errors: < 0.1%                                 │
│ • Saturation: CPU/Memory/Disk                    │
│ • Tracing: trace_id propagation                  │
│                                                  │
│ [Example trace visualization showing 50ms flow]  │
└──────────────────────────────────────────────────┘
```

-----

## **Senior-Level Signals You’re Demonstrating:**

✅ **Production Battle Scars**: These are real issues you’ve debugged at 3 AM
✅ **Defense in Depth**: Multiple layers of protection (rate limiting, validation, monitoring)
✅ **Specific Numbers**: Exact thresholds (p99 < 200ms, 0.1% error rate)
✅ **Operational Thinking**: Runbooks, dashboards, on-call readiness
✅ **Failure Modes**: You’ve thought through what breaks and how to detect it
✅ **Pragmatic Trade-offs**: 5-minute dedup window, 1% sampling for logs

**You’ve now proven you can ship AND operate this system in production. Time to wrap up with trade-offs and final thoughts!**
