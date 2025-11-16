# Object Storage Layer

The Object Storage Layer serves as the foundation of the blob store, responsible for the physical storage, retrieval, and protection of the actual binary data.

## Level 1: Key Concepts

- **Data Persistence**: Reliably stores raw binary object data at scale
- **Chunking System**: Divides large objects into manageable pieces
- **Redundancy Management**: Ensures data durability through replication or coding
- **Data Distribution**: Spreads data across physical resources for balance
- **Garbage Collection**: Reclaims space from deleted and obsolete data
- **Storage Efficiency**: Optimizes space utilization and I/O patterns

## Level 2: Implementation Details

### Physical Storage Approaches

Several implementation strategies exist for the physical storage layer:

| Approach | Description | Best For |
|----------|-------------|----------|
| **Custom Distributed File System** | Purpose-built file system designed specifically for object storage requirements | Hyperscale deployments with specialized requirements |
| **Block Storage with Metadata Layer** | Uses commodity block storage (SAN, cloud volumes) with a custom layer for object mapping | Hybrid environments leveraging existing infrastructure |
| **Commodity Servers with Direct Storage** | Uses standard servers with locally attached disks in a distributed system | Cost-efficient large-scale deployments |
| **Cloud Provider Object Storage** | Uses existing cloud storage (S3, Azure Blob) as the physical layer | Multi-cloud or hybrid architectures |

### Data Chunking Strategy

Objects are divided into chunks for several important reasons:

- **Size Management**: Handles objects much larger than typical file size limits
- **Parallel Operations**: Enables concurrent transfers of different chunks
- **Failure Isolation**: Limits the impact of storage failures to specific chunks
- **Efficient Updates**: Allows modification of specific portions of large objects
- **Deduplication Potential**: Enables identification of identical data segments

Chunks typically range from 4MB to 128MB depending on workload characteristics and are tracked in the metadata service.

### Redundancy Implementation

Data protection employs two primary strategies:

- **Replication**:
  - Multiple complete copies (typically 3+) stored on different nodes
  - Synchronous or asynchronous replication options
  - Placement across failure domains (racks, availability zones)
  - Simple implementation but higher storage overhead

- **Erasure Coding**:
  - Data split into k data chunks and m parity chunks
  - Can recover from up to m chunk failures
  - Significantly better storage efficiency (e.g., 40% vs. 200% overhead)
  - Higher computational cost for recovery operations
  - Example: 10+4 scheme requires only 14 chunks to store what would need 30 chunks in 3x replication

### Storage Tiering

Objects can be automatically moved between performance tiers:

- **Hot Storage**: High-performance media (SSDs) for frequently accessed data
- **Warm Storage**: Standard disks for moderately active data
- **Cold Storage**: High-capacity, lower-performance media for infrequent access
- **Archive Storage**: Optimized for lowest cost, with retrieval delays

Movement between tiers is managed by lifecycle policies and access patterns analysis.

## Level 3: Technical Deep Dives

### Data Placement Algorithms

Advanced algorithms govern how data is distributed across the storage infrastructure:

1. **Consistent Hashing**: Maps object chunks to storage nodes using a ring-based approach
   - Minimizes data redistribution when nodes join or leave
   - Handles heterogeneous node capacities through virtual nodes
   - Balances load across the system even with varying object sizes

2. **Failure Domain Awareness**: Strategically places replicas to maximize survivability
   - Ensures chunks are distributed across different racks, power domains, and zones
   - Incorporates network topology awareness to minimize transfer costs
   - Implements priority-based recovery to maintain redundancy levels

3. **Locality Optimization**: Places related data physically close when beneficial
   - Co-locates chunks of the same object when possible
   - Respects geographic constraints for regulatory compliance
   - Considers access patterns for performance optimization

### IO Path Optimization

The storage layer employs several techniques to maximize performance:

- **Write Optimization**:
  - Log-structured approaches for sequential writes
  - Write coalescing for small objects
  - Background compaction to optimize space
  - Delayed durability options with journaling

- **Read Optimization**:
  - Read-ahead prefetching for sequential access
  - Tiered caching (memory, SSD) for hot data
  - Parallel retrieval of chunks
  - Direct memory access for high-throughput paths

### Erasure Coding Implementation

A deeper look at erasure coding reveals its importance for large-scale systems:

```
Original Data: [D1][D2][D3][D4]

Reed-Solomon Encoding:
[D1][D2][D3][D4][P1][P2]

If D2 and D3 are lost:
[D1][??][??][D4][P1][P2]

Mathematical reconstruction:
[D1][D2][D3][D4][P1][P2]
```

The erasure coding system:
- Uses Reed-Solomon or similar algorithms to generate parity chunks
- Requires k out of (k+m) chunks to reconstruct data
- Performs encoding at ingest time
- Conducts decoding only when necessary during retrieval
- Implements efficient repair operations that minimize data transfer

### Garbage Collection and Compaction

Reclaiming space and maintaining efficiency requires specialized processes:

1. **Deletion Processing**:
   - Logical deletion (metadata update) vs. physical removal
   - Delayed space reclamation for potential undelete operations
   - Batch processing of deletion operations

2. **Background Compaction**:
   - Consolidation of partially filled storage units
   - Rebalancing after node additions or removals
   - Defragmentation to improve space utilization
   - Reorganization for optimized access patterns

3. **Tombstone Management**:
   - Tracking of deleted objects to prevent resurrection
   - Eventual purging of deletion markers
   - Consistency guarantees during cleanup operations

These processes must operate without impacting foreground operations while maintaining system integrity and performance.​​​​​​​​​​​​​​​​
