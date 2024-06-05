# [WIP] Conflict Resolution Protocols

- Aim to resolve conflicts that arise when multiple nodes attempt to update the same data concurrently.
- Examples include last-write-wins, timestamp-based conflict resolution, and conflict-free replicated data types (CRDTs).

- In systems where concurrent updates to data can occur, conflict resolution protocols help resolve conflicts that arise when conflicting updates are made to the same data item across different replicas.
- Conflict resolution protocols may employ techniques such as last-write-wins, version vectors, or application-specific conflict resolution logic.

- In distributed systems where multiple replicas can independently modify shared data, conflict resolution protocols are used to resolve conflicting updates and maintain data integrity.



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

Purpose: Resolve conflicts that arise when multiple nodes concurrently update the same data.

## Last-Writer-Wins (LWW) Conflict Resolution
    * How It Works: The system keeps the most recent write, typically based on a timestamp.
    * Use Case: Simple distributed systems where recent updates are prioritized.
    * Pros: Easy to implement.
    * Cons: Risk of losing important data from earlier writes.

## Vector Clocks (timestamp-based conflict resolution)
    * How It Works: Each write operation is tagged with a timestamp, and the system uses these timestamps to resolve conflicts.
    * Use Case: Systems where precise ordering of updates is critical.
    * Pros: Clear and logical resolution method.
    * Cons: Requires synchronized clocks across nodes.

## Conflict-Free Replicated Data Types (CRDTs)
    * How It Works: Data structures designed to merge without conflicts, ensuring eventual consistency.
    * Use Case: Real-time collaborative applications like Google Docs.
    * Pros: Automatic conflict resolution.
    * Cons: Limited to specific data types and operations.

- CRDTs are data structures designed to support concurrent updates across replicas without the need for synchronization or coordination.
- CRDTs ensure that updates commute and can be merged deterministically, allowing replicas to converge to a consistent state without conflicts.
- This approach is particularly useful for highly distributed systems where strong consistency is impractical.
