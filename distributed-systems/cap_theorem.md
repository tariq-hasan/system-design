# [WIP] CAP Theorem

- A network partition occurs when a network becomes divided into isolated subnetworks, preventing communication between nodes in different partitions while allowing communication within each partition.
- This division can occur due to various reasons, such as network failures, hardware malfunctions, misconfigurations, or deliberate actions.

<br/>

- In a distributed system, network partitions can have significant consequences, particularly when nodes rely on communication and coordination to perform tasks collectively.
- When a partition occurs, nodes in one partition may be unable to reach nodes in another partition, leading to inconsistencies, failures, or incorrect behavior in the system.

<br/>

- Network partitions are a challenging problem to handle in distributed systems because they can cause split-brain scenarios, where each partition believes it is the sole authority and continues to operate independently.
- This can result in conflicting decisions, data inconsistencies, or data loss when partitions later merge.

<br/>

- To address network partitions, distributed systems often employ fault-tolerant techniques such as consensus algorithms, replication, and data synchronization protocols.
- These mechanisms aim to ensure system correctness, availability, and resilience even in the face of network failures and partitions.



Network partition detection is the process of identifying and diagnosing network partitions in a distributed system.
A network partition occurs when a network failure or misconfiguration causes some nodes in a distributed system to become unreachable or isolated from each other, leading to a split in the system's communication network.

Network partition detection mechanisms are essential for maintaining the availability and consistency of the distributed system in the face of network failures. Here's how network partition detection typically works:
Heartbeats and Ping Messages: Nodes in the distributed system periodically exchange heartbeat or ping messages to signal their availability and detect the presence of other nodes. If a node stops receiving heartbeats or pings from a particular node within a specified time period, it may infer that a network partition has occurred.
Timeouts and Quorums: Distributed systems often use timeouts and quorums to detect network partitions. Timeouts are set for communication operations, and if a response is not received within the timeout period, the operation may be retried or marked as failed. Quorums are used to ensure that a majority of nodes agree on an operation, and if a quorum cannot be reached due to network partitions, the operation may be aborted.
Network Monitoring and Diagnostics: Network monitoring tools and diagnostic utilities can help detect abnormal network behavior, such as packet loss, high latency, or unreachable nodes, which may indicate the presence of a network partition.
Health Checking and Failure Detection: Distributed systems often employ health checking and failure detection mechanisms to continuously monitor the status of nodes and detect failures. If a node fails to respond to health checks or is unreachable, it may be considered as potentially affected by a network partition.
Consensus and Leader Election: Consensus algorithms and leader election protocols, such as Paxos and Raft, inherently involve network partition detection mechanisms to ensure that nodes agree on a common state or leader despite potential network partitions.

Overall, network partition detection is crucial for maintaining the availability, consistency, and reliability of distributed systems, as it allows the system to adapt to network failures and mitigate their impact on system operations.
