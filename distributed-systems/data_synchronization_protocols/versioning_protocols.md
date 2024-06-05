# [WIP] Versioning Protocols

- Techniques such as versioning and Merkle trees are used to efficiently synchronize data and detect changes in distributed systems.
- They are commonly used in distributed version control systems (DVCS) like Git and in distributed storage systems.

- Versioning protocols track different versions of data items and manage the reconciliation of divergent versions across replicas.
- Techniques such as vector clocks, Lamport timestamps, or hybrid logical clocks are commonly used to manage versioning in distributed systems.

- Maintain multiple versions of data to support concurrency control, conflict resolution, and rollback mechanisms.
- Examples include optimistic concurrency control and snapshot isolation.

Vector Clocks
* Use Case: Version control, conflict detection in distributed systems.
* How It Works: Each node maintains a vector of counters, one for each node, to track the causality of events.
* Pros: Allows detection of concurrent updates.
* Cons: Can become inefficient with a large number of nodes.



Purpose: Maintain multiple versions of data to support concurrency control, conflict resolution, and rollback mechanisms.
* Optimistic Concurrency Control:
    * How It Works: Each transaction proceeds without locking, but checks for conflicts before committing.
    * Use Case: Systems with low contention.
    * Pros: Reduces locking overhead.
    * Cons: Potential for conflicts at commit time.
* Snapshot Isolation:
    * How It Works: Each transaction operates on a snapshot of the database at a specific point in time.
    * Use Case: Databases requiring high consistency and isolation.
    * Pros: Prevents many common concurrency issues.
    * Cons: Increased storage and complexity.
