# Legend

I’m labeling each design as:
* 🟥 Must-know (Very common) — core patterns you will be asked.
* 🟧 Occasionally Asked (Moderately common) — appears at senior interviews or domain-aligned teams.
* 🟨 Rare / Specialized (Low frequency) — shows up mostly in infra, data, or niche roles.

# Foundational Topics

Tested indirectly, not direct prompts.

## Data Storage & Management
* Database fundamentals (SQL vs NoSQL) — 🟥
* Database indexing (B-trees, LSM trees) — 🟥
* Database transactions & isolation levels (ACID, read committed, serializable) - 🟥
* Normalization vs denormalization - 🟥
* Read Replicas — 🟥
* Data Partitioning / Sharding strategies — 🟥
* Consistent Hashing — 🟥
* Write-Ahead Logs (WAL) — 🟧

## Distributed Systems Concepts
* CAP Theorem — 🟥
* Consistency Models (strong, eventual, causal) — 🟥
* Replication strategies (leader-follower, multi-leader, leaderless) — 🟥
* Consensus algorithms (Raft, Paxos - high level) — 🟥
* Distributed transactions (2PC, Saga pattern) — 🟧
* Time synchronization & clocks (logical clocks, vector clocks) — 🟧
* Sequencer / ID generation — 🟥
* Deep dive on Paxos — 🟨
* Clock synchronization algorithms (e.g., NTP, GPS-based ordering) — 🟨
* Gossip protocols - 🟧
* Merkle trees (for data integrity/sync) - 🟨

Important for distributed coordination, leader election, and ordering problems.

## Caching & Performance
* Caching strategies (LRU, LFU, write-through, write-back, cache-aside) — 🟥
* CDN (conceptually, for global scaling) — 🟥
* Blob Storage (S3-like systems) — 🟧
* Bloom filters (comes up in cache/deduplication discussions) — 🟧
* CDN internals (cache invalidation, edge propagation) — 🟨
* Hot partitions / hot keys problem - 🟧

## Networking & Communication
* Load Balancer (L4 vs L7) — 🟥
* Reverse Proxy — 🟥
* DNS — 🟥
* WebSockets vs Server-Sent Events vs Long Polling — 🟥
* API Gateway patterns — 🟥
* Service Discovery — 🟥

Must know how global content is served efficiently and how real-time connections scale.

## Messaging & Events
* Pub-Sub pattern — 🟥
* Message Queues — 🟥
* Message delivery semantics (at-most-once, at-least-once, exactly-once) — 🟥
* Event sourcing — 🟧

Must know Kafka-style event logs, delivery semantics (at-least-once, exactly-once), and message ordering.

## Reliability & Observability
* Retry mechanisms (exponential backoff) — 🟥
* Circuit Breaker pattern — 🟥
* Rate limiting algorithms (token bucket, leaky bucket, sliding window) — 🟥
* Health checks & Heartbeats — 🟥
* Timeouts and deadlines — 🟥
* Back-pressure handling — 🟧
* Idempotency & Idempotency keys — 🟥
* Backpressure mechanisms (credit-based flow control, reactive streams) — 🟨

Required for distributed request handling and exactly-once semantics.
You’ll be expected to reason about scaling, fault isolation, and traffic shaping.

## Monitoring & Debugging
* Distributed Logging — 🟧
* Distributed Tracing — 🟧
* Metrics collection — 🟧
* Server-side error monitoring — 🟨
* Client-side error tracking — 🟨
* Observability tools (traces, metrics, logs) — 🟧
* Detailed metrics pipeline internals — 🟨

Needed for designing highly available, observable distributed systems.

## Scalability Patterns
* Horizontal vs Vertical Scaling — 🟥
* Sharded Counters — 🟧
* Top K problem solutions (heavy hitters, frequent items) — 🟧
* CQRS (Command Query Responsibility Segregation) — 🟨

## Security & Identity
* Authentication vs Authorization — 🟥
* Identity & Access Control (IAM) — 🟥
* OAuth, JWT, SSO (high-level) — 🟧

Discuss OAuth2, JWT, SSO, and least-privilege principles.

## Data Serialization
* Protocol Buffers, JSON, Avro, MessagePack — 🟧

# System Design Interview Prompts

## Tier 1: Core Scalable Systems — Must-Know for All Candidates
1. 🟥 Design a URL Shortener (e.g. TinyURL, bit.ly, etc.) → Tests storage, hashing, ID generation, database scaling, read/write tradeoffs.
2. 🟥 Design a Rate Limiter / Throttling System → Tests token bucket vs. leaky bucket, cache, quotas, distributed coordination.
3. 🟥 Design a News Feed System (Facebook, Instagram, Twitter) → Tests fanout-on-write vs. fanout-on-read, caching, ranking.
4. 🟥 Design a Chat Messaging System (WhatsApp, Slack, Discord) → Tests pub/sub, message delivery, delivery semantics, storage, consistency, scaling.
5. 🟥 Design a Notification System (push/email/SMS) → Tests message queues, pub/sub, retries, fanout.
6. 🟥 Design a File Storage System (Dropbox, Google Drive) → Tests chunking, deduplication, metadata storage, consistency.
7. 🟧 Design a Search Autocomplete / Typeahead System → Tests trie, caching, ranking, real-time updates.
8. 🟧 Design a Ride-Sharing Platform (Uber, Lyft) → Tests matching, location indexing, state tracking.
9. 🟧 Design a Audio/Video Streaming Service (YouTube, Netflix) → Tests CDN, transcoding, caching, scaling.
10. 🟨 Design a Web Crawler (Google crawler) → Tests distributed task coordination, politeness, deduplication, storage.

Mastering 1–6 is non-negotiable for all big tech interviews.
7–9 appear in specialized domains (maps, media, real-time).

## Tier 2: Real-Time & Collaboration — Strongly Favored in Senior Roles
11. 🟥 Design a Payment or Wallet System (Stripe, PayPal, Venmo) → Tests ACID guarantees, idempotency, consistency, transaction safety.
12. 🟧 Design a Live Streaming / Commenting System (Twitch) → Tests real-time pub/sub, fanout, latency, scalability, load balancing.
13. 🟧 Design a Real-Time Collaboration Tool (Google Docs) → Tests operational transforms or CRDTs, synchronization
14. 🟧 Design a Location-Based Service (Yelp, Google Maps) → Tests geo-partitioning, caching, location updates.
15. 🟨 Design a Video Conferencing System (Zoom, Meet) → Tests WebRTC, SFU/Mesh architecture, signaling servers, latency.

The Payment System is now a staple at Amazon, Stripe, and fintech-like teams.
Docs-style collaboration is seen at Google, Notion, and Dropbox interviews.

## Tier 3: Data & Search Systems — High-Value for Infra and Backend Roles
16. 🟥 Design a Search System (ElasticSearch, Google Search) → Tests indexing, sharding, ranking, distributed query execution.
17. 🟧 Design a Recommendation System (Netflix, Amazon) → Tests ML serving, feature stores, ranking pipelines.
18. 🟧 Design an Analytics Dashboard (Mixpanel, Google Analytics) → Tests rollups, aggregates, query latency.
19. 🟧 Design a Logging & Monitoring Platform (Datadog, Splunk) → Tests ingestion, indexing, search, retention policies.
20. 🟧 Design a Real-Time Analytics Pipeline → Tests stream vs batch processing, Kafka, Flink, aggregators.

Frequently appear at companies like Google Cloud, Amazon, Snowflake, LinkedIn.
Strong differentiator for data infrastructure or search backend teams.

## Tier 4: E-Commerce & Booking — Occasionally Asked (Amazon, Uber, Airbnb)
21. 🟥 Design an E-Commerce Platform (Amazon) → Tests microservices, ordering, inventory, payments.
22. 🟧 Design a Hotel / Flight Booking System (Airbnb, Booking.com) → Tests concurrency, availability, locking.
23. 🟧 Design a Ticket Booking System (Ticketmaster, Eventbrite) → Tests overbooking prevention, queueing
24. 🟧 Design a Food Delivery System (DoorDash, UberEats) → Tests order dispatch, location, load balancing

## Tier 5: Social & Content — Very Common at Meta / Reddit / Twitter
25. 🟥 Design a Social Media Platform (Twitter, Instagram, Reddit) → Tests feeds, caching, sharding, fanout, moderation.
26. 🟧 Design a Short Video Platform (TikTok, Instagram Stories) → Tests CDN, video ingestion, recommendation
27. 🟧 Design a Professional Network (Linked) → Tests feed ranking, connections graph
28. 🟨 Design a Content Moderation System → Tests ML pipelines, workflow orchestration, audit logging.

## Tier 6: Gaming & Competition — Low Frequency / Specialized
29. 🟧 Design a Leaderboard → Tests ranking, sharding, counters, high write throughput.
30. 🟨 Design an Online Code Execution / Judge System (LeetCode) → Tests isolation, job scheduling, result aggregation.
31. 🟨 Design a Multiplayer Game Backend → Tests state sync, latency, consistency

## Tier 7: Infrastructure & Advanced Systems — High Value for Senior-Level
32. 🟥 Design an API Gateway → Tests routing, authentication, rate limiting
33. 🟥 Design a Distributed Key-Value Store (like Redis) → Tests sharding, replication, leader election, consistency.
34. 🟥 Design a Distributed Cache → Tests cache invalidation, sharding, consistency, consistent hashing.
35. 🟥 Design an Event Streaming Platform (Kafka, Pub/Sub) → Tests log compaction, partitioning, offsets, delivery semantics.
36. 🟥 Design a Feature Flag / Experimentation Platform → Tests config rollout, A/B testing, metrics.
37. 🟧 Design a Stock Exchange / Trading System → Tests order matching, consistency, latency, fairness.
38. 🟧 Design a Distributed Lock Service (Chubby, ZooKeeper) → Tests consensus, leader election
39. 🟧 Design a Job Scheduler → Tests cron, retries, distributed queue
40. 🟧 Design a Distributed Task Queue → Tests idempotency, workers, reliability
41. 🟧 Design a Metrics / Logging System (Prometheus, Datadog, Grafana) → Tests distributed collection, aggregation, storage, querying, partitioning, time-series storage, compression, retention.
42. 🟨 Design a CI/CD Pipeline → Tests orchestration, queuing, scaling.

## Platform Infrastructure — Rare, but impresses Infra Interviewers
43. 🟧 Design a Configuration Service → Tests dynamic config updates, rollout safety
44. 🟧 Design a Service Mesh → Tests sidecars, traffic shaping, observability
45. 🟧 Design a Webhook System → Tests retry logic, deduplication, delivery guarantees
46. 🟨 Design a Dark Launch System → Tests shadow traffic, rollback safety

## Search & Content Infra — Google / Meta Infra-Level Depth
47. 🟧 Design a Content Delivery Network (CDN) → Tests edge caching, DNS, invalidation
48. 🟧 Design a Unified Search Service → Tests federation, ranking, deduplication

## Data-Intensive & Domain-Specific — Optional Depth
49. 🟧 Design a User Segmentation Service → Tests cohort storage, filtering, targeting
50. 🟨 Design an Ad Serving System → Tests fairness, low-latency ranking
51. 🟨 Design an Auction System → Tests bidding, fairness, consistency
