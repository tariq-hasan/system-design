# [WIP] Data Consistency Protocols

- Purpose: Enforce consistency guarantees across distributed data stores to maintain data integrity.
- Function: Ensure data consistency across replicas or partitions in a distributed system.

# Strong Consistency Models

## Strict Consistency

- Every read operation must return the value of the most recent write operation.

## Linearizability

- Every operation appears to take effect instantaneously at a single point in time between its invocation and response.
- A form of strict consistency.

# Weak Consistency Models

## Sequential Consistency

The result of any execution is the same as if the operations by all processes were executed in some sequential order.
Operations within a process appear in the order specified by its program.
Operations from different processes may be interleaved in any order.

In sequential consistency, the execution of operations on a distributed system appears as if they were executed in some sequential order that respects the real-time ordering of those operations.
This means that for any two operations, if one operation happens before another according to the real-time order, then all other nodes in the system must agree on that order.
However, operations from different nodes might be interleaved in a way that doesn't reflect the real-time order.

Sequential consistency is more about the order in which operations appear to occur in a distributed system.

Sequential consistency is stronger than the causal consistency model.
It preserves the ordering specified by each client’s program.
However, sequential consistency does not ensure that the writes are visible instantaneously or in the same order as they occurred according to some global clock.

Example
- In social networking applications, we usually do not care about the order in which some of our friends’ posts appear.
- However, we still anticipate a single friend’s posts to appear in the correct order in which they were created.
- Similarly, we expect our friends’ comments in a post to display in the order that they were submitted.
- The sequential consistency model captures all of these qualities.

Sequential consistency is a weaker consistency model, where operations are allowed to take effect before their invocation or after their completion.
As a result, it provides no real-time guarantees.
However, operations from different clients have to be seen in the same order by all other clients, and operations of every single client preserve the order specified by its program (in this global order).
This allows many more histories than linearizability, but still poses some constraints that can help real-life applications.

Example
- For example, in a social networking application, we usually do not care what is the ordering of posts between some of our friends.
- However, we still expect posts from a single friend to be displayed in the right order (i.e. the one they published them at).
- Following the same logic, we usually expect our friends’ comments in a post to appear in the order that they submitted them.
- These are all properties that the sequential consistency model captures.

## Causal Consistency

Preserves causal relationships between operations.
If operation A causally precedes operation B, then B must observe the effect of A.

## Eventual Consistency

Updates to a data item propagate through the system and eventually all replicas converge to the same value.
Guarantees consistency after a certain period of time in absence of further updates.

- Eventual consistency is a weaker consistency model that allows replicas to diverge temporarily but guarantees that they will eventually converge to the same state.
- In eventual consistency replication, updates are propagated asynchronously to replicas, and conflicts are resolved using reconciliation mechanisms.
- While eventual consistency offers high availability and scalability, it may lead to temporary inconsistencies in data.

Eventual consistency is the weakest consistency model.
The applications that do not have strict ordering requirements and do not require reads to return the latest write choose this model.
Eventual consistency ensures that all the replicas will eventually return the same value to the read request, but the returned value is not meant to be the latest value.
However, the value will finally reach its latest state.

Eventual consistency ensures high availability.

Examples
- The domain name system is a highly available system that enables name lookups to a hundred million devices across the Internet. It uses an eventual consistency model and does not necessarily reflect the latest values.
- Cassandra is a highly available NoSQL database that provides eventual consistency.

There are still even simpler applications that do not have the notion of a cause-and-effect and require an ever simpler consistency model.
The eventual consistency model is beneficial here.

Example
- For instance, we could accept that the order of operations can be different between the multiple clients of the system, and reads do not need to return the latest write as long as the system eventually arrives at a stable state.
- In this state, if no more write operations are performed, read operations will return the same result.
- This is the model of eventual consistency.

It is one of the weakest forms of consistency since it does not really provide any guarantees around the perceived order of operations or the final state the system converges to.

It can still be a useful model for some applications, which do not require stronger assumptions or can detect and resolve inconsistencies at the application level.

# Database Consistency Models

## Serializability

- Ensures that the result of executing transactions serially is the same as executing them concurrently.
- Transactions appear to be executed one after another without interleaving.
- More focused on database transactions rather than distributed systems.
- These models represent a spectrum ranging from strong consistency, where every operation must behave as if it were the only operation in the system, to weak consistency, where the system allows for more flexibility and eventual convergence over time.

Serializability is a property of a schedule of transactions in a database system.
A schedule is serializable if it's equivalent to some serial execution of transactions, meaning that the result of executing the transactions in parallel is the same as executing them one after the other in some order.
Serializability ensures that the execution of transactions doesn't violate the consistency constraints of the database.

Serializability is about ensuring that the execution of transactions in a database maintains consistency. They both aim to ensure consistency but at different levels and in different contexts.
