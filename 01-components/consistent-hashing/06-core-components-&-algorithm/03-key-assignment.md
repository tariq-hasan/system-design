# Key Assignment in Consistent Hashing

Key assignment is the core mechanism that determines which node in a consistent hashing system is responsible for storing and serving each piece of data. This process must be fast, deterministic, and mathematically sound to ensure consistent behavior across all system components. Understanding key assignment algorithms and their optimization is crucial for building high-performance distributed systems that can handle millions of operations per second.

## Key Assignment Algorithm

The key assignment algorithm forms the heart of consistent hashing, translating arbitrary data keys into specific node assignments through a deterministic process that remains stable as the system scales.

### Core Assignment Process

```python
import hashlib
import bisect
import time
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict

class KeyAssignment:
    """Core key assignment implementation for consistent hashing"""
    
    def __init__(self, hash_function: str = 'sha1'):
        self.hash_function = hash_function
        self.ring = {}  # position -> node_id mapping
        self.sorted_positions = []  # Sorted positions for binary search
        self.node_positions = defaultdict(list)  # node_id -> [positions] mapping
        
        # Performance metrics
        self.assignment_count = 0
        self.total_assignment_time = 0.0
        
        # Setup hash function
        self._setup_hash_function()
    
    def _setup_hash_function(self):
        """Configure hash function and space size"""
        hash_configs = {
            'sha1': {'func': hashlib.sha1, 'space_size': 2**160},
            'sha256': {'func': hashlib.sha256, 'space_size': 2**256},
            'md5': {'func': hashlib.md5, 'space_size': 2**128},
        }
        
        config = hash_configs[self.hash_function]
        self.hasher = config['func']
        self.space_size = config['space_size']
    
    def compute_key_position(self, key: str) -> int:
        """
        Compute hash ring position for a data key
        
        Args:
            key: The data key to position on the ring
            
        Returns:
            Integer position on the hash ring
        """
        if not isinstance(key, (str, bytes)):
            # Convert other types to string representation
            key = str(key)
        
        if isinstance(key, str):
            key_bytes = key.encode('utf-8')
        else:
            key_bytes = key
        
        # Generate hash
        hash_obj = self.hasher(key_bytes)
        hash_hex = hash_obj.hexdigest()
        
        # Convert to ring position
        hash_int = int(hash_hex, 16)
        position = hash_int % self.space_size
        
        return position
    
    def add_node(self, node_id: str, virtual_node_count: int = 150):
        """Add a node with virtual nodes to the ring"""
        if node_id in self.node_positions:
            raise ValueError(f"Node {node_id} already exists")
        
        positions = []
        for i in range(virtual_node_count):
            virtual_id = f"{node_id}:vnode_{i}"
            position = self.compute_key_position(virtual_id)
            
            # Handle collisions
            collision_count = 0
            while position in self.ring and collision_count < 1000:
                collision_count += 1
                virtual_id = f"{node_id}:vnode_{i}_collision_{collision_count}"
                position = self.compute_key_position(virtual_id)
            
            self.ring[position] = node_id
            positions.append(position)
        
        self.node_positions[node_id] = positions
        self.sorted_positions = sorted(self.ring.keys())
        
        return len(positions)
    
    def remove_node(self, node_id: str):
        """Remove a node and all its virtual nodes"""
        if node_id not in self.node_positions:
            raise ValueError(f"Node {node_id} does not exist")
        
        positions = self.node_positions[node_id]
        for position in positions:
            if position in self.ring:
                del self.ring[position]
        
        del self.node_positions[node_id]
        self.sorted_positions = sorted(self.ring.keys())
        
        return len(positions)
    
    def assign_key(self, key: str) -> Optional[str]:
        """
        Assign a key to the appropriate node using clockwise rule
        
        Args:
            key: The data key to assign
            
        Returns:
            Node ID responsible for the key, or None if no nodes exist
        """
        start_time = time.perf_counter()
        
        if not self.sorted_positions:
            return None
        
        # Step 1: Compute key position
        key_position = self.compute_key_position(key)
        
        # Step 2: Find first node clockwise from key position
        assigned_node = self._find_successor_node(key_position)
        
        # Update performance metrics
        end_time = time.perf_counter()
        self.assignment_count += 1
        self.total_assignment_time += (end_time - start_time)
        
        return assigned_node
    
    def _find_successor_node(self, position: int) -> str:
        """
        Find the first node at or after the given position (clockwise)
        
        Args:
            position: Position on the ring to search from
            
        Returns:
            Node ID of the successor node
        """
        # Binary search for first position >= key position
        index = bisect.bisect_left(self.sorted_positions, position)
        
        # If we found a position >= key position, use it
        if index < len(self.sorted_positions):
            successor_position = self.sorted_positions[index]
            return self.ring[successor_position]
        
        # Otherwise, wrap around to the first position
        first_position = self.sorted_positions[0]
        return self.ring[first_position]
    
    def demonstrate_assignment_process(self):
        """Demonstrate the step-by-step key assignment process"""
        
        print("Key Assignment Process Demonstration:")
        print("=" * 45)
        
        # Add some nodes
        nodes = ['cache-01', 'cache-02', 'cache-03']
        for node in nodes:
            vnode_count = self.add_node(node, virtual_node_count=5)  # Fewer for demo
            print(f"Added {node} with {vnode_count} virtual nodes")
        
        # Show ring state
        print(f"\nRing state ({len(self.ring)} total positions):")
        positions_by_node = defaultdict(list)
        for pos, node in self.ring.items():
            positions_by_node[node].append(pos)
        
        for node in sorted(positions_by_node.keys()):
            positions = sorted(positions_by_node[node])
            print(f"  {node}: {len(positions)} positions {positions[:3]}{'...' if len(positions) > 3 else ''}")
        
        # Demonstrate key assignments
        test_keys = [
            'user:12345',
            'session:abc123', 
            'product:67890',
            'cart:xyz789',
            'order:999888'
        ]
        
        print(f"\nKey assignment examples:")
        for key in test_keys:
            key_position = self.compute_key_position(key)
            assigned_node = self.assign_key(key)
            
            # Find the actual successor position for explanation
            successor_pos = self._find_successor_position(key_position)
            
            print(f"\n  Key: '{key}'")
            print(f"    Position: {key_position:,}")
            print(f"    Successor position: {successor_pos:,}")
            print(f"    Assigned node: {assigned_node}")
            print(f"    Distance to successor: {self._calculate_distance(key_position, successor_pos):,}")
    
    def _find_successor_position(self, position: int) -> int:
        """Find the actual position of the successor"""
        index = bisect.bisect_left(self.sorted_positions, position)
        if index < len(self.sorted_positions):
            return self.sorted_positions[index]
        return self.sorted_positions[0]
    
    def _calculate_distance(self, from_pos: int, to_pos: int) -> int:
        """Calculate clockwise distance between positions"""
        if to_pos >= from_pos:
            return to_pos - from_pos
        else:
            return (self.space_size - from_pos) + to_pos
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get assignment performance statistics"""
        if self.assignment_count == 0:
            return {'assignments': 0, 'avg_time_us': 0, 'total_time_ms': 0}
        
        avg_time_us = (self.total_assignment_time / self.assignment_count) * 1_000_000
        total_time_ms = self.total_assignment_time * 1000
        
        return {
            'assignments': self.assignment_count,
            'avg_time_us': avg_time_us,
            'total_time_ms': total_time_ms
        }

# Demonstrate key assignment
assignment_demo = KeyAssignment('sha1')
assignment_demo.demonstrate_assignment_process()

# Show performance stats
perf_stats = assignment_demo.get_performance_stats()
print(f"\nPerformance Statistics:")
print(f"  Total assignments: {perf_stats['assignments']}")
print(f"  Average time: {perf_stats['avg_time_us']:.2f} μs")
print(f"  Total time: {perf_stats['total_time_ms']:.2f} ms")
```

### Optimized Lookup Algorithm

```python
class OptimizedKeyLookup:
    """High-performance key lookup with various optimizations"""
    
    def __init__(self, hash_function: str = 'sha1', cache_size: int = 10000):
        self.hash_function = hash_function
        self.cache_size = cache_size
        
        # Core ring structures
        self.ring = {}
        self.sorted_positions = []
        
        # Performance optimizations
        self.lookup_cache = {}  # LRU cache for frequent lookups
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Batch lookup optimization
        self.batch_lookup_buffer = []
        
        # Setup hash function
        self._setup_hash_function()
    
    def _setup_hash_function(self):
        """Configure hash function"""
        if self.hash_function == 'sha1':
            self.hasher = hashlib.sha1
            self.space_size = 2**160
        elif self.hash_function == 'sha256':
            self.hasher = hashlib.sha256
            self.space_size = 2**256
        else:
            self.hasher = hashlib.md5
            self.space_size = 2**128
    
    def compute_key_position(self, key: str) -> int:
        """Optimized key position computation"""
        # Fast path for common key types
        if isinstance(key, str):
            key_bytes = key.encode('utf-8')
        else:
            key_bytes = str(key).encode('utf-8')
        
        hash_obj = self.hasher(key_bytes)
        hash_int = int(hash_obj.hexdigest(), 16)
        return hash_int % self.space_size
    
    def lookup_with_cache(self, key: str) -> Optional[str]:
        """Lookup with LRU caching for performance"""
        
        # Check cache first
        if key in self.lookup_cache:
            self.cache_hits += 1
            # Move to end (LRU update)
            value = self.lookup_cache.pop(key)
            self.lookup_cache[key] = value
            return value
        
        # Cache miss - compute assignment
        self.cache_misses += 1
        assigned_node = self._compute_assignment(key)
        
        # Update cache with LRU eviction
        if len(self.lookup_cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.lookup_cache))
            del self.lookup_cache[oldest_key]
        
        self.lookup_cache[key] = assigned_node
        return assigned_node
    
    def _compute_assignment(self, key: str) -> Optional[str]:
        """Core assignment computation"""
        if not self.sorted_positions:
            return None
        
        key_position = self.compute_key_position(key)
        
        # Binary search for successor
        index = bisect.bisect_left(self.sorted_positions, key_position)
        
        if index < len(self.sorted_positions):
            return self.ring[self.sorted_positions[index]]
        else:
            return self.ring[self.sorted_positions[0]]
    
    def batch_lookup(self, keys: List[str]) -> Dict[str, str]:
        """Optimized batch lookup for multiple keys"""
        
        results = {}
        cache_hits = []
        cache_misses = []
        
        # Separate cache hits from misses
        for key in keys:
            if key in self.lookup_cache:
                cache_hits.append(key)
                results[key] = self.lookup_cache[key]
            else:
                cache_misses.append(key)
        
        # Batch process cache misses
        if cache_misses:
            # Compute all positions at once
            key_positions = [(key, self.compute_key_position(key)) for key in cache_misses]
            
            # Sort by position for more efficient lookups
            key_positions.sort(key=lambda x: x[1])
            
            # Process in order
            for key, position in key_positions:
                assigned_node = self._find_successor_binary_search(position)
                results[key] = assigned_node
                
                # Update cache
                if len(self.lookup_cache) >= self.cache_size:
                    oldest_key = next(iter(self.lookup_cache))
                    del self.lookup_cache[oldest_key]
                self.lookup_cache[key] = assigned_node
        
        # Update metrics
        self.cache_hits += len(cache_hits)
        self.cache_misses += len(cache_misses)
        
        return results
    
    def _find_successor_binary_search(self, position: int) -> str:
        """Optimized binary search for successor"""
        left, right = 0, len(self.sorted_positions) - 1
        
        while left <= right:
            mid = (left + right) // 2
            mid_position = self.sorted_positions[mid]
            
            if mid_position >= position:
                if mid == 0 or self.sorted_positions[mid - 1] < position:
                    return self.ring[mid_position]
                right = mid - 1
            else:
                left = mid + 1
        
        # Wrap around to first position
        return self.ring[self.sorted_positions[0]]
    
    def demonstrate_optimization_benefits(self):
        """Demonstrate performance benefits of optimizations"""
        
        print("Lookup Optimization Performance Comparison:")
        print("=" * 50)
        
        # Setup test ring
        for i in range(20):
            node_id = f"node-{i:02d}"
            for j in range(100):  # 100 virtual nodes each
                virtual_id = f"{node_id}:vnode_{j}"
                position = self.compute_key_position(virtual_id)
                self.ring[position] = node_id
        
        self.sorted_positions = sorted(self.ring.keys())
        
        # Generate test keys
        test_keys = [f"test_key_{i}" for i in range(10000)]
        
        # Test 1: Cold cache performance
        print("Test 1: Cold cache (no cache hits)")
        start_time = time.perf_counter()
        
        for key in test_keys[:1000]:  # First 1000 keys
            self.lookup_with_cache(key)
        
        cold_time = time.perf_counter() - start_time
        cold_cache_ratio = self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        
        print(f"  Time: {cold_time*1000:.2f} ms")
        print(f"  Cache hit ratio: {cold_cache_ratio:.1%}")
        print(f"  Lookups per second: {1000/cold_time:,.0f}")
        
        # Test 2: Warm cache performance (repeat same keys)
        print("\nTest 2: Warm cache (high cache hit ratio)")
        start_time = time.perf_counter()
        
        for key in test_keys[:1000]:  # Same 1000 keys again
            self.lookup_with_cache(key)
        
        warm_time = time.perf_counter() - start_time
        warm_cache_ratio = self.cache_hits / (self.cache_hits + self.cache_misses)
        
        print(f"  Time: {warm_time*1000:.2f} ms")
        print(f"  Cache hit ratio: {warm_cache_ratio:.1%}")
        print(f"  Lookups per second: {1000/warm_time:,.0f}")
        print(f"  Speedup: {cold_time/warm_time:.1f}x faster")
        
        # Test 3: Batch lookup performance
        print("\nTest 3: Batch lookup optimization")
        
        # Clear cache for fair comparison
        self.lookup_cache.clear()
        
        start_time = time.perf_counter()
        batch_results = self.batch_lookup(test_keys[1000:2000])  # New 1000 keys
        batch_time = time.perf_counter() - start_time
        
        print(f"  Time: {batch_time*1000:.2f} ms")
        print(f"  Batch lookups per second: {1000/batch_time:,.0f}")
        print(f"  Results returned: {len(batch_results)}")
        
        # Test 4: Individual vs batch comparison
        self.lookup_cache.clear()
        
        start_time = time.perf_counter()
        individual_results = {}
        for key in test_keys[2000:3000]:
            individual_results[key] = self.lookup_with_cache(key)
        individual_time = time.perf_counter() - start_time
        
        print(f"\nComparison: Individual vs Batch")
        print(f"  Individual lookups: {individual_time*1000:.2f} ms")
        print(f"  Batch lookups: {batch_time*1000:.2f} ms")
        print(f"  Batch speedup: {individual_time/batch_time:.1f}x faster")
        
        return {
            'cold_time': cold_time,
            'warm_time': warm_time,
            'batch_time': batch_time,
            'individual_time': individual_time,
            'cache_hit_ratio': warm_cache_ratio
        }

# Demonstrate optimization benefits
optimized_lookup = OptimizedKeyLookup('sha1', cache_size=5000)
perf_results = optimized_lookup.demonstrate_optimization_benefits()
```

## Key Identification Strategies

Different types of data require different key identification strategies to ensure optimal distribution and operational clarity.

### Database Record Keys

```python
class DatabaseKeyStrategies:
    """Key identification strategies for database records"""
    
    def __init__(self):
        self.assignment = KeyAssignment('sha1')
        # Add some nodes for testing
        for i in range(5):
            self.assignment.add_node(f"db-shard-{i:02d}")
    
    def primary_key_strategy(self):
        """Demonstrate primary key-based assignment"""
        
        print("Database Primary Key Strategy:")
        print("=" * 35)
        
        # Different primary key formats
        primary_keys = [
            # Auto-increment integers
            ('users', [1, 2, 3, 1000, 9999]),
            # UUIDs
            ('orders', ['550e8400-e29b-41d4-a716-446655440000',
                       '6ba7b810-9dad-11d1-80b4-00c04fd430c8']),
            # Composite keys
            ('user_sessions', ['user_123_session_456', 'user_789_session_101']),
            # Natural keys
            ('products', ['SKU-LAPTOP-001', 'SKU-MOUSE-045'])
        ]
        
        print("Primary key distribution analysis:")
        
        for table, keys in primary_keys:
            print(f"\n{table.upper()} table:")
            
            # Track distribution
            node_assignments = defaultdict(int)
            
            for key in keys:
                # Create database-style key
                db_key = f"{table}:{key}"
                assigned_node = self.assignment.assign_key(db_key)
                node_assignments[assigned_node] += 1
                
                key_position = self.assignment.compute_key_position(db_key)
                print(f"  {db_key:<35} → {assigned_node} (pos: {key_position:>10,})")
            
            # Show distribution
            print(f"  Distribution: {dict(node_assignments)}")
    
    def composite_key_strategy(self):
        """Demonstrate composite key strategies for related data"""
        
        print("\nComposite Key Strategy for Related Data:")
        print("=" * 45)
        
        # User and their related data
        user_id = "user_12345"
        related_data_types = [
            'profile',
            'preferences', 
            'sessions',
            'orders',
            'wishlist'
        ]
        
        print(f"Related data for {user_id}:")
        
        # Strategy 1: Include user_id in all related keys
        print("\nStrategy 1: User ID prefix")
        strategy1_nodes = set()
        
        for data_type in related_data_types:
            composite_key = f"{user_id}:{data_type}"
            assigned_node = self.assignment.assign_key(composite_key)
            strategy1_nodes.add(assigned_node)
            
            print(f"  {composite_key:<25} → {assigned_node}")
        
        print(f"  Nodes used: {len(strategy1_nodes)} ({', '.join(sorted(strategy1_nodes))})")
        
        # Strategy 2: Hash user_id first, then append data type
        print("\nStrategy 2: Consistent user prefix")
        strategy2_nodes = set()
        
        # Get user's "home" position
        user_position = self.assignment.compute_key_position(user_id)
        
        for data_type in related_data_types:
            # Create key that will hash near user's position
            composite_key = f"{user_id}_{data_type}"
            assigned_node = self.assignment.assign_key(composite_key)
            strategy2_nodes.add(assigned_node)
            
            print(f"  {composite_key:<25} → {assigned_node}")
        
        print(f"  Nodes used: {len(strategy2_nodes)} ({', '.join(sorted(strategy2_nodes))})")
        
        # Compare strategies
        print(f"\nStrategy comparison:")
        print(f"  Strategy 1 data locality: {len(strategy1_nodes)} nodes")
        print(f"  Strategy 2 data locality: {len(strategy2_nodes)} nodes")
        
        if len(strategy1_nodes) < len(strategy2_nodes):
            print(f"  Better locality: Strategy 1 (fewer nodes)")
        elif len(strategy2_nodes) < len(strategy1_nodes):
            print(f"  Better locality: Strategy 2 (fewer nodes)")
        else:
            print(f"  Equal locality: Both strategies use same number of nodes")

# Demonstrate database key strategies
db_keys = DatabaseKeyStrategies()
db_keys.primary_key_strategy()
db_keys.composite_key_strategy()
```

### Cache Entry Keys

```python
class CacheKeyStrategies:
    """Key identification strategies for cache entries"""
    
    def __init__(self):
        self.assignment = KeyAssignment('sha1')
        # Add cache nodes
        for i in range(6):
            self.assignment.add_node(f"cache-{i:02d}")
    
    def namespace_strategy(self):
        """Demonstrate namespace-based cache key strategy"""
        
        print("Cache Namespace Strategy:")
        print("=" * 30)
        
        # Different cache namespaces
        cache_entries = [
            # User data cache
            ('user_data', ['user:123:profile', 'user:456:preferences', 'user:789:settings']),
            # Product catalog cache
            ('product', ['product:abc123:details', 'product:xyz789:pricing', 'product:def456:inventory']),
            # Session cache
            ('session', ['session:sess_abc123', 'session:sess_xyz789', 'session:sess_def456']),
            # API response cache
            ('api', ['api:v1:/users/123', 'api:v1:/products/abc', 'api:v2:/orders/456'])
        ]
        
        namespace_distribution = defaultdict(lambda: defaultdict(int))
        
        for namespace, keys in cache_entries:
            print(f"\n{namespace.upper()} namespace:")
            
            for key in keys:
                assigned_node = self.assignment.assign_key(key)
                namespace_distribution[namespace][assigned_node] += 1
                
                print(f"  {key:<30} → {assigned_node}")
        
        # Analyze namespace distribution
        print(f"\nNamespace distribution analysis:")
        for namespace, node_dist in namespace_distribution.items():
            total_keys = sum(node_dist.values())
            nodes_used = len(node_dist)
            print(f"  {namespace}: {total_keys} keys across {nodes_used} nodes {dict(node_dist)}")
    
    def expiration_aware_strategy(self):
        """Demonstrate expiration-aware cache key strategy"""
        
        print("\nExpiration-Aware Cache Strategy:")
        print("=" * 40)
        
        # Group cache keys by expiration time
        expiration_groups = [
            ('short_term', 300, ['temp:session_token', 'temp:csrf_token', 'temp:otp_code']),
            ('medium_term', 3600, ['cache:user_profile', 'cache:product_info', 'cache:api_response']),
            ('long_term', 86400, ['static:config', 'static:feature_flags', 'static:translations'])
        ]
        
        print("Cache entries grouped by expiration time:")
        
        expiration_distribution = {}
        
        for group_name, ttl_seconds, keys in expiration_groups:
            print(f"\n{group_name.upper()} ({ttl_seconds}s TTL):")
            
            group_nodes = defaultdict(int)
            
            for key in keys:
                # Include TTL in key for potential co-location
                cache_key = f"{key}:ttl_{ttl_seconds}"
                assigned_node = self.assignment.assign_key(cache_key)
                group_nodes[assigned_node] += 1
                
                print(f"  {key:<25} → {assigned_node}")
            
            expiration_distribution[group_name] = dict(group_nodes)
            print(f"  Distribution: {dict(group_nodes)}")
        
        # Analyze expiration-based locality
        print(f"\nExpiration-based locality analysis:")
        for group_name, distribution in expiration_distribution.items():
            nodes_count = len(distribution)
            total_keys = sum(distribution.values())
            locality_score = total_keys / nodes_count if nodes_count > 0 else 0
            
            print(f"  {group_name}: {locality_score:.1f} keys per node (higher = better locality)")
    
    def hierarchical_cache_strategy(self):
        """Demonstrate hierarchical cache key strategy"""
        
        print("\nHierarchical Cache Strategy:")
        print("=" * 35)
        
        # Multi-level cache hierarchy
        cache_hierarchy = [
            ('L1:memory', ['L1:user:123', 'L1:product:abc', 'L1:session:xyz']),
            ('L2:redis', ['L2:user:123:extended', 'L2:product:abc:reviews', 'L2:analytics:daily']),
            ('L3:disk', ['L3:historical:user:123', 'L3:backup:product:abc', 'L3:archive:logs'])
        ]
        
        hierarchy_distribution = {}
        
        for level_name, keys in cache_hierarchy:
            print(f"\n{level_name}:")
            
            level_nodes = defaultdict(int)
            
            for key in keys:
                assigned_node = self.assignment.assign_key(key)
                level_nodes[assigned_node] += 1
                
                print(f"  {key:<30} → {assigned_node}")
            
            hierarchy_distribution[level_name] = dict(level_nodes)
        
        # Cross-level analysis
        print(f"\nCross-level cache distribution:")
        for level, distribution in hierarchy_distribution.items():
            print(f"  {level}: {len(distribution)} nodes used")
        
        # Check for potential cache coherency challenges
        all_used_nodes = set()
        for distribution in hierarchy_distribution.values():
            all_used_nodes.update(distribution.keys())
        
        print(f"  Total unique nodes across all levels: {len(all_used_nodes)}")
        print(f"  Cache coherency complexity: {'High' if len(all_used_nodes) > 4 else 'Moderate' if len(all_used_nodes) > 2 else 'Low'}")

# Demonstrate cache key strategies
cache_keys = CacheKeyStrategies()
cache_keys.namespace_strategy()
cache_keys.expiration_aware_strategy()
cache_keys.hierarchical_cache_strategy()
```

### User Session Keys

```python
class UserSessionKeyStrategies:
    """Key identification strategies for user session management"""
    
    def __init__(self):
        self.assignment = KeyAssignment('sha1')
        # Add session storage nodes
        for i in range(4):
            self.assignment.add_node(f"session-store-{i:02d}")
    
    def user_id_based_strategy(self):
        """Demonstrate user ID-based session key strategy"""
        
        print("User ID-Based Session Strategy:")
        print("=" * 35)
        
        # Simulate user sessions
        users = ['user_123', 'user_456', 'user_789', 'user_101', 'user_202']
        
        print("Single session per user:")
        user_to_node = {}
        
        for user_id in users:
            session_key = f"session:{user_id}"
            assigned_node = self.assignment.assign_key(session_key)
            user_to_node[user_id] = assigned_node
            
            print(f"  {session_key:<20} → {assigned_node}")
        
        # Multiple sessions per user (different devices)
        print(f"\nMultiple sessions per user (different devices):")
        
        for user_id in users[:3]:  # Just first 3 users for demo
            devices = ['web', 'mobile', 'tablet']
            user_sessions = []
            
            for device in devices:
                session_key = f"session:{user_id}:{device}"
                assigned_node = self.assignment.assign_key(session_key)
                user_sessions.append((session_key, assigned_node))
                
                print(f"  {session_key:<25} → {assigned_node}")
            
            # Check session locality for this user
            nodes_used = set(node for _, node in user_sessions)
            print(f"    {user_id} uses {len(nodes_used)} nodes: {', '.join(sorted(nodes_used))}")
    
    def session_token_strategy(self):
        """Demonstrate session token-based strategy"""
        
        print("\nSession Token-Based Strategy:")
        print("=" * 35)
        
        # Generate session tokens (simulated)
        import uuid
        
        session_tokens = [
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            'sess_abc123def456',  # Custom format
            'sess_xyz789ghi012'   # Custom format
        ]
        
        print("Session token distribution:")
        
        for token in session_tokens:
            session_key = f"session_token:{token}"
            assigned_node = self.assignment.assign_key(session_key)
            
            print(f"  {token:<36} → {assigned_node}")
        
        print(f"\nToken strategy benefits:")
        print(f"  + Excellent distribution (random tokens)")
        print(f"  + No user-based clustering")
        print(f"  + Scales well with concurrent sessions")
        print(f"  - No session locality for same user")
    
    def geographic_session_strategy(self):
        """Demonstrate geographic session affinity strategy"""
        
        print("\nGeographic Session Strategy:")
        print("=" * 35)
        
        # Sessions with geographic information
        geographic_sessions = [
            ('user_123', 'us-east-1', 'web'),
            ('user_123', 'us-west-2', 'mobile'),  # Same user, different region
            ('user_456', 'eu-west-1', 'web'),
            ('user_789', 'ap-south-1', 'mobile'),
            ('user_101', 'us-east-1', 'tablet'),
        ]
        
        print("Geographic session distribution:")
        
        regional_distribution = defaultdict(list)
        
        for user_id, region, device in geographic_sessions:
            # Include region in session key for geographic affinity
            session_key = f"session:{region}:{user_id}:{device}"
            assigned_node = self.assignment.assign_key(session_key)
            regional_distribution[region].append(assigned_node)
            
            print(f"  {session_key:<35} → {assigned_node}")
        
        # Analyze regional clustering
        print(f"\nRegional clustering analysis:")
        for region, nodes in regional_distribution.items():
            unique_nodes = set(nodes)
            clustering_ratio = len(nodes) / len(unique_nodes) if unique_nodes else 0
            print(f"  {region}: {len(nodes)} sessions on {len(unique_nodes)} nodes (ratio: {clustering_ratio:.1f})")
    
    def session_lifecycle_strategy(self):
        """Demonstrate session lifecycle-aware strategy"""
        
        print("\nSession Lifecycle Strategy:")
        print("=" * 30)
        
        # Sessions at different lifecycle stages
        session_states = [
            ('active', ['session:active:user_123', 'session:active:user_456']),
            ('idle', ['session:idle:user_789', 'session:idle:user_101']),
            ('expired', ['session:expired:user_202', 'session:expired:user_303']),
            ('pending_cleanup', ['session:cleanup:user_404', 'session:cleanup:user_505'])
        ]
        
        lifecycle_distribution = {}
        
        for state, sessions in session_states:
            print(f"\n{state.upper()} sessions:")
            
            state_nodes = defaultdict(int)
            
            for session_key in sessions:
                assigned_node = self.assignment.assign_key(session_key)
                state_nodes[assigned_node] += 1
                
                print(f"  {session_key:<30} → {assigned_node}")
            
            lifecycle_distribution[state] = dict(state_nodes)
        
        # Analyze lifecycle-based patterns
        print(f"\nLifecycle distribution summary:")
        for state, distribution in lifecycle_distribution.items():
            nodes_count = len(distribution)
            total_sessions = sum(distribution.values())
            print(f"  {state}: {total_sessions} sessions on {nodes_count} nodes")

# Demonstrate user session strategies
session_keys = UserSessionKeyStrategies()
session_keys.user_id_based_strategy()
session_keys.session_token_strategy()
session_keys.geographic_session_strategy()
session_keys.session_lifecycle_strategy()
```

## Performance Optimization

```python
class KeyAssignmentPerformanceOptimization:
    """Advanced performance optimizations for key assignment"""
    
    def __init__(self):
        self.assignment = KeyAssignment('sha1')
    
    def benchmark_assignment_performance(self):
        """Benchmark key assignment performance under various conditions"""
        
        print("Key Assignment Performance Benchmark:")
        print("=" * 45)
        
        # Setup different ring sizes
        ring_sizes = [10, 100, 1000, 5000]
        key_counts = [1000, 10000, 100000]
        
        for ring_size in ring_sizes:
            print(f"\nRing size: {ring_size} nodes")
            
            # Create fresh assignment instance
            test_assignment = KeyAssignment('sha1')
            
            # Add nodes
            setup_start = time.perf_counter()
            for i in range(ring_size):
                test_assignment.add_node(f"node-{i:04d}", virtual_node_count=150)
            setup_time = time.perf_counter() - setup_start
            
            print(f"  Setup time: {setup_time*1000:.2f} ms")
            print(f"  Total ring positions: {len(test_assignment.ring):,}")
            
            # Test assignment performance
            for key_count in key_counts:
                test_keys = [f"test_key_{i}" for i in range(key_count)]
                
                assign_start = time.perf_counter()
                for key in test_keys:
                    test_assignment.assign_key(key)
                assign_time = time.perf_counter() - assign_start
                
                assignments_per_sec = key_count / assign_time
                avg_time_us = (assign_time / key_count) * 1_000_000
                
                print(f"    {key_count:,} keys: {assignments_per_sec:,.0f} ops/sec ({avg_time_us:.2f} μs avg)")
    
    def memory_usage_analysis(self):
        """Analyze memory usage patterns"""
        
        print("\nMemory Usage Analysis:")
        print("=" * 25)
        
        import sys
        
        # Test memory usage with different configurations
        configs = [
            (100, 50, "Small cluster, few virtual nodes"),
            (100, 150, "Small cluster, many virtual nodes"),
            (1000, 50, "Large cluster, few virtual nodes"),
            (1000, 150, "Large cluster, many virtual nodes")
        ]
        
        for node_count, virtual_nodes, description in configs:
            test_assignment = KeyAssignment('sha1')
            
            # Measure memory before
            initial_size = sys.getsizeof(test_assignment.ring) + sys.getsizeof(test_assignment.sorted_positions)
            
            # Add nodes
            for i in range(node_count):
                test_assignment.add_node(f"node-{i:04d}", virtual_node_count=virtual_nodes)
            
            # Measure memory after
            final_size = sys.getsizeof(test_assignment.ring) + sys.getsizeof(test_assignment.sorted_positions)
            total_positions = len(test_assignment.ring)
            
            print(f"\n{description}:")
            print(f"  Nodes: {node_count}, Virtual nodes each: {virtual_nodes}")
            print(f"  Total positions: {total_positions:,}")
            print(f"  Memory usage: {final_size:,} bytes")
            print(f"  Bytes per position: {final_size/total_positions:.1f}")

# Run performance benchmarks
perf_optimizer = KeyAssignmentPerformanceOptimization()
perf_optimizer.benchmark_assignment_performance()
perf_optimizer.memory_usage_analysis()
```

## Summary

Key assignment in consistent hashing involves three critical components:

1. **Assignment Algorithm**: Deterministic process that maps keys to nodes using clockwise successor lookup with O(log n) complexity through binary search

2. **Key Identification**: Strategic formatting of keys based on data type (database records, cache entries, user sessions) to optimize distribution and operational clarity

3. **Performance Optimization**: Caching, batch processing, and memory-efficient data structures to handle millions of assignments per second

The assignment process must be fast, consistent across all system components, and optimized for the specific access patterns of the application. Production implementations should include comprehensive benchmarking, monitoring, and optimization for the expected scale and performance requirements.​​​​​​​​​​​​​​​​
