# Caching

## Problems Solved
- Reduces expensive disk operations
- Minimizes network latency
- Accelerates data access
- Very fast in-memory access, especially when local to application servers

## System Architecture
```
Client → Load Balancer → Application/Web Servers → Cache Servers → Database
```

## Implementation Approaches
- Embed caches within application/web servers
- Deploy dedicated cache server fleet adjacent to application servers
- Scale caching layer independently from application layer

## Caching Strategies
- Store recently accessed items
- Prioritize most popular content
- Hash requests to specific cache servers
- Assign cache servers responsibility for specific data subsets

## Optimal Use Cases
- Applications with read-heavy workloads (e.g., Wikipedia, e-commerce)
- Content delivery systems where retrieving information happens more than writing
- Systems where data changes infrequently
- When writes occur, cached data for those items must be invalidated

## Cache Invalidation
- Write operations must invalidate corresponding cached data
- Cache effectiveness decreases with write frequency
- Smart caches monitor writes and automatically invalidate affected entries

## Expiration Policy Considerations
- Balance between staleness and effectiveness
- Too long: Data becomes outdated (unacceptable for financial applications)
- Too short: Cache becomes ineffective (only caching the past second of data)
- Application-specific requirements dictate appropriate TTL values
- Smart caches can intelligently monitor updates and invalidate entries as needed

## Cache Eviction Policies

When a cache reaches capacity, decisions must be made about what to keep and what to remove. Several algorithms exist for this purpose:

### LRU (Least Recently Used)
- The most common eviction policy
- Evicts the least recently accessed items when space is needed
- Implementation:
  - Maintains a HashMap for key lookups and a doubly linked list for tracking access order
  - Most recently accessed items move to the front of the list
  - Least recently accessed items naturally move toward the end
  - When eviction is necessary, the item at the tail of the list is removed
  - Head and tail pointers allow efficient operations at both ends of the list

### LFU (Least Frequently Used)
- Tracks how often each item is accessed
- Evicts items with the lowest access frequency
- More predictive of future access patterns in some cases
- More complex than LRU, but potentially more effective for smaller caches
- Better when you need to be selective about what stays and what goes

### FIFO (First In First Out)
- Simple queue-based approach
- The first item added to the cache is the first to be evicted
- Items are evicted in the exact order they were added
- Simple implementation but less adaptive to usage patterns

## Popular Caching Technologies

### Memcached
- Simple in-memory key-value store
- Very straightforward API
- Open source, tried and true
- Has been around for a long time with proven reliability
- Simplicity is its main advantage

### Redis
- More feature-rich in-memory data store
- Extremely popular and widely used
- Battle-hardened with broad adoption
- Advanced features include:
  - Snapshots
  - Replication
  - Transaction support
  - Pub/Sub messaging system
  - Support for complex data structures beyond simple key-value pairs
- More complex than Memcached but offers greater flexibility

### Ncache
- Specifically designed for .NET environments

### Ehcache
- Java caching technology
- Essentially a distributed map implementation in Java

### ElastiCache (AWS)
- Fully managed caching service from AWS
- Supports both Redis and Memcached implementations
- Great choice for AWS-based applications
- Eliminates the need to run and maintain cache servers yourself
- Particularly efficient when used with other AWS services
- Can be placed in front of DynamoDB or alongside EC2/Lambda applications

## Common Challenges

### Hotspot Problem ("Celebrity Problem")
- Popular items create uneven load distribution
- Example: Movie database with popular actors receiving disproportionate traffic
- Solutions:
  - Dynamic load-based distribution
  - Dedicated servers for high-traffic items
  - Data replication across multiple cache servers
  - Intelligent monitoring of traffic patterns to redistribute data

### Cold-Start Problem
- Empty caches after system startup/restart
- Initial traffic surge hits underlying database
- Can potentially overwhelm and crash database
- Solutions:
  - Controlled cache warming procedures
  - Artificial traffic generation before public exposure
  - Replaying historical requests
  - Gradual traffic ramping
  - Only expose the caching layer after it's been properly primed

## Best Practices Summary
1. Implement horizontally distributed caches for read-heavy applications
2. Carefully design expiration policies based on application needs
3. Address potential hotspots through intelligent distribution
4. Develop cache warming strategies to prevent cold-start issues
5. Monitor cache hit rates and adjust strategies accordingly
6. Choose an eviction policy appropriate for your access patterns
7. Select caching technology based on your application stack and feature requirements
