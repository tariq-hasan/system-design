# System Design Components

This repository contains detailed explanations of the most common components used in system design interviews. Components are organized by frequency of appearance in interviews and their fundamental importance to distributed systems.

## Table of Contents

- [Tier 1: Fundamental Components](#tier-1-fundamental-components)
- [Tier 2: Common Components](#tier-2-common-components)
- [Tier 3: Specialized Components](#tier-3-specialized-components)
- [Tier 4: Advanced Topics](#tier-4-advanced-topics)

## Tier 1: Fundamental Components

These components appear in almost every system design interview and form the backbone of most distributed systems.

| Component | Description | Use Cases | Key Considerations |
|-----------|-------------|-----------|-------------------|
| [Blob Store](./blob-store) | Storage service for large unstructured data | Media storage, backups, logs | Durability, availability, cost |
| [Consistent Hashing](./consistent-hashing) | Technique for distributing load across servers | Load balancing, data partitioning | Minimal reshuffling when nodes change |
| [Content Delivery Network](./cdn) | Distributed server network that delivers content | Static assets, media delivery | Edge caching, geographical distribution |
| [Database](./database) | Organized collection of structured data | Data persistence, querying, transactions | SQL vs NoSQL, ACID properties |
| [Distributed Cache](./distributed-cache) | In-memory data store for fast retrieval | Faster data access, session storage | Eviction policies, cache invalidation |
| [Load Balancer](./load-balancer) | Distributes network traffic across servers | High availability, horizontal scaling | Algorithm selection, health checks |
| [Pub-Sub](./pub-sub) | Messaging pattern for decoupling services | Event broadcasting, async workflows | Message ordering, delivery guarantees |
| [Rate Limiter](./rate-limiter) | Controls request rate to an API/service | API protection, resource allocation | Algorithms, distributed coordination |
| [Read Replicas](./read-replicas) | Database copies for read scalability | Read-heavy workloads, analytics | Consistency guarantees, replication lag |
| [Service Discovery](./service-discovery) | Mechanism for locating services dynamically | Microservices communication | Registration, health monitoring |
| [Sharded Counters](./sharded-counters) | Technique for high-throughput counting | View counts, analytics | Hot spots mitigation, consistency |

## Tier 2: Common Components

These components appear frequently, especially when specific use cases are involved (search, messaging, observability).

| Component | Description | Use Cases | Key Considerations |
|-----------|-------------|-----------|-------------------|
| [API Gateway](./api-gateway) | Entry point for API requests | Microservices, client request routing | Authentication, rate limiting |
| [Circuit Breaker Pattern](./circuit-breaker) | Prevents cascading failures | Fault tolerance, resilience | Failure thresholds, fallback mechanisms |
| [Data Partitioning Strategies](./data-partitioning) | Techniques for splitting data across systems | Scalability, performance | Partition schemes, data skew |
| [Distributed Logging](./distributed-logging) | Centralized log collection and analysis | Debugging, monitoring, auditing | Log aggregation, search capabilities |
| [Distributed Messaging Queue](./messaging-queue) | Asynchronous service communication | Workload decoupling, peak handling | Delivery guarantees, ordering |
| [Distributed Search](./distributed-search) | Text and data search across nodes | Full-text search, faceted search | Indexing, ranking, sharding |
| [Key-Value Store](./key-value-store) | Simple data storage using key-value pairs | Caching, configuration, session data | Performance, consistency models |
| [Observability Tools](./observability) | Monitoring and tracing systems | Performance insights, troubleshooting | Instrumentation, sampling |
| [Proxy](./proxy) | Intermediary for client-server communication | Security, caching, routing | Forward vs reverse, performance impact |
| [Retry Mechanisms](./retry-mechanisms) | Automatic retry of failed operations | Network instability, transient failures | Backoff strategies, idempotency |
| [WebSockets](./websockets) | Protocol for bidirectional communication | Real-time applications, chat systems | Connection maintenance, fallbacks |

## Tier 3: Specialized Components

Important components that are more specialized or appear less frequently in interviews.

| Component | Description | Use Cases | Key Considerations |
|-----------|-------------|-----------|-------------------|
| [Configuration Service](./configuration-service) | Centralized management of settings | Feature flags, environment variables | Versioning, dynamic updates |
| [Distributed Monitoring](./distributed-monitoring) | System health and performance tracking | Alerting, performance analysis | Metric collection, visualization |
| [Health Check Service](./health-check) | Verifies service operational status | Service availability, load balancing | Check frequency, dependency handling |
| [Idempotency Keys](./idempotency) | Enables safe retry operations | Payment processing, API submissions | Key generation, storage requirements |
| [Metrics Aggregator](./metrics-aggregator) | Collects and summarizes system metrics | Performance monitoring, capacity planning | Data resolution, retention policies |
| [Server-side Error Monitoring](./server-error-monitoring) | Tracks and analyzes server errors | Reliability improvements, debugging | Error classification, alerting |
| [Server-Sent Events](./server-sent-events) | One-way server-to-client messaging | Real-time updates, notifications | Connection handling, scaling |
| [Write-ahead Logs](./write-ahead-logs) | Durability and recovery mechanism | Database recovery, transaction processing | Performance impact, cleanup strategies |

## Tier 4: Advanced Topics

Advanced components that are mentioned less frequently but are important for specific system requirements.

| Component | Description | Use Cases | Key Considerations |
|-----------|-------------|-----------|-------------------|
| [Client-side Error Tracking](./client-error-tracking) | Monitors errors occurring in clients | UX improvement, frontend debugging | Privacy concerns, sampling |
| [Distributed Task Scheduler](./task-scheduler) | Schedules and executes future tasks | Batch processing, periodic tasks | Reliability, coordination |
| [Domain Name System](./dns) | Maps domains to IP addresses | Service discovery, load balancing | TTL settings, propagation delays |
| [Heartbeat Service](./heartbeat) | Regular signals to indicate aliveness | Cluster membership, failover detection | Frequency, false positive handling |
| [Sequencer](./sequencer) | Generates unique sequential IDs | Ordering guarantees, ID generation | Throughput, fault tolerance |
| [Time Synchronization](./time-sync) | Coordinates time across distributed nodes | Event ordering, distributed transactions | Clock drift, synchronization protocols |
| [Top K Problem Solutions](./top-k) | Efficiently finding most frequent items | Analytics, recommendations | Memory efficiency, approximation |
