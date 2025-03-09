# Caching

## Problems Solved
- Reduces expensive disk operations
- Minimizes network latency
- Accelerates data access

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
- Applications with read-heavy workloads
- Content delivery systems (e.g., Wikipedia, e-commerce)
- Systems where data changes infrequently

## Cache Invalidation
- Write operations must invalidate corresponding cached data
- Cache effectiveness decreases with write frequency
- Smart caches monitor writes and automatically invalidate affected entries

## Expiration Policy Considerations
- Balance between staleness and effectiveness
- Too long: Data becomes outdated (unacceptable for financial applications)
- Too short: Cache becomes ineffective
- Application-specific requirements dictate appropriate TTL values

## Common Challenges

### Hotspot Problem ("Celebrity Problem")
- Popular items create uneven load distribution
- Example: Movie database with popular actors receiving disproportionate traffic
- Solutions:
  - Dynamic load-based distribution
  - Dedicated servers for high-traffic items
  - Data replication across multiple cache servers

### Cold-Start Problem
- Empty caches after system startup/restart
- Initial traffic surge hits underlying database
- Can potentially overwhelm and crash database
- Solutions:
  - Controlled cache warming procedures
  - Artificial traffic generation before public exposure
  - Replaying historical requests
  - Gradual traffic ramping

## Best Practices Summary
1. Implement horizontally distributed caches for read-heavy applications
2. Carefully design expiration policies based on application needs
3. Address potential hotspots through intelligent distribution
4. Develop cache warming strategies to prevent cold-start issues
5. Monitor cache hit rates and adjust strategies accordingly
