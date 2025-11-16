# Data Placement and Replication

Data placement and replication strategies determine how objects are distributed across storage infrastructure, balancing availability, durability, performance, and cost efficiency.

## Diagram Overview

```
                  ┌────────────────────────────┐
                  │      Object Key Hash       │
                  └──────────────┬─────────────┘
                                 │
                                 ▼
           ┌───────────────────────────────────────┐
           │        Consistent Hash Ring          │
           └───────────────────┬───────────────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
         ┌───────────┐  ┌───────────┐  ┌───────────┐
         │ Data Node │  │ Data Node │  │ Data Node │
         │    # 1    │  │    # 2    │  │    # 3    │
         └───────────┘  └───────────┘  └───────────┘
```

## Detailed Process Flow

### 1. Object Key Hashing

**Object Key → Hash Function**

The process begins by converting the object key to a deterministic hash value:

- System extracts the full object key
- Applies cryptographic hash function (SHA-1, MD5, etc.)
- Produces fixed-length hash value
- Normalizes hash into usable range for ring position
- Ensures uniform distribution regardless of key patterns
- Maintains consistency for repeated operations on same key
- May incorporate tenant ID or bucket for multi-tenant isolation
- Result determines initial placement in the hash space

### 2. Consistent Hash Ring Mapping

**Hash Value → Ring Position**

The system maps the hash value to a position on a conceptual ring:

- Hash space represented as a circular ring (0 to 2^n-1)
- Storage nodes are placed at specific positions on ring
- Object hash determines its position on the ring
- System finds the next node clockwise from object position
- This node becomes primary storage location
- Additional nodes (for replication) found by continuing clockwise
- Virtual nodes may be used to improve distribution
- Ring structure maintains stability during cluster changes

### 3. Failure Domain Awareness

**Ring Position → Node Selection with Constraints**

The system refines node selection to ensure fault tolerance:

- Initial node selection from consistent hash ring
- Secondary selections modified to ensure diversity across:
  - Physical servers
  - Racks or chassis
  - Power domains
  - Network switches
  - Availability zones
  - Geographic regions
- Enforces minimum distance in failure domain hierarchy
- May override initial hash placement for better protection
- Ensures no single failure can affect all replicas
- Maintains specified replication factor across domains

### 4. Data Distribution to Nodes

**Selected Nodes → Physical Storage**

The system distributes data to the selected storage nodes:

- For simple replication:
  - Identical copies sent to each selected node
  - Each node stores complete object
  - Parallel or sequential distribution based on size
  - Acknowledgment required from each node
  
- For erasure coding:
  - Object divided into k data fragments
  - Mathematical algorithm generates m parity fragments
  - Each of the k+m fragments sent to different nodes
  - Distribution considers fragment importance
  - System records fragment placement in metadata

### 5. Storage Confirmation

**Node Storage → Metadata Update**

The system confirms successful storage and updates metadata:

- Each node verifies successful write
- Storage system confirms durability guarantees met
- Metadata service updated with physical locations
- Replication status recorded
- Object becomes available for retrieval
- Background processes monitor ongoing replication health
- Success result returned to client or initiating process

## Implementation Strategies

### Consistent Hashing Implementation

Ensuring balanced distribution and minimal disruption during changes:

1. **Basic Consistent Hashing**:
   - Nodes and data mapped to points on a conceptual circle
   - Data belongs to the next node clockwise on ring
   - When nodes join/leave, only nearby data points affected
   - Provides stability compared to modulo-based hashing

2. **Virtual Node Enhancement**:
   - Each physical node represented by multiple virtual nodes
   - Typically 100-200 virtual nodes per physical node
   - Spreads responsibility more evenly across cluster
   - Improves balance during node addition/removal
   - Allows for heterogeneous nodes (different capacities)
   - Adjustable virtual node count based on node capacity

3. **Bounded Load Variations**:
   - Additional constraints to prevent any node from becoming too loaded
   - Maximum load variance parameters (e.g., no node >25% above average)
   - Dynamic virtual node adjustment based on load
   - Gradual rebalancing to maintain system performance
   - Load-aware placement decisions

### Replication Strategies

Different approaches to storing redundant data:

1. **Simple Replication**:
   - Full copies of data on multiple nodes (typically 3+)
   - Provides fast access from any replica
   - Simple recovery (direct copy from healthy replica)
   - Higher storage overhead (200%+ for 3x replication)
   - Ideal for smaller objects and frequently accessed data

2. **Erasure Coding**:
   - Data split into k data chunks and m parity chunks
   - Can recover from up to m chunk failures
   - Much better storage efficiency (e.g., 40% vs. 200% overhead)
   - Higher computational cost for encoding/decoding
   - Recovery requires accessing multiple chunks
   - Better for larger objects and less frequently accessed data

3. **Hybrid Approaches**:
   - Small objects use replication
   - Large objects use erasure coding
   - Metadata always uses replication for performance
   - Different strategies based on access patterns
   - Tiered approach based on object importance

### Failure Domain Design

Ensuring resilience against correlated failures:

1. **Hierarchical Failure Domains**:
   ```
   Region
     │
     ├─► Availability Zone
     │         │
     │         ├─► Datacenter
     │         │       │
     │         │       ├─► Room
     │         │       │     │
     │         │       │     ├─► Rack
     │         │       │     │     │
     │         │       │     │     ├─► Server
     │         │       │     │     │      │
     │         │       │     │     │      ├─► Disk
     │         │       │     │     │      │
     │         │       │     │     │      └─► SSD
     │         │       │     │     │
     │         │       │     │     └─► Network Switch
     │         │       │     │
     │         │       │     └─► Power Distribution
     │         │       │
     │         │       └─► Network Backbone
     │         │
     │         └─► Regional Network
     │
     └─► Geographic Region
   ```

2. **Replica Placement Rules**:
   - Minimum distance in failure domain tree
   - No two replicas in same failure domain at specified level
   - Prioritize diversity at higher levels of hierarchy
   - Balance between distance and performance
   - Custom rules for regulatory or business requirements

3. **Correlation Detection**:
   - Identifying less obvious correlations in failures
   - Historical failure analysis
   - Hardware batch/model diversification
   - Software version diversification
   - Maintenance schedule diversification

## Technical Optimizations

### Performance Considerations

Balancing distribution with performance requirements:

1. **Locality Optimization**:
   - Consider access patterns in placement decisions
   - Keep related objects close for common access patterns
   - Co-locate objects frequently accessed together
   - Balance between strict distribution and performance
   - Custom placement rules for special workloads

2. **Tiering Integration**:
   - Different replication strategies by storage tier
   - Hot data optimized for read performance
   - Cold data optimized for storage efficiency
   - Replica count variation by importance
   - Automatic migration between tiers based on access

3. **Geographic Distribution**:
   - Data locality for regional access patterns
   - Cross-region replication for disaster recovery
   - Latency-based replica selection for reads
   - Cost-optimized transfer for replication
   - Compliance-aware placement across jurisdictions

### Scaling and Rebalancing

Managing distribution as the system evolves:

1. **Node Addition Process**:
   - New node joins ring at specific position(s)
   - Only objects between new node and predecessor move
   - Approximately 1/N data movement for N nodes
   - Gradual data migration to maintain performance
   - Background rebalancing with throttling

2. **Node Removal/Failure**:
   - Affected data identified via ring positions
   - New replicas created from existing copies
   - Prioritization based on at-risk data (low replica count)
   - Parallel recovery for faster restoration
   - Progress tracking and reporting

3. **Cluster Expansion**:
   - Adding multiple nodes simultaneously
   - Coordinated rebalancing to minimize movements
   - Pre-calculation of expected data distribution
   - Phased approach for large expansions
   - Validation of distribution before and after

Data placement and replication form the foundation of a blob store's durability and availability guarantees, with consistent hashing providing the scalable framework necessary to manage the placement of billions of objects across a dynamic storage infrastructure.​​​​​​​​​​​​​​​​
