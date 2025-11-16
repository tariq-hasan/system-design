# 2. Use Cases

Consistent hashing is a foundational technique that enables scalable, fault-tolerant distributed systems across various domains. The following use cases demonstrate how different system architectures leverage consistent hashing to solve real-world problems, highlighting specific technical advantages and implementation patterns.

## Distributed Database Sharding
Partition data across multiple database instances to achieve horizontal scaling while maintaining efficient data distribution and query performance.

**The Problem**: Traditional database sharding approaches often lead to uneven data distribution, creating hot spots where some shards become overwhelmed while others remain underutilized. When resharding is required due to capacity changes, massive data movement can cause extended downtime and performance degradation.

**The Solution**: Consistent hashing determines which shard stores each record by hashing the partition key (typically a primary key or composite key) and mapping it to a node on the hash ring. Each shard is responsible for a range of hash values, and records are automatically distributed based on their hash values.

*Example*: A social media platform with 100 million users needs to shard user data across 50 database servers. Using consistent hashing on user_id ensures even distribution where each shard handles approximately 2 million users, and adding 10 new shards only requires moving about 1.67 million users (1/6th of the data) rather than reshuffling all 100 million records.

**Technical Advantages**:
- **Even Distribution**: Hash functions provide statistical uniformity, preventing hot spots that plague range-based partitioning
- **Minimal Data Movement**: Adding or removing shards only affects 1/n of the data, enabling online resharding operations
- **Predictable Performance**: Query routing is deterministic and efficient, with O(1) shard determination
- **Automatic Load Balancing**: No manual intervention required to maintain balanced data distribution

**Real-World Examples**:
- **Apache Cassandra**: Uses consistent hashing with virtual nodes to distribute data across cluster nodes. Each row is assigned to a node based on the hash of its partition key, and the system automatically handles node additions and failures.
- **Amazon DynamoDB**: Employs consistent hashing for partition management, automatically splitting and merging partitions based on throughput and storage requirements while maintaining even distribution.
- **MongoDB with Hashed Sharding**: Provides hashed shard keys as an alternative to range-based sharding, using consistent hashing principles for better data distribution.

**Design Considerations**:
- Choose partition keys with high cardinality to ensure good hash distribution
- Implement cross-shard query capabilities for operations that span multiple partitions
- Consider replication strategies that work with the consistent hashing topology
- Monitor shard utilization to detect and address any emerging imbalances

## Distributed Caching
Distribute cache entries across multiple cache servers to scale memory capacity while maintaining high cache hit rates and consistent performance.

**The Problem**: As applications scale, single cache servers become bottlenecks due to memory limitations and request volume. Traditional approaches like modulo hashing cause cache stampedes when servers are added or removed, as most cache keys get remapped to different servers, effectively invalidating the entire cache.

**The Solution**: Hash cache keys using consistent hashing to determine which cache server should store each entry. When cache topology changes, only keys that were stored on affected servers need to be invalidated, preserving the majority of cached data.

*Example*: An e-commerce platform uses 20 Memcached servers to cache product information, user sessions, and search results. When adding 5 new servers during peak traffic, consistent hashing ensures that only 20% of cache entries (those that migrate to new servers) become cache misses, while 80% remain valid, maintaining system performance during scaling.

**Technical Advantages**:
- **Consistent Cache Hit Rates**: Server changes only affect a small portion of cached data, maintaining overall cache efficiency
- **Minimal Cache Invalidation**: Adding servers doesn't trigger a complete cache flush, preserving valuable cached data
- **Transparent Scaling**: Cache clients can add or remove servers without application-level changes
- **Improved Availability**: Server failures are gracefully handled by redistributing load to remaining servers

**Real-World Examples**:
- **Memcached with Consistent Hashing Clients**: Libraries like libmemcached implement consistent hashing to distribute keys across Memcached servers, providing stable cache behavior during topology changes.
- **Redis Cluster**: Uses a slot-based approach inspired by consistent hashing, with 16,384 hash slots distributed across cluster nodes for automatic sharding and migration.
- **Hazelcast**: Implements consistent hashing for distributed cache partitioning, providing both data distribution and fault tolerance.

**Design Considerations**:
- Implement cache warming strategies for new servers to quickly build up cache hit rates
- Use virtual nodes to ensure better load distribution across cache servers
- Consider cache replication for high availability of critical cached data
- Monitor cache hit rates and server utilization to optimize the number of virtual nodes

## Load Balancing with Session Affinity
Route user requests to the same backend server consistently to maintain session state while providing graceful failover when servers become unavailable.

**The Problem**: Stateful applications that maintain user sessions in server memory need to route each user to the same server for the duration of their session. Traditional round-robin or random load balancing breaks session affinity, while static session-to-server mappings don't handle server failures gracefully.

**The Solution**: Hash user identifiers (session IDs, user IDs, or client IP addresses) to consistently route requests to the same backend server. When a server fails, affected users are automatically routed to the next available server on the hash ring.

*Example*: An online gaming platform with 50 game servers needs to maintain player sessions containing game state, inventory, and active connections. Using consistent hashing on player_id ensures each player always connects to the same server, while server failures only affect the players assigned to that specific server (2% of the user base), who can be gracefully migrated to alternative servers.

**Technical Advantages**:
- **Session Persistence**: Users consistently reach the same server, maintaining session state without external storage
- **Graceful Failover**: Server failures only affect users assigned to that server, with automatic redirection to healthy servers
- **Simplified State Management**: Applications can use local memory for session storage without complex distributed session mechanisms
- **Improved Performance**: Session data locality reduces the need for external session stores and database lookups

**Real-World Examples**:
- **Web Application Load Balancers**: HAProxy and NGINX can be configured with consistent hashing for sticky sessions, maintaining user affinity across server restarts and scaling events.
- **Gaming Session Management**: Multiplayer game servers use consistent hashing to assign players to game instances, ensuring stable connections and reducing latency.
- **WebSocket Connection Management**: Real-time applications route WebSocket connections consistently to maintain persistent connections and message ordering.

**Design Considerations**:
- Implement session migration mechanisms for handling server failures
- Consider using hybrid approaches that combine consistent hashing with external session storage for critical applications
- Monitor session distribution to ensure balanced load across servers
- Plan for gradual traffic shifting when adding new servers to avoid overwhelming them

## Content Distribution
Distribute content objects across CDN edge servers or storage nodes to optimize content delivery and minimize data movement during infrastructure changes.

**The Problem**: Content delivery networks and distributed storage systems need to determine where to store content objects to optimize access patterns, minimize bandwidth usage, and provide fault tolerance. Traditional approaches often result in suboptimal placement and expensive data movement when infrastructure changes.

**The Solution**: Hash content identifiers (URLs, content hashes, or object keys) to determine which edge servers or storage nodes should cache or store each content object. This ensures deterministic placement that all system components can independently calculate.

*Example*: A video streaming CDN with 500 edge servers worldwide uses consistent hashing on video content IDs. When 50 new edge servers are added to handle increased traffic, only 9% of content needs to be redistributed (50/550), while 91% remains optimally placed, minimizing bandwidth usage and maintaining cache hit rates.

**Technical Advantages**:
- **Efficient Content Location**: Any system component can independently determine where content is stored without central coordination
- **Minimal Data Movement**: Infrastructure changes only require moving content from a small subset of locations
- **Predictable Caching Behavior**: Content placement is deterministic and consistent across all edge locations
- **Improved Cache Efficiency**: Content objects are consistently placed, avoiding duplicate caching across multiple locations

**Real-World Examples**:
- **Content Delivery Networks**: Akamai and Cloudflare use consistent hashing principles to distribute content across global edge servers, optimizing cache hit rates and reducing origin server load.
- **Distributed File Systems**: Systems like GlusterFS and Ceph use consistent hashing for data placement across storage nodes, providing fault tolerance and even distribution.
- **Object Storage Systems**: Amazon S3 and similar services use consistent hashing for internal data placement across storage clusters.

**Design Considerations**:
- Implement replication strategies that work with consistent hashing topology
- Consider geographic factors when implementing consistent hashing for global content distribution
- Use virtual nodes to improve load balancing across storage nodes with different capacities
- Monitor content access patterns to optimize cache policies and placement strategies

## Microservice Routing
Route requests to service instances based on request characteristics to ensure consistent routing behavior and enable stateful service patterns.

**The Problem**: Microservice architectures with multiple instances of the same service need intelligent routing that considers request characteristics, maintains consistency for stateful operations, and adapts gracefully to service scaling events without disrupting ongoing requests.

**The Solution**: Hash request attributes (tenant IDs, user IDs, or resource identifiers) to select target service instances consistently. This ensures that related requests are routed to the same service instance while distributing load evenly across available instances.

*Example*: A multi-tenant SaaS platform with 100 service instances uses consistent hashing on tenant_id to ensure all requests from the same tenant reach the same service instance. This enables tenant-specific caching, connection pooling, and state management while maintaining even load distribution across instances.

**Technical Advantages**:
- **Consistent Routing**: Related requests are deterministically routed to the same service instance
- **Smooth Scaling**: Adding or removing service instances doesn't disrupt the majority of existing request flows
- **Stateful Service Support**: Services can maintain local state or caches for improved performance
- **Improved Resource Utilization**: Even distribution prevents some instances from being overwhelmed while others remain idle

**Real-World Examples**:
- **API Gateways**: Kong and Ambassador can use consistent hashing for upstream service selection, providing sticky routing based on request headers or parameters.
- **Service Meshes**: Istio and Linkerd support consistent hashing for load balancing, enabling advanced routing patterns for microservice architectures.
- **Event Processing**: Apache Kafka uses consistent hashing principles for partition assignment, ensuring related events are processed by the same consumer instances.

**Design Considerations**:
- Choose appropriate hash keys that provide good distribution while maintaining routing consistency
- Implement health checking and circuit breaker patterns to handle service instance failures
- Consider using weighted consistent hashing for services with different capacity requirements
- Monitor request distribution to ensure balanced load across service instances

## Peer-to-Peer Systems
Distribute data and operational responsibility across peer nodes in decentralized networks, enabling scalable and fault-tolerant distributed systems without central coordination.

**The Problem**: Peer-to-peer systems need to distribute data and coordinate operations across numerous autonomous nodes without central authority. Traditional approaches require complex coordination protocols and often create bottlenecks or single points of failure.

**The Solution**: Use consistent hashing to create a distributed hash table (DHT) where each peer is responsible for a portion of the key space. Data objects are placed and located based on their hash values, and peers can join or leave the network with minimal disruption.

*Example*: A decentralized file storage network with 10,000 peer nodes uses consistent hashing on file content hashes. Each peer stores files for a specific range of hash values, and when 1,000 new peers join the network, only about 9% of files need to be redistributed, while the system's capacity increases proportionally.

**Technical Advantages**:
- **Decentralized Operation**: No central authority or coordination required for data placement and retrieval
- **Scalable Architecture**: System capacity grows linearly with the number of participating peers
- **Fault Tolerance**: Peer failures are handled automatically through data redistribution and replication
- **Efficient Data Location**: Any peer can determine data location without global knowledge or complex search algorithms

**Real-World Examples**:
- **BitTorrent DHT**: Uses consistent hashing to distribute tracker information across peer nodes, enabling tracker-less torrent coordination and improving system resilience.
- **Chord Protocol**: A fundamental DHT algorithm that uses consistent hashing with finger tables to enable efficient routing in O(log n) hops across the peer network.
- **Kademlia**: Used in various P2P applications including BitTorrent and IPFS, employs consistent hashing principles for node organization and data location.

**Design Considerations**:
- Implement efficient routing algorithms (finger tables, neighbor sets) for fast data location
- Design replication strategies to handle peer churn and provide data availability
- Consider using virtual nodes to improve load balancing across peers with different capabilities
- Implement peer discovery and bootstrap mechanisms for network participation

These use cases demonstrate how consistent hashing serves as a foundational building block for creating scalable, resilient distributed systems across diverse application domains. The technique's ability to minimize disruption during topology changes while maintaining predictable data placement makes it invaluable for modern cloud-native and distributed architectures.
