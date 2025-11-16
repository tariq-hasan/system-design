05-consistent-hashing-solution/03-key-properties.md

# Key Properties of Consistent Hashing

The theoretical guarantees provided by consistent hashing are formalized through four fundamental properties that distinguish it from other data distribution schemes. These properties—monotonicity, balance, spread, and load—provide the mathematical foundation for consistent hashing's practical benefits and help system designers understand when and how to apply it effectively. Each property addresses specific challenges in distributed systems and provides quantifiable guarantees about system behavior.

## Monotonicity: Stability Under Growth

Monotonicity is perhaps the most important property of consistent hashing, ensuring that adding new nodes to the system doesn't disrupt existing data assignments unnecessarily.

### Formal Definition

**Monotonicity Property**: When a new node is added to the hash ring, the only keys that change their node assignment are those that should be assigned to the new node according to the consistent hashing algorithm. All other key-node mappings remain unchanged.

Mathematically, for a hash ring with nodes N = {n₁, n₂, ..., nₖ} and keys K = {k₁, k₂, ..., kₘ}, if we add a new node nₖ₊₁ to create N' = N ∪ {nₖ₊₁}, then:

```
For any key kᵢ ∈ K:
  If assignment(kᵢ, N) ≠ assignment(kᵢ, N'), 
  then assignment(kᵢ, N') = nₖ₊₁
```

### Implementation and Demonstration

```python
class MonotonicityDemo:
    def __init__(self):
        self.ring = {}  # position -> node mapping
        self.sorted_positions = []
    
    def _hash_value(self, key):
        """Simple hash function for demonstration"""
        import hashlib
        if isinstance(key, str):
            key = key.encode('utf-8')
        return int(hashlib.md5(key).hexdigest(), 16) % (2**32)
    
    def add_node(self, node_id):
        """Add a node to the ring"""
        position = self._hash_value(node_id)
        self.ring[position] = node_id
        self.sorted_positions = sorted(self.ring.keys())
        return position
    
    def get_node_for_key(self, key):
        """Find responsible node for key using clockwise rule"""
        if not self.sorted_positions:
            return None
        
        key_position = self._hash_value(key)
        
        # Find first node position >= key position
        for node_position in self.sorted_positions:
            if node_position >= key_position:
                return self.ring[node_position]
        
        # Wrap around to first node
        return self.ring[self.sorted_positions[0]]
    
    def demonstrate_monotonicity(self):
        """Prove monotonicity property with concrete example"""
        
        print("Monotonicity Property Demonstration:")
        print("=" * 40)
        
        # Initial setup with 3 nodes
        initial_nodes = ['NodeA', 'NodeB', 'NodeC']
        for node in initial_nodes:
            self.add_node(node)
        
        # Test with sample keys
        test_keys = [f"key_{i}" for i in range(20)]
        
        # Record initial assignments
        initial_assignments = {}
        for key in test_keys:
            node = self.get_node_for_key(key)
            initial_assignments[key] = node
        
        print("Initial assignments (3 nodes):")
        assignment_counts = {}
        for key, node in initial_assignments.items():
            assignment_counts[node] = assignment_counts.get(node, 0) + 1
        
        for node in sorted(assignment_counts.keys()):
            keys_for_node = [k for k, n in initial_assignments.items() if n == node]
            print(f"  {node}: {assignment_counts[node]} keys {keys_for_node[:3]}{'...' if len(keys_for_node) > 3 else ''}")
        
        # Add new node
        new_node = 'NodeD'
        new_node_position = self.add_node(new_node)
        
        print(f"\nAdding {new_node} at position {new_node_position}")
        
        # Record new assignments
        new_assignments = {}
        moved_keys = []
        unchanged_keys = []
        
        for key in test_keys:
            new_node_assignment = self.get_node_for_key(key)
            new_assignments[key] = new_node_assignment
            
            if initial_assignments[key] != new_node_assignment:
                moved_keys.append({
                    'key': key,
                    'from': initial_assignments[key],
                    'to': new_node_assignment,
                    'key_position': self._hash_value(key)
                })
            else:
                unchanged_keys.append(key)
        
        print(f"\nResults after adding {new_node}:")
        print(f"  Keys unchanged: {len(unchanged_keys)} ({len(unchanged_keys)/len(test_keys)*100:.1f}%)")
        print(f"  Keys moved: {len(moved_keys)} ({len(moved_keys)/len(test_keys)*100:.1f}%)")
        
        # Verify monotonicity property
        monotonicity_violated = False
        for moved_key in moved_keys:
            if moved_key['to'] != new_node:
                monotonicity_violated = True
                print(f"  ❌ VIOLATION: {moved_key['key']} moved to {moved_key['to']} instead of {new_node}")
        
        if not monotonicity_violated:
            print(f"  ✅ MONOTONICITY PRESERVED: All moved keys assigned to {new_node}")
        
        # Show which keys moved
        if moved_keys:
            print(f"\nKeys that moved to {new_node}:")
            for moved in moved_keys:
                print(f"  {moved['key']}: {moved['from']} → {moved['to']} (pos: {moved['key_position']})")
        
        return len(moved_keys), len(unchanged_keys)

# Demonstrate monotonicity
mono_demo = MonotonicityDemo()
mono_demo.demonstrate_monotonicity()
```

### Quantitative Analysis

```python
class MonotonicityAnalysis:
    def analyze_monotonicity_across_scales(self):
        """Analyze monotonicity behavior across different system scales"""
        
        print("\nMonotonicity Analysis Across System Scales:")
        print("=" * 45)
        
        scales = [
            (5, 1000, "Small system"),
            (50, 10000, "Medium system"),
            (500, 100000, "Large system"),
            (5000, 1000000, "Massive system")
        ]
        
        for num_nodes, num_keys, description in scales:
            print(f"\n{description} ({num_nodes} nodes, {num_keys:,} keys):")
            
            # Simulate adding a node
            ring = MonotonicityDemo()
            
            # Add initial nodes
            for i in range(num_nodes):
                ring.add_node(f"node_{i}")
            
            # Generate and assign keys
            test_keys = [f"key_{i}" for i in range(num_keys)]
            initial_assignments = {}
            for key in test_keys:
                initial_assignments[key] = ring.get_node_for_key(key)
            
            # Add new node
            new_node = f"node_{num_nodes}"
            ring.add_node(new_node)
            
            # Analyze changes
            moved_count = 0
            violation_count = 0
            
            for key in test_keys:
                new_assignment = ring.get_node_for_key(key)
                if initial_assignments[key] != new_assignment:
                    moved_count += 1
                    if new_assignment != new_node:
                        violation_count += 1
            
            # Calculate metrics
            expected_moved = num_keys / (num_nodes + 1)  # Theoretical expectation
            actual_moved_percentage = (moved_count / num_keys) * 100
            expected_percentage = (expected_moved / num_keys) * 100
            
            print(f"  Expected keys moved: {expected_moved:.0f} ({expected_percentage:.2f}%)")
            print(f"  Actual keys moved: {moved_count} ({actual_moved_percentage:.2f}%)")
            print(f"  Monotonicity violations: {violation_count}")
            print(f"  Monotonicity preserved: {'✅ YES' if violation_count == 0 else '❌ NO'}")
            
            # Efficiency assessment
            efficiency = abs(actual_moved_percentage - expected_percentage) / expected_percentage
            if efficiency < 0.1:
                assessment = "Excellent"
            elif efficiency < 0.25:
                assessment = "Good"
            elif efficiency < 0.5:
                assessment = "Acceptable"
            else:
                assessment = "Poor"
            
            print(f"  Movement efficiency: {assessment} ({efficiency:.1%} deviation)")

# Run monotonicity analysis
mono_analysis = MonotonicityAnalysis()
mono_analysis.analyze_monotonicity_across_scales()
```

## Balance: Even Load Distribution

The balance property ensures that consistent hashing distributes keys roughly evenly across all nodes, preventing hot spots and ensuring efficient resource utilization.

### Theoretical Foundation

**Balance Property**: In a system with n nodes and uniform hash function, each node should receive approximately 1/n of the total keys, with the deviation decreasing as the system size increases.

For large systems, the load balance can be quantified as:
```
Load per node = (1/n) ± O(√(log n / n))
```

### Implementation and Analysis

```python
import statistics
import math
from collections import defaultdict

class BalanceDemo:
    def __init__(self, use_virtual_nodes=False, virtual_nodes_per_physical=100):
        self.ring = {}
        self.sorted_positions = []
        self.use_virtual_nodes = use_virtual_nodes
        self.virtual_nodes_per_physical = virtual_nodes_per_physical
        self.physical_to_virtual = defaultdict(list)  # Track virtual nodes per physical node
    
    def _hash_value(self, key):
        """Hash function for ring positions"""
        import hashlib
        if isinstance(key, str):
            key = key.encode('utf-8')
        return int(hashlib.md5(key).hexdigest(), 16) % (2**32)
    
    def add_node(self, physical_node_id):
        """Add a node (with virtual nodes if enabled)"""
        if self.use_virtual_nodes:
            # Add multiple virtual nodes for this physical node
            for i in range(self.virtual_nodes_per_physical):
                virtual_id = f"{physical_node_id}:vnode_{i}"
                position = self._hash_value(virtual_id)
                self.ring[position] = physical_node_id
                self.physical_to_virtual[physical_node_id].append(position)
        else:
            # Add single node
            position = self._hash_value(physical_node_id)
            self.ring[position] = physical_node_id
        
        self.sorted_positions = sorted(self.ring.keys())
    
    def get_node_for_key(self, key):
        """Find responsible node for key"""
        if not self.sorted_positions:
            return None
        
        key_position = self._hash_value(key)
        
        # Find first node position >= key position
        for node_position in self.sorted_positions:
            if node_position >= key_position:
                return self.ring[node_position]
        
        # Wrap around
        return self.ring[self.sorted_positions[0]]
    
    def analyze_balance(self, num_keys):
        """Analyze load balance across nodes"""
        
        # Generate test keys
        test_keys = [f"key_{i}" for i in range(num_keys)]
        
        # Count assignments per node
        load_distribution = defaultdict(int)
        for key in test_keys:
            node = self.get_node_for_key(key)
            if node:
                load_distribution[node] += 1
        
        # Calculate statistics
        loads = list(load_distribution.values())
        if not loads:
            return None
        
        num_nodes = len(loads)
        expected_load = num_keys / num_nodes
        
        stats = {
            'num_nodes': num_nodes,
            'num_keys': num_keys,
            'expected_load': expected_load,
            'actual_loads': loads,
            'mean_load': statistics.mean(loads),
            'std_dev': statistics.stdev(loads) if len(loads) > 1 else 0,
            'min_load': min(loads),
            'max_load': max(loads),
            'coefficient_of_variation': statistics.stdev(loads) / statistics.mean(loads) if len(loads) > 1 and statistics.mean(loads) > 0 else 0
        }
        
        # Additional balance metrics
        stats['load_imbalance_ratio'] = stats['max_load'] / stats['min_load'] if stats['min_load'] > 0 else float('inf')
        stats['relative_std_dev'] = stats['std_dev'] / expected_load if expected_load > 0 else 0
        
        return stats
    
    def demonstrate_balance_improvement(self):
        """Show how virtual nodes improve balance"""
        
        print("Balance Property Demonstration:")
        print("=" * 35)
        
        num_nodes = 10
        num_keys = 10000
        
        # Test without virtual nodes
        print("WITHOUT Virtual Nodes:")
        ring_no_vnodes = BalanceDemo(use_virtual_nodes=False)
        for i in range(num_nodes):
            ring_no_vnodes.add_node(f"node_{i}")
        
        stats_no_vnodes = ring_no_vnodes.analyze_balance(num_keys)
        
        print(f"  Expected load per node: {stats_no_vnodes['expected_load']:.1f}")
        print(f"  Load range: {stats_no_vnodes['min_load']} - {stats_no_vnodes['max_load']}")
        print(f"  Standard deviation: {stats_no_vnodes['std_dev']:.1f}")
        print(f"  Coefficient of variation: {stats_no_vnodes['coefficient_of_variation']:.3f}")
        print(f"  Load imbalance ratio: {stats_no_vnodes['load_imbalance_ratio']:.2f}:1")
        
        # Test with virtual nodes
        print("\nWITH Virtual Nodes (100 per physical node):")
        ring_with_vnodes = BalanceDemo(use_virtual_nodes=True, virtual_nodes_per_physical=100)
        for i in range(num_nodes):
            ring_with_vnodes.add_node(f"node_{i}")
        
        stats_with_vnodes = ring_with_vnodes.analyze_balance(num_keys)
        
        print(f"  Expected load per node: {stats_with_vnodes['expected_load']:.1f}")
        print(f"  Load range: {stats_with_vnodes['min_load']} - {stats_with_vnodes['max_load']}")
        print(f"  Standard deviation: {stats_with_vnodes['std_dev']:.1f}")
        print(f"  Coefficient of variation: {stats_with_vnodes['coefficient_of_variation']:.3f}")
        print(f"  Load imbalance ratio: {stats_with_vnodes['load_imbalance_ratio']:.2f}:1")
        
        # Calculate improvement
        cv_improvement = stats_no_vnodes['coefficient_of_variation'] / stats_with_vnodes['coefficient_of_variation']
        imbalance_improvement = stats_no_vnodes['load_imbalance_ratio'] / stats_with_vnodes['load_imbalance_ratio']
        
        print(f"\nImprovement with virtual nodes:")
        print(f"  Coefficient of variation: {cv_improvement:.1f}x better")
        print(f"  Load imbalance ratio: {imbalance_improvement:.1f}x better")
        
        return stats_no_vnodes, stats_with_vnodes

# Demonstrate balance improvements
balance_demo = BalanceDemo()
balance_demo.demonstrate_balance_improvement()
```

### Balance Across Different Scales

```python
class BalanceScaling:
    def analyze_balance_scaling(self):
        """Analyze how balance improves with system scale"""
        
        print("\nBalance Scaling Analysis:")
        print("=" * 30)
        
        scenarios = [
            (5, 1000, 50),      # Small: 5 nodes, 1k keys, 50 vnodes
            (20, 10000, 100),   # Medium: 20 nodes, 10k keys, 100 vnodes  
            (100, 100000, 150), # Large: 100 nodes, 100k keys, 150 vnodes
            (500, 1000000, 200) # Massive: 500 nodes, 1M keys, 200 vnodes
        ]
        
        for num_nodes, num_keys, vnodes_per_node in scenarios:
            print(f"\nScale: {num_nodes} nodes, {num_keys:,} keys, {vnodes_per_node} virtual nodes each")
            
            # Test with virtual nodes
            ring = BalanceDemo(use_virtual_nodes=True, virtual_nodes_per_physical=vnodes_per_node)
            for i in range(num_nodes):
                ring.add_node(f"node_{i}")
            
            stats = ring.analyze_balance(num_keys)
            
            # Theoretical predictions
            theoretical_cv = 1 / math.sqrt(num_nodes * vnodes_per_node)
            theoretical_max_load_factor = 1 + math.sqrt(2 * math.log(num_nodes) / num_nodes)
            
            print(f"  Actual coefficient of variation: {stats['coefficient_of_variation']:.4f}")
            print(f"  Theoretical CV prediction: {theoretical_cv:.4f}")
            print(f"  Actual max load factor: {stats['max_load']/stats['expected_load']:.3f}")
            print(f"  Theoretical max load factor: {theoretical_max_load_factor:.3f}")
            
            # Quality assessment
            if stats['coefficient_of_variation'] < 0.05:
                quality = "Excellent"
            elif stats['coefficient_of_variation'] < 0.1:
                quality = "Good"
            elif stats['coefficient_of_variation'] < 0.2:
                quality = "Acceptable"
            else:
                quality = "Poor"
            
            print(f"  Balance quality: {quality}")

# Run balance scaling analysis
balance_scaling = BalanceScaling()
balance_scaling.analyze_balance_scaling()
```

## Spread: Limited Disagreement

The spread property ensures that when different nodes have slightly different views of the ring topology, the number of keys for which they disagree is bounded and small.

### Formal Definition

**Spread Property**: If two nodes have ring views that differ by at most a small number of nodes, then they will disagree on the assignment of at most a small number of keys.

Formally, if views V₁ and V₂ differ by k nodes, then the number of keys assigned differently is O(k).

### Implementation and Demonstration

```python
class SpreadDemo:
    def __init__(self):
        self.ring = {}
        self.sorted_positions = []
    
    def _hash_value(self, key):
        import hashlib
        if isinstance(key, str):
            key = key.encode('utf-8')
        return int(hashlib.md5(key).hexdigest(), 16) % (2**32)
    
    def create_ring_view(self, nodes):
        """Create a ring view with specified nodes"""
        ring = {}
        for node in nodes:
            position = self._hash_value(node)
            ring[position] = node
        return ring, sorted(ring.keys())
    
    def get_node_for_key_in_view(self, key, ring, sorted_positions):
        """Get node assignment in specific ring view"""
        if not sorted_positions:
            return None
        
        key_position = self._hash_value(key)
        
        for node_position in sorted_positions:
            if node_position >= key_position:
                return ring[node_position]
        
        return ring[sorted_positions[0]]
    
    def compare_ring_views(self, view1_nodes, view2_nodes, test_keys):
        """Compare key assignments between two ring views"""
        
        # Create both ring views
        ring1, positions1 = self.create_ring_view(view1_nodes)
        ring2, positions2 = self.create_ring_view(view2_nodes)
        
        # Compare assignments
        agreements = 0
        disagreements = []
        
        for key in test_keys:
            assignment1 = self.get_node_for_key_in_view(key, ring1, positions1)
            assignment2 = self.get_node_for_key_in_view(key, ring2, positions2)
            
            if assignment1 == assignment2:
                agreements += 1
            else:
                disagreements.append({
                    'key': key,
                    'view1_assignment': assignment1,
                    'view2_assignment': assignment2,
                    'key_position': self._hash_value(key)
                })
        
        return agreements, disagreements
    
    def demonstrate_spread_property(self):
        """Demonstrate spread property with different view differences"""
        
        print("Spread Property Demonstration:")
        print("=" * 35)
        
        # Base set of nodes
        base_nodes = [f"node_{i}" for i in range(10)]
        test_keys = [f"key_{i}" for i in range(1000)]
        
        # Test different levels of view disagreement
        disagreement_scenarios = [
            (base_nodes, base_nodes[:-1], "1 node difference"),
            (base_nodes, base_nodes[:-2], "2 nodes difference"),
            (base_nodes, base_nodes[:-3], "3 nodes difference"),
            (base_nodes, base_nodes[:-5], "5 nodes difference"),
        ]
        
        for view1_nodes, view2_nodes, description in disagreement_scenarios:
            agreements, disagreements = self.compare_ring_views(view1_nodes, view2_nodes, test_keys)
            
            num_different_nodes = len(set(view1_nodes) ^ set(view2_nodes))
            disagreement_percentage = len(disagreements) / len(test_keys) * 100
            
            print(f"\n{description}:")
            print(f"  View 1: {len(view1_nodes)} nodes")
            print(f"  View 2: {len(view2_nodes)} nodes")
            print(f"  Different nodes: {num_different_nodes}")
            print(f"  Key agreements: {agreements}")
            print(f"  Key disagreements: {len(disagreements)} ({disagreement_percentage:.1f}%)")
            
            # Theoretical bound: disagreements should be proportional to different nodes
            theoretical_bound = num_different_nodes / len(view1_nodes) * 100
            print(f"  Theoretical bound: ~{theoretical_bound:.1f}%")
            
            # Check if spread property holds
            if disagreement_percentage <= theoretical_bound * 2:  # Allow 2x tolerance
                spread_quality = "✅ Good"
            else:
                spread_quality = "❌ Poor"
            
            print(f"  Spread property: {spread_quality}")
            
            # Show sample disagreements
            if disagreements and len(disagreements) <= 5:
                print(f"  Sample disagreements:")
                for d in disagreements[:3]:
                    print(f"    {d['key']}: {d['view1_assignment']} vs {d['view2_assignment']}")

# Demonstrate spread property
spread_demo = SpreadDemo()
spread_demo.demonstrate_spread_property()
```

### Network Partition Scenarios

```python
class NetworkPartitionSpread:
    def simulate_network_partition_spread(self):
        """Simulate spread behavior during network partitions"""
        
        print("\nNetwork Partition Spread Analysis:")
        print("=" * 40)
        
        # Simulate cluster with network partitions
        all_nodes = [f"node_{i}" for i in range(20)]
        test_keys = [f"key_{i}" for i in range(2000)]
        
        # Different partition scenarios
        partition_scenarios = [
            (all_nodes[:15], all_nodes[5:], "Overlapping partitions"),
            (all_nodes[:10], all_nodes[10:], "Clean split"),
            (all_nodes[:18], all_nodes, "Minor partition (2 nodes unreachable)"),
            (all_nodes[:12], all_nodes[8:], "Majority overlap")
        ]
        
        spread_demo = SpreadDemo()
        
        for partition1, partition2, description in partition_scenarios:
            print(f"\n{description}:")
            print(f"  Partition 1: {len(partition1)} nodes")
            print(f"  Partition 2: {len(partition2)} nodes")
            
            agreements, disagreements = spread_demo.compare_ring_views(
                partition1, partition2, test_keys
            )
            
            # Calculate overlap and difference
            overlap = len(set(partition1) & set(partition2))
            total_different = len(set(partition1) ^ set(partition2))
            
            disagreement_rate = len(disagreements) / len(test_keys) * 100
            
            print(f"  Overlapping nodes: {overlap}")
            print(f"  Different nodes: {total_different}")
            print(f"  Key disagreement rate: {disagreement_rate:.1f}%")
            
            # Impact assessment
            if disagreement_rate < 5:
                impact = "Low impact"
            elif disagreement_rate < 15:
                impact = "Moderate impact"
            elif disagreement_rate < 30:
                impact = "High impact"
            else:
                impact = "Severe impact"
            
            print(f"  Impact assessment: {impact}")
            
            # Spread efficiency
            efficiency = total_different / len(all_nodes)
            spread_efficiency = disagreement_rate / (efficiency * 100)
            
            print(f"  Spread efficiency: {spread_efficiency:.2f} (lower is better)")

# Simulate network partition scenarios
partition_spread = NetworkPartitionSpread()
partition_spread.simulate_network_partition_spread()
```

## Load: Bounded Maximum Load

The load property guarantees that no individual node receives significantly more than its fair share of keys, preventing hot spots and ensuring system stability.

### Theoretical Bounds

**Load Property**: With high probability, no node receives more than (1 + ε) times the average load, where ε decreases with system size and the number of virtual nodes.

For n nodes with v virtual nodes each:
```
Maximum load ≤ (1 + O(√(log n / (nv)))) × average load
```

### Implementation and Validation

```python
class LoadDemo:
    def __init__(self, virtual_nodes_per_physical=100):
        self.virtual_nodes_per_physical = virtual_nodes_per_physical
    
    def analyze_load_bounds(self, num_physical_nodes, num_keys):
        """Analyze load bounds for different configurations"""
        
        # Create ring with virtual nodes
        ring = BalanceDemo(use_virtual_nodes=True, 
                         virtual_nodes_per_physical=self.virtual_nodes_per_physical)
        
        for i in range(num_physical_nodes):
            ring.add_node(f"node_{i}")
        
        # Analyze load distribution
        stats = ring.analyze_balance(num_keys)
        
        # Calculate theoretical bounds
        total_virtual_nodes = num_physical_nodes * self.virtual_nodes_per_physical
        theoretical_max_load_factor = 1 + math.sqrt(2 * math.log(num_physical_nodes) / total_virtual_nodes)
        
        # Calculate actual bounds
        actual_max_load_factor = stats['max_load'] / stats['expected_load']
        
        return {
            'num_physical_nodes': num_physical_nodes,
            'num_virtual_nodes': total_virtual_nodes,
            'num_keys': num_keys,
            'expected_load': stats['expected_load'],
            'actual_max_load': stats['max_load'],
            'actual_max_load_factor': actual_max_load_factor,
            'theoretical_max_load_factor': theoretical_max_load_factor,
            'load_bound_satisfied': actual_max_load_factor <= theoretical_max_load_factor * 1.1,  # 10% tolerance
            'coefficient_of_variation': stats['coefficient_of_variation']
        }
    
    def demonstrate_load_bounds(self):
        """Demonstrate load bounds across different system configurations"""
        
        print("Load Property Demonstration:")
        print("=" * 30)
        
        configurations = [
            (10, 10000, 50),     # Small system
            (50, 100000, 100),   # Medium system
            (200, 1000000, 150), # Large system
            (1000, 10000000, 200) # Massive system
        ]
        
        for num_nodes, num_keys, vnodes_per_node in configurations:
            self.virtual_nodes_per_physical = vnodes_per_node
            results = self.analyze_load_bounds(num_nodes, num_keys)
            
            print(f"\nConfiguration: {num_nodes} nodes, {num_keys:,} keys, {vnodes_per_node} vnodes/node")
            print(f"  Expected load per node: {results['expected_load']:.1f}")
            print(f"  Actual maximum load: {results['actual_max_load']}")
            print(f"  Actual max load factor: {results['actual_max_load_factor']:.3f}")
            print(f"  Theoretical bound: {results['theoretical_max_load_factor']:.3f}")
            print(f"  Bound satisfied: {'✅ YES' if results['load_bound_satisfied'] else '❌ NO'}")
            print(f"  Coefficient of variation: {results['coefficient_of_variation']:.4f}")
            
            # Performance assessment
            if results['actual_max_load_factor'] < 1.1:
                performance = "Excellent"
            elif results['actual_max_load_factor'] < 1.25:
                performance = "Good"
            elif results['actual_max_load_factor'] < 1.5:
                performance = "Acceptable"
            else:
                performance = "Poor"
            
            print(f"  Load balance performance: {performance}")

# Demonstrate load bounds
load_demo = LoadDemo()
load_demo.demonstrate_load_bounds()
```

### Hot Spot Prevention

```python
class HotSpotPrevention:
    def demonstrate_hot_spot_resistance(self):
        """Show how consistent hashing prevents hot spots"""
        
        print("\nHot Spot Prevention Analysis:")
        print("=" * 35)
        
        # Compare with naive approaches
        print("Comparison: Consistent Hashing vs Naive Round-Robin")
        
        num_nodes = 10
        num_keys = 10000
        
        # Consistent hashing distribution
        ring = BalanceDemo(use_virtual_nodes=True, virtual_nodes_per_physical=100)
        for i in range(num_nodes):
            ring.add_node(f"node_{i}")
        
        ch_stats = ring.analyze_balance(num_keys)
        
        # Naive round-robin distribution
        rr_loads = [num_keys // num_nodes] * num_nodes
        remainder = num_keys % num_nodes
        for i in range(remainder):
            rr_loads[i] += 1
        
        print(f"\nConsistent Hashing:")
        print(f"  Load range: {ch_stats['min_load']} - {ch_stats['max_load']}")
        print(f"  Standard deviation: {ch_stats['std_dev']:.1f}")
        print(f"  Max load factor: {ch_stats['max_load']/ch_stats['expected_load']:.3f}")
        
        print(f"\nRound-Robin:")
        rr_min, rr_max = min(rr_loads), max(rr_loads)
        rr_std = statistics.stdev(rr_loads)
        rr_mean = statistics.mean(rr_loads)
        print(f"  Load range: {rr_min} - {rr_max}")
        print(f"  Standard deviation: {rr_std:.1f}")
        print(f"  Max load factor: {rr_max/rr_mean:.3f}")
        
        # Node failure simulation
        print(f"\nSimulating node failure impact:")
        
        # Remove one node and redistribute
        failed_node_load = ch_stats['actual_loads'][0]  # Assume first node fails
        remaining_nodes = num_nodes - 1
        
        # Consistent hashing: load redistributes to successor
        ch_successor_additional_load = failed_node_load
        ch_max_after_failure = max(ch_stats['actual_loads'][1:]) + ch_successor_additional_load
        
        # Round-robin: load redistributes evenly
        rr_additional_per_node = failed_node_load / remaining_nodes
        rr_max_after_failure = rr_max + rr_additional_per_node
        
        print(f"  Consistent hashing max load after failure: {ch_max_after_failure:.0f}")
        print(f"  Round-robin max load after failure: {rr_max_after_failure:.0f}")
        
        # Hot spot resistance conclusion
        ch_hot_spot_factor = ch_max_after_failure / ch_stats['expected_load']
        rr_hot_spot_factor = rr_max_after_failure / rr_mean
        
        print(f"\nHot spot resistance:")
        print(f"  Consistent hashing factor: {ch_hot_spot_factor:.2f}x")
        print(f"  Round-robin factor: {rr_hot_spot_factor:.2f}x")
        
        if ch_hot_spot_factor < rr_hot_spot_factor:
            print(f"  Winner: Consistent hashing (better hot spot resistance)")
        else:
            print(f"  Winner: Round-robin (better hot spot resistance)")

# Demonstrate hot spot prevention
hot_spot_demo = HotSpotPrevention()
hot_spot_demo.demonstrate_hot_spot_resistance()
```

## Property Interdependencies

```python
class PropertyInterdependencies:
    def demonstrate_property_relationships(self):
        """Show how the four properties work together"""
        
        print("\nProperty Interdependencies:")
        print("=" * 30)
        
        print("1. MONOTONICITY enables SPREAD:")
        print("   • Stable assignments reduce disagreement between views")
        print("   • Only keys near topology changes create disagreements")
        
        print("\n2. BALANCE improves LOAD:")
        print("   • Even distribution prevents individual node overload")
        print("   • Virtual nodes enhance balance, tightening load bounds")
        
        print("\n3. SPREAD supports BALANCE:")
        print("   • Limited disagreement maintains consistent load distribution")
        print("   • Prevents avalanche effects from view inconsistencies")
        
        print("\n4. LOAD guarantees operational stability:")
        print("   • Bounded maximum load prevents performance degradation")
        print("   • Enables predictable capacity planning")
        
        print("\nSynergistic effects:")
        print("   • All properties together provide strong guarantees")
        print("   • Individual properties would be insufficient alone")
        print("   • Mathematical foundation ensures properties hold at scale")

# Demonstrate property relationships
interdep_demo = PropertyInterdependencies()
interdep_demo.demonstrate_property_relationships()
```

## Summary

The four key properties of consistent hashing work together to provide strong theoretical guarantees:

1. **Monotonicity** ensures stability during topology changes
2. **Balance** provides even load distribution across nodes
3. **Spread** limits disagreement when views differ slightly
4. **Load** bounds maximum load to prevent hot spots

These properties make consistent hashing suitable for production distributed systems by providing predictable behavior, automatic load balancing, and graceful handling of failures and topology changes. Understanding these properties helps system designers make informed decisions about when and how to apply consistent hashing effectively.​​​​​​​​​​​​​​​​
