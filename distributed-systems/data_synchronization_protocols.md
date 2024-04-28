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

- Used to achieve scalability, consistency, availability, fault tolerance, reliability, load balancing and data locality.
- Ensures that data remains accessible even in the presence of node failures, network partitions, or other types of system disruptions.
- The choice of replication protocol depends on the specific requirements of the system, including consistency guarantees, availability constraints, and performance considerations.

### Pessimistic vs Optimistic

- Pessimistic replication prioritizes strong consistency by ensuring immediate synchronization across all replicas, while optimistic replication prioritizes low latency and high throughput by allowing temporary divergence with eventual convergence.

#### Pessimistic Replication

- Goal: Pessimistic replication aims to ensure that all replicas of the data are identical from the outset, as if there was only one copy of the data throughout the system.
- Process: When an update or modification to the data occurs, it is propagated to all replicas immediately and synchronously. This means that before acknowledging a write operation as successful, the system ensures that the update has been applied to all replicas and that they are consistent.
- Guarantee: This approach provides strong consistency guarantees, as all replicas are guaranteed to be identical at any point in time.
- Trade-offs: Pessimistic replication tends to be more resource-intensive and may introduce higher latency due to the need for synchronous updates across replicas. However, it ensures that the system maintains strong consistency, which is crucial for applications where data integrity is paramount.

#### Optimistic Replication / Lazy Replication

- Goal: Optimistic replication, also known as lazy replication, allows replicas to diverge temporarily, with the expectation that they will converge again later.
- Process: When an update occurs, it is applied to a single replica, and then propagated asynchronously to other replicas in the background. Rather than waiting for confirmation from all replicas before acknowledging a write operation, the system acknowledges the write immediately to the client.
- Guarantee: While replicas may diverge temporarily, lazy replication guarantees eventual consistency. If the system does not receive any updates for a period of time or enters a quiescent state, replicas have the opportunity to converge again by reconciling their differences.
- Trade-offs: Lazy replication reduces latency and improves throughput by allowing the system to acknowledge writes quickly, without waiting for synchronization across all replicas. However, it may introduce temporary inconsistencies between replicas, which applications must handle gracefully.

### Active vs Passive

- Active-active replication distributes workload across multiple replicas for improved performance and fault tolerance but requires careful management of conflicts and consistency.
- Active-passive replication simplifies management and ensures data consistency but may underutilize resources and introduce latency during failover events.

#### Active-Active Replication / Active Replication

- Goal: Active-active replication, also known as symmetric or bi-directional replication, involves multiple replicas being actively involved in processing requests simultaneously.
- Process: In an active-active setup, all replicas are capable of serving read and write requests concurrently. Each replica independently processes incoming requests and updates its local state accordingly.
- Benefits:
  - Load Distribution: Active-active replication distributes the workload across multiple replicas, enabling better scalability and improved performance under high loads.
  - Fault Tolerance: If one replica fails or becomes unavailable, the system can continue to operate seamlessly using other available replicas.
  - Low Latency: With multiple replicas serving requests, users may experience lower latency since requests can be processed by the nearest available replica.
- Challenges:
  - Conflict Resolution: Handling conflicts that arise when concurrent updates occur on different replicas can be complex and requires robust conflict resolution mechanisms.
  - Data Consistency: Ensuring consistency across all replicas can be challenging, especially in scenarios with high update rates or network partitions.
  - Complexity: Implementing and managing an active-active replication setup can be more complex compared to active-passive configurations.

#### Active-Passive Replication / Passive Replication

- Goal: Active-passive replication, also known as primary-backup or master-slave replication, involves designating one replica as the primary or active node, while the others remain passive or standby.
- Process: In an active-passive setup, the primary replica processes all incoming requests, while the passive replicas remain idle, only receiving updates from the primary replica.
- Benefits:
  - Simplicity: Active-passive replication is often simpler to implement and manage compared to active-active setups since there is a clear distinction between the active and passive replicas.
  - Consistency: Data consistency is easier to maintain since updates are applied sequentially on the primary replica and then propagated to passive replicas.
  - Failover: In the event of a failure or unavailability of the primary replica, one of the passive replicas can be promoted to the active role to ensure continuous operation.
- Challenges:
  - Resource Underutilization: Passive replicas in an active-passive setup may remain idle for extended periods, leading to underutilization of resources.
  - Potential for Increased Latency: Failover to a passive replica may introduce additional latency, especially if the replica needs to be initialized or updated before becoming active.
  - Scalability Limits: Scaling read operations may be limited by the capacity of the primary replica since passive replicas do not serve requests directly.

### Master vs Workers

#### Primary-Backup Replication

- One replica is designated as the primary replica, while the others are backup replicas.
- All write operations are directed to the primary replica, which then forwards the updates to the backup replicas for synchronization.
- If the primary replica fails, one of the backup replicas is promoted to the new primary, ensuring continuous availability.

#### Multi-Primary Replication

- Allows multiple replicas to accept write operations independently.
- Each replica can act as a primary replica, handling write requests from clients.
- Requires coordination mechanisms, such as distributed concurrency control or conflict resolution techniques, to ensure data consistency across replicas.

- used in distributed databases like Cassandra

### Chain Replication

- Provides fault tolerance and consistency in distributed systems

- In chain replication, nodes are organized in a linear chain topology, where each node acts as a replica responsible for storing a copy of the data.

- The chain consists of three main components:
  - Head: The head of the chain is the first node in the replication chain. Client requests are initially directed to the head node.
  - Tail: The tail of the chain is the last node in the replication chain. The tail node is responsible for acknowledging the completion of an operation and ensuring durability.
  - Intermediate Nodes: Between the head and tail nodes, there are one or more intermediate nodes, also known as internal nodes. These nodes serve as relay points for propagating updates from the head to the tail.

- The replication process in chain replication typically involves the following steps:
  - Write Operation: When a client sends a write operation to the head node, the head node appends the operation to its local log and forwards the operation to the next node in the chain.
  - Propagation: Each intermediate node in the chain receives the write operation, appends it to its local log, and forwards it to the next node in the chain until it reaches the tail node.
  - Execution: Once the tail node receives the write operation, it executes the operation, updates its local state, and acknowledges the completion of the operation back to the client.
  - Acknowledgment: The acknowledgment from the tail node is propagated backward through the chain, confirming the completion of the write operation.

- Chain replication offers several benefits:
  - Fault Tolerance: Chain replication can tolerate node failures by replicating data across multiple nodes in the chain. If a node fails, the chain can continue to operate by bypassing the failed node and redirecting requests to the next node in the chain.
  - Consistency: Chain replication ensures strong consistency by enforcing a strict order of operations. All nodes in the chain apply operations in the same order, ensuring that replicas remain consistent with the primary copy of the data.
  - Durability: Write operations are durably stored on the tail node, ensuring that data remains available even in the event of node failures or network partitions.

- However, chain replication also has some limitations, including:
  - Performance Bottlenecks: Chain replication may introduce performance bottlenecks, especially if the tail node becomes a bottleneck due to increased write traffic.
  - Scalability: Adding new nodes to the chain may be challenging, as it requires coordination and synchronization among existing nodes.

- Overall, chain replication is a useful replication protocol for systems that require strong consistency and fault tolerance, particularly in scenarios where a linear ordering of operations is essential.

### Conflict-Free Replicated Data Types (CRDTs)

- CRDTs are data structures designed to support concurrent updates across replicas without the need for synchronization or coordination.
- CRDTs ensure that updates commute and can be merged deterministically, allowing replicas to converge to a consistent state without conflicts.
- This approach is particularly useful for highly distributed systems where strong consistency is impractical.

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

<br/>

- Consensus algorithms, such as Paxos and Raft, are often used to achieve replication and consistency in distributed systems.
- These algorithms ensure that all replicas agree on the order of operations or transactions, even in the presence of failures or network partitions.
- Consensus-based replication provides strong consistency guarantees but may introduce additional latency due to the need for coordination among replicas.

<br/>

Consensus protocols can be considered a form of both replication and data synchronization, depending on how they are used in a distributed system.
- Replication: In some cases, consensus protocols are used to ensure that multiple replicas of the same data are consistent with each other. For example, in distributed databases or replicated state machines, consensus protocols like Paxos or Raft are employed to replicate data across multiple nodes while ensuring that all replicas maintain the same state. This replication ensures fault tolerance and high availability by allowing the system to continue operating even if some nodes fail.
- Data Synchronization: Consensus protocols are also used to synchronize the state of distributed systems by agreeing on a common order of operations or events. In this context, consensus ensures that all nodes in the system apply operations in the same order, leading to consistent state across the distributed system. This synchronization is crucial for maintaining consistency and correctness in distributed systems where multiple nodes may concurrently process requests or updates.
In summary, consensus protocols serve dual purposes: they facilitate replication by ensuring that replicas maintain consistency, and they enable data synchronization by agreeing on a common order of operations or events. Depending on the specific application and requirements of the distributed system, consensus protocols may be utilized primarily for replication, data synchronization, or both.

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

### Eventual Consistency

- Eventual consistency is a weaker consistency model that allows replicas to diverge temporarily but guarantees that they will eventually converge to the same state.
- In eventual consistency replication, updates are propagated asynchronously to replicas, and conflicts are resolved using reconciliation mechanisms.
- While eventual consistency offers high availability and scalability, it may lead to temporary inconsistencies in data.

## Conflict Resolution Protocols

- In systems where concurrent updates to data can occur, conflict resolution protocols help resolve conflicts that arise when conflicting updates are made to the same data item across different replicas.
- Conflict resolution protocols may employ techniques such as last-write-wins, version vectors, or application-specific conflict resolution logic.

- In distributed systems where multiple replicas can independently modify shared data, conflict resolution protocols are used to resolve conflicting updates and maintain data integrity.

### Last-Writer-Wins (LWW) Conflict Resolution

### Vector Clocks

## Quorum-based Protocols

- Quorum-based protocols define rules for coordinating read and write operations across distributed replicas based on the concept of a quorum, which is a subset of replicas required to reach agreement.
- Quorum-based protocols ensure that a sufficient number of replicas acknowledge read and write operations to maintain consistency and availability.

<br/>

- Quorum-based replication relies on a quorum, which is a subset of replicas required to reach an agreement for read and write operations.
- Quorums ensure that a majority of replicas must acknowledge an operation to guarantee consistency and durability.
- This approach allows systems to tolerate failures and network partitions while maintaining strong consistency.

<br/>

Quorum-based protocols can be considered a form of both replication and data synchronization, similar to consensus protocols.
- Replication: Quorum-based protocols are often used to replicate data across multiple nodes in a distributed system while ensuring consistency and fault tolerance. By requiring a minimum number of nodes to agree on an operation or update before it is considered successful, quorum-based protocols ensure that replicas maintain consistency even in the presence of failures or network partitions. Each replica maintains a copy of the data, and updates are replicated to a subset of nodes known as the quorum. This replication mechanism enhances fault tolerance and availability by allowing the system to continue functioning even if some nodes fail.
- Data Synchronization: Quorum-based protocols also facilitate data synchronization by defining rules for achieving consensus among a subset of nodes. By requiring a quorum of nodes to agree on the order of operations or updates, quorum-based protocols ensure that all replicas apply changes in a consistent manner, leading to synchronized state across the distributed system. This synchronization ensures that all nodes observe the same sequence of operations, maintaining data consistency and correctness.
In summary, quorum-based protocols serve dual purposes: they support replication by ensuring that replicas maintain consistency, and they enable data synchronization by defining rules for achieving consensus among a subset of nodes. Depending on the specific application and requirements of the distributed system, quorum-based protocols may be utilized primarily for replication, data synchronization, or both.

## Versioning Protocols

- Techniques such as versioning and Merkle trees are used to efficiently synchronize data and detect changes in distributed systems.
- They are commonly used in distributed version control systems (DVCS) like Git and in distributed storage systems.

- Versioning protocols track different versions of data items and manage the reconciliation of divergent versions across replicas.
- Techniques such as vector clocks, Lamport timestamps, or hybrid logical clocks are commonly used to manage versioning in distributed systems.
