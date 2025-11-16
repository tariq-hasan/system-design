# Cassandra

- Wide-column store with ring architecture
  - Addresses single point of failure using a different approach
  - Any node can serve as the primary interface point for the application
  - Data is replicated across multiple nodes in the ring
  - Trades consistency for availability (eventual consistency model)
  - Eliminates the need for dedicated primary servers, reducing maintenance overhead
