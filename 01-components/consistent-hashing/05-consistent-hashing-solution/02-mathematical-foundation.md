# Mathematical Foundation of Consistent Hashing

The mathematical principles underlying consistent hashing provide the theoretical guarantees that make it suitable for production distributed systems. Understanding these foundations is crucial for system designers because they explain why consistent hashing works reliably at scale and help in making informed decisions about hash functions, ring sizes, and performance trade-offs. The mathematics also reveal the elegant properties that emerge from seemingly simple design choices.

## Hash Space Design Principles

The choice of hash space size is fundamental to consistent hashing's effectiveness. The hash space must be large enough to minimize collisions while remaining computationally tractable for production systems.

### Hash Space Size Selection

Modern consistent hashing implementations typically use one of several well-established hash space sizes:

```python
import math

class HashSpaceAnalysis:
    def __init__(self):
        self.hash_spaces = {
            'SHA-1': 2**160,
            'SHA-256': 2**256,
            'MD5': 2**128,
            'CRC32': 2**32,
            'Custom64': 2**64
        }
    
    def analyze_hash_spaces(self):
        """Analyze different hash space options"""
        print("Hash Space Comparison:")
        print("=" * 80)
        
        for name, size in self.hash_spaces.items():
            # Calculate key properties
            decimal_digits = len(str(size))
            hex_digits = math.ceil(math.log(size, 16))
            collision_resistance = math.log2(math.sqrt(size))  # Birthday paradox
            
            # Storage requirements per ring position
            bytes_per_position = math.ceil(math.log(size, 256))
            
            print(f"\n{name} Hash Space:")
            print(f"  Size: 2^{int(math.log2(size))} = {size:,}")
            print(f"  Decimal digits: {decimal_digits}")
            print(f"  Hex digits: {hex_digits}")
            print(f"  Collision resistance: ~2^{collision_resistance:.0f} operations")
            print(f"  Storage per position: {bytes_per_position} bytes")
            
            # Practical considerations
            if size >= 2**128:
                security_level = "Cryptographically secure"
            elif size >= 2**64:
                security_level = "Strong for most applications"
            elif size >= 2**32:
                security_level = "Adequate for small-medium systems"
            else:
                security_level = "Weak, use only for testing"
            
            print(f"  Security assessment: {security_level}")

# Demonstrate hash space analysis
analyzer = HashSpaceAnalysis()
analyzer.analyze_hash_spaces()
```

### SHA-1 Based Hash Space (2^160 - 1)

SHA-1 provides a 160-bit hash space, which has been the traditional choice for many consistent hashing implementations:

```python
class SHA1HashSpace:
    def __init__(self):
        self.space_size = 2**160
        self.max_value = self.space_size - 1
    
    def demonstrate_sha1_properties(self):
        """Demonstrate mathematical properties of SHA-1 hash space"""
        
        print("SHA-1 Hash Space Properties:")
        print("=" * 40)
        
        # Basic properties
        print(f"Space size: 2^160 = {self.space_size:,}")
        print(f"Maximum value: {self.max_value:,}")
        print(f"Range: [0, {self.max_value}]")
        
        # Scale comparison
        print(f"\nScale comparison:")
        atoms_in_universe = 10**80
        print(f"Estimated atoms in universe: ~{atoms_in_universe:.0e}")
        print(f"SHA-1 space size: {self.space_size:.2e}")
        print(f"Ratio: {self.space_size/atoms_in_universe:.1e} times larger")
        
        # Collision resistance
        birthday_bound = math.sqrt(self.space_size)
        print(f"\nCollision resistance:")
        print(f"Birthday paradox bound: ~2^{math.log2(birthday_bound):.0f} = {birthday_bound:.2e}")
        print(f"Practical security: Effectively collision-free for distributed systems")
        
        # Node distribution analysis
        max_reasonable_nodes = 10**6  # 1 million nodes
        average_space_per_node = self.space_size // max_reasonable_nodes
        print(f"\nNode distribution (1 million nodes):")
        print(f"Average space per node: {average_space_per_node:.2e}")
        print(f"Space utilization: {max_reasonable_nodes/self.space_size:.2e} (essentially zero)")
    
    def calculate_collision_probability(self, num_items):
        """Calculate collision probability using birthday paradox"""
        if num_items >= math.sqrt(self.space_size):
            return 1.0  # Certain collision
        
        # Approximation for birthday paradox
        exponent = -(num_items * (num_items - 1)) / (2 * self.space_size)
        probability = 1 - math.exp(exponent)
        return probability
    
    def demonstrate_collision_analysis(self):
        """Show collision probabilities for various system sizes"""
        
        print("\nCollision Probability Analysis:")
        print("-" * 40)
        
        test_scenarios = [
            (1000, "Small cluster"),
            (10000, "Medium cluster"), 
            (100000, "Large cluster"),
            (1000000, "Massive cluster"),
            (10000000, "Theoretical maximum")
        ]
        
        for num_items, description in test_scenarios:
            prob = self.calculate_collision_probability(num_items)
            print(f"{description} ({num_items:,} items):")
            print(f"  Collision probability: {prob:.2e}")
            print(f"  Assessment: {'Negligible' if prob < 1e-10 else 'Low' if prob < 1e-6 else 'Moderate' if prob < 0.01 else 'High'}")

sha1_demo = SHA1HashSpace()
sha1_demo.demonstrate_sha1_properties()
sha1_demo.demonstrate_collision_analysis()
```

### SHA-256 Based Hash Space (2^256 - 1)

SHA-256 provides an even larger hash space, offering enhanced security margins:

```python
class SHA256HashSpace:
    def __init__(self):
        self.space_size = 2**256
        self.max_value = self.space_size - 1
    
    def compare_with_sha1(self):
        """Compare SHA-256 with SHA-1 hash space"""
        
        sha1_size = 2**160
        ratio = self.space_size / sha1_size
        
        print("SHA-256 vs SHA-1 Comparison:")
        print("=" * 40)
        
        print(f"SHA-1 space: 2^160 = {sha1_size:.2e}")
        print(f"SHA-256 space: 2^256 = {self.space_size:.2e}")
        print(f"Size ratio: 2^96 = {ratio:.2e}")
        print(f"SHA-256 is {ratio:.0e} times larger than SHA-1")
        
        # Security implications
        sha1_birthday = math.sqrt(sha1_size)
        sha256_birthday = math.sqrt(self.space_size)
        
        print(f"\nCollision resistance comparison:")
        print(f"SHA-1 birthday bound: 2^{math.log2(sha1_birthday):.0f}")
        print(f"SHA-256 birthday bound: 2^{math.log2(sha256_birthday):.0f}")
        print(f"Security improvement: 2^{math.log2(sha256_birthday) - math.log2(sha1_birthday):.0f}")
        
        # Practical implications
        print(f"\nPractical implications:")
        print(f"SHA-1: Secure for current distributed systems")
        print(f"SHA-256: Future-proof against quantum computing threats")
        print(f"Performance: SHA-256 ~20% slower than SHA-1")
        print(f"Memory usage: Same for ring storage (positions truncated)")

sha256_demo = SHA256HashSpace()
sha256_demo.compare_with_sha1()
```

## Circular Mapping Mathematics

The circular nature of the hash space is mathematically crucial for consistent hashing's properties. This wraparound behavior ensures that the ring has no "edges" that could create asymmetries.

### Modular Arithmetic Foundation

```python
class CircularMappingMath:
    def __init__(self, hash_space_size):
        self.space_size = hash_space_size
        self.max_value = hash_space_size - 1
    
    def demonstrate_wraparound(self):
        """Demonstrate mathematical wraparound properties"""
        
        print("Circular Mapping Mathematics:")
        print("=" * 40)
        
        # Basic wraparound
        print("Basic wraparound examples:")
        examples = [
            (self.max_value, 1),
            (self.max_value - 5, 10),
            (0, -1),
            (5, -10)
        ]
        
        for start, offset in examples:
            result = (start + offset) % self.space_size
            print(f"({start} + {offset}) mod {self.space_size} = {result}")
            
            if start + offset < 0:
                unwrapped = start + offset + self.space_size
                print(f"  Negative wraparound: {start + offset} → {unwrapped} → {result}")
            elif start + offset >= self.space_size:
                print(f"  Positive wraparound: {start + offset} → {result}")
    
    def calculate_ring_distance(self, pos1, pos2):
        """Calculate minimum distance between two positions on ring"""
        
        # Forward distance (pos1 to pos2 clockwise)
        if pos2 >= pos1:
            forward_distance = pos2 - pos1
        else:
            forward_distance = (self.space_size - pos1) + pos2
        
        # Backward distance (pos1 to pos2 counterclockwise)
        backward_distance = self.space_size - forward_distance
        
        # Minimum distance
        min_distance = min(forward_distance, backward_distance)
        
        return {
            'forward': forward_distance,
            'backward': backward_distance,
            'minimum': min_distance,
            'clockwise_distance': forward_distance
        }
    
    def demonstrate_distance_calculations(self):
        """Show distance calculations on circular ring"""
        
        print("\nRing Distance Calculations:")
        print("-" * 30)
        
        # Use smaller space for clearer examples
        small_space = CircularMappingMath(100)
        
        test_pairs = [
            (10, 30),   # Simple forward
            (80, 20),   # Wraparound
            (50, 50),   # Same position
            (25, 75),   # Exactly opposite
        ]
        
        for pos1, pos2 in test_pairs:
            distances = small_space.calculate_ring_distance(pos1, pos2)
            print(f"Distance from {pos1} to {pos2}:")
            print(f"  Clockwise: {distances['clockwise_distance']}")
            print(f"  Counterclockwise: {distances['backward']}")
            print(f"  Minimum: {distances['minimum']}")
            print()

# Demonstrate circular mapping
circular_demo = CircularMappingMath(2**32)  # Use 32-bit for clearer examples
circular_demo.demonstrate_wraparound()
circular_demo.demonstrate_distance_calculations()
```

### Geometric Properties

The ring can be visualized geometrically, which helps understand its mathematical properties:

```python
import math

class RingGeometry:
    def __init__(self, hash_space_size):
        self.space_size = hash_space_size
        # Map hash space to circle with circumference = space_size
        self.circumference = hash_space_size
        self.radius = hash_space_size / (2 * math.pi)
    
    def hash_to_angle(self, hash_value):
        """Convert hash value to angle on circle (0 to 2π)"""
        return (hash_value / self.space_size) * 2 * math.pi
    
    def angle_to_cartesian(self, angle):
        """Convert angle to Cartesian coordinates"""
        x = self.radius * math.cos(angle)
        y = self.radius * math.sin(angle)
        return (x, y)
    
    def hash_to_cartesian(self, hash_value):
        """Convert hash value directly to Cartesian coordinates"""
        angle = self.hash_to_angle(hash_value)
        return self.angle_to_cartesian(angle)
    
    def demonstrate_geometric_properties(self):
        """Show geometric interpretation of hash ring"""
        
        print("Geometric Properties of Hash Ring:")
        print("=" * 40)
        
        print(f"Hash space size: {self.space_size:,}")
        print(f"Equivalent circle circumference: {self.circumference:,}")
        print(f"Equivalent circle radius: {self.radius:.2e}")
        
        # Show some positions
        print(f"\nSample positions on geometric ring:")
        sample_hashes = [
            0,
            self.space_size // 4,
            self.space_size // 2,
            3 * self.space_size // 4,
            self.space_size - 1
        ]
        
        for hash_val in sample_hashes:
            angle = self.hash_to_angle(hash_val)
            x, y = self.hash_to_cartesian(hash_val)
            percentage = (hash_val / self.space_size) * 100
            
            print(f"Hash {hash_val:>15,} ({percentage:5.1f}%):")
            print(f"  Angle: {angle:.3f} radians ({math.degrees(angle):6.1f}°)")
            print(f"  Cartesian: ({x:.2e}, {y:.2e})")
    
    def calculate_arc_length(self, start_hash, end_hash):
        """Calculate arc length between two hash positions"""
        
        # Ensure we go clockwise from start to end
        if end_hash >= start_hash:
            arc_distance = end_hash - start_hash
        else:
            # Wraparound case
            arc_distance = (self.space_size - start_hash) + end_hash
        
        # Convert to geometric arc length
        arc_proportion = arc_distance / self.space_size
        arc_length = arc_proportion * self.circumference
        
        return {
            'hash_distance': arc_distance,
            'arc_proportion': arc_proportion,
            'arc_length': arc_length
        }

# Demonstrate geometric properties
geometry_demo = RingGeometry(2**32)
geometry_demo.demonstrate_geometric_properties()
```

## Uniform Distribution Theory

The effectiveness of consistent hashing depends critically on the uniform distribution properties of the hash function used. This mathematical foundation ensures load balancing and predictable performance.

### Hash Function Requirements

```python
import random
import statistics
from collections import defaultdict

class UniformDistributionAnalysis:
    def __init__(self, hash_space_size):
        self.space_size = hash_space_size
    
    def theoretical_uniform_properties(self):
        """Analyze theoretical properties of uniform distribution"""
        
        print("Theoretical Uniform Distribution Properties:")
        print("=" * 50)
        
        # For n nodes uniformly distributed on ring
        node_counts = [10, 100, 1000, 10000]
        
        for n in node_counts:
            expected_space_per_node = self.space_size / n
            expected_load_per_node = 1.0 / n  # Fraction of total load
            
            # Standard deviation for uniform distribution
            variance = (self.space_size ** 2) / (12 * n)  # Uniform distribution variance
            std_dev = math.sqrt(variance)
            coefficient_of_variation = std_dev / expected_space_per_node
            
            print(f"\n{n} nodes uniformly distributed:")
            print(f"  Expected space per node: {expected_space_per_node:,.0f}")
            print(f"  Expected load per node: {expected_load_per_node:.3f} ({expected_load_per_node*100:.1f}%)")
            print(f"  Standard deviation: {std_dev:,.0f}")
            print(f"  Coefficient of variation: {coefficient_of_variation:.3f}")
            
            # Load balance quality assessment
            if coefficient_of_variation < 0.1:
                balance_quality = "Excellent"
            elif coefficient_of_variation < 0.2:
                balance_quality = "Good"
            elif coefficient_of_variation < 0.5:
                balance_quality = "Acceptable"
            else:
                balance_quality = "Poor"
            
            print(f"  Load balance quality: {balance_quality}")
    
    def simulate_hash_distribution(self, num_keys, num_nodes, hash_function_name='simple'):
        """Simulate hash function distribution quality"""
        
        # Simple hash function for testing
        def simple_hash(key):
            return hash(str(key)) % self.space_size
        
        # Better hash function simulation
        def good_hash(key):
            import hashlib
            hash_obj = hashlib.md5(str(key).encode())
            return int(hash_obj.hexdigest(), 16) % self.space_size
        
        hash_func = good_hash if hash_function_name == 'good' else simple_hash
        
        # Generate random keys and hash them
        keys = [f"key_{i}" for i in range(num_keys)]
        hash_values = [hash_func(key) for key in keys]
        
        # Create node positions (uniformly distributed)
        node_positions = []
        for i in range(num_nodes):
            position = (i * self.space_size // num_nodes) % self.space_size
            node_positions.append(position)
        node_positions.sort()
        
        # Assign keys to nodes using consistent hashing rule
        key_assignments = defaultdict(int)
        for hash_val in hash_values:
            # Find first node >= hash_val (clockwise)
            assigned_node = None
            for i, node_pos in enumerate(node_positions):
                if node_pos >= hash_val:
                    assigned_node = i
                    break
            
            if assigned_node is None:
                assigned_node = 0  # Wrap around to first node
            
            key_assignments[assigned_node] += 1
        
        # Analyze distribution quality
        loads = list(key_assignments.values())
        expected_load = num_keys / num_nodes
        
        return {
            'loads': loads,
            'mean_load': statistics.mean(loads),
            'expected_load': expected_load,
            'std_dev': statistics.stdev(loads) if len(loads) > 1 else 0,
            'min_load': min(loads),
            'max_load': max(loads),
            'coefficient_of_variation': statistics.stdev(loads) / statistics.mean(loads) if len(loads) > 1 and statistics.mean(loads) > 0 else 0
        }
    
    def analyze_distribution_quality(self):
        """Analyze distribution quality for different scenarios"""
        
        print("\nEmpirical Distribution Quality Analysis:")
        print("=" * 45)
        
        scenarios = [
            (1000, 10, "Small system"),
            (10000, 100, "Medium system"),
            (100000, 1000, "Large system")
        ]
        
        for num_keys, num_nodes, description in scenarios:
            print(f"\n{description} ({num_keys:,} keys, {num_nodes} nodes):")
            
            # Test with good hash function
            result = self.simulate_hash_distribution(num_keys, num_nodes, 'good')
            
            load_imbalance = (result['max_load'] - result['min_load']) / result['expected_load']
            
            print(f"  Expected load per node: {result['expected_load']:.1f}")
            print(f"  Actual mean load: {result['mean_load']:.1f}")
            print(f"  Load range: {result['min_load']} - {result['max_load']}")
            print(f"  Standard deviation: {result['std_dev']:.2f}")
            print(f"  Coefficient of variation: {result['coefficient_of_variation']:.3f}")
            print(f"  Load imbalance: {load_imbalance:.1%}")
            
            # Quality assessment
            if result['coefficient_of_variation'] < 0.1:
                quality = "Excellent"
            elif result['coefficient_of_variation'] < 0.2:
                quality = "Good" 
            elif result['coefficient_of_variation'] < 0.3:
                quality = "Acceptable"
            else:
                quality = "Poor"
            
            print(f"  Distribution quality: {quality}")

# Demonstrate uniform distribution analysis
uniform_demo = UniformDistributionAnalysis(2**32)
uniform_demo.theoretical_uniform_properties()
uniform_demo.analyze_distribution_quality()
```

### Statistical Properties

Understanding the statistical properties helps in predicting system behavior:

```python
class StatisticalProperties:
    def __init__(self):
        self.space_size = 2**32  # 32-bit space for clearer numbers
    
    def birthday_paradox_analysis(self):
        """Analyze birthday paradox implications for hash collisions"""
        
        print("Birthday Paradox Analysis for Hash Collisions:")
        print("=" * 50)
        
        # Calculate collision probability for different numbers of items
        def collision_probability(n, space_size):
            if n >= space_size:
                return 1.0
            
            # Exact calculation for small n
            if n <= 100:
                prob_no_collision = 1.0
                for i in range(n):
                    prob_no_collision *= (space_size - i) / space_size
                return 1.0 - prob_no_collision
            
            # Approximation for large n
            exponent = -(n * (n - 1)) / (2 * space_size)
            return 1.0 - math.exp(exponent)
        
        print(f"Hash space size: 2^32 = {self.space_size:,}")
        print(f"Birthday bound (50% collision): ~{math.sqrt(self.space_size):,.0f} items")
        
        test_sizes = [1000, 10000, 50000, 65536, 100000, 200000]
        
        for n in test_sizes:
            prob = collision_probability(n, self.space_size)
            print(f"{n:>6,} items: {prob:.6f} collision probability ({prob*100:.4f}%)")
    
    def load_distribution_mathematics(self):
        """Mathematical analysis of load distribution"""
        
        print("\nLoad Distribution Mathematics:")
        print("=" * 35)
        
        # For n nodes on ring, analyze expected load distribution
        node_counts = [10, 100, 1000]
        
        for n in node_counts:
            print(f"\n{n} nodes analysis:")
            
            # Expected load per node
            expected_load = 1.0 / n
            print(f"  Expected load per node: {expected_load:.4f} ({expected_load*100:.2f}%)")
            
            # Variance in load (theoretical)
            # For uniform distribution on circle, variance scales as 1/n
            load_variance = 1.0 / (n * n)  # Simplified model
            load_std_dev = math.sqrt(load_variance)
            
            print(f"  Theoretical load variance: {load_variance:.6f}")
            print(f"  Theoretical load std dev: {load_std_dev:.4f}")
            
            # Coefficient of variation
            cv = load_std_dev / expected_load if expected_load > 0 else 0
            print(f"  Coefficient of variation: {cv:.4f}")
            
            # Expected maximum and minimum loads
            # Using order statistics approximation
            expected_max_factor = 1 + math.sqrt(2 * math.log(n) / n)
            expected_min_factor = 1 - math.sqrt(2 * math.log(n) / n)
            
            expected_max_load = expected_load * expected_max_factor
            expected_min_load = expected_load * expected_min_factor
            
            print(f"  Expected max load: {expected_max_load:.4f} ({expected_max_factor:.2f}x average)")
            print(f"  Expected min load: {expected_min_load:.4f} ({expected_min_factor:.2f}x average)")
            
            # Imbalance ratio
            imbalance_ratio = expected_max_load / expected_min_load if expected_min_load > 0 else float('inf')
            print(f"  Load imbalance ratio: {imbalance_ratio:.2f}:1")

# Demonstrate statistical properties
stats_demo = StatisticalProperties()
stats_demo.birthday_paradox_analysis()
stats_demo.load_distribution_mathematics()
```

## Hash Function Comparative Analysis

Different hash functions have different mathematical properties that affect consistent hashing performance:

```python
class HashFunctionComparison:
    def __init__(self):
        self.test_data_size = 10000
    
    def compare_hash_functions(self):
        """Compare different hash functions for consistent hashing"""
        
        print("Hash Function Comparison for Consistent Hashing:")
        print("=" * 55)
        
        # Test different hash functions
        import hashlib
        import time
        
        hash_functions = {
            'SHA-1': lambda x: hashlib.sha1(x.encode()).hexdigest(),
            'SHA-256': lambda x: hashlib.sha256(x.encode()).hexdigest(),
            'MD5': lambda x: hashlib.md5(x.encode()).hexdigest(),
            'SHA-512': lambda x: hashlib.sha512(x.encode()).hexdigest(),
        }
        
        test_keys = [f"test_key_{i}" for i in range(self.test_data_size)]
        
        for name, hash_func in hash_functions.items():
            print(f"\n{name} Analysis:")
            
            # Performance timing
            start_time = time.time()
            hash_values = []
            for key in test_keys:
                hash_str = hash_func(key)
                hash_int = int(hash_str, 16) % (2**32)  # Normalize to 32-bit
                hash_values.append(hash_int)
            end_time = time.time()
            
            # Performance metrics
            hashes_per_second = len(test_keys) / (end_time - start_time)
            time_per_hash_us = (end_time - start_time) * 1000000 / len(test_keys)
            
            print(f"  Performance: {hashes_per_second:,.0f} hashes/sec")
            print(f"  Time per hash: {time_per_hash_us:.2f} microseconds")
            
            # Distribution quality
            # Divide space into bins and check uniformity
            num_bins = 100
            bin_size = (2**32) // num_bins
            bin_counts = [0] * num_bins
            
            for hash_val in hash_values:
                bin_index = min(hash_val // bin_size, num_bins - 1)
                bin_counts[bin_index] += 1
            
            expected_per_bin = len(test_keys) / num_bins
            chi_squared = sum((count - expected_per_bin)**2 / expected_per_bin 
                            for count in bin_counts)
            
            print(f"  Distribution chi-squared: {chi_squared:.2f}")
            print(f"  Expected (uniform): ~{num_bins:.0f}")
            
            # Distribution quality assessment
            if chi_squared < num_bins * 1.1:
                quality = "Excellent"
            elif chi_squared < num_bins * 1.3:
                quality = "Good"
            elif chi_squared < num_bins * 1.5:
                quality = "Acceptable"
            else:
                quality = "Poor"
            
            print(f"  Distribution quality: {quality}")
            
            # Hash length and collision resistance
            hash_example = hash_func(test_keys[0])
            bit_length = len(hash_example) * 4  # Hex chars to bits
            collision_resistance = bit_length // 2  # Birthday bound
            
            print(f"  Hash length: {len(hash_example)} hex chars ({bit_length} bits)")
            print(f"  Collision resistance: ~2^{collision_resistance}")

# Demonstrate hash function comparison
hash_comparison = HashFunctionComparison()
hash_comparison.compare_hash_functions()
```

## Mathematical Guarantees

The mathematical foundation provides several important guarantees:

```python
class MathematicalGuarantees:
    def demonstrate_guarantees(self):
        """Demonstrate the mathematical guarantees of consistent hashing"""
        
        print("Mathematical Guarantees of Consistent Hashing:")
        print("=" * 50)
        
        print("1. MONOTONICITY GUARANTEE:")
        print("   Adding nodes never changes existing key-node mappings")
        print("   except for keys that should move to the new node.")
        print("   Mathematical basis: Clockwise assignment rule preserves")
        print("   all existing assignments when new nodes are inserted.")
        
        print("\n2. BALANCE GUARANTEE:")
        print("   With uniform hash function, load is distributed evenly.")
        print("   Expected load per node: 1/n ± O(sqrt(log n / n))")
        print("   Mathematical basis: Uniform distribution on circle")
        print("   with law of large numbers convergence.")
        
        print("\n3. SPREAD GUARANTEE:")
        print("   Small changes in ring view affect few key assignments.")
        print("   Bounded disagreement between nodes with similar views.")
        print("   Mathematical basis: Locality properties of circular")
        print("   ordering and bounded view differences.")
        
        print("\n4. LOAD GUARANTEE:")
        print("   No node receives significantly more than average load.")
        print("   With high probability: load ≤ (1+ε) × average")
        print("   Mathematical basis: Concentration inequalities")
        print("   for sums of random variables.")
        
        # Quantitative example
        print("\n5. QUANTITATIVE EXAMPLE:")
        n = 1000  # Number of nodes
        expected_keys_moved_percentage = 100 / n
        max_load_factor = 1 + math.sqrt(2 * math.log(n) / n)
        
        print(f"   For {n} nodes:")
        print(f"   • Adding 1 node moves ~{expected_keys_moved_percentage:.1f}% of keys")
        print(f"   • Maximum node load ≤ {max_load_factor:.3f} × average")
        print(f"   • Load balance coefficient of variation ≤ {1/math.sqrt(n):.3f}")

# Demonstrate mathematical guarantees
guarantees_demo = MathematicalGuarantees()
guarantees_demo.demonstrate_guarantees()
```

The mathematical foundation of consistent hashing provides the theoretical underpinnings that make it suitable for production distributed systems. The large hash spaces ensure collision resistance, the circular mapping provides elegant wraparound behavior, and uniform distribution guarantees predictable load balancing. These mathematical properties combine to create the strong theoretical guarantees that make consistent hashing a reliable building block for large-scale distributed systems.

Understanding these mathematical foundations enables system designers to:
- Choose appropriate hash functions for their performance and security requirements
- Predict system behavior under various load and scaling scenarios
- Optimize implementations based on theoretical performance bounds
- Debug distribution issues by understanding the underlying mathematical principles

The elegance of consistent hashing lies not just in its practical benefits, but in how simple mathematical concepts—circular geometry, uniform distribution, and modular arithmetic—combine to solve complex distributed systems challenges with provable guarantees.
