# Split-brain Scenarios

- Split-brain scenarios occur in distributed systems when network partitions cause nodes to become divided into multiple disjoint groups, each believing it is the sole authority.
- In other words, the system perceives itself as having multiple independent "brains," hence the term "split-brain."

<br/>

- In a split-brain scenario, each partition operates independently and may make decisions or perform actions without coordination with nodes in other partitions. - This can lead to inconsistencies, conflicts, or divergent behavior within the system.
- For example:
  - In a database cluster, if a network partition occurs, each partition may elect its own leader, resulting in multiple leaders concurrently managing the same data. This can lead to data corruption or inconsistencies when the partitions later merge.
  - In a distributed computing environment, if a network partition separates nodes responsible for processing a shared task, each partition may continue processing independently. This can result in duplicated or inconsistent processing outcomes when the partitions reunite.
  - In a replicated system, if a partition divides the replicas of a data store, each partition may continue serving read and write requests independently. This can lead to conflicting updates or data inconsistencies when the partitions rejoin.

<br/>

- Split-brain scenarios are undesirable because they can compromise system correctness, consistency, and reliability.
- Distributed systems employ various mechanisms such as quorum-based algorithms, leader election protocols, and network partition detection to mitigate the risk of split-brain situations and ensure system integrity during network partitions.

# Data Synchronization Protocols

- Ensures data consistency, availability, fault tolerance, and reliability across nodes in distributed systems, especially in environments where data may be subject to concurrent updates, network partitions, or node failures.
- Facilitates the synchronization of data changes made at different locations within the distributed system.
- Types
  - Conflict resolution protocols
  - Consensus protocols
  - Data consistency protocols
  - Quorum-based protocols
  - Replication protocols
  - Versioning protocols
