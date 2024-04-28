# Replication Protocols

- Used to achieve scalability, consistency, availability, fault tolerance, reliability, load balancing and data locality.
- Ensures that data remains accessible even in the presence of node failures, network partitions, or other types of system disruptions.
- The choice of replication protocol depends on the specific requirements of the system, including consistency guarantees, availability constraints, and performance considerations.

## Pessimistic vs Optimistic

- Pessimistic replication prioritizes strong consistency by ensuring immediate synchronization across all replicas, while optimistic replication prioritizes low latency and high throughput by allowing temporary divergence with eventual convergence.

### Pessimistic Replication

- Goal: Pessimistic replication aims to ensure that all replicas of the data are identical from the outset, as if there was only one copy of the data throughout the system.
- Process: When an update or modification to the data occurs, it is propagated to all replicas immediately and synchronously. This means that before acknowledging a write operation as successful, the system ensures that the update has been applied to all replicas and that they are consistent.
- Guarantee: This approach provides strong consistency guarantees, as all replicas are guaranteed to be identical at any point in time.
- Trade-offs: Pessimistic replication tends to be more resource-intensive and may introduce higher latency due to the need for synchronous updates across replicas. However, it ensures that the system maintains strong consistency, which is crucial for applications where data integrity is paramount.

### Optimistic Replication / Lazy Replication

- Goal: Optimistic replication, also known as lazy replication, allows replicas to diverge temporarily, with the expectation that they will converge again later.
- Process: When an update occurs, it is applied to a single replica, and then propagated asynchronously to other replicas in the background. Rather than waiting for confirmation from all replicas before acknowledging a write operation, the system acknowledges the write immediately to the client.
- Guarantee: While replicas may diverge temporarily, lazy replication guarantees eventual consistency. If the system does not receive any updates for a period of time or enters a quiescent state, replicas have the opportunity to converge again by reconciling their differences.
- Trade-offs: Lazy replication reduces latency and improves throughput by allowing the system to acknowledge writes quickly, without waiting for synchronization across all replicas. However, it may introduce temporary inconsistencies between replicas, which applications must handle gracefully.

## Active vs Passive

- Active-active replication distributes workload across multiple replicas for improved performance and fault tolerance but requires careful management of conflicts and consistency.
- Active-passive replication simplifies management and ensures data consistency but may underutilize resources and introduce latency during failover events.

### Active-Active Replication / Active Replication

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

### Active-Passive Replication / Passive Replication

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

## Masters vs Workers

- Single-master replication simplifies data consistency by designating one master for write operations but may face scalability and availability limitations.
- Multi-master replication offers better scalability, availability, and lower latency by distributing write operations across multiple masters but requires robust conflict resolution mechanisms and introduces complexity in system design and management.

### Primary-Backup Replication / Single-Master Replication

- Goal: In single-master replication, also known as master-slave replication, one designated replica serves as the master or primary node, while the other replicas act as slaves or secondary nodes.
- Process: The master replica is responsible for processing all write operations (updates, inserts, deletes) from clients and propagating these changes to the slave replicas. The slave replicas asynchronously replicate the changes from the master and serve read requests from clients.
- Benefits:
  - Data Consistency: With a single authoritative source for writes (the master), data consistency is easier to maintain since all writes are applied in a sequential manner.
  - Simplicity: Single-master replication setups are often simpler to design, implement, and manage compared to multi-master configurations due to the clear distinction between master and slave nodes.
  - Failover: In the event of master failure, one of the slave replicas can be promoted to the master role, ensuring continuous operation with minimal disruption.
- Challenges:
  - Scalability: Write operations are bottlenecked by the master node since all writes must go through it, potentially limiting scalability as the workload increases.
  - Read Scalability: While reads can be distributed across slave replicas, they may lag behind the master in terms of data freshness due to asynchronous replication.
  - Single Point of Failure: The master node represents a single point of failure, and its failure can impact the entire system until failover occurs.
- Techniques for propagating updates
  - Synchronous replication
    - the node replies to the client to indicate that the update is complete - only after receiving acknowledgments from the other replicas that they have also
    performed the update on their local storage
    - guarantees that the client is able to view the update in a subsequent read after acknowledging it, no matter which replica the client reads from
    - provides increased durability because the update is not lost even if the leader crashes right after it acknowledges the update
    - makes writing requests slower because the leader has to wait until it receives responses from all the replicas
    - Steps
      - a distributed system with a leader-follower architecture, where the primary node is the leader while secondary nodes are followers
      - client sends a write request to primary node
      - primary nodes performs write request locally
      - primary node propagates the write request to the secondary nodes
      - secondary I performs write request and sends acknowledgement to the primary node
      - secondary II performs write request and sends acknowledgment to the primary node
      - synchronous replication: primary/leader node sends an acknowledgement to the client after writing updates to all nodes (leader and followers)
  - Asynchronous replication
    - the node replies to the client as soon as it performs the update in its local storage, without waiting for responses from the other replicas
    - increases performance for write requests because the client no longer pays the penalty of the network requests to the other replicas
    - reduces consistency - after a client receives a response for an update request the client might read older/stale values in a subsequent read; this is only possible if the operation happens in one of the replicas that have not yet performed the update
    - reduces durability - if the leader node crashes right after it acknowledges an update, and the propagation requests to the other replicas are lost, any acknowledged update is eventually lost
    - Steps
      - a distributed system with leader-follower architecture, where the primary node is the leader while secondary nodes are followers
      - client sends a write request to primary node
      - primary node performs write request locally
      - asynchronous replication: primary/leader node sends acknowledgement to the client right after performing update in its local storage without waiting to send and perform updates to other replica nodes (secondary/followers)
      - primary node propagates the write request to the secondary nodes
      - secondary I performs write request and sends acknowledgement to the primary node
      - secondary II performs write request and sends acknowledgement to the primary node
- Examples
  - Most widely used databases, such as PostgreSQL or MySQL, use a single-master replication technique that supports both asynchronous and synchronous replication.
- Advantages of single-master replication
  - simple to understand and implement
  - concurrent operations serialized in the leader node, remove the need for more complicated, distributed concurrency protocols; makes it easier to support transactional operations
  - scalable for read-heavy workloads because the capacity for reading requests can be increased by adding more read replicas
- Disadvantages of single-master replication
  - not very scalable for write-heavy workloads because a single node (the leader)’s capacity determines the capacity for writes
  - imposes an obvious trade-off between performance, durability, and consistency - scaling the read capacity by adding more follower nodes can create a bottleneck in the network bandwidth of the leader node, if there’s a large number of followers listening for updates
  - the process of failing over to a follower node when the leader node crashes is not instant; this may create some downtime and also introduce the risk of errors

#### Failover

- Failover is when the master node crashes and a random follower node takes over.
- This process may involve downtime and potential data loss.
- Manual approach
  - The operator selects the new leader node and instructs all the nodes accordingly.
  - This is the safest approach, but it incurs significant downtime.
- Automated approach
  - Follower nodes detect that the leader node has crashed (e.g. via periodic heartbeats (periodic messages sent by a node that indicate that it is working failure-free)) and attempt to elect a new leader node.
  - This is faster but is quite risky because there are many different ways in which the nodes can get confused and arrive at an incorrect state.

### Multi-Primary Replication

- Goal: Multi-master replication, also known as symmetric or peer-to-peer replication, allows multiple replicas to function as independent masters, each capable of processing both read and write operations.
- Process: In a multi-master setup, all replicas are considered equal peers, and each can accept write operations from clients. Changes made to any master are propagated asynchronously to other masters, ensuring data consistency across the system.
- Benefits:
  - Scalability: Multi-master replication distributes write operations across multiple nodes, enabling better scalability and higher throughput compared to single-master setups.
  - High Availability: Since multiple masters are available to process writes, the system can continue to operate even if one or more masters fail.
  - Low Latency: With multiple masters serving write operations, clients can write to the nearest available master, reducing latency.
- Challenges:
  - Conflict Resolution: Conflicts may arise when concurrent writes occur on different masters, requiring robust conflict resolution mechanisms to maintain data consistency.
  - Complexity: Multi-master replication setups are often more complex to design, implement, and manage compared to single-master configurations due to the need for conflict resolution and coordination among masters.
  - Data Consistency: Ensuring data consistency across multiple masters can be challenging, especially in scenarios with high update rates or network partitions.



- Independent Write Operations
    - Each leader can independently accept write operations from clients or applications without coordination with other leaders.
    - This allows for horizontal scalability and improved write throughput since write requests can be distributed across multiple nodes.
- Conflict Resolution
    - Since multiple leaders can accept write operations concurrently, conflicts may arise when two or more leaders modify the same data item concurrently.
    - Conflict resolution mechanisms are needed to resolve conflicts and ensure data consistency across the system.
    - Common conflict resolution strategies include last-write-wins, timestamp-based conflict resolution, or application-specific conflict resolution logic.
- Asynchronous Replication
    - Changes made by one leader need to be replicated to other leaders in the system to ensure consistency.
    - This replication process is typically asynchronous, meaning that changes are propagated to other nodes after they have been applied locally.
    - Asynchronous replication introduces the possibility of eventual consistency, where updates may not be immediately visible on all nodes.
- Network Partition Handling
    - Multi-leader replication systems need to handle network partitions gracefully to ensure availability and consistency.
    - Techniques such as quorum-based replication or automatic failover mechanisms can be employed to maintain system operation in the presence of network partitions.

Overall, multi-leader replication provides flexibility, scalability, and fault tolerance in distributed database systems by allowing multiple nodes to accept write operations independently. However, it also introduces challenges related to conflict resolution, consistency, and network partition handling that need to be addressed to ensure the correctness and reliability of the system.

- Single-master replication
  - easy to implement and operate
  - can easily support transactions and hide the distributed nature of the underlying system, i.e. when using synchronous replication
  - has some limitations in terms of performance, scalability, and availability

- There are many applications where availability and performance are much more important than data consistency or transactional semantics.
- example of e-commerce shopping cart
  - most important thing is for customers to be able to access their cart at all times and add items quickly and easily
  - acceptable to compromise consistency to achieve this, as long as there is data reconciliation at some point e.g. if two replicas diverge because of intermittent failures, the customer can still resolve conflicts during the checkout process

- Multi-master/Multi-primary replication
  - favors higher availability and performance over data consistency
  - case where all replicas are equal, can accept write requests and are responsible for propagating the data modifications to the rest of the group
  - no single master node that serializes the requests and imposes a single order, as write requests are concurrently handled by all the nodes => nodes might disagree on what is the right order for some requests (called a conflict)
  - for the system to remain operational the nodes need to resolve this conflict when it occurs by agreeing on a single order from the available ones

- instance where two write requests can potentially result in a conflict, depending on the latency of the propagation requests between the nodes of the system
  - a client and three replicated nodes A, B, and C
  - client sends a write request to Node A
  - node A receives the write request
  - node A writes the value of X locally
  - node A propagates the value of X to nodes B and C
  - node C receives the value of X; however, before node B receives this, client sends another write request to node B
  - node C writes the value of X locally; node B receives the later write request (X = 14) before the earlier write request (X = 10)
  - node B writes the value of X it received locally
  - node B propagates the value of X to nodes A and C
  - nodes A and C receive the updated values for X
  - nodes A and C update the value of X locally
  - node B finally receives the first write request (X = 10)
  - node B updates the value of X; at this time, after executing both write requests by client, the value of X at node B is 10 while the other nodes A and C contain value of X equal to 14
  - now, if client reads X what will it get?; either 10 or 14 depending on which node serves the read request

- In the case of a conflict, a subsequent read request could receive different results depending on the node that handles the request - unless we resolve the conflict so that all the nodes converge again to a single value.

Conflict resolution approaches
- differ depending on
  - the guarantees the system wants to provide
  - whether the approach is eager or lazy
    - eager: conflict resolved during the write operation
    - lazy: the write operation proceeds to maintain multiple, alternative versions of the data record that are eventually resolved to a single version later on i.e. during a subsequent read operation
- 01: exposing conflict resolution to the clients
  - when there is a conflict the multiple available versions return to the client
  - the client then selects the right version and returns it to the system
  - this resolves the conflict
  - example: shopping cart application where the customer selects the correct version of their cart
- 02: last-write-wins conflict resolution
  - each node in the system tags each version with a timestamp, using a local clock
  - during a conflict, the version with the latest timestamp is selected
  - can lead to some unexpected behaviors, as there is no global notion of time
  - e.g. write A can override write B, even though B happened “as a result” of A
- 03: causality tracking algorithms
  - the system uses an algorithm that keeps track of causal relationships between different requests
  - when there is a conflict between two writes (A, B) and one is determined to be the cause of the other one (suppose A is the cause of B), then the resulting write (B) is retained
  - there can still be writes that are not causally related i.e. requests are actually concurrent; in such cases the system cannot make an easy decision

## Chain Replication

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

## Single-Master Replication vs Multi-Master Replication vs Chain Topology

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
