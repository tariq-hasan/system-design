# Consistent Hashing

## Table of Contents
- [1. Overview](#1-overview)
- [2. Use Cases](#2-use-cases)
- [3. Problem Statement](#3-problem-statement)
- [4. Traditional Hashing Limitations](#4-traditional-hashing-limitations)
- [5. Consistent Hashing Solution](#5-consistent-hashing-solution)
- [6. Core Components & Algorithm](#6-core-components--algorithm)
  - [6.1 Hash Ring Construction](#61-hash-ring-construction)
  - [6.2 Node Placement](#62-node-placement)
  - [6.3 Key Assignment](#63-key-assignment)
  - [6.4 Node Addition/Removal](#64-node-additionremoval)
- [7. Virtual Nodes (Vnodes)](#7-virtual-nodes-vnodes)
  - [7.1 Problem with Basic Consistent Hashing](#71-problem-with-basic-consistent-hashing)
  - [7.2 Virtual Node Solution](#72-virtual-node-solution)
  - [7.3 Virtual Node Configuration](#73-virtual-node-configuration)
- [8. Implementation Details](#8-implementation-details)
  - [8.1 Hash Function Selection](#81-hash-function-selection)
  - [8.2 Data Structures](#82-data-structures)
  - [8.3 Node Discovery & Membership](#83-node-discovery--membership)
  - [8.4 Replication Strategy](#84-replication-strategy)
- [9. Load Balancing Optimization](#9-load-balancing-optimization)
  - [9.1 Heterogeneous Node Handling](#91-heterogeneous-node-handling)
  - [9.2 Hot Spot Mitigation](#92-hot-spot-mitigation)
  - [9.3 Dynamic Weight Adjustment](#93-dynamic-weight-adjustment)
- [10. Failure Handling & Recovery](#10-failure-handling--recovery)
  - [10.1 Node Failure Detection](#101-node-failure-detection)
  - [10.2 Temporary vs Permanent Failures](#102-temporary-vs-permanent-failures)
  - [10.3 Data Recovery Mechanisms](#103-data-recovery-mechanisms)
  - [10.4 Consistent Hashing with Replication](#104-consistent-hashing-with-replication)
- [11. Performance Characteristics](#11-performance-characteristics)
  - [11.1 Time Complexity](#111-time-complexity)
  - [11.2 Space Complexity](#112-space-complexity)
  - [11.3 Network Overhead](#113-network-overhead)
  - [11.4 Cache Performance](#114-cache-performance)
- [12. Advanced Variations](#12-advanced-variations)
  - [12.1 Bounded Load Consistent Hashing](#121-bounded-load-consistent-hashing)
  - [12.2 Consistent Hashing with Minimal Disruption](#122-consistent-hashing-with-minimal-disruption)
  - [12.3 Multi-Level Consistent Hashing](#123-multi-level-consistent-hashing)
  - [12.4 Consistent Hashing with Preferences](#124-consistent-hashing-with-preferences)
- [13. Real-World Implementation Challenges](#13-real-world-implementation-challenges)
  - [13.1 Configuration Management](#131-configuration-management)
  - [13.2 Monitoring & Observability](#132-monitoring--observability)
  - [13.3 Data Migration](#133-data-migration)
  - [13.4 Testing Strategies](#134-testing-strategies)
- [14. System Integration Patterns](#14-system-integration-patterns)
  - [14.1 Database Sharding](#141-database-sharding)
  - [14.2 Distributed Caching](#142-distributed-caching)
  - [14.3 Load Balancing](#143-load-balancing)
  - [14.4 Content Delivery Networks](#144-content-delivery-networks)
- [15. Comparison with Alternatives](#15-comparison-with-alternatives)
  - [15.1 vs Range-Based Partitioning](#151-vs-range-based-partitioning)
  - [15.2 vs Directory-Based Partitioning](#152-vs-directory-based-partitioning)
  - [15.3 vs Rendezvous Hashing](#153-vs-rendezvous-hashing)
  - [15.4 Trade-off Analysis](#154-trade-off-analysis)
- [16. Industry Examples](#16-industry-examples)
- [17. Interview Discussion Points](#17-interview-discussion-points)
- [18. System Design Diagrams](#18-system-design-diagrams)
  - [18.1 Basic Hash Ring](#181-basic-hash-ring)
  - [18.2 Virtual Nodes Distribution](#182-virtual-nodes-distribution)
  - [18.3 Node Addition/Removal Flow](#183-node-additionremoval-flow)
  - [18.4 Replication with Consistent Hashing](#184-replication-with-consistent-hashing)

## 1. Overview

**Consistent Hashing** is a distributed systems technique that solves the problem of distributing data across multiple nodes in a way that minimizes data movement when nodes are added or removed from the system.

**Key Properties:**
- **Minimal Disruption**: Only K/n keys need to be remapped when nodes change (K = total keys, n = number of nodes)
- **Load Distribution**: Attempts to distribute load evenly across nodes
- **Scalability**: Supports dynamic addition and removal of nodes
- **Fault Tolerance**: Gracefully handles node failures

**Core Concept:**
- Maps both data keys and node identifiers to points on a circular hash space (hash ring)
- Data is assigned to the first node found by moving clockwise around the ring
- Node changes only affect data between the changed node and its predecessor

**When to Use:**
- Distributed databases (Cassandra, DynamoDB, Riak)
- Distributed caching systems (Memcached clusters, Redis clusters)
- Load balancers with sticky sessions
- Content delivery networks
- Peer-to-peer systems
- Microservice routing

## 2. Use Cases

### 2.1 Distributed Database Sharding
- **Problem**: Distribute data across database shards without hot spots
- **Solution**: Use consistent hashing to determine which shard stores each record
- **Benefits**: Even distribution, minimal data movement during resharding
- **Examples**: Cassandra's partitioning, Amazon DynamoDB

### 2.2 Distributed Caching
- **Problem**: Distribute cache entries across multiple cache servers
- **Solution**: Hash cache keys to determine target server
- **Benefits**: Consistent cache hit rates, minimal cache misses during node changes
- **Examples**: Memcached with consistent hashing clients, Redis Cluster

### 2.3 Load Balancing with Session Affinity
- **Problem**: Route user requests to same server for session stickiness
- **Solution**: Hash user identifiers to consistently route to same server
- **Benefits**: Session persistence, graceful handling of server changes
- **Examples**: Web application load balancers, gaming session management

### 2.4 Content Distribution
- **Problem**: Distribute content across CDN edge servers or storage nodes
- **Solution**: Hash content identifiers to determine storage location
- **Benefits**: Efficient content location, minimal movement during node changes
- **Examples**: Content delivery networks, distributed file systems

### 2.5 Microservice Routing
- **Problem**: Route requests to service instances based on request characteristics
- **Solution**: Hash request attributes to select target service instance
- **Benefits**: Consistent routing, smooth scaling of service instances
- **Examples**: API gateways, service meshes

### 2.6 Peer-to-Peer Systems
- **Problem**: Distribute data and responsibility across peer nodes
- **Solution**: Use consistent hashing for data placement and routing
- **Benefits**: Decentralized operation, efficient data location
- **Examples**: BitTorrent DHT, Chord protocol, Kademlia

## 3. Problem Statement

### 3.1 The Distributed Data Placement Challenge
When building distributed systems, we need to solve the fundamental problem of **where to place data** across multiple nodes while satisfying these requirements:

- **Even Distribution**: Data should be distributed roughly evenly across all nodes
- **Minimal Movement**: Adding or removing nodes should move as little data as possible
- **Efficient Lookup**: Finding where data is stored should be fast (preferably O(1) or O(log n))
- **Fault Tolerance**: System should continue operating when nodes fail
- **Scalability**: Should handle dynamic growth and shrinkage of the cluster

### 3.2 Real-World Scenario
Consider a distributed cache system with 1 billion cache entries distributed across 1000 servers:

- **Initial State**: Each server holds ~1 million entries
- **Adding One Server**: Ideally, each server should now hold ~999,000 entries
- **Challenge**: How do we redistribution only ~1 million entries (1/1000th) instead of potentially having to rehash and move all 1 billion entries?

### 3.3 Business Impact
Poor data distribution strategies can lead to:
- **Service Outages**: Massive data movement during scaling events
- **Performance Degradation**: Hot spots and uneven load distribution
- **Increased Costs**: Over-provisioning to handle redistribution overhead
- **Operational Complexity**: Complex manual intervention required for scaling

## 4. Traditional Hashing Limitations

### 4.1 Simple Modulo Hashing
```
node = hash(key) % number_of_nodes
```

**Problems:**
- **Massive Redistribution**: When nodes change, almost all keys get remapped
- **Cascading Failures**: Single node failure can trigger system-wide redistribution
- **Poor Scalability**: Cannot add/remove nodes without significant disruption

**Example Impact:**
- 4 nodes → 5 nodes: 80% of keys need to move
- 5 nodes → 4 nodes: 75% of keys need to move

### 4.2 Range-Based Partitioning
**Approach**: Assign key ranges to nodes (e.g., A-F → Node1, G-M → Node2)

**Problems:**
- **Hot Spots**: Uneven data distribution based on key patterns
- **Manual Management**: Requires manual range assignment and rebalancing
- **Complex Splits**: Splitting busy ranges is operationally complex

### 4.3 Directory-Based Partitioning
**Approach**: Maintain a lookup table mapping keys/ranges to nodes

**Problems:**
- **Single Point of Failure**: Directory service becomes bottleneck
- **Consistency Challenges**: Keeping directory updated across all clients
- **Scalability Limits**: Directory size grows with data size or becomes distributed system problem itself

### 4.4 Why These Approaches Fail at Scale
- **Operational Overhead**: Manual intervention required for common operations
- **Availability Impact**: System disruption during routine maintenance
- **Resource Waste**: Significant CPU/network overhead for redistribution
- **Complexity**: Difficult to reason about and debug in production

## 5. Consistent Hashing Solution

### 5.1 Core Innovation
Instead of mapping keys directly to nodes, consistent hashing:
1. **Creates a Hash Ring**: Maps both keys and nodes to points on a circular hash space
2. **Assigns Keys Clockwise**: Each key belongs to the first node found moving clockwise
3. **Localizes Changes**: Node additions/removals only affect adjacent regions

### 5.2 Mathematical Foundation
- **Hash Space**: Typically 0 to 2^160 - 1 (using SHA-1) or 0 to 2^256 - 1 (using SHA-256)
- **Circular Mapping**: Hash space wraps around (2^160 - 1 + 1 = 0)
- **Uniform Distribution**: Good hash functions distribute nodes and keys uniformly

### 5.3 Key Properties
- **Monotonicity**: Adding nodes doesn't change existing key-node mappings except for keys that should move to the new node
- **Balance**: Keys are distributed roughly evenly across nodes (with virtual nodes)
- **Spread**: A key is mapped to at most a constant number of nodes when views differ slightly
- **Load**: No node is assigned significantly more keys than others

### 5.4 Redistribution Efficiency
- **Optimal Movement**: Only K/n keys move when adding/removing nodes (where K = total keys, n = nodes)
- **Localized Impact**: Changes only affect keys between changed node and its predecessor
- **Incremental Updates**: Can update mappings gradually rather than all at once

## 6. Core Components & Algorithm

### 6.1 Hash Ring Construction
```
Hash Space: [0, 2^160 - 1] (circular)

Step 1: Choose hash function (SHA-1, MD5, etc.)
Step 2: Define ring boundaries (0 wraps to 2^160 - 1)
Step 3: Initialize empty ring structure
```

**Implementation Considerations:**
- **Hash Function Choice**: Cryptographic hash functions provide good distribution
- **Ring Size**: Large enough to minimize collisions (2^128 or 2^160 typical)
- **Data Structure**: Sorted map/tree for efficient lookups

### 6.2 Node Placement
```
For each node N:
  1. Compute hash(node_identifier) → position on ring
  2. Insert node at computed position
  3. Update ring's sorted structure
```

**Node Identification Strategies:**
- **IP:Port**: `hash("192.168.1.100:6379")`
- **Unique ID**: `hash("node-uuid-12345")`
- **Composite**: `hash("datacenter1-rack2-server5")`

**Placement Considerations:**
- **Deterministic**: Same node ID always maps to same position
- **Collision Handling**: Different nodes must not hash to same position
- **Distribution**: Nodes should be reasonably spread around ring

### 6.3 Key Assignment
```
For each key K:
  1. Compute hash(key) → position on ring
  2. Find first node clockwise from key position
  3. Assign key to that node

Lookup Algorithm:
  1. position = hash(key)
  2. node = ring.successor(position)  // First node >= position
  3. if no successor found: node = ring.first()  // Wrap around
```

**Key Identification:**
- **Database Records**: `hash(primary_key)`
- **Cache Entries**: `hash(cache_key)`
- **User Sessions**: `hash(user_id)`

### 6.4 Node Addition/Removal
**Adding Node N:**
```
1. Compute position = hash(N)
2. Find successor node S at ring.successor(position)
3. Insert N at position
4. Move keys in range (predecessor(N), N] from S to N
```

**Removing Node N:**
```
1. Find successor node S = ring.successor(N)
2. Move all keys from N to S
3. Remove N from ring
```

**Movement Calculation:**
- **Keys Affected**: Only keys in range between new node and its predecessor
- **Percentage Moved**: Approximately 1/n of total keys (where n = number of nodes)
- **Direction**: Keys always move from successor to new node (addition) or from removed node to successor (removal)

## 7. Virtual Nodes (Vnodes)

### 7.1 Problem with Basic Consistent Hashing
**Uneven Distribution Issues:**
- Random node placement can create uneven segments
- Some nodes may get 2-3x more data than others
- Node failures can create very large segments
- Adding nodes may not significantly reduce load on heavily loaded nodes

**Example:**
```
4 nodes on ring with poor distribution:
- Node A: 50% of keys
- Node B: 30% of keys  
- Node C: 15% of keys
- Node D: 5% of keys
```

### 7.2 Virtual Node Solution
**Concept**: Each physical node is represented by multiple virtual nodes distributed around the ring.

**Benefits:**
- **Better Distribution**: More opportunities for even key distribution
- **Smoother Scaling**: Adding node affects multiple ring segments
- **Improved Fault Tolerance**: Node failure impact spread across multiple segments
- **Heterogeneous Support**: Different nodes can have different numbers of virtual nodes

### 7.3 Virtual Node Configuration
**Typical Setup:**
```
Physical Node A → Virtual Nodes: A1, A2, A3, ..., A_v
Physical Node B → Virtual Nodes: B1, B2, B3, ..., B_v

Where v = virtual nodes per physical node (typically 100-1000)
```

**Virtual Node Placement:**
```
For physical node N with v virtual nodes:
  For i = 1 to v:
    vnode_id = N + ":" + i  // e.g., "node1:1", "node1:2"
    position = hash(vnode_id)
    place virtual node at position on ring
```

**Load Distribution Math:**
- **Without Virtual Nodes**: Load variance can be O(log n)
- **With Virtual Nodes**: Load variance reduces to O(sqrt(log n / v))
- **Rule of Thumb**: 100-500 virtual nodes per physical node provides good balance

**Memory vs Distribution Trade-off:**
- **More Virtual Nodes**: Better distribution, more memory for ring metadata
- **Fewer Virtual Nodes**: Less memory, potentially uneven distribution
- **Sweet Spot**: 150-300 virtual nodes per physical node for most applications

## 8. Implementation Details

### 8.1 Hash Function Selection
**Requirements:**
- **Uniform Distribution**: Keys should be evenly distributed
- **Deterministic**: Same input always produces same output
- **Fast Computation**: Low latency for lookups
- **Good Avalanche Effect**: Small input changes cause large output changes

**Popular Choices:**
```
SHA-1: Good distribution, 160-bit output, slower
MD5: Fast, 128-bit output, sufficient for most use cases
MurmurHash: Very fast, good distribution, non-cryptographic
xxHash: Extremely fast, excellent distribution
CRC32: Fast but poor distribution for some patterns
```

**Performance Comparison:**
- **MD5**: ~500MB/s, good enough for most applications
- **MurmurHash3**: ~2GB/s, excellent for high-throughput systems
- **xxHash**: ~5GB/s, best for performance-critical applications

### 8.2 Data Structures
**Ring Representation:**
```
Option 1: Sorted Array
- Simple implementation
- O(log n) lookups with binary search
- O(n) insertion/deletion

Option 2: Balanced Tree (Red-Black, AVL)
- O(log n) for all operations
- More complex implementation
- Good for frequent topology changes

Option 3: Skip List
- Probabilistic data structure
- O(log n) expected performance
- Simpler than balanced trees
```

**Recommended Implementation:**
```java
class ConsistentHashRing {
    private TreeMap<Long, Node> ring = new TreeMap<>();
    private int virtualNodesPerNode = 150;
    
    public void addNode(Node node) {
        for (int i = 0; i < virtualNodesPerNode; i++) {
            String vnodeId = node.getId() + ":" + i;
            long hash = hash(vnodeId);
            ring.put(hash, node);
        }
    }
    
    public Node getNode(String key) {
        long hash = hash(key);
        Map.Entry<Long, Node> entry = ring.ceilingEntry(hash);
        if (entry == null) {
            entry = ring.firstEntry(); // Wrap around
        }
        return entry.getValue();
    }
}
```

### 8.3 Node Discovery & Membership
**Challenges:**
- **Dynamic Membership**: Nodes join and leave dynamically
- **Consistency**: All nodes need consistent view of ring topology
- **Failure Detection**: Distinguish between network partitions and node failures

**Solutions:**
```
Option 1: Centralized Coordinator
- Single source of truth for ring topology
- Simple to implement and understand
- Single point of failure

Option 2: Gossip Protocol
- Nodes exchange topology information periodically
- Eventually consistent
- Resilient to failures

Option 3: Consensus System (Raft, etcd)
- Strongly consistent topology updates
- Complex but reliable
- Higher operational overhead
```

### 8.4 Replication Strategy
**N-Way Replication:**
```
For replication factor R:
  Primary node = successor(hash(key))
  Replica nodes = next R-1 successors on ring
  
Example with R=3:
  Key X maps to position P
  Replica 1: first node >= P
  Replica 2: second node >= P  
  Replica 3: third node >= P
```

**Coordination Strategies:**
- **Synchronous Replication**: Wait for all replicas before acknowledging write
- **Asynchronous Replication**: Acknowledge after primary write, replicate in background
- **Quorum-Based**: Require majority of replicas for reads/writes

## 9. Load Balancing Optimization

### 9.1 Heterogeneous Node Handling
**Problem**: Different nodes have different capacities (CPU, memory, storage)

**Solutions:**
```
Weighted Virtual Nodes:
- High-capacity node: 300 virtual nodes
- Medium-capacity node: 200 virtual nodes  
- Low-capacity node: 100 virtual nodes

Capacity-Based Assignment:
weight = node_capacity / average_capacity
virtual_nodes = base_virtual_nodes * weight
```

**Dynamic Weight Adjustment:**
```
Monitor node metrics:
- CPU utilization
- Memory usage
- Disk I/O
- Network bandwidth

Adjust virtual node count based on:
- Current load
- Historical performance
- SLA requirements
```

### 9.2 Hot Spot Mitigation
**Hot Key Detection:**
```
Track key access patterns:
- Request frequency per key
- Temporal access patterns
- Geographic access patterns

Hot key indicators:
- >1% of total requests to single key
- Sustained high access rate
- Disproportionate resource usage
```

**Mitigation Strategies:**
```
1. Key Splitting:
   - Split hot key across multiple nodes
   - Use secondary hash for distribution
   
2. Caching Layer:
   - Cache hot keys in memory
   - Use dedicated cache nodes
   
3. Load Shedding:
   - Rate limit access to hot keys
   - Implement backpressure mechanisms
```

### 9.3 Dynamic Weight Adjustment
**Real-Time Adaptation:**
```
def adjust_weights():
    for node in nodes:
        current_load = measure_load(node)
        target_load = cluster_average_load
        
        if current_load > target_load * 1.2:
            reduce_virtual_nodes(node, 10%)
        elif current_load < target_load * 0.8:
            increase_virtual_nodes(node, 10%)
```

**Gradual Adjustment:**
- **Small Changes**: Adjust 5-10% at a time to avoid oscillation
- **Cooldown Period**: Wait between adjustments to observe effects
- **Hysteresis**: Different thresholds for increasing vs decreasing

## 10. Failure Handling & Recovery

### 10.1 Node Failure Detection
**Detection Mechanisms:**
```
Heartbeat Monitoring:
- Periodic health checks (every 5-30 seconds)
- Timeout-based failure detection
- False positive rate considerations

Gossip-Based Detection:
- Nodes exchange status information
- Phi Accrual Failure Detector
- Adaptive timeout based on network conditions

Application-Level Monitoring:
- Request success/failure rates
- Response time degradation
- Error pattern analysis
```

**Failure Detection Tuning:**
- **Fast Detection**: Lower timeouts, higher false positive rate
- **Stable Detection**: Higher timeouts, more reliable but slower
- **Adaptive**: Adjust based on network conditions and historical data

### 10.2 Temporary vs Permanent Failures
**Temporary Failure Handling:**
```
Node appears failed but may recover:
- Network partition
- Temporary overload
- Brief maintenance

Strategy:
- Keep node in ring for grace period
- Route traffic to replicas
- Monitor for recovery
```

**Permanent Failure Handling:**
```
Node definitively failed:
- Hardware failure  
- Extended downtime
- Administrative removal

Strategy:
- Remove from ring immediately
- Redistribute data to successors
- Update cluster membership
```

### 10.3 Data Recovery Mechanisms
**Recovery After Node Addition:**
```
When failed node returns:
1. Determine data that should belong to returning node
2. Identify current owners of that data
3. Transfer data back to returning node
4. Update routing to include returning node
```

**Anti-Entropy Mechanisms:**
```
Merkle Trees:
- Build hash trees of data ranges
- Compare trees between replicas
- Identify and sync differences

Read Repair:
- Detect inconsistencies during reads
- Sync inconsistent replicas
- Return consistent data to client

Hinted Handoff:
- Store writes for temporarily failed nodes
- Replay writes when node recovers
- Maintain write availability during failures
```

### 10.4 Consistent Hashing with Replication
**Replica Placement:**
```
For key K with replication factor N:
  primary_position = hash(K)
  replicas = []
  
  current_position = primary_position
  for i in range(N):
    node = ring.successor(current_position)
    replicas.append(node)
    current_position = node.position + 1  // Next position
```

**Consistency Models:**
```
Strong Consistency:
- Synchronous replication to all replicas
- High latency, guaranteed consistency

Eventual Consistency:
- Asynchronous replication
- Lower latency, temporary inconsistencies

Tunable Consistency:
- Read/Write quorums (R + W > N)
- Balance consistency vs availability
```

## 11. Performance Characteristics

### 11.1 Time Complexity
**Basic Operations:**
```
Key Lookup: O(log V)
- V = total virtual nodes in system
- Binary search in sorted ring structure

Node Addition: O(V/N + K/N)
- V/N = virtual nodes to add
- K/N = keys to redistribute

Node Removal: O(V/N + K/N)
- V/N = virtual nodes to remove  
- K/N = keys to redistribute

Ring Rebalancing: O(V log V)
- Rare operation, typically done offline
```

**With Optimizations:**
```
Cached Lookups: O(1)
- Cache recent key-to-node mappings
- LRU eviction for cache management

Batch Operations: O(B log V)
- Process multiple keys together
- Amortize lookup costs
```

### 11.2 Space Complexity
**Memory Requirements:**
```
Ring Metadata: O(V)
- Store virtual node positions and mappings
- Typically 8-16 bytes per virtual node

Key Mapping Cache: O(C)
- C = cache size
- Trade memory for lookup performance

Replication Metadata: O(V * R)
- R = replication factor
- Track replica locations
```

**Typical Memory Usage:**
```
1000 physical nodes × 150 virtual nodes = 150K entries
150K entries × 16 bytes = 2.4 MB ring metadata
Additional cache: 10-100 MB
Total: ~100 MB for large cluster
```

### 11.3 Network Overhead
**Steady State:**
```
Gossip Protocol: O(N) messages per round
- Each node communicates with subset of other nodes
- Bandwidth: ~1KB per node per second

Heartbeat: O(N) messages per interval
- Direct health checking
- Bandwidth: ~100 bytes per node per second
```

**During Changes:**
```
Node Addition/Removal:
- Ring topology updates: O(N) messages
- Data migration: depends on data size
- Typically completes in seconds to minutes

Failure Detection:
- Immediate gossip propagation
- Full cluster awareness in O(log N) rounds
```

### 11.4 Cache Performance
**Lookup Caching:**
```
Cache Hit Rate: 90-99% typical
- Depends on key access patterns
- Higher hit rates for skewed distributions

Cache Efficiency:
- LRU eviction works well for most workloads
- Consider workload-specific policies

Memory vs Performance:
- 1MB cache: ~65K cached mappings
- 10MB cache: ~650K cached mappings
- Diminishing returns beyond working set size
```

## 12. Advanced Variations

### 12.1 Bounded Load Consistent Hashing
**Problem**: Standard consistent hashing can still create load imbalances
**Solution**: Limit maximum load any node can handle

**Algorithm:**
```
def get_node_bounded(key, load_factor=1.25):
    avg_load = total_keys / num_nodes
    max_load = avg_load * load_factor
    
    position = hash(key)
    while True:
        node = ring.successor(position)
        if node.current_load < max_load:
            return node
        position = node.position + 1  // Try next node
```

**Benefits:**
- **Load Guarantee**: No node exceeds (1 + ε) times average load
- **Gradual Degradation**: System doesn't fail catastrophically under load
- **Predictable Performance**: More consistent response times

**Trade-offs:**
- **Lookup Complexity**: May need to check multiple nodes
- **Load Tracking**: Need to maintain accurate load metrics
- **Implementation Complexity**: More complex than basic consistent hashing

### 12.2 Consistent Hashing with Minimal Disruption
**Goal**: Minimize the number of keys that move during ring changes

**Jump Consistent Hashing:**
```
def jump_hash(key, num_buckets):
    b, j = -1, 0
    while j < num_buckets:
        b = j
        key = key * 2862933555777941757 + 1
        j = floor((b + 1) * (2^31 / ((key >> 33) + 1)))
    return b
```

**Power of Two Choices:**
```
def power_of_two_hash(key):
    # Choose two random nodes
    node1 = ring.successor(hash(key + "1"))
    node2 = ring.successor(hash(key + "2"))
    
    # Return less loaded node
    return node1 if node1.load < node2.load else node2
```

### 12.3 Multi-Level Consistent Hashing
**Use Case**: Hierarchical systems (datacenter → rack → server)

**Implementation:**
```
Level 1: Hash to datacenter
Level 2: Hash to rack within datacenter  
Level 3: Hash to server within rack

def multi_level_hash(key):
    dc = datacenter_ring.successor(hash(key + "dc"))
    rack = dc.rack_ring.successor(hash(key + "rack"))
    server = rack.server_ring.successor(hash(key + "server"))
    return server
```

**Benefits:**
- **Locality Awareness**: Keep data close to compute
- **Failure Isolation**: Datacenter failure doesn't affect others
- **Bandwidth Optimization**: Minimize cross-datacenter traffic

### 12.4 Consistent Hashing with Preferences
**Use Case**: Some nodes are preferred for certain keys

**Preference-Aware Hashing:**
```
def preference_hash(key, preferences):
    candidates = []
    position = hash(key)
    
    # Find multiple candidate nodes
    for i in range(num_candidates):
        node = ring.successor(position + i * offset)
        score = calculate_preference_score(node, key, preferences)
        candidates.append((node, score))
    
    # Return highest scoring node
    return max(candidates, key=lambda x: x[1])[0]
```

**Applications:**
- **Geographic Preferences**: Route based on user location
- **Hardware Preferences**: Prefer SSD nodes for hot data
- **Cost Preferences**: Balance between performance and cost

## 13. Real-World Implementation Challenges

### 13.1 Configuration Management
**Ring Configuration:**
```yaml
consistent_hash:
  virtual_nodes_per_node: 150
  hash_function: "murmur3"
  replication_factor: 3
  failure_detection:
    timeout_ms: 30000
    retry_count: 3
  load_balancing:
    enable_bounded_load: true
    load_factor: 1.25
```

**Dynamic Configuration:**
- **Hot Reloading**: Update configuration without restart
- **Gradual Rollout**: Apply changes incrementally
- **Validation**: Verify configuration before applying
- **Rollback**: Quick rollback for problematic changes

### 13.2 Monitoring & Observability
**Key Metrics:**
```
Ring Health:
- Number of active nodes
- Virtual node distribution variance
- Ring topology change frequency
- Time since last topology change

Load Distribution:
- Keys per node (min, max, avg, p95, p99)
- Load imbalance ratio (max_load / avg_load)
- Hot spot detection (keys with >X% of traffic)
- Node utilization distribution

Performance Metrics:
- Lookup latency (p50, p95, p99)
- Cache hit ratio for key-to-node mappings
- Ring update latency
- Data migration time during node changes

Failure Metrics:
- Node failure detection time
- False positive failure detection rate
- Recovery time after node addition
- Data consistency check results
```

**Alerting Thresholds:**
```
Critical:
- >50% nodes unavailable
- Load imbalance ratio >3.0
- Lookup latency p99 >1000ms

Warning:
- >20% nodes unavailable
- Load imbalance ratio >2.0
- Cache hit ratio <80%
- Ring topology changes >5/hour
```

**Dashboards:**
- **Ring Topology Visualization**: Visual representation of ring with node positions
- **Load Distribution Heatmap**: Show load across all nodes
- **Performance Trends**: Latency and throughput over time
- **Failure Detection**: Timeline of node failures and recoveries

### 13.3 Data Migration
**Migration Strategies:**
```
Incremental Migration:
1. Add new nodes to ring
2. Gradually migrate data in small batches
3. Verify data integrity after each batch
4. Update client routing incrementally

Dual-Write Migration:
1. Write to both old and new locations
2. Gradually migrate reads to new locations
3. Background copy of existing data
4. Remove old locations after verification

Shadow Traffic Migration:
1. Send copy of production traffic to new ring
2. Compare results without affecting production
3. Gradually shift traffic to new ring
4. Fallback to old ring if issues detected
```

**Migration Coordination:**
```
Phase 1: Preparation
- Validate new ring configuration
- Pre-provision new nodes
- Set up monitoring and alerting

Phase 2: Migration
- Execute migration plan
- Monitor key metrics continuously
- Perform data integrity checks

Phase 3: Verification
- Validate data completeness
- Performance testing
- Rollback preparation

Phase 4: Cleanup
- Remove old nodes
- Update documentation
- Post-migration analysis
```

### 13.4 Testing Strategies
**Unit Testing:**
```java
@Test
public void testKeyDistribution() {
    ConsistentHashRing ring = new ConsistentHashRing();
    ring.addNode(new Node("node1"));
    ring.addNode(new Node("node2"));
    ring.addNode(new Node("node3"));
    
    Map<Node, Integer> distribution = new HashMap<>();
    for (int i = 0; i < 100000; i++) {
        String key = "key" + i;
        Node node = ring.getNode(key);
        distribution.merge(node, 1, Integer::sum);
    }
    
    // Assert roughly even distribution (within 10%)
    int avgLoad = 100000 / 3;
    for (int load : distribution.values()) {
        assertThat(load).isBetween(avgLoad * 0.9, avgLoad * 1.1);
    }
}
```

**Integration Testing:**
```java
@Test
public void testNodeFailureRecovery() {
    // Setup cluster with data
    ConsistentHashCluster cluster = setupCluster(5);
    loadTestData(cluster, 10000);
    
    // Simulate node failure
    Node failedNode = cluster.getNodes().get(0);
    cluster.removeNode(failedNode);
    
    // Verify data accessibility
    for (String key : testKeys) {
        assertThat(cluster.get(key)).isNotNull();
    }
    
    // Verify load redistribution
    assertLoadBalance(cluster, 0.2); // Within 20% of average
}
```

**Chaos Engineering:**
```
Failure Scenarios:
- Random node failures (10-50% of cluster)
- Network partitions between datacenters
- Slow nodes (high latency responses)
- Memory pressure causing cache misses
- Partial ring updates (some nodes with old topology)

Validation:
- Data availability during failures
- Performance degradation bounds
- Recovery time measurements
- Consistency violation detection
```

**Load Testing:**
```
Scenarios:
- Gradual load increase (10x over 1 hour)
- Traffic spikes (5x normal load for 10 minutes)
- Hot key scenarios (80% traffic to 20% of keys)
- Mixed workloads (reads, writes, deletes)

Metrics:
- Latency percentiles under load
- Error rate thresholds
- Resource utilization
- Auto-scaling behavior
```

## 14. System Integration Patterns

### 14.1 Database Sharding
**Horizontal Partitioning with Consistent Hashing:**
```sql
-- Shard routing function
CREATE FUNCTION get_shard(user_id BIGINT) 
RETURNS TEXT AS $$
BEGIN
    RETURN consistent_hash(user_id::text, 'shard_ring');
END;
$$ LANGUAGE plpgsql;

-- Application usage
SELECT * FROM users 
WHERE shard = get_shard(user_id) 
AND user_id = ?;
```

**Cross-Shard Operations:**
```java
public class ShardedUserService {
    private ConsistentHashRing shardRing;
    private Map<String, DatabaseConnection> shardConnections;
    
    public User getUser(Long userId) {
        String shard = shardRing.getNode(userId.toString()).getId();
        return shardConnections.get(shard).query(
            "SELECT * FROM users WHERE user_id = ?", userId);
    }
    
    public List<User> getUsers(List<Long> userIds) {
        // Group by shard to minimize database connections
        Map<String, List<Long>> idsByShard = userIds.stream()
            .collect(groupingBy(id -> 
                shardRing.getNode(id.toString()).getId()));
        
        return idsByShard.entrySet().parallelStream()
            .flatMap(entry -> batchQuery(entry.getKey(), entry.getValue()))
            .collect(toList());
    }
}
```

**Rebalancing Considerations:**
- **Online Schema Changes**: Use tools like gh-ost or pt-online-schema-change
- **Foreign Key Constraints**: Minimize cross-shard relationships
- **Transaction Boundaries**: Keep transactions within single shards when possible
- **Backup Strategies**: Coordinate backups across shards for consistency

### 14.2 Distributed Caching
**Cache Cluster Management:**
```java
public class ConsistentHashCache {
    private ConsistentHashRing cacheRing;
    private Map<String, CacheClient> cacheClients;
    private CacheClient localCache; // L1 cache
    
    public <T> T get(String key, Class<T> type) {
        // Try L1 cache first
        T value = localCache.get(key, type);
        if (value != null) return value;
        
        // Route to appropriate cache node
        Node cacheNode = cacheRing.getNode(key);
        CacheClient client = cacheClients.get(cacheNode.getId());
        
        value = client.get(key, type);
        if (value != null) {
            localCache.put(key, value, Duration.ofMinutes(5));
        }
        return value;
    }
    
    public void put(String key, Object value, Duration ttl) {
        Node cacheNode = cacheRing.getNode(key);
        CacheClient client = cacheClients.get(cacheNode.getId());
        
        // Write to distributed cache
        client.put(key, value, ttl);
        
        // Update L1 cache
        localCache.put(key, value, Duration.ofMinutes(5));
    }
}
```

**Cache Warming Strategies:**
```java
public class CacheWarmingService {
    public void warmCacheAfterNodeAddition(Node newNode) {
        // Find keys that moved to new node
        Set<String> movedKeys = findKeysMappedToNode(newNode);
        
        // Parallel warming to avoid overwhelming new node
        movedKeys.parallelStream()
            .limit(1000) // Rate limiting
            .forEach(key -> {
                try {
                    Object value = database.get(key);
                    cache.put(key, value);
                    Thread.sleep(10); // Throttle
                } catch (Exception e) {
                    log.warn("Failed to warm cache for key: " + key, e);
                }
            });
    }
}
```

### 14.3 Load Balancing
**Session Affinity with Consistent Hashing:**
```java
public class SessionAffinityLoadBalancer {
    private ConsistentHashRing serverRing;
    private HealthChecker healthChecker;
    
    public Server selectServer(HttpRequest request) {
        String sessionId = extractSessionId(request);
        
        if (sessionId != null) {
            // Route to same server for session affinity
            Node primaryNode = serverRing.getNode(sessionId);
            if (healthChecker.isHealthy(primaryNode)) {
                return (Server) primaryNode;
            }
            
            // Fallback to next healthy server for session migration
            return findNextHealthyServer(primaryNode);
        }
        
        // New session - route based on other criteria
        return selectServerForNewSession(request);
    }
    
    private Server findNextHealthyServer(Node failedNode) {
        Iterator<Node> iterator = serverRing.successors(failedNode);
        while (iterator.hasNext()) {
            Node candidate = iterator.next();
            if (healthChecker.isHealthy(candidate)) {
                return (Server) candidate;
            }
        }
        throw new NoHealthyServersException();
    }
}
```

**Gradual Traffic Shifting:**
```java
public class GradualTrafficShifter {
    public void addServerGradually(Server newServer) {
        // Start with limited virtual nodes
        serverRing.addNode(newServer, 10); // 10 virtual nodes initially
        
        // Gradually increase over time
        scheduler.scheduleAtFixedRate(() -> {
            int currentVnodes = serverRing.getVirtualNodeCount(newServer);
            int targetVnodes = 150;
            
            if (currentVnodes < targetVnodes) {
                int increment = Math.min(20, targetVnodes - currentVnodes);
                serverRing.addVirtualNodes(newServer, increment);
                
                log.info("Increased {} virtual nodes to {}", 
                    newServer.getId(), currentVnodes + increment);
            }
        }, 2, 2, TimeUnit.MINUTES);
    }
}
```

### 14.4 Content Delivery Networks
**CDN Edge Server Selection:**
```java
public class GeographicConsistentHash {
    private Map<String, ConsistentHashRing> regionalRings;
    private ConsistentHashRing globalRing;
    
    public EdgeServer selectEdgeServer(String contentId, String clientLocation) {
        // First, select region based on client location
        String region = selectRegion(clientLocation);
        ConsistentHashRing regionalRing = regionalRings.get(region);
        
        if (regionalRing != null && regionalRing.hasHealthyNodes()) {
            // Route within region for best latency
            return (EdgeServer) regionalRing.getNode(contentId);
        }
        
        // Fallback to global ring if regional unavailable
        return (EdgeServer) globalRing.getNode(contentId);
    }
    
    private String selectRegion(String clientLocation) {
        // Use geolocation to find closest region
        GeoLocation clientGeo = geoLocationService.lookup(clientLocation);
        return regionSelector.findClosestRegion(clientGeo);
    }
}
```

**Content Distribution Strategy:**
```java
public class ContentDistributionManager {
    public void distributeContent(String contentId, byte[] content) {
        // Determine primary and replica edge servers
        List<EdgeServer> servers = selectServersForContent(contentId);
        
        // Distribute to multiple servers for redundancy
        CompletableFuture<?>[] uploadFutures = servers.stream()
            .map(server -> CompletableFuture.runAsync(() -> 
                server.uploadContent(contentId, content)))
            .toArray(CompletableFuture[]::new);
        
        // Wait for majority to complete
        CompletableFuture.allOf(uploadFutures).join();
    }
    
    private List<EdgeServer> selectServersForContent(String contentId) {
        List<EdgeServer> servers = new ArrayList<>();
        
        // Primary server
        servers.add((EdgeServer) globalRing.getNode(contentId));
        
        // Replica servers (next N servers on ring)
        Iterator<Node> successors = globalRing.successors(contentId);
        for (int i = 0; i < replicationFactor - 1 && successors.hasNext(); i++) {
            servers.add((EdgeServer) successors.next());
        }
        
        return servers;
    }
}
```

## 15. Comparison with Alternatives

### 15.1 vs Range-Based Partitioning
**Range-Based Partitioning:**
```
Partitioning Strategy:
- Partition 1: keys A-F
- Partition 2: keys G-M  
- Partition 3: keys N-S
- Partition 4: keys T-Z

Advantages:
- Simple to understand and implement
- Efficient range queries
- Preserves key ordering
- Good for sequential access patterns

Disadvantages:
- Hot spots with non-uniform key distribution
- Manual rebalancing required
- Complex splitting of hot partitions
- Poor load distribution for skewed data
```

**Consistent Hashing:**
```
Advantages over Range-Based:
- Automatic load balancing
- No hot spots from key distribution
- Minimal data movement during rebalancing
- Works well with any key distribution

Disadvantages vs Range-Based:
- No support for range queries
- Hash-based routing only
- Slightly more complex implementation
- May not preserve data locality
```

**When to Choose:**
- **Range-Based**: Time-series data, ordered access patterns, range queries required
- **Consistent Hashing**: Web applications, caching, unordered key access

### 15.2 vs Directory-Based Partitioning
**Directory-Based Partitioning:**
```
Architecture:
- Central directory service maps keys to nodes
- Clients query directory for routing decisions
- Directory updated when nodes added/removed

Advantages:
- Flexible partition assignment
- Supports complex routing policies
- Easy to implement custom load balancing
- Good for heterogeneous clusters

Disadvantages:
- Directory service is single point of failure
- Additional network hop for each request
- Directory must be distributed for scale
- Consistency challenges for directory updates
```

**Consistent Hashing:**
```
Advantages over Directory-Based:
- No central directory dependency
- Direct routing without extra hops
- Built-in fault tolerance
- Simpler architecture

Disadvantages vs Directory-Based:
- Less flexible routing policies
- Harder to implement custom load balancing
- Fixed algorithmic approach
- Limited support for complex constraints
```

**When to Choose:**
- **Directory-Based**: Complex routing requirements, heterogeneous environments, need for centralized control
- **Consistent Hashing**: High-performance requirements, simple routing, fault tolerance priority

### 15.3 vs Rendezvous Hashing
**Rendezvous Hashing (Highest Random Weight):**
```python
def rendezvous_hash(key, nodes):
    max_weight = -1
    selected_node = None
    
    for node in nodes:
        weight = hash(key + node.id)
        if weight > max_weight:
            max_weight = weight
            selected_node = node
    
    return selected_node
```

**Comparison:**
```
Rendezvous Hashing:
- Perfect load balance (1/n keys per node)
- O(n) lookup time (must check all nodes)
- Minimal key movement on topology changes
- Stateless (no ring to maintain)

Consistent Hashing:
- Good load balance (with virtual nodes)
- O(log n) lookup time (binary search on ring)
- Minimal key movement on topology changes
- Requires ring state maintenance
```

**Performance Trade-offs:**
```
Small Clusters (< 100 nodes):
- Rendezvous: Acceptable O(n) performance
- Consistent: O(log n) advantage less significant

Large Clusters (> 1000 nodes):
- Rendezvous: O(n) becomes prohibitive
- Consistent: O(log n) provides clear advantage

Memory Usage:
- Rendezvous: O(1) - no state to maintain
- Consistent: O(n) - ring state storage
```

### 15.4 Trade-off Analysis
**Decision Matrix:**

| Factor | Consistent Hashing | Range-Based | Directory-Based | Rendezvous |
|--------|-------------------|-------------|-----------------|------------|
| **Lookup Performance** | O(log n) | O(1) with index | O(1) + directory lookup | O(n) |
| **Load Balance** | Good (w/ vnodes) | Poor (hot spots) | Excellent | Perfect |
| **Rebalancing Cost** | Low | High | Medium | Low |
| **Implementation Complexity** | Medium | Low | High | Low |
| **Fault Tolerance** | High | Medium | Low (SPOF) | High |
| **Range Queries** | No | Yes | Possible | No |
| **Memory Overhead** | Medium | Low | High | Low |
| **Operational Complexity** | Medium | High | High | Low |

**Selection Guidelines:**
```
Choose Consistent Hashing when:
- Need automatic load balancing
- Want minimal operational overhead
- Have uniform key access patterns
- Require good fault tolerance
- Cluster size > 100 nodes

Choose Range-Based when:
- Need range query support
- Have time-series or ordered data
- Can tolerate manual rebalancing
- Have predictable key distribution

Choose Directory-Based when:
- Need complex routing policies
- Have heterogeneous hardware
- Require centralized control
- Can invest in directory infrastructure

Choose Rendezvous when:
- Have small cluster (< 50 nodes)
- Need perfect load balance
- Want stateless operation
- Can tolerate O(n) lookup cost
```

## 16. Industry Examples

### 16.1 Amazon DynamoDB
**Implementation Details:**
```
Partitioning Strategy:
- Uses consistent hashing for data distribution
- Partition key determines placement
- Virtual nodes for load balancing
- Automatic scaling and rebalancing

Key Features:
- MD5 hash function for 128-bit key space
- Replica placement across availability zones
- Background data movement for scaling
- Predictive scaling based on access patterns
```

**DynamoDB Partition Logic:**
```python
def dynamodb_partition(partition_key, table_partitions):
    # MD5 hash of partition key
    hash_value = md5(partition_key).hexdigest()
    hash_int = int(hash_value, 16)
    
    # Map to partition using consistent hashing
    partition_ring = table_partitions.get_ring()
    return partition_ring.get_node(hash_int)
```

### 16.2 Apache Cassandra
**Ring-Based Architecture:**
```
Token Ring Design:
- Each node assigned token range
- Murmur3 hash function (default)
- Configurable replication factor
- Multiple consistency levels

Vnodes Implementation:
- 256 virtual nodes per physical node (default)
- Better load distribution than single token
- Faster bootstrapping and repairs
- Improved availability during failures
```

**Cassandra Token Assignment:**
```cql
-- View token ranges
SELECT token, rack, host_id FROM system.local;

-- Manual token assignment (not recommended)
ALTER TABLE keyspace.table 
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};
```

### 16.3 Redis Cluster
**Slot-Based Consistent Hashing:**
```
Design:
- 16384 hash slots (2^14)
- CRC16 hash function
- Each node owns subset of slots
- Client-side routing with redirection

Slot Calculation:
slot = CRC16(key) % 16384
```

**Redis Cluster Commands:**
```bash
# View cluster slots
CLUSTER SLOTS

# Manual slot assignment
CLUSTER ADDSLOTS 0 1 2 3 4 5

# Migrate slot between nodes
CLUSTER SETSLOT 12345 MIGRATING target-node-id
```

### 16.4 Memcached with Ketama
**Ketama Algorithm:**
```python
class KetamaRing:
    def __init__(self, servers, replicas=160):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        
        for server in servers:
            self.add_server(server)
    
    def add_server(self, server):
        for i in range(self.replicas):
            key = self.hash(f"{server.ip}:{server.port}:{i}")
            self.ring[key] = server
            self.sorted_keys.append(key)
        self.sorted_keys.sort()
    
    def get_server(self, key):
        hash_key = self.hash(key)
        idx = bisect.bisect_right(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]
```

### 16.5 MongoDB Sharding
**Shard Key Hashing:**
```javascript
// Hashed shard key
db.collection.createIndex({ user_id: "hashed" })

// Enable sharding with hashed key
sh.shardCollection("mydb.mycollection", { user_id: "hashed" })

// MongoDB uses MD5 for hashed sharding
function mongoHash(key) {
    return md5(BSON.encode({user_id: key}));
}
```

### 16.6 Chord DHT Protocol
**Distributed Hash Table Implementation:**
```python
class ChordNode:
    def __init__(self, node_id, m=160):  # m-bit identifier space
        self.id = node_id
        self.m = m
        self.finger_table = [None] * m
        self.successor = None
        self.predecessor = None
    
    def find_successor(self, key):
        if self.in_range(key, self.id, self.successor.id):
            return self.successor
        
        # Forward to closest preceding node
        node = self.closest_preceding_finger(key)
        return node.find_successor(key)
    
    def closest_preceding_finger(self, key):
        for i in range(self.m - 1, -1, -1):
            finger = self.finger_table[i]
            if finger and self.in_range(finger.id, self.id, key):
                return finger
        return self
```

## 17. Interview Discussion Points

### 17.1 Core Concept Questions
**"Explain consistent hashing and why it's useful"**
```
Key Points to Cover:
1. Problem: Traditional hashing causes massive redistribution
2. Solution: Hash ring maps both keys and nodes
3. Benefits: Minimal data movement (only 1/n keys move)
4. Applications: Distributed caches, databases, load balancers

Example Answer:
"Consistent hashing solves the problem of data distribution in distributed systems. 
With traditional modulo hashing, adding or removing a server causes almost all 
keys to be remapped to different servers. Consistent hashing creates a circular 
hash space where both keys and servers are mapped to points on the ring. Each 
key is assigned to the first server found clockwise on the ring. When a server 
is added or removed, only the keys between that server and its predecessor need 
to be moved, which is approximately 1/n of all keys."
```

**"What are virtual nodes and why do we need them?"**
```
Key Points:
1. Problem: Basic consistent hashing can create uneven load distribution
2. Solution: Each physical node represented by multiple virtual nodes
3. Benefits: Better load distribution, smoother scaling
4. Trade-off: Memory overhead vs load balance

Example Answer:
"Virtual nodes address the load imbalance problem in basic consistent hashing. 
When nodes are randomly placed on the ring, some nodes might get much larger 
segments than others. By representing each physical node with multiple virtual 
nodes (typically 100-300), we get more opportunities for even distribution. 
This also makes scaling smoother since adding a node affects multiple small 
segments rather than one large segment."
```

### 17.2 Design Deep-Dive Questions
**"Design a distributed cache using consistent hashing"**
```
Components to Discuss:
1. Hash ring implementation (data structure, lookup algorithm)
2. Virtual node configuration (how many, how to place)
3. Client-side routing vs proxy-based routing
4. Failure detection and recovery
5. Replication strategy
6. Cache warming during scaling

Architecture Elements:
- ConsistentHashRing class with TreeMap for O(log n) lookups
- CacheClient with connection pooling
- Health checking and circuit breakers
- Read repair for consistency
- Metrics and monitoring
```

**"How would you handle node failures in consistent hashing?"**
```
Discussion Points:
1. Failure detection mechanisms (heartbeat, gossip, application-level)
2. Temporary vs permanent failure handling
3. Data replication and replica selection
4. Read repair and anti-entropy processes
5. Graceful degradation strategies

Implementation Details:
- Configurable failure detection timeouts
- Quorum-based reads/writes during failures
- Background data consistency checks
- Automated vs manual recovery procedures
```

### 17.3 Optimization Questions
**"How would you optimize consistent hashing for hot keys?"**
```
Strategies to Discuss:
1. Hot key detection (monitoring, thresholds)
2. Caching layers (local cache, dedicated cache nodes)
3. Key splitting/sharding
4. Load shedding and rate limiting
5. Replication of hot data

Advanced Techniques:
- Bounded load consistent hashing
- Power of two choices
- Consistent hashing with preferences
- Dynamic virtual node adjustment
```

**"What are the performance characteristics of consistent hashing?"**
```
Complexity Analysis:
- Lookup: O(log V) where V is virtual nodes
- Node addition/removal: O(V/N + K/N) 
- Memory usage: O(V) for ring metadata
- Network overhead: O(N) for topology updates

Optimization Opportunities:
- Caching recent lookups for O(1) performance
- Batch operations for amortized costs
- Efficient data structures (TreeMap vs Skip List)
- Async topology updates
```

### 17.4 Comparison Questions
**"When would you choose consistent hashing over other partitioning schemes?"**
```
Decision Criteria:
1. Access patterns (random vs sequential)
2. Scaling requirements (dynamic vs static)
3. Load balancing needs
4. Query requirements (point lookups vs range queries)
5. Operational complexity tolerance

Specific Scenarios:
- Choose consistent hashing: web caching, session storage, user data
- Choose range partitioning: time-series data, log storage
- Choose directory-based: complex routing policies, heterogeneous hardware
```

### 17.5 Real-World Implementation Questions
**"How would you migrate an existing system to use consistent hashing?"**
```
Migration Strategy:
1. Dual-write phase (write to old and new systems)
2. Data migration (background copying with validation)
3. Read migration (gradually shift reads to new system)
4. Cleanup phase (remove old system)

Risk Mitigation:
- Shadow traffic testing
- Rollback procedures
- Performance monitoring
- Data integrity validation
```

**"What monitoring would you implement for a consistent hashing system?"**
```
Key Metrics:
1. Load distribution (coefficient of variation across nodes)
2. Performance metrics (lookup latency, cache hit rates)
3. Reliability metrics (failure detection time, recovery time)
4. Operational metrics (topology change frequency, data movement)

Alerting:
- Load imbalance above threshold
- Performance degradation
- Node failure detection
- Ring topology inconsistencies
```

## 18. System Design Diagrams

### 18.1 Basic Hash Ring
```
        Hash Ring (0 to 2^160-1)
                 ┌─────────┐
             ┌───┤    A    ├───┐
         ┌───┤   └─────────┘   ├───┐
     ┌───┤ D                     B ├───┐
     │   └─────────────┬─────────────┘   │
     │                 │                 │
     │                 │                 │
     │                 │                 │
     │   ┌─────────────┴─────────────┐   │
     └───┤ C                         ├───┘
         └───┐   ┌─────────┐   ┌───┘
             └───┤ Key X   ├───┘
                 └─────────┘

Key X maps to Node B (first node clockwise)
Nodes: A, B, C, D distributed around ring
```

### 18.2 Virtual Nodes Distribution
```
        Hash Ring with Virtual Nodes
                 ┌─────────┐
             ┌───┤   A2    ├───┐
         ┌───┤   └─────────┘   ├───┐
     ┌───┤ D1        B3          A1 ├───┐
     │   └─────────────┬─────────────┘   │
     │        D3       │      B1         │
     │                 │                 │
     │        C2       │      A3         │
     │   ┌─────────────┴─────────────┐   │
     └───┤ C1        B2        D2    ├───┘
         └───┐   ┌─────────┐   ┌───┘
             └───┤ Key X   ├───┘
                 └─────────┘

Each physical node (A,B,C,D) has 3 virtual nodes
Better load distribution across ring segments
Key X now maps to virtual node B2 (physical node B)
```

### 18.3 Node Addition/Removal Flow
```
Before Adding Node E:
┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
│  A  │────│  B  │────│  C  │────│  D  │
└─────┘    └─────┘    └─────┘    └─────┘
   │                                 │
   └─────────────────────────────────┘

After Adding Node E:
┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
│  A  │────│  B  │────│  E  │────│  C  │────│  D  │
└─────┘    └─────┘    └─────┘    └─────┘    └─────┘
   │                                           │
   └───────────────────────────────────────────┘

Data Movement:
- Keys between D and E move from C to E
- All other key mappings remain unchanged
- Approximately 1/5 of C's keys move to E
```

### 18.4 Replication with Consistent Hashing
```
Hash Ring with Replication Factor = 3

                Primary    Replica 1   Replica 2
Key X     →        B    →      C    →      D
Key Y     →        A    →      B    →      C  
Key Z     →        D    →      A    →      B

                 ┌─────────┐
             ┌───┤    A    ├───┐
         ┌───┤   └─────────┘   ├───┐
     ┌───┤ D                     B ├───┐
     │   └─────────────┬─────────────┘   │
     │                 │                 │
     │     Key Z       │     Key X       │
     │   (Primary=D)   │   (Primary=B)   │
     │   ┌─────────────┴─────────────┐   │
     └───┤ C           Key Y         ├───┘
         └───┐     (Primary=A)  ┌───┘
             └───┐   ┌─────┐   ┌───┘
                 └───┤     ├───┘
                     └─────┘

Replication Strategy:
- Each key stored on N consecutive nodes (N=3 here)
- Primary node handles writes
- Replicas provide read scalability and fault tolerance
- Consistent ordering ensures same replicas chosen by all clients

Failure Handling:
- If node B fails: Key X served from replicas C and D
- If node A fails: Key Y served from replicas B and C
- Read/write quorums ensure consistency during failures

Data Placement Rules:
1. Primary = successor(hash(key))
2. Replica1 = successor(primary)
3. Replica2 = successor(replica1)
4. Skip failed nodes when selecting replicas
```

**Additional Replication Scenarios:**

```
Write Path with Replication:
1. Client sends PUT request for Key X
2. Route to primary node B
3. B writes locally and forwards to replicas C, D
4. Wait for quorum (2 out of 3) before acknowledging
5. Return success to client

Read Path with Replication:
1. Client sends GET request for Key X
2. Route to any replica (B, C, or D)
3. If inconsistency detected, perform read repair
4. Return data to client

Consistency Options:
- Strong: Read/write from majority (quorum)
- Eventual: Async replication, faster but temporarily inconsistent
- Tunable: Client chooses consistency level per operation
```

**Node Failure Impact:**

```
Normal Operation (All nodes healthy):
Key X: B(primary), C(replica), D(replica)

Node B Fails:
Key X: C(primary), D(replica), A(new replica)
- C promoted to primary
- New replica added at A
- Background repair when B recovers

Node Recovery:
- When B returns, it becomes replica again
- Anti-entropy process syncs missed writes
- Gradual load rebalancing
