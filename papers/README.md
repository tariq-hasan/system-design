# Resources for Advanced Components

This repository contains a collection of markdown files covering various advanced components.

- Distributed File Systems
  - [WIP] [Google File System](google_file_system.md)
  - [WIP] [Google Colossus File System](google_colossus_file_system.md)
  - [WIP] [Facebook Tectonic File System](facebook_tectonic_file_system.md)

<br/>

- Databases
  - [WIP] [Google Bigtable](google_bigtable.md)
  - [WIP] [Google Megastore](google_megastore.md)
  - [WIP] [Google Spanner](google_spanner.md)

<br/>

- Key-value Stores
  - [WIP] [Many-core Key-value Store](many-core_key-value_store.md)
  - [WIP] [Scaling Memcache](scaling_memcache.md)
  - [WIP] [SILT](silt.md)
  - [WIP] [Amazon DynamoDB](amazon_dynamodb.md)

<br/>

- Concurrency Management
  - [WIP] [Google Chubby Locking Service](google_chubby_locking_service.md)
  - [WIP] [ZooKeeper](zookeeper.md)

<br/>

- Big Data Processing: Batch to Stream Processing
  - [WIP] [MapReduce](mapreduce.md)
  - [WIP] [Spark](spark.md)
  - [WIP] [Kafka](kafka.md)




## 🧠 Advanced Components

### Distributed File Systems
* Facebook Tectonic File System
* Google Colossus File System
* Google File System
* Ceph
* HDFS (Hadoop Distributed File System)

### Databases
* Google Bigtable
* Google Megastore
* Google Spanner
* Time Series Databases (InfluxDB, Prometheus)
* Graph Databases (Neo4j, Amazon Neptune)
* Multi-model Databases (ArangoDB, FaunaDB)
* Document Databases (MongoDB, Couchbase)
* NewSQL Databases (CockroachDB, TiDB)

### Key-value Stores
* Amazon DynamoDB
* Many-core Key-value Store
* SILT
* Scaling Memcache
* Redis Cluster
* etcd

### Concurrency Management
* Google Chubby Locking Service
* ZooKeeper
* Distributed Semaphores
* Optimistic vs Pessimistic Locking
* Two-Phase Locking

### Big Data / Stream Processing
* Apache Flink
* Apache Beam
* Kafka
* MapReduce
* Spark
* Apache Storm
* Samza

### Additional Advanced Topics
* Blue-Green Deployment
* Canary Deployment Systems
* Chaos Engineering Systems
* CRDT-based Systems
* Data Lake / Lakehouse Architecture
* Distributed Graph Processing Systems
* Distributed Rate Limiting
* Distributed Transaction Coordinator / Saga Pattern
* Event Sourcing and CQRS
* Kubernetes Operators
* Multi-region Deployment Strategies
* Real-Time Analytics Engine (Druid/Pinot)
* Secure Secret Management (Vault, AWS KMS)
* Self-healing Systems
* Serverless Architecture
* Service Mesh (Istio, Linkerd)
* Vector Databases
* Zero-trust Network Architecture

### Data Processing Architectures
* Lambda Architecture
* Kappa Architecture
* Omega Architecture
* Data Mesh
* Data Fabric

### Resilience Patterns
* Bulkhead Pattern
* Fallback Pattern
* Timeout Pattern
* Sidecar Pattern
* Throttling Pattern
* Retry Pattern

### Consensus Algorithms
* Paxos
* Raft
* Byzantine Fault Tolerance
* Practical Byzantine Fault Tolerance (PBFT)
* Proof of Work/Stake (Blockchain-related)




















research papers
Foundational Distributed Systems Research
System Design Academic Foundations

research-oriented (seminal papers that established key concepts in distributed systems) 

## Research Papers for System Design Preparation

Below is a curated list of influential research papers that provide deep insights into the principles and techniques underlying modern distributed systems design.

| Paper | Key Contribution | Relevance to System Design |
|-------|------------------|----------------------------|
| [The Google File System](https://research.google/pubs/pub51/) | Distributed file system architecture | Storage systems, Fault tolerance |
| [MapReduce: Simplified Data Processing on Large Clusters](https://research.google/pubs/pub62/) | Parallel data processing paradigm | Batch processing, Analytics systems |
| [Dynamo: Amazon's Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) | Eventually consistent database design | NoSQL databases, Availability vs consistency |
| [Bigtable: A Distributed Storage System for Structured Data](https://research.google/pubs/pub27898/) | Distributed column-oriented database | Structured data storage, Scalability |
| [The Chubby Lock Service for Loosely-Coupled Distributed Systems](https://research.google/pubs/pub27897/) | Distributed consensus and coordination | Service discovery, Leader election |
| [Spanner: Google's Globally-Distributed Database](https://research.google/pubs/pub39966/) | Globally consistent database | Distributed transactions, Clock synchronization |
| [Kafka: a Distributed Messaging System](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/09/Kafka.pdf) | Distributed commit log | Messaging systems, Event streaming |
| [ZooKeeper: Wait-free coordination for Internet-scale systems](https://www.usenix.org/legacy/event/usenix10/tech/full_papers/Hunt.pdf) | Distributed coordination | Service discovery, Configuration management |
| [Consistent Hashing and Random Trees](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf) | Load balancing algorithm | Data partitioning, Caching systems |
| [Cassandra - A Decentralized Structured Storage System](https://www.cs.cornell.edu/projects/ladis2009/papers/lakshman-ladis2009.pdf) | P2P database architecture | NoSQL databases, Tunable consistency |
| [The Anatomy of a Large-Scale Hypertextual Web Search Engine](http://infolab.stanford.edu/pub/papers/google.pdf) | Search engine architecture (Google) | Web search, Ranking algorithms |
| [Raft: In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf) | Consensus algorithm | Distributed coordination, Fault tolerance |
| [Amazon Aurora: Design Considerations](https://pages.awscloud.com/rs/112-TZM-766/images/amazon-aurora-design-considerations-paper.pdf) | Cloud-native database architecture | Database systems, Cloud migration |
| [F1: A Distributed SQL Database That Scales](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/41344.pdf) | Scalable relational database | SQL databases, Global distribution |
| [Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing](https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf) | In-memory processing (Spark) | Big data processing, Fault tolerance |





















# Research Papers for System Design Interview Preparation

This section complements the "System Design Components" and "System Design Applications" lists by providing a structured approach to foundational research papers in distributed systems. These papers establish the theoretical underpinnings and real-world implementations that inform modern system design practices.

## Table of Contents

- [Core Distributed System Foundations](#core-distributed-system-foundations)
- [Storage and Database Systems](#storage-and-database-systems)
- [Processing and Computation](#processing-and-computation)
- [Coordination and Consensus](#coordination-and-consensus)
- [Modern System Design Papers](#modern-system-design-papers)
- [How to Approach Research Papers](#how-to-approach-research-papers)

## Core Distributed System Foundations

These papers establish fundamental principles that underlie virtually all distributed systems and are frequently referenced in system design interviews.

| Paper | Authors & Year | Key Contribution | Component Connection | Application Relevance | Interview Value |
|-------|---------------|------------------|----------------------|----------------------|----------------|
| [Fallacies of Distributed Computing](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing) | Peter Deutsch, et al. (1994-1997) | Eight fundamental assumptions that architects incorrectly make | Applies to all distributed components | Framework for evaluating any distributed application | Provides critical thinking framework for answering any system design question |
| [CAP Theorem](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/) | Eric Brewer (2000) | Impossibility of simultaneously guaranteeing consistency, availability, and partition tolerance | Database systems, caching strategies | Trade-off analysis for any distributed application | Essential theory for explaining design choices in distributed data systems |
| [Harvest, Yield, and Scalable Tolerant Systems](https://radlab.cs.berkeley.edu/people/fox/static/pubs/pdf/c18.pdf) | Fox, Brewer (1999) | Refinement of the CAP theorem with graceful degradation | Caching, service degradation strategies | How real applications handle partial failures | Shows sophistication in understanding failure modes and degradation |
| [The Byzantine Generals Problem](https://lamport.azurewebsites.net/pubs/byz.pdf) | Lamport, Shostak, Pease (1982) | Consensus in distributed systems with malicious actors | Consensus algorithms, fault tolerance | Blockchain, secure distributed systems | Demonstrates understanding of fundamental limits in distributed trust |
| [Time, Clocks, and the Ordering of Events](https://lamport.azurewebsites.net/pubs/time-clocks.pdf) | Leslie Lamport (1978) | Logical clock algorithm for ordering events in distributed systems | Time synchronization, distributed transactions | Event ordering in any distributed application | Shows depth on causality and time coordination challenges |

## Storage and Database Systems

These papers describe influential storage and database architectures that have shaped modern distributed storage patterns.

| Paper | Authors & Year | Key Contribution | Component Connection | Application Relevance | Interview Value |
|-------|---------------|------------------|----------------------|----------------------|----------------|
| [The Google File System](https://static.googleusercontent.com/media/research.google.com/en//archive/gfs-sosp2003.pdf) | Ghemawat, Gobioff, Leung (2003) | Distributed file system for large datasets | Blob storage, fault-tolerant file systems | Distributed storage applications, big data systems | Explains core patterns in modern cloud storage services |
| [Dynamo: Amazon's Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) | DeCandia et al. (2007) | Eventually consistent, highly available distributed database | NoSQL databases, consistent hashing | High-availability services, e-commerce systems | Shows trade-offs between consistency and availability |
| [Bigtable: A Distributed Storage System for Structured Data](https://static.googleusercontent.com/media/research.google.com/en//archive/bigtable-osdi06.pdf) | Chang et al. (2006) | Wide-column store for structured data | Structured data storage, key-value systems | Search engines, analytics platforms | Explains patterns for storing massive structured datasets |
| [Spanner: Google's Globally-Distributed Database](https://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf) | Corbett et al. (2012) | Globally consistent database with "TrueTime" | Distributed SQL databases, transactions | Global applications, financial systems | Shows how to achieve strong consistency at global scale |
| [Amazon Aurora: Design Considerations](https://www.amazon.science/publications/amazon-aurora-design-considerations-for-high-throughput-cloud-native-relational-databases) | Verbitski et al. (2017) | Cloud-native database architecture | Database systems, storage optimization | High-throughput applications, cloud migrations | Demonstrates cloud-native database patterns |

## Processing and Computation

These papers focus on distributed computation models that enable processing of large datasets and streaming data.

| Paper | Authors & Year | Key Contribution | Component Connection | Application Relevance | Interview Value |
|-------|---------------|------------------|----------------------|----------------------|----------------|
| [MapReduce: Simplified Data Processing on Large Clusters](https://static.googleusercontent.com/media/research.google.com/en//archive/mapreduce-osdi04.pdf) | Dean, Ghemawat (2004) | Parallel processing framework for large datasets | Batch processing systems, distributed computation | Data processing pipelines, analytics systems | Explains the batch processing programming model |
| [Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing](https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf) | Zaharia et al. (2012) | In-memory processing model (Apache Spark) | Distributed computation, fault tolerance | Real-time analytics, iterative algorithms | Shows evolution from batch to more interactive models |
| [Kafka: a Distributed Messaging System](https://notes.stephenholiday.com/Kafka.pdf) | Kreps, Narkhede, Rao (2011) | Log-based messaging system for high throughput | Message brokers, event streaming | Event-driven architectures, log processing | Demonstrates log-centered integration patterns |
| [MillWheel: Fault-Tolerant Stream Processing at Internet Scale](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/41378.pdf) | Akidau et al. (2013) | Streaming computation with exactly-once semantics | Stream processors, event handling | Real-time analytics, continuous processing | Explains streaming data processing guarantees |
| [The Dataflow Model](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43864.pdf) | Akidau et al. (2015) | Unified model for batch and streaming | Stream processing, event-time processing | Real-time and batch data pipelines | Shows unification of batch and streaming models |

## Coordination and Consensus

These papers address the challenges of coordination, service discovery, and consensus in distributed systems.

| Paper | Authors & Year | Key Contribution | Component Connection | Application Relevance | Interview Value |
|-------|---------------|------------------|----------------------|----------------------|----------------|
| [The Chubby Lock Service for Loosely-Coupled Distributed Systems](https://static.googleusercontent.com/media/research.google.com/en//archive/chubby-osdi06.pdf) | Burrows (2006) | Distributed lock service | Service discovery, leader election | Distributed coordination, metadata services | Explains patterns for distributed coordination |
| [ZooKeeper: Wait-free coordination for Internet-scale systems](https://www.usenix.org/legacy/event/usenix10/tech/full_papers/Hunt.pdf) | Hunt et al. (2010) | Distributed coordination service | Configuration management, leader election | Service discovery, distributed configuration | Shows practical implementation of coordination service |
| [Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf) | Leslie Lamport (2001) | Consensus algorithm explained simply | Distributed consensus, replication | High-reliability systems, distributed databases | Demonstrates fundamental consensus mechanisms |
| [Raft: In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf) | Ongaro, Ousterhout (2014) | More understandable consensus algorithm | Distributed consensus, log replication | Distributed state machines, configuration management | Explains modern approach to distributed consensus |
| [Consistent Hashing and Random Trees](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf) | Karger et al. (1997) | Algorithm for distributing load across dynamic set of servers | Load balancing, data partitioning | Distributed caches, distributed databases | Shows key technique for scalable distributed systems |

## Modern System Design Papers

These more recent papers reflect cutting-edge approaches to specific application domains and emerging patterns.

| Paper | Authors & Year | Key Contribution | Component Connection | Application Relevance | Interview Value |
|-------|---------------|------------------|----------------------|----------------------|----------------|
| [The Tail at Scale](https://research.google/pubs/pub40801/) | Dean, Barroso (2013) | Techniques for handling latency variability | Latency management, request hedging | Interactive services, real-time applications | Explains how to handle tail latency in distributed systems |
| [Cassandra: A Decentralized Structured Storage System](https://www.cs.cornell.edu/projects/ladis2009/papers/lakshman-ladis2009.pdf) | Lakshman, Malik (2009) | P2P database with tunable consistency | NoSQL systems, structured storage | High-write applications, time-series data | Shows architectural patterns for write-optimized databases |
| [Designing Data-Intensive Applications](https://dataintensive.net/) | Martin Kleppmann (2017) | Comprehensive overview of data system design | Multiple components across all tiers | End-to-end application architectures | Provides framework for discussing trade-offs in interviews |
| [Zanzibar: Google's Consistent, Global Authorization System](https://research.google/pubs/pub48190/) | Pang et al. (2019) | Large-scale permission management | Authorization systems, distributed consistency | Permission systems, access control | Demonstrates modern approach to authorization at scale |
| [The Anatomy of a Large-Scale Web Search Engine](http://infolab.stanford.edu/pub/papers/google.pdf) | Brin, Page (1998) | Search engine architecture (Google) | Indexing, ranking, query processing | Search systems, information retrieval | Shows architecture of complex information retrieval systems |

## How to Approach Research Papers for Interviews

When studying these papers for system design interviews, focus on:

1. **Core Principles**: Understand the fundamental problems each paper addresses
2. **Design Decisions**: Identify key architectural choices and their justifications
3. **Trade-offs**: Recognize the trade-offs made and alternatives considered
4. **Practical Application**: Consider how these concepts apply to modern applications
5. **Evolution**: Understand how newer papers build upon and refine concepts from older ones

Rather than memorizing implementation details, emphasize:

- **Problem Framing**: How the authors define and bound the problem
- **Architectural Patterns**: Reusable design approaches that solved specific challenges
- **Evaluation Methods**: How systems measure success against their design goals
- **Limitations**: Understanding where approaches break down or require modification

During interviews, referencing these papers demonstrates depth of knowledge, but focus on applying the concepts rather than simply citing them. Being able to explain why certain approaches would or wouldn't work for the system you're designing shows true understanding.

## Connection to Component and Application Lists

This research paper collection provides the theoretical foundation that supports both the component-oriented and application-oriented approaches:

1. **Components**: These papers explain why components are designed the way they are and the theoretical limits that constrain them
2. **Applications**: The papers demonstrate how components can be integrated to solve specific real-world problems at scale
3. **Design Principles**: They establish the fundamental principles that guide architectural decisions across all distributed systems

By understanding these papers, you gain insight into not just what the best practices are, but why they exist and when they might change in the future.
