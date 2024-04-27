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

## Replication Protocols

- Replication protocols govern how data is replicated across multiple nodes or replicas in a distributed system.
- Replication protocols ensure that data updates made at one replica are propagated to other replicas to maintain consistency.
- These protocols are used to replicate data across multiple nodes in a distributed system to achieve fault tolerance, load balancing, and data locality.

### Primary-Backup Replication

### Chain Replication

### Multi-leader Replication

- used in distributed databases like Cassandra

## Consensus Protocols

- Consensus protocols are used to achieve agreement among distributed nodes on a single value or decision, even in the presence of faults or network partitions.
- Examples include the Raft consensus algorithm and the Paxos protocol.
- Consensus protocols are often employed in distributed databases and distributed file systems to ensure consistency and fault tolerance.

- While consensus algorithms like Paxos and Raft are often associated with leader election, they also play a crucial role in data synchronization by ensuring that all nodes in a distributed system agree on a common sequence of operations or a consistent state.

- Consensus algorithms are fundamental in distributed systems to achieve agreement among a group of nodes or processes on a certain value or decision, even in the presence of failures or network partitions.
- The goal is to ensure that all nodes in the system reach the same conclusion or state, despite potential failures or communication delays.

<br/>

- In distributed systems, nodes often need to agree on critical decisions such as electing a leader, committing a transaction, or maintaining consistency across replicas.
- Consensus algorithms provide a way for nodes to coordinate and agree on such decisions reliably.

<br/>

- These algorithms typically involve a set of nodes communicating with each other to propose and agree on a value.
- They must satisfy several properties to ensure correctness and reliability, including:
  - Agreement: All correct nodes must eventually agree on the same value.
  - Validity: The decided value must be proposed by some correct node.
  - Termination: All correct nodes must eventually terminate and decide on a value.
  - Integrity: Nodes cannot change their decision once they have agreed on a value.
  - Fault Tolerance: The algorithm should continue to operate correctly even if some nodes fail or exhibit arbitrary behavior.

<br/>

- Consensus algorithms are commonly used in distributed databases, distributed file systems, distributed locking mechanisms, and other distributed applications where maintaining consistency and coordination among multiple nodes is essential for the system's correctness and reliability.

<br/>

Failures a consensus algorithm might have to deal with:
- Fail-stop
- Network partition
- Fail-recover
- Byzantine failure

### Paxos

- https://martinfowler.com/articles/patterns-of-distributed-systems/paxos.html

### Chandra-Toueg

### Raft

### Practical Byzantine Fault Tolerance (PBFT)

### Leader Election Protocols

- Leader election protocols can be considered part of the broader category of coordination and synchronization protocols used in distributed systems.
- Leader election protocols are specifically designed to establish a single node as the leader among a group of nodes in a distributed system.
- The leader node typically assumes responsibilities such as coordinating distributed transactions, managing system-wide metadata, or making global decisions on behalf of the system.

<br/>

- Leader election protocols ensure that only one node acts as the leader at any given time, even in the presence of failures or network partitions.
- Examples of leader election protocols include the Bully algorithm, the Ring algorithm, and the Paxos-based approach used in systems like Apache ZooKeeper.

<br/>

- By electing a leader, distributed systems can achieve centralized coordination and decision-making while maintaining fault tolerance and resilience to failures. - Leader election protocols play a critical role in enabling distributed systems to operate efficiently and reliably in various scenarios, including consensus-based replication, distributed databases, and distributed computing platforms.

## Data Consistency Protocols

- These protocols ensure that data remains consistent across replicas or partitions in a distributed system.
- Examples include:
  - Eventual Consistency
  - Strong Consistency (e.g., Linearizability, Serializability)
  - Causal Consistency

## Conflict Resolution Protocols

- In systems where concurrent updates to data can occur, conflict resolution protocols help resolve conflicts that arise when conflicting updates are made to the same data item across different replicas.
- Conflict resolution protocols may employ techniques such as last-write-wins, version vectors, or application-specific conflict resolution logic.

- In distributed systems where multiple replicas can independently modify shared data, conflict resolution protocols are used to resolve conflicting updates and maintain data integrity.

### Last-Writer-Wins (LWW) Conflict Resolution

### Vector Clocks

## Quorum-based Protocols

- Quorum-based protocols define rules for coordinating read and write operations across distributed replicas based on the concept of a quorum, which is a subset of replicas required to reach agreement.
- Quorum-based protocols ensure that a sufficient number of replicas acknowledge read and write operations to maintain consistency and availability.

## Versioning Protocols

- Techniques such as versioning and Merkle trees are used to efficiently synchronize data and detect changes in distributed systems.
- They are commonly used in distributed version control systems (DVCS) like Git and in distributed storage systems.

- Versioning protocols track different versions of data items and manage the reconciliation of divergent versions across replicas.
- Techniques such as vector clocks, Lamport timestamps, or hybrid logical clocks are commonly used to manage versioning in distributed systems.
