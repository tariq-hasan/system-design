# Database

## Database Scaling Approaches

Databases can scale in two primary ways:
- **Vertical Scaling**: Increasing resources (CPU, RAM) on a single server
- **Horizontal Scaling**: Distributing load across multiple database servers

## Database Failover Strategy Comparison

### Cold Standby Database Server

A basic approach that provides minimal protection:

- **Backup Process**: Periodic backups from primary database to external storage (S3, tape)
- **Recovery Process**: Upon failure, manually provision new server, restore backup, and redirect traffic
- **Disadvantages**:
  - Extended downtime during server provisioning and backup restoration
  - Data loss of all transactions since last backup
  - Manual intervention required
- **Advantages**:
  - Low cost implementation
  - Simple configuration

### Warm Standby Database Server

An intermediate approach balancing cost and availability:

- **Configuration**: Secondary database server continuously receives replicated data from primary
- **Replication Strategies**:
  - Asynchronous replication (slight lag, potential for minimal data loss)
  - Synchronous replication (real-time consistency, higher latency)
- **Recovery Process**:
  - Automatic or manual traffic redirection to standby when primary fails
  - Minimal downtime during failover switch
- **Considerations**:
  - Brief service interruption during failover detection and routing changes
  - Near-zero data loss with proper configuration
  - Standby server experiences increased load during failover, potentially affecting stability

### Hot Standby Database Server

The highest availability solution for critical systems:

- **Architecture**: Multiple active database instances operating simultaneously
- **Data Write Process**: Application servers write data directly to all database instances in parallel
- **Read Strategy Options**:
  - Read from primary only
  - Distribute reads across all instances for load balancing
- **Recovery Process**:
  - Seamless failover when a database instance fails
  - Remaining connections continue without interruption
- **Advantages**:
  - Near-zero downtime
  - No data loss
  - Built-in load distribution capabilities
- **Disadvantages**:
  - Higher implementation complexity
  - Increased infrastructure costs
  - More complex application logic for write consistency

## Implementation Considerations

When selecting a failover strategy, consider:

1. **Recovery Time Objective (RTO)**: Maximum acceptable downtime
2. **Recovery Point Objective (RPO)**: Maximum acceptable data loss
3. **Cost constraints**: Infrastructure and operational expenses
4. **Application requirements**: Transaction volume, consistency needs
5. **Operational capabilities**: Team expertise for managing complex systems

## Advanced Techniques

For enterprise-grade high availability:
- **Database clustering** with automatic leader election
- **Multi-region replication** for disaster recovery
- **Read replicas** for distributing query load
- **Automated health checks and failover triggers**
- **Database proxy layers** to abstract connection management

By choosing the appropriate failover strategy based on your specific requirements, you can achieve the right balance of availability, data integrity, and cost efficiency for your database infrastructure.

## Sharding

### Modern Scalable Database Architecture

A modern, scalable database design typically includes:

1. **Router Layer** - Directs client requests to appropriate database shards
2. **Shards** - Horizontal partitions of the database that store subsets of data
3. **Backup Systems** - Each shard has one or more backup instances for redundancy

This architecture combines horizontal scaling with high availability. The router determines which shard should handle each request, typically using a hashing function on the data's key. Each shard maintains its own backup mechanism, providing both scalability and resiliency.

### Challenges with Sharded Architecture

- **Cross-Shard Operations**: Combining data across shards can be inefficient
- **Join Complexity**: Traditional SQL joins across shards are possible but not optimal
- **Design Implications**: Systems should minimize joins and favor key-value lookups

### Common Challenges in Sharded Systems

1. **Re-sharding**: Redistributing data when adding new shards is complex
   - When scaling up by adding more servers, data must be redistributed
   - Determining what data goes to new hosts and what gets removed from existing hosts
   - Must be done in a fault-tolerant manner

2. **Hotspots**: Uneven data access patterns (the "celebrity problem")
   - Example: In a system like IMDb, data for popular actors (e.g., Brad Pitt) receives disproportionate traffic compared to obscure actors from 1937
   - Creates imbalanced load on specific shards
   - Solution: Modern systems monitor traffic from the routing server and dynamically reshard/repartition in response to hotspots

3. **Interface Considerations**: 
   - Despite the name "NoSQL," most of these databases actually do use SQL as their primary API
   - SQL has become the "lingua franca" of databases, even in the NoSQL world
   - While joins across shards are possible, they're inefficient and should be avoided
   - Best performance comes from simple key-value lookups
   - Design recommendation: Structure data to enable key-value lookups and "fake" joins with secondary lookups

4. **Schema Flexibility**:
   - Many NoSQL systems don't require formal schemas
   - Can function as "object stores" where any data can be stored under a given key
   - Client interprets the data structure
   - Can still enforce specific data types and column names if desired, but with more flexibility

## Data Normalization vs. Denormalization

When discussing NoSQL databases, we must address data denormalization, which often plays a crucial role in their performance characteristics.

### Normalized Data Example (Restaurant Reservation System)

Consider a simple restaurant reservation system:
- Reservation table: `reservation_id`, `customer_id`, `time_slot`
- Customer table: `customer_id`, `name`, `phone_number`, `email`

In this normalized structure, to display reservation information to an end user:
1. Retrieve data from the reservation table using the reservation ID
2. Use the customer ID to look up customer information in the customer table
3. Combine the data to show complete reservation details

In a traditional relational database, this would be implemented as a JOIN operation in a single SQL query. In a NoSQL context, this might require two separate queries—one to each table—though the practical result is similar.

**Advantages**:
- Reduced storage requirements (customer information stored only once)
- Simplified updates (change customer information in one place)
- Changes to customer data automatically reflected everywhere
- Data consistency maintained

**Disadvantages**:
- Requires multiple lookups/queries to retrieve complete information
- In a horizontally distributed database, this could mean two separate database hits
- Potential performance impact at scale

### Denormalized Data Example

In a denormalized structure:
- Reservation table: `reservation_id`, `customer_id`, `name`, `phone_number`, `email`, `time_slot`

Here, customer details are duplicated in every reservation row rather than being referenced through a separate table.

**Advantages**:
- Single database query retrieves all information
- A single database hit provides everything needed to display a reservation
- Improved read performance
- Eliminated join operations
- More efficient when prioritizing performance and scaling

**Disadvantages**:
- Increased storage requirements (duplicating customer information in every row)
- Update challenges (must go through every row to change customer information)
- Difficult to perform atomic updates across all instances
- Changes to customer data likely to be eventually consistent rather than immediate
- Wasteful of space (duplicating strings of names, phone numbers, etc.)
- Higher potential for data inconsistency

## Making the Right Decision

While denormalization is often associated with NoSQL databases for performance at scale, it's not always the clear choice. When discussing this in an interview setting, demonstrate understanding of the trade-offs rather than presenting it as a binary decision.

The choice between normalized and denormalized designs should consider:

1. **Customer Experience**: What are the most common database operations in your application?
2. **Query Patterns**: Will your application frequently need to join data from multiple tables?
3. **Performance Bottlenecks**: Is the extra database query likely to become a bottleneck?
4. **Update Frequency**: How often will customer data need to be updated?
5. **Read vs. Write Ratio**: Is your application read-heavy or write-heavy?
6. **Storage Constraints**: Is storage space a significant concern?
7. **Consistency Requirements**: How important is immediate consistency of data?

**Recommended Approach**:
- Start with a normalized approach as it's simpler for handling updates and more space-efficient
- Monitor performance and identify actual bottlenecks through testing
- Apply denormalization selectively only where needed to address specific performance issues
- Consider that denormalizing can be an effective way to cut database traffic in half for operations that previously required joins between two tables

The goal isn't to choose one approach universally but to make informed decisions based on your application's specific requirements and actual observed performance characteristics.
