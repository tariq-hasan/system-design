# Hash Ring Construction

Hash ring construction forms the foundational layer of consistent hashing, establishing the abstract coordinate system that enables stable data distribution. The design choices made during ring construction—hash function selection, ring size determination, and data structure implementation—directly impact the system's performance, security, and scalability characteristics. Understanding these construction principles is essential for building production-ready consistent hashing implementations.

## Hash Space Design and Boundaries

The hash space defines the coordinate system for the consistent hashing ring, providing a fixed framework that remains constant regardless of the number of nodes in the system.

### Hash Space Selection Criteria

The choice of hash space size involves balancing several competing factors:

```python
import math
import hashlib
from typing import Dict, List, Optional, Tuple

class HashSpaceAnalysis:
    """Analyze different hash space options for consistent hashing"""
    
    def __init__(self):
        self.hash_spaces = {
            'SHA-1': {'bits': 160, 'size': 2**160},
            'SHA-256': {'bits': 256, 'size': 2**256},
            'MD5': {'bits': 128, 'size': 2**128},
            'SHA-512': {'bits': 512, 'size': 2**512},
            'CRC32': {'bits': 32, 'size': 2**32},
            'Custom64': {'bits': 64, 'size': 2**64}
        }
    
    def analyze_hash_space_properties(self):
        """Analyze mathematical properties of different hash spaces"""
        
        print("Hash Space Analysis for Consistent Hashing:")
        print("=" * 50)
        
        for name, props in self.hash_spaces.items():
            bits = props['bits']
            size = props['size']
            
            # Collision resistance (birthday paradox)
            collision_bound = 2 ** (bits // 2)
            
            # Practical node limits
            max_practical_nodes = min(1000000, size // 1000)  # Conservative estimate
            
            # Storage requirements per position
            bytes_per_position = math.ceil(bits / 8)
            
            print(f"\n{name} Hash Space ({bits}-bit):")
            print(f"  Total positions: 2^{bits} = {size:.2e}")
            print(f"  Collision resistance: ~2^{bits//2} = {collision_bound:.2e}")
            print(f"  Bytes per position: {bytes_per_position}")
            print(f"  Max practical nodes: {max_practical_nodes:,}")
            
            # Security assessment
            if bits >= 256:
                security = "Quantum-resistant"
            elif bits >= 160:
                security = "Cryptographically secure"
            elif bits >= 128:
                security = "Strong for most applications"
            elif bits >= 64:
                security = "Adequate for medium systems"
            else:
                security = "Weak, testing only"
            
            print(f"  Security level: {security}")
            
            # Performance characteristics
            if name in ['CRC32', 'Custom64']:
                performance = "Very fast"
            elif name == 'MD5':
                performance = "Fast"
            elif name == 'SHA-1':
                performance = "Moderate"
            else:
                performance = "Slower"
            
            print(f"  Performance: {performance}")

# Demonstrate hash space analysis
space_analyzer = HashSpaceAnalysis()
space_analyzer.analyze_hash_space_properties()
```

### Circular Boundary Mathematics

The circular nature of the hash space is implemented through modular arithmetic:

```python
class CircularHashSpace:
    """Implementation of circular hash space mathematics"""
    
    def __init__(self, hash_function='sha1'):
        """Initialize hash space with specified hash function"""
        self.hash_function = hash_function
        
        # Define space size based on hash function
        if hash_function == 'sha1':
            self.space_size = 2**160
            self.hash_func = hashlib.sha1
        elif hash_function == 'sha256':
            self.space_size = 2**256
            self.hash_func = hashlib.sha256
        elif hash_function == 'md5':
            self.space_size = 2**128
            self.hash_func = hashlib.md5
        else:
            # Default to 32-bit for demonstration
            self.space_size = 2**32
            self.hash_func = hashlib.md5
        
        self.max_position = self.space_size - 1
    
    def hash_to_position(self, key: str) -> int:
        """Convert any key to a position on the ring"""
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        # Generate hash
        hash_obj = self.hash_func(key)
        hash_hex = hash_obj.hexdigest()
        
        # Convert to integer and map to ring
        hash_int = int(hash_hex, 16)
        position = hash_int % self.space_size
        
        return position
    
    def demonstrate_circular_properties(self):
        """Demonstrate circular wraparound properties"""
        
        print("Circular Hash Space Properties:")
        print("=" * 35)
        
        print(f"Hash function: {self.hash_function}")
        print(f"Space size: {self.space_size:,}")
        print(f"Position range: [0, {self.max_position:,}]")
        
        # Demonstrate wraparound
        print(f"\nWraparound demonstration:")
        print(f"Maximum position: {self.max_position:,}")
        print(f"Next position: ({self.max_position} + 1) % {self.space_size} = 0")
        
        # Show sample positions
        sample_keys = ['node1', 'node2', 'node3', 'key1', 'key2']
        print(f"\nSample positions:")
        
        positions = []
        for key in sample_keys:
            pos = self.hash_to_position(key)
            percentage = (pos / self.space_size) * 100
            positions.append((key, pos, percentage))
            print(f"  {key}: {pos:,} ({percentage:.6f}% around ring)")
        
        # Sort by position to show ring order
        positions.sort(key=lambda x: x[1])
        print(f"\nRing order (clockwise):")
        for i, (key, pos, pct) in enumerate(positions):
            next_key = positions[(i + 1) % len(positions)][0]
            print(f"  {key} → {next_key}")
        
        return positions
    
    def calculate_ring_distances(self, pos1: int, pos2: int) -> Dict[str, int]:
        """Calculate distances between positions on ring"""
        
        # Clockwise distance from pos1 to pos2
        if pos2 >= pos1:
            clockwise = pos2 - pos1
        else:
            clockwise = (self.space_size - pos1) + pos2
        
        # Counterclockwise distance
        counterclockwise = self.space_size - clockwise
        
        # Minimum distance
        minimum = min(clockwise, counterclockwise)
        
        return {
            'clockwise': clockwise,
            'counterclockwise': counterclockwise,
            'minimum': minimum
        }

# Demonstrate circular hash space
circular_space = CircularHashSpace('sha1')
positions = circular_space.demonstrate_circular_properties()

# Show distance calculations
if len(positions) >= 2:
    pos1 = positions[0][1]
    pos2 = positions[1][1]
    distances = circular_space.calculate_ring_distances(pos1, pos2)
    
    print(f"\nDistance from {positions[0][0]} to {positions[1][0]}:")
    print(f"  Clockwise: {distances['clockwise']:,}")
    print(f"  Counterclockwise: {distances['counterclockwise']:,}")
    print(f"  Minimum: {distances['minimum']:,}")
```

## Hash Function Selection

The choice of hash function significantly impacts both the performance and security characteristics of the consistent hashing implementation.

### Hash Function Comparison

```python
import time
import hashlib
from collections import defaultdict

class HashFunctionComparison:
    """Compare different hash functions for consistent hashing"""
    
    def __init__(self):
        self.hash_functions = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512,
        }
        
        # Non-cryptographic hash functions (simulated)
        self.fast_functions = {
            'crc32': self._crc32_hash,
            'murmur3': self._murmur3_hash,  # Simplified simulation
        }
    
    def _crc32_hash(self, data):
        """Simulate CRC32 hash function"""
        import zlib
        if isinstance(data, str):
            data = data.encode('utf-8')
        return zlib.crc32(data).to_bytes(4, 'big')
    
    def _murmur3_hash(self, data):
        """Simulate MurmurHash3 (simplified)"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        # Simple simulation - not actual MurmurHash3
        hash_val = hash(data) % (2**32)
        return hash_val.to_bytes(4, 'big')
    
    def benchmark_hash_functions(self, num_keys: int = 10000):
        """Benchmark hash function performance"""
        
        print("Hash Function Performance Benchmark:")
        print("=" * 40)
        
        # Generate test keys
        test_keys = [f"key_{i:06d}" for i in range(num_keys)]
        
        all_functions = {**self.hash_functions, **self.fast_functions}
        
        results = {}
        
        for name, hash_func in all_functions.items():
            print(f"\nTesting {name.upper()}:")
            
            # Performance timing
            start_time = time.perf_counter()
            hash_values = []
            
            try:
                for key in test_keys:
                    if name in self.hash_functions:
                        # Cryptographic hash functions
                        hash_obj = hash_func(key.encode('utf-8'))
                        hash_bytes = hash_obj.digest()
                    else:
                        # Non-cryptographic functions
                        hash_bytes = hash_func(key)
                    
                    # Convert to integer for distribution analysis
                    hash_int = int.from_bytes(hash_bytes[:4], 'big')  # Use first 4 bytes
                    hash_values.append(hash_int)
                
                end_time = time.perf_counter()
                
                # Calculate performance metrics
                total_time = end_time - start_time
                hashes_per_second = num_keys / total_time
                microseconds_per_hash = (total_time * 1_000_000) / num_keys
                
                print(f"  Performance: {hashes_per_second:,.0f} hashes/sec")
                print(f"  Time per hash: {microseconds_per_hash:.2f} μs")
                
                # Analyze distribution quality
                distribution_quality = self._analyze_distribution(hash_values)
                
                print(f"  Distribution chi-squared: {distribution_quality['chi_squared']:.2f}")
                print(f"  Distribution quality: {distribution_quality['quality']}")
                
                # Security assessment
                if name in ['sha256', 'sha512']:
                    security = "Cryptographically secure"
                elif name in ['sha1', 'md5']:
                    security = "Legacy cryptographic"
                else:
                    security = "Non-cryptographic"
                
                print(f"  Security level: {security}")
                
                results[name] = {
                    'hashes_per_second': hashes_per_second,
                    'microseconds_per_hash': microseconds_per_hash,
                    'distribution_quality': distribution_quality,
                    'security': security
                }
                
            except Exception as e:
                print(f"  Error testing {name}: {e}")
                results[name] = None
        
        return results
    
    def _analyze_distribution(self, hash_values: List[int], num_bins: int = 100) -> Dict:
        """Analyze hash value distribution quality"""
        
        # Create bins for chi-squared test
        max_val = max(hash_values)
        bin_size = max_val // num_bins
        
        bin_counts = [0] * num_bins
        for val in hash_values:
            bin_index = min(val // bin_size, num_bins - 1)
            bin_counts[bin_index] += 1
        
        # Chi-squared test for uniformity
        expected_per_bin = len(hash_values) / num_bins
        chi_squared = sum((count - expected_per_bin)**2 / expected_per_bin 
                         for count in bin_counts)
        
        # Quality assessment
        if chi_squared < num_bins * 1.1:
            quality = "Excellent"
        elif chi_squared < num_bins * 1.3:
            quality = "Good"
        elif chi_squared < num_bins * 1.5:
            quality = "Acceptable"
        else:
            quality = "Poor"
        
        return {
            'chi_squared': chi_squared,
            'expected_chi_squared': num_bins,
            'quality': quality
        }
    
    def recommend_hash_function(self, requirements: Dict[str, str]) -> str:
        """Recommend hash function based on requirements"""
        
        security_level = requirements.get('security', 'medium')
        performance_priority = requirements.get('performance', 'medium')
        system_scale = requirements.get('scale', 'medium')
        
        print(f"\nHash Function Recommendation:")
        print(f"Requirements: {requirements}")
        
        if security_level == 'high':
            if performance_priority == 'high':
                recommendation = "SHA-256 (best balance of security and performance)"
            else:
                recommendation = "SHA-512 (maximum security)"
        elif security_level == 'medium':
            if performance_priority == 'high':
                recommendation = "SHA-1 (good security, better performance)"
            else:
                recommendation = "SHA-256 (good security and performance)"
        else:  # low security requirements
            if performance_priority == 'high':
                recommendation = "MurmurHash3 (maximum performance)"
            else:
                recommendation = "MD5 (reasonable performance and distribution)"
        
        print(f"Recommendation: {recommendation}")
        return recommendation

# Benchmark hash functions
hash_comparison = HashFunctionComparison()
results = hash_comparison.benchmark_hash_functions(5000)

# Get recommendation
requirements = {
    'security': 'medium',
    'performance': 'high',
    'scale': 'large'
}
recommendation = hash_comparison.recommend_hash_function(requirements)
```

### Hash Function Implementation Best Practices

```python
class HashFunctionImplementation:
    """Best practices for implementing hash functions in consistent hashing"""
    
    def __init__(self, hash_function_name: str = 'sha1'):
        self.hash_function_name = hash_function_name
        self._setup_hash_function()
    
    def _setup_hash_function(self):
        """Set up hash function based on name"""
        hash_configs = {
            'sha1': {'func': hashlib.sha1, 'space_size': 2**160},
            'sha256': {'func': hashlib.sha256, 'space_size': 2**256},
            'md5': {'func': hashlib.md5, 'space_size': 2**128},
        }
        
        if self.hash_function_name not in hash_configs:
            raise ValueError(f"Unsupported hash function: {self.hash_function_name}")
        
        config = hash_configs[self.hash_function_name]
        self.hash_func = config['func']
        self.space_size = config['space_size']
    
    def hash_with_validation(self, key: str) -> int:
        """Hash a key with input validation and error handling"""
        
        # Input validation
        if not isinstance(key, (str, bytes)):
            raise TypeError("Key must be string or bytes")
        
        if isinstance(key, str):
            if not key:
                raise ValueError("Key cannot be empty")
            key_bytes = key.encode('utf-8')
        else:
            key_bytes = key
        
        try:
            # Generate hash
            hash_obj = self.hash_func(key_bytes)
            hash_hex = hash_obj.hexdigest()
            
            # Convert to position
            hash_int = int(hash_hex, 16)
            position = hash_int % self.space_size
            
            return position
            
        except Exception as e:
            raise RuntimeError(f"Hash computation failed: {e}")
    
    def demonstrate_hash_consistency(self):
        """Demonstrate hash function consistency properties"""
        
        print("Hash Function Consistency Demonstration:")
        print("=" * 45)
        
        test_key = "test_key_12345"
        
        # Test deterministic property
        print(f"Testing deterministic property with key: '{test_key}'")
        
        positions = []
        for i in range(5):
            pos = self.hash_with_validation(test_key)
            positions.append(pos)
        
        all_same = all(p == positions[0] for p in positions)
        print(f"  5 consecutive hashes: {all_same}")
        print(f"  All positions: {positions}")
        print(f"  Result: {'✅ DETERMINISTIC' if all_same else '❌ NON-DETERMINISTIC'}")
        
        # Test avalanche effect
        print(f"\nTesting avalanche effect:")
        
        similar_keys = [
            "test_key_12345",
            "test_key_12346",  # Last character changed
            "Test_key_12345",  # Case changed
            "test_key_12345 ", # Space added
        ]
        
        avalanche_positions = []
        for key in similar_keys:
            pos = self.hash_with_validation(key)
            avalanche_positions.append((key, pos))
            print(f"  '{key}' → {pos}")
        
        # Calculate position differences
        base_pos = avalanche_positions[0][1]
        for key, pos in avalanche_positions[1:]:
            diff = abs(pos - base_pos)
            diff_percentage = (diff / self.space_size) * 100
            print(f"  Difference from base: {diff:,} ({diff_percentage:.4f}%)")
        
        # Test uniformity with multiple keys
        print(f"\nTesting distribution uniformity:")
        
        num_test_keys = 1000
        test_keys = [f"uniform_test_{i}" for i in range(num_test_keys)]
        positions = [self.hash_with_validation(key) for key in test_keys]
        
        # Analyze distribution
        num_bins = 10
        bin_size = self.space_size // num_bins
        bin_counts = [0] * num_bins
        
        for pos in positions:
            bin_index = min(pos // bin_size, num_bins - 1)
            bin_counts[bin_index] += 1
        
        expected_per_bin = num_test_keys / num_bins
        max_deviation = max(abs(count - expected_per_bin) for count in bin_counts)
        deviation_percentage = (max_deviation / expected_per_bin) * 100
        
        print(f"  Test keys: {num_test_keys}")
        print(f"  Bins: {num_bins}")
        print(f"  Expected per bin: {expected_per_bin}")
        print(f"  Max deviation: {max_deviation:.1f} ({deviation_percentage:.1f}%)")
        
        if deviation_percentage < 20:
            uniformity = "Good"
        elif deviation_percentage < 40:
            uniformity = "Acceptable"
        else:
            uniformity = "Poor"
        
        print(f"  Uniformity: {uniformity}")

# Demonstrate hash function implementation
hash_impl = HashFunctionImplementation('sha1')
hash_impl.demonstrate_hash_consistency()
```

## Data Structure Implementation

The choice of data structure for maintaining the hash ring significantly impacts lookup performance and memory usage.

### Ring Data Structure Options

```python
import bisect
import time
from typing import List, Optional, Dict, Any

class RingDataStructureComparison:
    """Compare different data structures for hash ring implementation"""
    
    def __init__(self):
        self.test_sizes = [100, 1000, 10000, 100000]
    
    def benchmark_data_structures(self):
        """Benchmark different ring data structures"""
        
        print("Ring Data Structure Performance Comparison:")
        print("=" * 50)
        
        for size in self.test_sizes:
            print(f"\nTesting with {size:,} nodes:")
            
            # Generate test data
            nodes = [(f"node_{i}", hash(f"node_{i}") % (2**32)) for i in range(size)]
            test_keys = [f"key_{i}" for i in range(1000)]  # Fixed number of lookups
            
            # Test different implementations
            implementations = {
                'SortedList': SortedListRing(),
                'BTreeRing': BTreeRing(),
                'SkipListRing': SkipListRing()
            }
            
            for name, impl in implementations.items():
                # Setup
                setup_start = time.perf_counter()
                for node_id, position in nodes:
                    impl.add_node(node_id, position)
                setup_time = time.perf_counter() - setup_start
                
                # Lookup performance
                lookup_start = time.perf_counter()
                for key in test_keys:
                    impl.get_node_for_key(key)
                lookup_time = time.perf_counter() - lookup_start
                
                # Memory usage (estimated)
                memory_estimate = impl.estimate_memory_usage()
                
                print(f"  {name}:")
                print(f"    Setup time: {setup_time*1000:.2f} ms")
                print(f"    Lookup time: {lookup_time*1000:.2f} ms (1000 lookups)")
                print(f"    Avg lookup: {lookup_time/len(test_keys)*1000000:.2f} μs")
                print(f"    Memory estimate: {memory_estimate/1024:.1f} KB")

class SortedListRing:
    """Hash ring implementation using sorted list"""
    
    def __init__(self):
        self.positions = []  # Sorted list of positions
        self.position_to_node = {}  # Position -> node mapping
    
    def add_node(self, node_id: str, position: int):
        """Add a node at specified position"""
        if position not in self.position_to_node:
            bisect.insort(self.positions, position)
        self.position_to_node[position] = node_id
    
    def remove_node(self, node_id: str, position: int):
        """Remove a node from specified position"""
        if position in self.position_to_node:
            self.positions.remove(position)
            del self.position_to_node[position]
    
    def get_node_for_key(self, key: str) -> Optional[str]:
        """Find node responsible for key using binary search"""
        if not self.positions:
            return None
        
        key_position = hash(key) % (2**32)
        
        # Binary search for first position >= key_position
        index = bisect.bisect_left(self.positions, key_position)
        
        # If exact match or found larger position
        if index < len(self.positions):
            return self.position_to_node[self.positions[index]]
        
        # Wrap around to first position
        return self.position_to_node[self.positions[0]]
    
    def estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes"""
        # Rough estimate: 8 bytes per position + 50 bytes per node_id
        return len(self.positions) * (8 + 50)

class BTreeRing:
    """Hash ring implementation using B-tree-like structure"""
    
    def __init__(self):
        self.tree = {}  # Simplified tree representation
        self.position_to_node = {}
    
    def add_node(self, node_id: str, position: int):
        """Add node to B-tree structure"""
        self.tree[position] = node_id
        self.position_to_node[position] = node_id
    
    def remove_node(self, node_id: str, position: int):
        """Remove node from B-tree structure"""
        if position in self.tree:
            del self.tree[position]
            del self.position_to_node[position]
    
    def get_node_for_key(self, key: str) -> Optional[str]:
        """Find node using tree traversal"""
        if not self.tree:
            return None
        
        key_position = hash(key) % (2**32)
        
        # Find smallest position >= key_position
        candidates = [pos for pos in self.tree.keys() if pos >= key_position]
        
        if candidates:
            return self.tree[min(candidates)]
        
        # Wrap around
        return self.tree[min(self.tree.keys())]
    
    def estimate_memory_usage(self) -> int:
        """Estimate memory usage"""
        # Tree overhead + position storage + node references
        return len(self.tree) * (8 + 50 + 20)  # Additional overhead for tree structure

class SkipListRing:
    """Hash ring implementation using skip list"""
    
    def __init__(self):
        self.nodes = {}  # Simplified skip list representation
        self.position_to_node = {}
    
    def add_node(self, node_id: str, position: int):
        """Add node to skip list"""
        self.nodes[position] = node_id
        self.position_to_node[position] = node_id
    
    def remove_node(self, node_id: str, position: int):
        """Remove node from skip list"""
        if position in self.nodes:
            del self.nodes[position]
            del self.position_to_node[position]
    
    def get_node_for_key(self, key: str) -> Optional[str]:
        """Find node using skip list traversal"""
        if not self.nodes:
            return None
        
        key_position = hash(key) % (2**32)
        
        # Simplified skip list lookup (using sorted keys for demo)
        sorted_positions = sorted(self.nodes.keys())
        
        for pos in sorted_positions:
            if pos >= key_position:
                return self.nodes[pos]
        
        # Wrap around
        return self.nodes[sorted_positions[0]]
    
    def estimate_memory_usage(self) -> int:
        """Estimate memory usage"""
        # Skip list has higher overhead but better performance characteristics
        return len(self.nodes) * (8 + 50 + 30)  # Additional overhead for skip list levels

# Run data structure comparison
ds_comparison = RingDataStructureComparison()
ds_comparison.benchmark_data_structures()
```

### Production Implementation Template

```python
class ProductionHashRing:
    """Production-ready hash ring implementation"""
    
    def __init__(self, hash_function: str = 'sha1', virtual_nodes: int = 150):
        """Initialize hash ring with production defaults"""
        self.hash_function = hash_function
        self.virtual_nodes_per_physical = virtual_nodes
        
        # Core ring data structures
        self.ring = {}  # position -> physical_node_id
        self.sorted_positions = []  # Sorted list for binary search
        
        # Virtual node management
        self.physical_nodes = set()
        self.virtual_node_map = {}  # virtual_node_id -> (position, physical_node_id)
        
        # Performance optimization
        self._lookup_cache = {}  # LRU cache for frequent lookups
        self._cache_size = 1000
        
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
        elif self.hash_function == 'md5':
            self.hasher = hashlib.md5
            self.space_size = 2**128
        else:
            raise ValueError(f"Unsupported hash function: {self.hash_function}")
    
    def _hash_to_position(self, key: str) -> int:
        """Convert key to ring position"""
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        hash_obj = self.hasher(key)
        hash_int = int(hash_obj.hexdigest(), 16)
        return hash_int % self.space_size
    
    def add_physical_node(self, node_id: str) -> Dict[str, Any]:
        """Add a physical node with virtual nodes"""
        if node_id in self.physical_nodes:
            raise ValueError(f"Node {node_id} already exists")
        
        self.physical_nodes.add(node_id)
        virtual_positions = []
        
        # Create virtual nodes
        for i in range(self.virtual_nodes_per_physical):
            virtual_id = f"{node_id}:vnode_{i}"
            position = self._hash_to_position(virtual_id)
            
            # Handle position collisions (very rare but possible)
            while position in self.ring:
                virtual_id = f"{node_id}:vnode_{i}_collision_{hash(virtual_id)}"
                position = self._hash_to_position(virtual_id)
            
            # Add to ring
            self.ring[position] = node_id
            self.virtual_node_map[virtual_id] = (position, node_id)
            virtual_positions.append(position)
        
        # Update sorted positions
        self.sorted_positions = sorted(self.ring.keys())
        
        # Clear lookup cache (topology changed)
        self._lookup_cache.clear()
        
        return {
            'node_id': node_id,
            'virtual_nodes_created': len(virtual_positions),
            'positions': virtual_positions,
            'total_ring_size': len(self.ring)
        }
    
    def remove_physical_node(self, node_id: str) -> Dict[str, Any]:
        """Remove a physical node and all its virtual nodes"""
        if node_id not in self.physical_nodes:
            raise ValueError(f"Node {node_id} does not exist")
        
        self.physical_nodes.remove(node_id)
        removed_positions = []
        
        # Remove all virtual nodes for this physical node
        positions_to_remove = [pos for pos, phys_node in self.ring.items() 
                              if phys_node == node_id]
        
        for position in positions_to_remove:
            del self.ring[position]
            removed_positions.append(position)
        
        # Remove virtual node mappings
        virtual_nodes_to_remove = [vnode_id for vnode_id, (pos, phys_node) 
                                  in self.virtual_node_map.items() 
                                  if phys_node == node_id]
        
        for vnode_id in virtual_nodes_to_remove:
            del self.virtual_node_map[vnode_id]
        
        # Update sorted positions
        self.sorted_positions = sorted(self.ring.keys())
        
        # Clear lookup cache
        self._lookup_cache.clear()
        
        return {
            'node_id': node_id,
            'virtual_nodes_removed': len(removed_positions),
            'positions': removed_positions,
            'total_ring_size': len(self.ring)
        }
    
    def get_node_for_key(self, key: str) -> Optional[str]:
        """Find responsible node for key with caching"""
        
        # Check cache first
        if key in self._lookup_cache:
            return self._lookup_cache[key]
        
        if not self.sorted_positions:
            return None
        
        key_position = self._hash_to_position(key)
        
        # Binary search for first position >= key_position
        index = bisect.bisect_left(self.sorted_positions, key_position)
        
        if index < len(self.sorted_positions):
            responsible_position = self.sorted_positions[index]
        else:
            # Wrap around to first position
            responsible_position = self.sorted_positions[0]
        
        responsible_node = self.ring[responsible_position]
        
        # Update cache (with simple LRU eviction)
        if len(self._lookup_cache) >= self._cache_size:
            # Remove oldest entry (simplified LRU)
            oldest_key = next(iter(self._lookup_cache))
            del self._lookup_cache[oldest_key]
        
        self._lookup_cache[key] = responsible_node
        return responsible_node
    
    def get_ring_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ring statistics"""
        
        if not self.physical_nodes:
            return {'empty_ring': True}
        
        # Load distribution analysis
        load_distribution = {}
        for position, node in self.ring.items():
            load_distribution[node] = load_distribution.get(node, 0) + 1
        
        loads = list(load_distribution.values())
        expected_load = len(self.ring) / len(self.physical_nodes)
        
        return {
            'physical_nodes': len(self.physical_nodes),
            'virtual_nodes': len(self.ring),
            'virtual_nodes_per_physical': self.virtual_nodes_per_physical,
            'hash_function': self.hash_function,
            'space_size': self.space_size,
            'load_distribution': load_distribution,
            'expected_load_per_node': expected_load,
            'min_load': min(loads),
            'max_load': max(loads),
            'load_imbalance_ratio': max(loads) / min(loads) if min(loads) > 0 else float('inf'),
            'cache_hit_ratio': len(self._lookup_cache) / max(1, self._cache_size)
        }
    
    def demonstrate_ring_construction(self):
        """Demonstrate complete ring construction process"""
        
        print("Production Hash Ring Construction Demo:")
        print("=" * 45)
        
        # Add nodes incrementally
        nodes_to_add = ['web-01', 'web-02', 'web-03', 'cache-01', 'cache-02']
        
        for node in nodes_to_add:
            print(f"\nAdding node: {node}")
            result = self.add_physical_node(node)
            
            print(f"  Virtual nodes created: {result['virtual_nodes_created']}")
            print(f"  Total ring positions: {result['total_ring_size']}")
            
            # Show ring statistics
            stats = self.get_ring_statistics()
            print(f"  Load balance ratio: {stats['load_imbalance_ratio']:.2f}:1")
        
        # Test key assignments
        print(f"\nTesting key assignments:")
        test_keys = ['user:12345', 'session:abc123', 'product:67890', 'cart:xyz789']
        
        for key in test_keys:
            node = self.get_node_for_key(key)
            key_position = self._hash_to_position(key)
            print(f"  {key} (pos: {key_position}) → {node}")
        
        # Final statistics
        final_stats = self.get_ring_statistics()
        print(f"\nFinal Ring Statistics:")
        print(f"  Physical nodes: {final_stats['physical_nodes']}")
        print(f"  Virtual nodes: {final_stats['virtual_nodes']}")
        print(f"  Load balance: {final_stats['min_load']}-{final_stats['max_load']} virtual nodes per physical node")
        print(f"  Imbalance ratio: {final_stats['load_imbalance_ratio']:.2f}:1")

# Demonstrate production hash ring construction
production_ring = ProductionHashRing(hash_function='sha1', virtual_nodes=150)
production_ring.demonstrate_ring_construction()
```

## Summary

Hash ring construction involves three critical design decisions:

1. **Hash Space Selection**: Choose appropriate size (2^128 to 2^256) balancing security and performance needs
2. **Hash Function Choice**: Select function optimizing for security requirements, performance characteristics, and distribution quality
3. **Data Structure Implementation**: Use sorted arrays with binary search for O(log n) lookups, or more advanced structures for specialized needs

These foundational choices directly impact system performance, security, and operational characteristics. Production implementations should include virtual nodes, lookup caching, comprehensive monitoring, and robust error handling to ensure reliable operation at scale.​​​​​​​​​​​​​​​​
