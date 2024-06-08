# Table of Contents

1. [Motivation](#motivation)
2. [Pessimistic vs Optimistic](#pessimistic-vs-optimistic)
   - [Pessimistic Replication](#pessimistic-replication)
   - [Optimistic Replication / Lazy Replication](#optimistic-replication--lazy-replication)
3. [Active vs Passive](#active-vs-passive)
   - [Active-Active Replication / Active Replication](#active-active-replication--active-replication)
   - [Active-Passive Replication / Passive Replication](#active-passive-replication--passive-replication)
4. [Masters vs Workers](#masters-vs-workers)
   - [Primary-Backup Replication / Single-Master Replication](#primary-backup-replication--single-master-replication)
   - [Multi-Master Replication](#multi-master-replication)
5. [Chain Replication](#chain-replication)
6. [Single-Master Replication vs Multi-Master Replication vs Chain Topology](#single-master-replication-vs-multi-master-replication-vs-chain-topology)

# Motivation

- Used to achieve scalability, consistency, availability, fault tolerance, reliability, load balancing and data locality.
- Ensures that data remains accessible even in the presence of node failures, network partitions, or other types of system disruptions.
- The choice of replication protocol depends on the specific requirements of the system, including consistency guarantees, availability constraints, and performance considerations.

# Pessimistic vs Optimistic

- Pessimistic replication prioritizes strong consistency by ensuring immediate synchronization across all replicas, while optimistic replication prioritizes low latency and high throughput by allowing temporary divergence with eventual convergence.

## Pessimistic Replication

- Goal: Pessimistic replication aims to ensure that all replicas of the data are identical from the outset, as if there was only one copy of the data throughout the system.
- Process: When an update or modification to the data occurs, it is propagated to all replicas immediately and synchronously. This means that before acknowledging a write operation as successful, the system ensures that the update has been applied to all replicas and that they are consistent.
- Guarantee: This approach provides strong consistency guarantees, as all replicas are guaranteed to be identical at any point in time.
- Trade-offs: Pessimistic replication tends to be more resource-intensive and may introduce higher latency due to the need for synchronous updates across replicas. However, it ensures that the system maintains strong consistency, which is crucial for applications where data integrity is paramount.

## Optimistic Replication / Lazy Replication

- Goal: Optimistic replication, also known as lazy replication, allows replicas to diverge temporarily, with the expectation that they will converge again later.
- Process: When an update occurs, it is applied to a single replica, and then propagated asynchronously to other replicas in the background. Rather than waiting for confirmation from all replicas before acknowledging a write operation, the system acknowledges the write immediately to the client.
- Guarantee: While replicas may diverge temporarily, lazy replication guarantees eventual consistency. If the system does not receive any updates for a period of time or enters a quiescent state, replicas have the opportunity to converge again by reconciling their differences.
- Trade-offs: Lazy replication reduces latency and improves throughput by allowing the system to acknowledge writes quickly, without waiting for synchronization across all replicas. However, it may introduce temporary inconsistencies between replicas, which applications must handle gracefully.

# Active vs Passive

- Active-active replication distributes workload across multiple replicas for improved performance and fault tolerance but requires careful management of conflicts and consistency.
- Active-passive replication simplifies management and ensures data consistency but may underutilize resources and introduce latency during failover events.

## Active-Active Replication / Active Replication

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

## Active-Passive Replication / Passive Replication

- Goal: Active-passive replication involves designating one replica as the primary or active node, while the others remain passive or standby.
- Process: In an active-passive setup, the primary replica processes all incoming requests, while the passive replicas remain idle, only receiving updates from the primary replica.
- Benefits:
  - Simplicity: Active-passive replication is often simpler to implement and manage compared to active-active setups since there is a clear distinction between the active and passive replicas.
  - Consistency: Data consistency is easier to maintain since updates are applied sequentially on the primary replica and then propagated to passive replicas.
  - Failover: In the event of a failure or unavailability of the primary replica, one of the passive replicas can be promoted to the active role to ensure continuous operation.
- Challenges:
  - Resource Underutilization: Passive replicas in an active-passive setup may remain idle for extended periods, leading to underutilization of resources.
  - Potential for Increased Latency: Failover to a passive replica may introduce additional latency, especially if the replica needs to be initialized or updated before becoming active.
  - Scalability Limits: Scaling read operations may be limited by the capacity of the primary replica since passive replicas do not serve requests directly.

# Masters vs Workers

- Single-master replication simplifies data consistency by designating one master for write operations but may face scalability and availability limitations.
- Multi-master replication offers better scalability, availability, and lower latency by distributing write operations across multiple masters but requires robust conflict resolution mechanisms and introduces complexity in system design and management.

## Primary-Backup Replication / Single-Master Replication

- Overview
  - Goal: In single-master replication, one designated replica serves as the master or primary node, while others act as slaves or secondary nodes.
  - Process: Master handles writes, slaves replicate changes, and serve read requests.
  - Examples: Widely used in databases like PostgreSQL and MySQL.
- Benefits
  - Data Consistency: Sequential writes maintain consistency.
  - Simplicity: Clear master-slave setup.
  - Failover: Slave can take over if master fails.
- Challenges
  - Scalability: Write bottleneck at master.
  - Read Scalability: Slaves may lag in data freshness.
  - Single Point of Failure: Master failure impacts system.
- Techniques for Propagating Updates
  - Synchronous Replication
    - Ensures update acknowledgment from all replicas.
    - Increased durability and consistency.
    - Slower writes due to wait for acknowledgments.
  - Asynchronous Replication
    - Immediate response to client, then updates replicas.
    - Performance boost for writes.
    - Reduced consistency and durability risks.
- Advantages
  - Simple Implementation: Easy to understand.
  - Concurrent Operations: Serialized in master, supports transactions.
  - Read Scalability: Read-heavy workloads scalable with more replicas.
- Disadvantages
  - Write Scalability: Limited by master's capacity.
  - Performance-Durability-Consistency Trade-off: Adding followers can bottleneck.
  - Failover Process: Not instant, downtime risk.

<br/>

- Failover
  - Failover occurs when the master node fails, and a follower node takes over its role.
  - This process aims to maintain system operation despite node failures but may involve downtime and potential data loss.
  - Manual approach
    - The operator selects the new leader node and instructs all nodes accordingly.
    - This approach is safer but results in significant downtime.
  - Automated approach
    - Follower nodes detect the leader node's failure, often through periodic heartbeats (periodic messages indicating normal operation).
    - Follower nodes then attempt to elect a new leader node automatically.
    - This approach is faster but carries a higher risk of incorrect state due to potential confusion among nodes.

## Multi-Master Replication

- Goal: Multi-master replication, also known as symmetric or peer-to-peer replication, allows multiple replicas to function as independent masters, each capable of processing both read and write operations.
- Process: In a multi-master setup, all replicas are considered equal peers, and each can accept write operations from clients. Changes made to any master are propagated asynchronously to other masters, ensuring data consistency across the system.
- Characteristics:
  - Favors higher availability and performance over strict data consistency.
  - All replicas are equal and can accept write requests, responsible for propagating data modifications to the rest of the group.
  - No single master node serializes requests; write requests are concurrently handled by all nodes.
  - Nodes might disagree on the order of some requests, leading to conflicts.
  - Nodes need to resolve conflicts to maintain system operation.
- Example:
  - Applications prioritize availability and performance over data consistency or transactional semantics.
  - E-commerce shopping cart: Customers need continuous access to their cart, and performance is crucial. Consistency can be compromised as long as conflicts are reconciled during the checkout process.
- Benefits:
  - Scalability: Distributes write operations across multiple nodes, enabling better scalability and higher throughput compared to single-master setups.
  - High Availability: Multiple masters are available to process writes, allowing the system to continue operating even if one or more masters fail.
  - Low Latency: Clients can write to the nearest available master, reducing latency with multiple masters serving write operations.
- Challenges:
  - Conflict Resolution: Conflicts may arise when concurrent writes occur on different masters, requiring robust conflict resolution mechanisms.
  - Complexity: More complex to design, implement, and manage compared to single-master configurations due to conflict resolution and coordination among masters.
  - Data Consistency: Ensuring data consistency across multiple masters can be challenging, especially in scenarios with high update rates or network partitions.
  - Network Partition Handling:
    - Need to handle network partitions gracefully to ensure availability and consistency.
    - Techniques such as quorum-based replication or automatic failover mechanisms can maintain system operation in the presence of network partitions.

# Chain Replication

- Chain replication is a distributed replication protocol designed to provide fault tolerance and consistency in distributed systems.
- In chain replication, nodes are organized in a linear chain topology, where each node acts as a replica responsible for storing a copy of the data.
- Components of Chain Replication
  - Head Node: The head of the chain is the first node in the replication chain. Client requests are initially directed to the head node.
  - Tail Node: The tail of the chain is the last node in the replication chain. The tail node is responsible for acknowledging the completion of an operation and ensuring durability.
  - Intermediate Nodes: Between the head and tail nodes, there are one or more intermediate nodes, also known as internal nodes. These nodes serve as relay points for propagating updates from the head to the tail.
- Replication Process
  - The replication process in chain replication typically involves the following steps:
    - Write Operation: When a client sends a write operation to the head node, the head node appends the operation to its local log and forwards the operation to the next node in the chain.
    - Propagation: Each intermediate node in the chain receives the write operation, appends it to its local log, and forwards it to the next node in the chain until it reaches the tail node.
    - Execution: Once the tail node receives the write operation, it executes the operation, updates its local state, and acknowledges the completion of the operation back to the client.
    - Acknowledgment: The acknowledgment from the tail node is propagated backward through the chain, confirming the completion of the write operation.
- Benefits of Chain Replication
  - Fault Tolerance: Chain replication can tolerate node failures by replicating data across multiple nodes in the chain. If a node fails, the chain can continue to operate by bypassing the failed node and redirecting requests to the next node in the chain.
  - Consistency: Chain replication ensures strong consistency by enforcing a strict order of operations. All nodes in the chain apply operations in the same order, ensuring that replicas remain consistent with the primary copy of the data.
  - Durability: Write operations are durably stored on the tail node, ensuring that data remains available even in the event of node failures or network partitions.
- Limitations of Chain Replication
  - Performance Bottlenecks: Chain replication may introduce performance bottlenecks, especially if the tail node becomes a bottleneck due to increased write traffic.
  - Scalability: Adding new nodes to the chain may be challenging, as it requires coordination and synchronization among existing nodes.
- Overall, chain replication is a useful replication protocol for systems that require strong consistency and fault tolerance, particularly in scenarios where a linear ordering of operations is essential.

# Single-Master Replication vs Multi-Master Replication vs Chain Topology

- Topology:
  - Single-Master Replication: Has a centralized master node with replica nodes.
  - Multi-Master Replication: Employs a peer-to-peer or mesh network topology.
  - Chain Replication: Follows a linear chain topology.
- Operation Flow:
  - Single-Master Replication: All write operations are directed to the master node.
  - Multi-Master Replication: Write operations can be processed independently by any master node.
  - Chain Replication: Write operations flow sequentially through the chain.
- Consistency:
  - Single-Master Replication: Ensures consistency through coordination from the master node.
  - Multi-Master Replication: Often allows for eventual consistency with conflict resolution.
  - Chain Replication: Enforces strong consistency.
- Fault Tolerance:
  - Single-Master Replication: Relies on failover mechanisms to handle master node failures.
  - Multi-Master Replication: Offers fault tolerance by allowing multiple master nodes to handle write operations independently.
  - Chain Replication: Provides fault tolerance by distributing data across multiple nodes in the chain.
