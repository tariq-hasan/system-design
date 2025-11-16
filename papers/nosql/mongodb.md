# MongoDB

MongoDB exemplifies a NoSQL database architecture:

- **Document-oriented database** with replica sets and primary/secondary architecture
- **Application Servers** run the `mongos` processes that distribute data
- **Replica Sets** (MongoDB's term for shards) contain:
  - A primary server handling writes and acting as the router within that shard
  - Multiple secondary servers for redundancy
  - Automatic failover with primary election if the primary fails
- **Configuration Servers** store the partitioning scheme and maintain information about which primary servers are active
  - Also have redundancy with at least three servers for high availability
  - If the primary config server fails, the remaining servers elect a new primary
- **Traffic Distribution** is based on data keys (e.g., user IDs)
  - Example: Replica set 1 handles users 0-1000, replica set 2 handles users 1000-5000, etc.
- **Geographic Distribution** across different data centers and regions for disaster resilience
- **Automatic Election** of a new primary when failures occur (typically requires at least three hosts)
