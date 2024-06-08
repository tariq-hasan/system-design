# [WIP] Transactional Models

- theoretical frameworks that define the rules and properties for how transactions should be executed and managed to ensure the ACID properties

## ACID Properties

- Atomicity: Atomicity ensures that all operations within a transaction are completed successfully or none of them are applied, providing an "all-or-nothing" approach.
- Consistency: Consistency ensures that a transaction takes the database from one valid state to another, maintaining the integrity of the data according to all defined rules (such as constraints, cascades, and triggers).
- Isolation: Isolation ensures that the concurrent execution of transactions leaves the database in the same state as if the transactions were executed serially (one after the other).
- Durability: Durability ensures that once a transaction has been committed, its effects are permanently recorded in the database, even in the event of a system failure.

## Types of Transaction Models

- Flat Transactions: Traditional, simple transaction model where a transaction is a single, indivisible unit.
- Nested Transactions: Allows transactions to contain sub-transactions, providing more granularity and flexibility.
- Long-Running Transactions: Transactions that span a long period and may involve multiple steps or user interactions.
- Saga: A sequence of transactions that can be partially rolled back, used often in long-running business processes.

- Examples
  - A flat transaction updating a customer record in a single database.
  - A nested transaction where a main transaction spawns sub-transactions to update related records in a hierarchical manner.

# Concurrency Control Protocols

- Transactional models include various concurrency control mechanisms such as locking, timestamp ordering, and multiversion concurrency control to manage simultaneous transactions.

- manage access to data in a way that ensures consistency and isolation of transactions, especially when multiple transactions are occurring concurrently
- ensure that transactions are executed concurrently without violating the integrity of the database
- address issues like data consistency, isolation, and preventing phenomena like dirty reads, non-repeatable reads, and phantom reads

Each of these protocols has its strengths and weaknesses, and the choice of protocol often depends on the specific requirements of the database system, such as the expected workload, the types of transactions, and the desired balance between concurrency and consistency.

- Concurrency control mechanisms are essential for maintaining the Isolation property of ACID, ensuring that transactions do not interfere with each other and that the concurrent execution of transactions does not lead to inconsistent states. By ensuring isolation, concurrency control also indirectly supports Consistency and Atomicity. However, Durability is primarily the responsibility of the DBMS's logging and recovery mechanisms.
- Isolation: Concurrency control mechanisms like locking, timestamp ordering, multiversion concurrency control, and optimistic concurrency control are designed to ensure that transactions do not interfere with each other. They prevent phenomena like dirty reads, non-repeatable reads, and phantom reads, thereby maintaining isolation.
- Consistency: While consistency is primarily the responsibility of the transaction logic and the database management system (DBMS) enforcing integrity constraints, concurrency control helps maintain consistency by ensuring that transactions do not leave the database in an inconsistent state due to concurrent modifications. By ensuring isolation, concurrency control prevents transactions from reading inconsistent or intermediate states.
- Atomicity: Concurrency control indirectly supports atomicity by ensuring that transactions are isolated. If a transaction is aborted due to conflicts detected by concurrency control mechanisms, the system can roll back the transaction, ensuring that partial updates do not occur. This rollback capability is crucial for maintaining atomicity in the presence of concurrent transactions.
- Durability: Durability is primarily handled by the DBMS's logging and recovery mechanisms rather than concurrency control. However, concurrency control ensures that only consistent and isolated transactions are committed, thus ensuring that the data that is made durable is reliable and correct.

## Optimistic Concurrency Control

- uses version numbers to detect conflicts during the validation phase
- manages data versions to detect conflicts at the end of a transaction
- each transaction works on a snapshot of the data and checks for conflicts before committing

- Purpose: Allows transactions to execute without locking resources, assuming conflicts are rare. When a transaction is ready to commit, it checks for conflicts.
- How It Works:
  - Begin Transaction: A transaction starts and operates on a snapshot of the database.
  - Transaction Execution: Changes are made in isolation.
  - Validation Phase: Before committing, the transaction checks if any data it read has been modified by other transactions.
  - Commit or Rollback: If no conflicts are detected, the transaction commits. If conflicts are found, the transaction rolls back and can be retried.
- Use Case: Suitable for systems with low contention, such as read-heavy workloads.
- Pros:
  - Reduces the need for locking mechanisms.
  - Improves performance in low-contention scenarios.
- Cons:
  - High potential for rollbacks in high-contention environments.
  - Requires conflict detection and resolution logic.

- How It Works: Each transaction proceeds without locking, but checks for conflicts before committing.
- Use Case: Systems with low contention.
- Pros: Reduces locking overhead.
- Cons: Potential for conflicts at commit time.



- In the context of database systems and transaction management, a versioning protocol is one that tracks different versions of data items to manage concurrent access.
- Optimistic concurrency control works under the assumption that conflicts between transactions are rare and that it is more efficient to allow transactions to proceed without locking resources.
- At the end of the transaction, OCC checks whether a conflict has occurred.
- If a conflict is detected, the transaction is rolled back and can be retried.

- OCC typically involves the following phases:
  - Read Phase: The transaction reads the values of the required data items. At this stage, it keeps track of the versions of these data items.
  - Validation Phase: Before committing, the transaction checks whether any of the data items it read have been modified by other transactions since it was read. This involves checking the version numbers.
  - Write Phase: If the validation is successful (i.e., no conflicts are found), the transaction writes its updates to the database. If the validation fails, the transaction is rolled back.

- The use of version numbers to track changes and ensure that a transaction's view of the data is consistent with the actual state of the database at commit time makes OCC a versioning protocol.
- By comparing version numbers, OCC ensures that no other transaction has modified the data items since they were read by the current transaction, thus maintaining data consistency.

## Pessimistic Concurrency Control

### Lock-Based Protocols

- These protocols use locks to control access to data items and do not maintain multiple versions of the data.

- This is the most common form of PCC, where transactions acquire locks on data items before accessing them to prevent conflicts.

#### Two-Phase Locking (2PL)

This ensures serializability by dividing the transaction into two phases: a growing phase (where locks are acquired) and a shrinking phase (where locks are released). Variants include:
- Strict 2PL: Holds all exclusive locks until the transaction commits or aborts.
- Rigorous 2PL: Holds all locks (shared and exclusive) until the transaction commits or aborts.

#### Hierarchical Locking (or Multigranularity Locking)

Locks at different granularities (e.g., table-level, row-level) to improve concurrency by allowing multiple transactions to work on different parts of the data.

## Timestamp-Based Protocols

- Basic Timestamp Ordering (TO) and Thomas’s Write Rule: These protocols order transactions based on timestamps but do not maintain multiple versions of data items.

### Basic Timestamp Ordering

Each transaction is given a unique timestamp. Transactions are ordered by their timestamps, and conflicts are resolved based on these timestamps.

### Thomas’s Write Rule

An optimization of basic TO, which allows certain out-of-order writes if they do not affect the final state.

### Multiversion Concurrency Control

- In MVCC, each transaction operates on a snapshot of the database, which includes multiple versions of data items.
- Read operations access the appropriate version of each data item based on the transaction's timestamp, ensuring that transactions only see committed data.
- Write operations create new versions of data items, and transactions maintain isolation by not affecting other transactions' snapshots.

- maintains multiple versions of data items to allow concurrent reads and writes, making it a clear example of a versioning protocol
- readers can access older versions of data while writers update newer versions, reducing conflicts

Maintains multiple versions of data items, allowing transactions to read older versions while new versions are being written. This reduces read-write conflicts.

- Purpose: Allows multiple versions of data to coexist, enabling transactions to operate on different versions of the data without interfering with each other.
- How It Works:
  - Version Creation: Each write operation creates a new version of the data.
  - Version Selection: Read operations select the appropriate version based on the transaction's snapshot.
  - Garbage Collection: Old versions are periodically cleaned up to free space.
- Use Case: Widely used in relational databases like PostgreSQL and NoSQL databases like CouchDB.
- Pros:
  - High read performance due to reduced locking.
  - Supports long-running transactions without blocking.
- Cons:
  - Increased storage requirements for maintaining multiple versions.
  - Complexity in managing and cleaning up old versions.

## Validation-Based Protocols

- While similar to OCC, specific implementations of validation protocols might or might not use versioning explicitly. However, in their traditional form, they don't necessarily maintain multiple versions of data items.

These are essentially OCC protocols, but some variations exist. Transactions are validated before committing to ensure no conflicts with other concurrent transactions.

## Graph-Based Protocols

- Wait-Die and Wound-Wait and Deadlock Detection: These protocols manage transaction dependencies and prevent or resolve deadlocks but do not involve versioning of data items.

### Wait-Die and Wound-Wait

These are deadlock prevention schemes that use timestamps to decide whether a transaction should wait or abort when a conflict occurs.

### Deadlock Detection

Constructs a waits-for graph to detect cycles, indicating deadlocks, and then breaks the deadlock by aborting one of the transactions.

## Snapshot Isolation

- uses multiple versions of data items to provide a consistent view of the database at a particular point in time
- provides transactions with a consistent snapshot of the database as of a particular point in time
- uses multiple versions of data to ensure that transactions do not interfere with each other

- Purpose: Provides a consistent view of the database by ensuring that transactions operate on a snapshot of data at a specific point in time.
- How It Works:
  - Snapshot Creation: When a transaction starts, it gets a snapshot of the database at that moment.
  - Transaction Execution: All reads are done from this snapshot, while writes are isolated.
  - Validation: Before committing, the system checks for write-write conflicts.
  - Commit or Abort: If no conflicts are found, the transaction commits; otherwise, it aborts.
- Use Case: Databases requiring strong consistency and isolation, such as PostgreSQL and Microsoft SQL Server.
- Pros:
  - Prevents many common concurrency issues, such as dirty reads and non-repeatable reads.
  - Ensures consistency without locking the entire database.
- Cons:
  - Increased storage overhead due to maintaining multiple snapshots.
  - May require complex conflict detection mechanisms.

- How It Works: Each transaction operates on a snapshot of the database at a specific point in time.
- Use Case: Databases requiring high consistency and isolation.
- Pros: Prevents many common concurrency issues.
- Cons: Increased storage and complexity.

- SI provides a view of the database as of a particular snapshot (or point in time).
- Transactions read from this snapshot and make changes in a way that they do not interfere with each other.
- SI allows higher concurrency by allowing multiple versions of the data.

## Hybrid Protocols

- Combine elements of the above methods to optimize for specific workloads or performance characteristics.
- For example, some systems might use 2PL for writes and OCC for reads.

- The use of versioning in hybrid protocols depends on the specific combination of methods used. For instance, a hybrid protocol combining 2PL and MVCC would involve versioning, whereas one combining 2PL and basic TO might not.
