# [WIP] Consensus Protocols

- Ensure that a group of nodes agrees on a single value or outcome, even in the presence of failures or partitions.

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

## Paxos

- https://martinfowler.com/articles/patterns-of-distributed-systems/paxos.html

## Chandra-Toueg

## Raft

## Zab

## Practical Byzantine Fault Tolerance (PBFT)

## Leader Election Protocols

- Leader election protocols can be considered part of the broader category of coordination and synchronization protocols used in distributed systems.
- Leader election protocols are specifically designed to establish a single node as the leader among a group of nodes in a distributed system.
- The leader node typically assumes responsibilities such as coordinating distributed transactions, managing system-wide metadata, or making global decisions on behalf of the system.

<br/>

- Leader election protocols ensure that only one node acts as the leader at any given time, even in the presence of failures or network partitions.
- Examples of leader election protocols include the Bully algorithm, the Ring algorithm, and the Paxos-based approach used in systems like Apache ZooKeeper.

<br/>

- By electing a leader, distributed systems can achieve centralized coordination and decision-making while maintaining fault tolerance and resilience to failures. - Leader election protocols play a critical role in enabling distributed systems to operate efficiently and reliably in various scenarios, including consensus-based replication, distributed databases, and distributed computing platforms.
