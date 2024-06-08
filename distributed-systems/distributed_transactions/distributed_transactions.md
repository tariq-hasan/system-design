# [WIP] Distributed Transactions

- Scope: Focus on the coordination of a single transaction across multiple distributed nodes.
- Complexity and Coordination: Involve significant complexity in coordinating across multiple systems, dealing with network issues, and ensuring global consistency.
- Application: Applied in scenarios where a single transaction must be executed across multiple distributed databases or resource managers.

# Definition

- Distributed transactions are transactions that span multiple, geographically dispersed databases or resource managers.
- These transactions involve operations that must be coordinated across different nodes or systems to ensure consistency and atomicity.

# Key Characteristics

- Multiple Nodes: Distributed transactions involve multiple database nodes or resource managers that may be located on different servers.
- Coordination: These transactions require coordination across the different nodes to ensure that the transaction is either fully committed or fully rolled back on all nodes.
- Two-Phase Commit Protocol (2PC): A common protocol used in distributed transactions to ensure atomicity. The first phase (prepare phase) involves asking all nodes to prepare to commit, and the second phase (commit phase) involves committing the transaction if all nodes agree to commit.
- Complexity: Managing distributed transactions is more complex due to network latency, potential node failures, and the need for coordination across multiple systems.
- Latency and Performance: Distributed transactions often have higher latency and can be less performant compared to local transactions because of the communication overhead between nodes.

# Examples

- A transaction that updates inventory in multiple distributed databases for a large e-commerce platform.
- A financial transaction that needs to update records in different banking systems.
