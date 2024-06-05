# [WIP] Quorum-based Protocols

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

<br/>

- Rely on a threshold of votes or acknowledgments from a subset of nodes to make decisions or perform operations.
- Ensure that a sufficient number of replicas agree on a particular action.
- Examples include read and write quorums in distributed databases.

<br/>

Writes are performed to all the replica nodes, while reads are performed to one of them.
When we ensure that writes are performed to all of them synchronously before replying to the client, we guarantee that the subsequent reads see all the previous writes - regardless of the node that processes the read operation.

<br/>

Problem in synchronous replication
- low availability for write operations because the failure of a single node makes the system unable to process writes until the node recovers
Solution
- use the reverse strategy: write data only to the node that is responsible for processing a write operation, but process read operations by reading from all the nodes and returning the latest value
- increases the availability of writes significantly but decreases the availability of reads at the same time; so we have a trade-off that needs a mechanism to achieve a balance

<br/>

Quorums
- useful mechanism to achieve a balance in this trade-off
- example
  - in a system of three replicas, we can say that writes need to complete in two nodes (as a quorum of two), while reads need to retrieve data from two nodes
  - this way, we can be sure that the reads will read the latest value
  - this is because at least one of the nodes in the read quorum will also be included in the latest write quorum
  - this is based on the fact that in a set of three elements, two subsets of two elements must have at least one common element
  - this technique is known as a quorum-based voting protocol for replica control
- in a system that has a total of V replicas, V_r + V_w > V and V_w > V/2, where every read operation should obtain a read quorum of V_r replicas and a write operation should obtain a write quorum of V_w replicas
- The first rule ensures that a data item is not read and written by two operations concurrently
- The second rule ensures that at least one node receives both of the two write operations and imposes an order on them. This means that two write operations from two different operations cannot occur concurrently on the same data item.
- Both of the rules together guarantee that the associated distributed database behaves as a centralized, one-replica database system.
- The concept of a quorum is really useful in distributed systems that have multiple nodes.
- The concept of a quorum is used extensively in other areas, like distributed transactions or consensus protocols.







Purpose: Rely on a threshold of votes or acknowledgments from a subset of nodes to make decisions or perform operations.
* Read and Write Quorums:
    * How It Works: Operations require a certain number of nodes (quorum) to agree before proceeding.
    * Use Case: Distributed databases like Cassandra and DynamoDB.
    * Pros: Ensures a level of consistency and fault tolerance.
    * Cons: Can result in higher latency due to quorum requirements.
Replication Protocols
Purpose: Replicate data across multiple nodes to enhance availability, fault tolerance, and load distribution.
* Single-Master Replication:
    * How It Works: One node (master) handles all write operations, which are then replicated to other nodes (slaves).
    * Use Case: Simple replication setups.
    * Pros: Easy to manage and implement.
    * Cons: Single point of failure at the master.
* Multi-Master Replication:
    * How It Works: Multiple nodes can handle write operations, replicating changes to each other.
    * Use Case: Systems requiring high availability and write capabilities.
    * Pros: High availability and fault tolerance.
    * Cons: Complexity in conflict resolution.
* Chain Replication:
    * How It Works: Nodes are organized in a chain; writes go to the head and propagate down, while reads are served from the tail.
    * Use Case: Systems needing high throughput and reliability.
    * Pros: Provides strong consistency and fault tolerance.
    * Cons: Can be complex to implement.
