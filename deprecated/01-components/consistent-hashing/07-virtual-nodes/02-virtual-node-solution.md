# Virtual Node Solution

Virtual nodes represent a fundamental advancement in consistent hashing that transforms the algorithm from a basic partitioning scheme into a robust, production-ready distributed system primitive. By creating multiple virtual representations of each physical node on the hash ring, virtual nodes solve the core distribution problems of basic consistent hashing while introducing new capabilities for heterogeneous systems and fine-grained load balancing.

## Core Virtual Node Concept

The virtual node solution replaces the single position per physical node with multiple positions, dramatically improving the statistical properties of load distribution.

### Fundamental Architecture

```python
import hashlib
import bisect
import random
import statistics
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

class VirtualNodeConsistentHashing:
    """Complete virtual node implementation with comprehensive analysis"""
    
    def __init__(self, hash_function: str = 'sha1'):
        self.hash_function = hash_function
        self.ring = {}  # position -> physical_node_id mapping
        self.sorted_positions = []  # Sorted positions for efficient lookups
        self.physical_to_virtual = defaultdict(list)  # physical_node -> [virtual_positions]
        self.virtual_node_map = {}  # position -> (virtual_id, physical_node) mapping
        
        # Performance tracking
        self.lookup_count = 0
        self.total_lookup_time = 0.0
        
        self._setup_hash_function()
    
    def _setup_hash_function(self):
        """Configure hash function and space size"""
        if self.hash_function == 'sha1':
            self.hasher = hashlib.sha1
            self.space_size = 2**32  # Use 32-bit for manageable demo numbers
        elif self.hash_function == 'md5':
            self.hasher = hashlib.md5
            self.space_size = 2**32
        else:
            self.hasher = hashlib.sha1
            self.space_size = 2**32
    
    def _hash_value(self, data: str) -> int:
        """Compute hash value for data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_obj = self.hasher(data)
        return int(hash_obj.hexdigest(), 16) % self.space_size
    
    def add_physical_node(self, node_id: str, virtual_node_count: int = 150) -> Dict:
        """
        Add a physical node with specified number of virtual nodes
        
        Args:
            node_id: Unique identifier for physical node
            virtual_node_count: Number of virtual nodes to create
            
        Returns:
            Dictionary with placement statistics
        """
        if node_id in self.physical_to_virtual:
            raise ValueError(f"Physical node {node_id} already exists")
        
        virtual_positions = []
        collision_count = 0
        
        print(f"Adding physical node: {node_id}")
        print(f"Creating {virtual_node_count} virtual nodes...")
        
        for i in range(virtual_node_count):
            # Create unique virtual node identifier
            virtual_id = f"{node_id}:vnode_{i}"
            position = self._hash_value(virtual_id)
            
            # Handle position collisions
            original_position = position
            attempts = 0
            while position in self.ring and attempts < 1000:
                collision_count += 1
                attempts += 1
                collision_virtual_id = f"{virtual_id}_collision_{attempts}"
                position = self._hash_value(collision_virtual_id)
            
            if attempts >= 1000:
                raise RuntimeError(f"Cannot resolve collision for {virtual_id}")
            
            # Place virtual node
            self.ring[position] = node_id
            virtual_positions.append(position)
            self.virtual_node_map[position] = (virtual_id, node_id)
        
        # Update tracking structures
        self.physical_to_virtual[node_id] = virtual_positions
        self.sorted_positions = sorted(self.ring.keys())
        
        # Calculate placement statistics
        placement_stats = self._analyze_virtual_node_placement(node_id, virtual_positions)
        
        print(f"✅ Placement complete:")
        print(f"  Virtual nodes placed: {len(virtual_positions)}")
        print(f"  Collisions resolved: {collision_count}")
        print(f"  Average gap: {placement_stats['avg_gap']:,}")
        print(f"  Distribution quality: {placement_stats['quality']}")
        
        return {
            'node_id': node_id,
            'virtual_nodes_created': len(virtual_positions),
            'collisions_resolved': collision_count,
            'placement_stats': placement_stats,
            'total_ring_size': len(self.ring)
        }
    
    def _analyze_virtual_node_placement(self, node_id: str, positions: List[int]) -> Dict:
        """Analyze the quality of virtual node placement"""
        
        if len(positions) < 2:
            return {'avg_gap': 0, 'quality': 'Insufficient data'}
        
        # Calculate gaps between consecutive virtual nodes for this physical node
        sorted_positions = sorted(positions)
        gaps = []
        
        for i in range(len(sorted_positions)):
            current = sorted_positions[i]
            next_pos = sorted_positions[(i + 1) % len(sorted_positions)]
            
            if next_pos > current:
                gap = next_pos - current
            else:
                # Wrap around
                gap = (self.space_size - current) + next_pos
            
            gaps.append(gap)
        
        # Calculate gap statistics
        avg_gap = statistics.mean(gaps)
        min_gap = min(gaps)
        max_gap = max(gaps)
        gap_std = statistics.stdev(gaps) if len(gaps) > 1 else 0
        coefficient_of_variation = gap_std / avg_gap if avg_gap > 0 else 0
        
        # Quality assessment
        if coefficient_of_variation < 0.3:
            quality = "Excellent"
        elif coefficient_of_variation < 0.5:
            quality = "Good"
        elif coefficient_of_variation < 0.8:
            quality = "Acceptable"
        else:
            quality = "Poor"
        
        return {
            'avg_gap': avg_gap,
            'min_gap': min_gap,
            'max_gap': max_gap,
            'gap_std': gap_std,
            'cv': coefficient_of_variation,
            'quality': quality
        }
    
    def remove_physical_node(self, node_id: str) -> Dict:
        """Remove a physical node and all its virtual nodes"""
        
        if node_id not in self.physical_to_virtual:
            raise ValueError(f"Physical node {node_id} does not exist")
        
        virtual_positions = self.physical_to_virtual[node_id]
        
        print(f"Removing physical node: {node_id}")
        print(f"Removing {len(virtual_positions)} virtual nodes...")
        
        # Remove all virtual nodes
        for position in virtual_positions:
            if position in self.ring:
                del self.ring[position]
            if position in self.virtual_node_map:
                del self.virtual_node_map[position]
        
        # Update tracking structures
        del self.physical_to_virtual[node_id]
        self.sorted_positions = sorted(self.ring.keys())
        
        print(f"✅ Removal complete")
        
        return {
            'node_id': node_id,
            'virtual_nodes_removed': len(virtual_positions),
            'remaining_ring_size': len(self.ring)
        }
    
    def get_node_for_key(self, key: str) -> Optional[str]:
        """Find responsible physical node for a key"""
        
        if not self.sorted_positions:
            return None
        
        key_position = self._hash_value(key)
        
        # Binary search for first position >= key position
        index = bisect.bisect_left(self.sorted_positions, key_position)
        
        if index < len(self.sorted_positions):
            responsible_position = self.sorted_positions[index]
        else:
            # Wrap around to first position
            responsible_position = self.sorted_positions[0]
        
        return self.ring[responsible_position]
    
    def analyze_load_distribution(self, test_keys: List[str] = None) -> Dict:
        """Analyze load distribution across physical nodes"""
        
        if test_keys is None:
            # Generate test keys
            test_keys = [f"test_key_{i:06d}" for i in range(100000)]
        
        print(f"\nLoad Distribution Analysis:")
        print(f"Testing with {len(test_keys):,} keys...")
        
        # Count keys per physical node
        node_key_counts = defaultdict(int)
        
        for key in test_keys:
            responsible_node = self.get_node_for_key(key)
            if responsible_node:
                node_key_counts[responsible_node] += 1
        
        # Calculate statistics
        total_keys = len(test_keys)
        physical_node_count = len(self.physical_to_virtual)
        expected_keys_per_node = total_keys / physical_node_count if physical_node_count > 0 else 0
        
        load_percentages = []
        load_details = []
        
        for node_id in sorted(self.physical_to_virtual.keys()):
            key_count = node_key_counts[node_id]
            percentage = (key_count / total_keys) * 100 if total_keys > 0 else 0
            virtual_node_count = len(self.physical_to_virtual[node_id])
            
            load_percentages.append(percentage)
            load_details.append({
                'node_id': node_id,
                'key_count': key_count,
                'percentage': percentage,
                'virtual_nodes': virtual_node_count,
                'keys_per_vnode': key_count / virtual_node_count if virtual_node_count > 0 else 0
            })
            
            print(f"  {node_id}: {key_count:,} keys ({percentage:.2f}%) "
                  f"[{virtual_node_count} vnodes]")
        
        # Calculate distribution quality metrics
        if load_percentages:
            min_percentage = min(load_percentages)
            max_percentage = max(load_percentages)
            avg_percentage = statistics.mean(load_percentages)
            std_dev = statistics.stdev(load_percentages) if len(load_percentages) > 1 else 0
            cv = std_dev / avg_percentage if avg_percentage > 0 else 0
            imbalance_ratio = max_percentage / min_percentage if min_percentage > 0 else float('inf')
        else:
            min_percentage = max_percentage = avg_percentage = std_dev = cv = imbalance_ratio = 0
        
        print(f"\nDistribution Statistics:")
        print(f"  Expected per node: {100/physical_node_count:.2f}%")
        print(f"  Actual range: {min_percentage:.2f}% - {max_percentage:.2f}%")
        print(f"  Standard deviation: {std_dev:.3f}%")
        print(f"  Coefficient of variation: {cv:.3f}")
        print(f"  Imbalance ratio: {imbalance_ratio:.2f}:1")
        
        # Quality assessment
        if cv < 0.1:
            quality = "Excellent"
        elif cv < 0.2:
            quality = "Good"
        elif cv < 0.3:
            quality = "Acceptable"
        else:
            quality = "Poor"
        
        print(f"  Distribution quality: {quality}")
        
        return {
            'total_keys': total_keys,
            'physical_nodes': physical_node_count,
            'load_details': load_details,
            'statistics': {
                'min_percentage': min_percentage,
                'max_percentage': max_percentage,
                'std_dev': std_dev,
                'cv': cv,
                'imbalance_ratio': imbalance_ratio,
                'quality': quality
            }
        }
    
    def demonstrate_virtual_node_benefits(self):
        """Demonstrate the benefits of virtual nodes with comprehensive examples"""
        
        print("Virtual Node Benefits Demonstration:")
        print("=" * 45)
        
        # Add physical nodes with virtual nodes
        nodes_config = [
            ('web-server-01', 150),
            ('web-server-02', 150), 
            ('web-server-03', 150),
            ('web-server-04', 150)
        ]
        
        print("Setting up virtual node cluster...")
        for node_id, vnode_count in nodes_config:
            self.add_physical_node(node_id, vnode_count)
        
        # Analyze distribution
        distribution_analysis = self.analyze_load_distribution()
        
        # Show virtual node positions for one node
        sample_node = nodes_config[0][0]
        sample_positions = self.physical_to_virtual[sample_node]
        
        print(f"\nVirtual node positions for {sample_node} (showing first 10):")
        for i, pos in enumerate(sorted(sample_positions)[:10]):
            virtual_id, _ = self.virtual_node_map[pos]
            print(f"  {i+1:2d}. {virtual_id}: position {pos:,}")
        
        return distribution_analysis

# Demonstrate virtual node solution
vnode_demo = VirtualNodeConsistentHashing('sha1')
demo_results = vnode_demo.demonstrate_virtual_node_benefits()
```

### Comparison with Basic Consistent Hashing

```python
class VirtualNodeComparison:
    """Compare virtual nodes with basic consistent hashing"""
    
    def __init__(self):
        # Basic consistent hashing (1 node per position)
        self.basic_hash = BasicConsistentHashingFromPrevious()
        
        # Virtual node consistent hashing
        self.vnode_hash = VirtualNodeConsistentHashing()
    
    def side_by_side_comparison(self):
        """Compare basic vs virtual node approaches side by side"""
        
        print("Basic vs Virtual Node Comparison:")
        print("=" * 45)
        
        # Test with same physical nodes
        test_nodes = ['server-A', 'server-B', 'server-C', 'server-D']
        test_keys = [f"test_key_{i:05d}" for i in range(50000)]
        
        print("Setting up both systems...")
        
        # Setup basic consistent hashing
        print("\n1. Basic Consistent Hashing (1 position per node):")
        for node in test_nodes:
            self.basic_hash.add_node(node)
        
        basic_distribution = self.basic_hash.analyze_segment_distribution(test_nodes)
        basic_stats = basic_distribution['statistics']
        
        print(f"   Imbalance ratio: {basic_stats['imbalance_ratio']:.2f}:1")
        print(f"   Quality: {basic_stats['quality']}")
        
        # Setup virtual node hashing
        print("\n2. Virtual Node Hashing (150 positions per node):")
        for node in test_nodes:
            self.vnode_hash.add_physical_node(node, virtual_node_count=150)
        
        vnode_distribution = self.vnode_hash.analyze_load_distribution(test_keys)
        vnode_stats = vnode_distribution['statistics']
        
        print(f"   Imbalance ratio: {vnode_stats['imbalance_ratio']:.2f}:1")
        print(f"   Quality: {vnode_stats['quality']}")
        
        # Detailed comparison
        print(f"\nDetailed Comparison:")
        print(f"{'Metric':<25} {'Basic':<15} {'Virtual Nodes':<15} {'Improvement'}")
        print("-" * 70)
        
        metrics = [
            ('Imbalance Ratio', basic_stats['imbalance_ratio'], vnode_stats['imbalance_ratio']),
            ('Coefficient of Variation', basic_stats['cv'], vnode_stats['cv']),
            ('Std Deviation', basic_stats['std_dev'], vnode_stats['std_dev'])
        ]
        
        for metric_name, basic_val, vnode_val in metrics:
            if vnode_val > 0:
                improvement = ((basic_val - vnode_val) / basic_val) * 100
                improvement_str = f"{improvement:+.1f}%"
            else:
                improvement_str = "Perfect"
            
            print(f"{metric_name:<25} {basic_val:<15.3f} {vnode_val:<15.3f} {improvement_str}")
        
        return {
            'basic_stats': basic_stats,
            'vnode_stats': vnode_stats
        }
    
    def scaling_behavior_comparison(self):
        """Compare scaling behavior between basic and virtual nodes"""
        
        print("\nScaling Behavior Comparison:")
        print("=" * 35)
        
        # Start with 3 nodes, add nodes one by one
        initial_nodes = ['node-1', 'node-2', 'node-3']
        additional_nodes = ['node-4', 'node-5', 'node-6']
        
        basic_scaling_results = []
        vnode_scaling_results = []
        
        # Test basic consistent hashing scaling
        print("Basic Consistent Hashing Scaling:")
        basic_test = BasicConsistentHashingFromPrevious()
        
        current_basic_nodes = initial_nodes.copy()
        for node in current_basic_nodes:
            basic_test.add_node(node)
        
        for new_node in additional_nodes:
            basic_dist = basic_test.analyze_segment_distribution(current_basic_nodes)
            basic_scaling_results.append({
                'node_count': len(current_basic_nodes),
                'imbalance': basic_dist['statistics']['imbalance_ratio'],
                'quality': basic_dist['statistics']['quality']
            })
            
            print(f"  {len(current_basic_nodes)} nodes: {basic_dist['statistics']['imbalance_ratio']:.2f}:1 "
                  f"({basic_dist['statistics']['quality']})")
            
            # Add new node
            basic_test.add_node(new_node)
            current_basic_nodes.append(new_node)
        
        # Test virtual node scaling
        print("\nVirtual Node Scaling:")
        vnode_test = VirtualNodeConsistentHashing()
        
        current_vnode_nodes = initial_nodes.copy()
        for node in current_vnode_nodes:
            vnode_test.add_physical_node(node, 150)
        
        for new_node in additional_nodes:
            vnode_dist = vnode_test.analyze_load_distribution()
            vnode_scaling_results.append({
                'node_count': len(current_vnode_nodes),
                'imbalance': vnode_dist['statistics']['imbalance_ratio'],
                'quality': vnode_dist['statistics']['quality']
            })
            
            print(f"  {len(current_vnode_nodes)} nodes: {vnode_dist['statistics']['imbalance_ratio']:.2f}:1 "
                  f"({vnode_dist['statistics']['quality']})")
            
            # Add new node
            vnode_test.add_physical_node(new_node, 150)
            current_vnode_nodes.append(new_node)
        
        # Summary comparison
        print(f"\nScaling Summary:")
        print(f"Basic: Imbalance varies from "
              f"{min(r['imbalance'] for r in basic_scaling_results):.2f}:1 to "
              f"{max(r['imbalance'] for r in basic_scaling_results):.2f}:1")
        print(f"Virtual: Imbalance varies from "
              f"{min(r['imbalance'] for r in vnode_scaling_results):.2f}:1 to "
              f"{max(r['imbalance'] for r in vnode_scaling_results):.2f}:1")
        
        return {
            'basic_results': basic_scaling_results,
            'vnode_results': vnode_scaling_results
        }

# Note: We'll need to create a simplified BasicConsistentHashingFromPrevious class
class BasicConsistentHashingFromPrevious:
    """Simplified basic consistent hashing for comparison"""
    
    def __init__(self):
        self.ring = {}
        self.sorted_positions = []
        self.space_size = 2**32
    
    def _hash_value(self, key: str) -> int:
        hash_obj = hashlib.sha1(key.encode('utf-8'))
        return int(hash_obj.hexdigest(), 16) % self.space_size
    
    def add_node(self, node_id: str):
        position = self._hash_value(node_id)
        
        collision_count = 0
        while position in self.ring and collision_count < 1000:
            collision_count += 1
            position = self._hash_value(f"{node_id}_collision_{collision_count}")
        
        self.ring[position] = node_id
        self.sorted_positions = sorted(self.ring.keys())
    
    def analyze_segment_distribution(self, node_ids: List[str]) -> Dict:
        """Simplified analysis for comparison"""
        
        segments = []
        for i, position in enumerate(self.sorted_positions):
            current_pos = position
            next_pos = self.sorted_positions[(i + 1) % len(self.sorted_positions)]
            
            if next_pos > current_pos:
                segment_size = next_pos - current_pos
            else:
                segment_size = (self.space_size - current_pos) + next_pos
            
            percentage = (segment_size / self.space_size) * 100
            segments.append(percentage)
        
        if segments:
            min_pct = min(segments)
            max_pct = max(segments)
            std_dev = statistics.stdev(segments)
            avg_pct = statistics.mean(segments)
            cv = std_dev / avg_pct if avg_pct > 0 else 0
            imbalance = max_pct / min_pct if min_pct > 0 else float('inf')
            
            if cv < 0.2:
                quality = "Excellent"
            elif cv < 0.4:
                quality = "Good"
            elif cv < 0.6:
                quality = "Acceptable"
            else:
                quality = "Poor"
        else:
            min_pct = max_pct = std_dev = cv = imbalance = 0
            quality = "No data"
        
        return {
            'statistics': {
                'min_percentage': min_pct,
                'max_percentage': max_pct,
                'std_dev': std_dev,
                'cv': cv,
                'imbalance_ratio': imbalance,
                'quality': quality
            }
        }

# Run comparison
comparison = VirtualNodeComparison()
comparison_results = comparison.side_by_side_comparison()
scaling_comparison = comparison.scaling_behavior_comparison()
```

## Better Distribution Analysis

Virtual nodes fundamentally improve load distribution by increasing the number of decision points on the hash ring.

### Statistical Distribution Properties

```python
class DistributionAnalysis:
    """Analyze distribution properties of virtual nodes"""
    
    def __init__(self):
        self.vnode_system = VirtualNodeConsistentHashing()
    
    def analyze_virtual_node_count_impact(self):
        """Analyze how virtual node count affects distribution quality"""
        
        print("Virtual Node Count Impact Analysis:")
        print("=" * 45)
        
        # Test different virtual node counts
        vnode_counts = [10, 25, 50, 100, 150, 200, 300, 500]
        physical_nodes = ['server-1', 'server-2', 'server-3', 'server-4']
        test_keys = [f"key_{i:06d}" for i in range(100000)]
        
        results = []
        
        for vnode_count in vnode_counts:
            print(f"\nTesting {vnode_count} virtual nodes per physical node:")
            
            # Create fresh system
            test_system = VirtualNodeConsistentHashing()
            
            # Add nodes with specified virtual node count
            for node in physical_nodes:
                test_system.add_physical_node(node, vnode_count)
            
            # Analyze distribution
            distribution = test_system.analyze_load_distribution(test_keys)
            stats = distribution['statistics']
            
            results.append({
                'vnode_count': vnode_count,
                'imbalance_ratio': stats['imbalance_ratio'],
                'cv': stats['cv'],
                'quality': stats['quality']
            })
            
            print(f"  Imbalance ratio: {stats['imbalance_ratio']:.3f}:1")
            print(f"  Coefficient of variation: {stats['cv']:.4f}")
            print(f"  Quality: {stats['quality']}")
        
        # Find optimal range
        print(f"\nOptimal Virtual Node Count Analysis:")
        
        # Find where quality becomes "Excellent" consistently
        excellent_results = [r for r in results if r['quality'] == 'Excellent']
        if excellent_results:
            min_excellent = min(r['vnode_count'] for r in excellent_results)
            print(f"  Minimum for excellent quality: {min_excellent} vnodes")
        
        # Find diminishing returns point
        cv_improvements = []
        for i in range(1, len(results)):
            prev_cv = results[i-1]['cv']
            curr_cv = results[i]['cv']
            improvement = ((prev_cv - curr_cv) / prev_cv) * 100 if prev_cv > 0 else 0
            cv_improvements.append(improvement)
        
        diminishing_threshold = 5.0  # Less than 5% improvement
        diminishing_point = None
        
        for i, improvement in enumerate(cv_improvements):
            if improvement < diminishing_threshold:
                diminishing_point = vnode_counts[i + 1]
                break
        
        if diminishing_point:
            print(f"  Diminishing returns start at: {diminishing_point} vnodes")
        
        # Recommendations
        print(f"\nRecommendations:")
        if excellent_results:
            recommended_min = min(r['vnode_count'] for r in excellent_results)
            recommended_optimal = diminishing_point or recommended_min
            print(f"  Minimum recommended: {recommended_min} vnodes")
            print(f"  Optimal range: {recommended_min}-{recommended_optimal} vnodes")
            print(f"  Production standard: 150 vnodes (good balance)")
        
        return results
    
    def demonstrate_distribution_convergence(self):
        """Show how distribution converges as virtual nodes increase"""
        
        print("\nDistribution Convergence Demonstration:")
        print("=" * 45)
        
        # Fixed setup
        physical_nodes = ['node-A', 'node-B', 'node-C']
        test_keys = [f"test_{i:05d}" for i in range(50000)]
        
        # Test progression of virtual node counts
        progression = [1, 5, 10, 25, 50, 100, 150, 200]
        
        print("Virtual Node Count → Load Distribution:")
        print("Nodes per Physical | Imbalance Ratio | Std Dev | Quality")
        print("-" * 55)
        
        convergence_data = []
        
        for vnode_count in progression:
            test_system = VirtualNodeConsistentHashing()
            
            for node in physical_nodes:
                test_system.add_physical_node(node, vnode_count)
            
            distribution = test_system.analyze_load_distribution(test_keys)
            stats = distribution['statistics']
            
            convergence_data.append({
                'vnode_count': vnode_count,
                'imbalance': stats['imbalance_ratio'],
                'std_dev': stats['std_dev'],
                'quality': stats['quality']
            })
            
            print(f"{vnode_count:>17} | {stats['imbalance_ratio']:>14.3f} | "
                  f"{stats['std_dev']:>7.4f} | {stats['quality']}")
        
        # Show convergence trend
        print(f"\nConvergence Analysis:")
        
        # Calculate improvement rates
        for i in range(1, len(convergence_data)):
            prev = convergence_data[i-1]
            curr = convergence_data[i]
            
            imbalance_improvement = ((prev['imbalance'] - curr['imbalance']) / prev['imbalance']) * 100
            std_improvement = ((prev['std_dev'] - curr['std_dev']) / prev['std_dev']) * 100
            
            print(f"  {prev['vnode_count']} → {curr['vnode_count']} vnodes: "
                  f"{imbalance_improvement:+.1f}% imbalance, {std_improvement:+.1f}% std dev")
        
        return convergence_data
    
    def heterogeneous_cluster_analysis(self):
        """Analyze virtual nodes in heterogeneous clusters"""
        
        print("\nHeterogeneous Cluster Analysis:")
        print("=" * 40)
        
        # Simulate different capacity nodes
        cluster_config = [
            ('small-node-1', 50, '2 CPU, 4GB RAM'),
            ('small-node-2', 50, '2 CPU, 4GB RAM'),
            ('medium-node-1', 100, '4 CPU, 8GB RAM'),
            ('medium-node-2', 100, '4 CPU, 8GB RAM'),
            ('large-node-1', 200, '8 CPU, 16GB RAM'),
            ('large-node-2', 200, '8 CPU, 16GB RAM')
        ]
        
        print("Heterogeneous cluster configuration:")
        for node_id, vnode_count, specs in cluster_config:
            print(f"  {node_id}: {vnode_count} vnodes ({specs})")
        
        # Setup heterogeneous cluster
        hetero_system = VirtualNodeConsistentHashing()
        
        total_vnodes = 0
        for node_id, vnode_count, _ in cluster_config:
            hetero_system.add_physical_node(node_id, vnode_count)
            total_vnodes += vnode_count
        
        # Analyze load distribution
        test_keys = [f"hetero_key_{i:06d}" for i in range(100000)]
        distribution = hetero_system.analyze_load_distribution(test_keys)
        
        print(f"\nLoad distribution results:")
        for detail in distribution['load_details']:
            node_id = detail['node_id']
            percentage = detail['percentage']
            virtual_nodes = detail['virtual_nodes']
            expected_percentage = (virtual_nodes / total_vnodes) * 100
            
            print(f"  {node_id}: {percentage:.2f}% "
                  f"(expected: {expected_percentage:.2f}%, "
                  f"ratio: {percentage/expected_percentage:.2f})")
        
        # Calculate capacity-weighted fairness
        print(f"\nCapacity-weighted analysis:")
        total_capacity_units = sum(vnode_count for _, vnode_count, _ in cluster_config)
        
        for detail in distribution['load_details']:
            node_id = detail['node_id']
            actual_load = detail['percentage']
            virtual_nodes = detail['virtual_nodes']
            
            # Find node specs
            node_specs = None
            for config_node, config_vnodes, specs in cluster_config:
                if config_node == node_id:
                    node_specs = specs
                    break
            
            expected_load = (virtual_nodes / total_capacity_units) * 100
            load_efficiency = actual_load / expected_load if expected_load > 0 else 0
            
            print(f"  {node_id}: Load efficiency {load_efficiency:.3f} "
                  f"({node_specs})")
        
        # Overall heterogeneous cluster quality
        stats = distribution['statistics']
        print(f"\nHeterogeneous cluster quality:")
        print(f"  Imbalance ratio: {stats['imbalance_ratio']:.3f}:1")
        print(f"  Quality: {stats['quality']}")
        print(f"  Capacity utilization efficiency: "
              f"{'Excellent' if stats['imbalance_ratio'] < 1.2 else 'Good' if stats['imbalance_ratio'] < 1.5 else 'Needs tuning'}")
        
        return distribution

# Run distribution analysis
dist_analyzer = DistributionAnalysis()
vnode_count_impact = dist_analyzer.analyze_virtual_node_count_impact()
convergence_demo = dist_analyzer.demonstrate_distribution_convergence()
hetero_analysis = dist_analyzer.heterogeneous_cluster_analysis()
```

## Smoother Scaling Benefits

Virtual nodes provide more predictable and effective scaling behavior compared to basic consistent hashing.

### Scaling Impact Analysis

```python
class SmoothScalingAnalysis:
    """Analyze smooth scaling benefits of virtual nodes"""
    
    def __init__(self):
        pass
    
    def demonstrate_scaling_smoothness(self):
        """Demonstrate how virtual nodes provide smoother scaling"""
        
        print("Smooth Scaling Demonstration:")
        print("=" * 35)
        
        # Start with baseline cluster
        baseline_nodes = ['web-01', 'web-02', 'web-03']
        
        print("Baseline 3-node cluster setup...")
        baseline_system = VirtualNodeConsistentHashing()
        
        for node in baseline_nodes:
            baseline_system.add_physical_node(node, 150)
        
        # Analyze initial distribution
        initial_distribution = baseline_system.analyze_load_distribution()
        initial_stats = initial_distribution['statistics']
        
        print(f"Initial state:")
        print(f"  Nodes: {len(baseline_nodes)}")
        print(f"  Imbalance ratio: {initial_stats['imbalance_ratio']:.3f}:1")
        print(f"  Quality: {initial_stats['quality']}")
        
        # Add nodes one by one and track impact
        additional_nodes = ['web-04', 'web-05', 'web-06']
        scaling_history = []
        
        current_system = baseline_system
        current_nodes = baseline_nodes.copy()
        
        for new_node in additional_nodes:
            print(f"\nAdding {new_node}...")
            
            # Add new node
            current_system.add_physical_node(new_node, 150)
            current_nodes.append(new_node)
            
            # Analyze new distribution
            new_distribution = current_system.analyze_load_distribution()
            new_stats = new_distribution['statistics']
            
            # Calculate scaling impact
            nodes_before = len(current_nodes) - 1
            nodes_after = len(current_nodes)
            theoretical_reduction = (1 / nodes_after) * 100
            
            scaling_history.append({
                'nodes_after': nodes_after,
                'imbalance_ratio': new_stats['imbalance_ratio'],
                'quality': new_stats['quality'],
                'theoretical_reduction': theoretical_reduction
            })
            
            print(f"  Cluster size: {nodes_before} → {nodes_after} nodes")
            print(f"  Imbalance ratio: {new_stats['imbalance_ratio']:.3f}:1")
            print(f"  Quality: {new_stats['quality']}")
            print(f"  Theoretical load reduction: {theoretical_reduction:.1f}%")
        
        # Analyze scaling smoothness
        print(f"\nScaling Smoothness Analysis:")
        
        imbalance_ratios = [entry['imbalance_ratio'] for entry in scaling_history]
        max_imbalance = max(imbalance_ratios)
        min_imbalance = min(imbalance_ratios)
        imbalance_variance = statistics.variance(imbalance_ratios)
        
        print(f"  Imbalance ratio range: {min_imbalance:.3f} - {max_imbalance:.3f}")
        print(f"  Imbalance variance: {imbalance_variance:.6f}")
        print(f"  Scaling stability: {'Excellent' if imbalance_variance < 0.001 else 'Good' if imbalance_variance < 0.01 else 'Needs improvement'}")
        
        return scaling_history
    
    def compare_single_vs_multiple_node_addition(self):
        """Compare adding one large node vs multiple small nodes"""
        
        print("\nSingle vs Multiple Node Addition Comparison:")
        print("=" * 50)
        
        # Baseline cluster
        base_nodes = ['server-1', 'server-2', 'server-3']
        
        # Scenario 1: Add one large node (300 vnodes)
        print("Scenario 1: Adding one large node (300 vnodes)")
        scenario1_system = VirtualNodeConsistentHashing()
        
        for node in base_nodes:
            scenario1_system.add_physical_node(node, 150)
        
        scenario1_before = scenario1_system.analyze_load_distribution()
        print(f"  Before: {scenario1_before['statistics']['imbalance_ratio']:.3f}:1")
        
        scenario1_system.add_physical_node('large-server', 300)
        scenario1_after = scenario1_system.analyze_load_distribution()
        print(f"  After: {scenario1_after['statistics']['imbalance_ratio']:.3f}:1")
        
        # Scenario 2: Add two normal nodes (150 vnodes each)
        print("\nScenario 2: Adding two normal nodes (150 vnodes each)")
        scenario2_system = VirtualNodeConsistentHashing()
        
        for node in base_nodes:
            scenario2_system.add_physical_node(node, 150)
        
        scenario2_before = scenario2_system.analyze_load_distribution()
        print(f"  Before: {scenario2_before['statistics']['imbalance_ratio']:.3f}:1")
        
        scenario2_system.add_physical_node('server-4', 150)
        scenario2_system.add_physical_node('server-5', 150)
        scenario2_after = scenario2_system.analyze_load_distribution()
        print(f"  After: {scenario2_after['statistics']['imbalance_ratio']:.3f}:1")
        
        # Compare final results
        print(f"\nComparison Results:")
        print(f"  Single large node: {scenario1_after['statistics']['quality']}")
        print(f"  Multiple normal nodes: {scenario2_after['statistics']['quality']}")
        
        # Calculate capacity distribution efficiency
        s1_details = scenario1_after['load_details']
        s2_details = scenario2_after['load_details']
        
        print(f"\nCapacity utilization:")
        print(f"  Scenario 1 - Large node load: {s1_details[-1]['percentage']:.2f}% "
              f"(expected: {s1_details[-1]['virtual_nodes'] / sum(d['virtual_nodes'] for d in s1_details) * 100:.2f}%)")
        
        s2_new_nodes = [d for d in s2_details if d['node_id'] in ['server-4', 'server-5']]
        avg_new_load = statistics.mean([d['percentage'] for d in s2_new_nodes])
        print(f"  Scenario 2 - New nodes avg load: {avg_new_load:.2f}% "
              f"(expected: {150 / sum(d['virtual_nodes'] for d in s2_details) * 100:.2f}%)")
        
        return {
            'scenario1': scenario1_after,
            'scenario2': scenario2_after
        }
    
    def analyze_gradual_capacity_scaling(self):
        """Analyze gradual capacity scaling patterns"""
        
        print("\nGradual Capacity Scaling Analysis:")
        print("=" * 40)
        
        # Start with small cluster
        initial_system = VirtualNodeConsistentHashing()
        
        # Add initial nodes
        initial_nodes = ['start-1', 'start-2']
        for node in initial_nodes:
            initial_system.add_physical_node(node, 100)
        
        # Scaling plan: gradually increase capacity
        scaling_plan = [
            ('phase-1-node', 100, "Match existing capacity"),
            ('phase-2-node', 150, "50% more capacity"),
            ('phase-3-node', 200, "100% more capacity"),
            ('phase-4-node', 250, "150% more capacity")
        ]
        
        scaling_results = []
        current_system = initial_system
        
        print("Gradual scaling progression:")
        
        # Initial state
        initial_dist = current_system.analyze_load_distribution()
        print(f"  Initial (2 nodes): {initial_dist['statistics']['imbalance_ratio']:.3f}:1")
        
        for node_id, vnode_count, description in scaling_plan:
            current_system.add_physical_node(node_id, vnode_count)
            
            new_dist = current_system.analyze_load_distribution()
            total_nodes = len(current_system.physical_to_virtual)
            
            scaling_results.append({
                'phase': node_id,
                'total_nodes': total_nodes,
                'new_node_vnodes': vnode_count,
                'imbalance': new_dist['statistics']['imbalance_ratio'],
                'quality': new_dist['statistics']['quality']
            })
            
            print(f"  {node_id} ({total_nodes} nodes, {vnode_count} vnodes): "
                  f"{new_dist['statistics']['imbalance_ratio']:.3f}:1 - {description}")
        
        # Analyze scaling trend
        imbalances = [r['imbalance'] for r in scaling_results]
        print(f"\nScaling trend analysis:")
        print(f"  Best balance: {min(imbalances):.3f}:1")
        print(f"  Worst balance: {max(imbalances):.3f}:1")
        print(f"  Balance stability: {max(imbalances) - min(imbalances):.3f} variation")
        
        if max(imbalances) - min(imbalances) < 0.1:
            print(f"  ✅ Excellent scaling stability")
        elif max(imbalances) - min(imbalances) < 0.3:
            print(f"  ✅ Good scaling stability")
        else:
            print(f"  ⚠️  Consider adjusting virtual node counts")
        
        return scaling_results

# Run smooth scaling analysis
scaling_analyzer = SmoothScalingAnalysis()
smoothness_demo = scaling_analyzer.demonstrate_scaling_smoothness()
addition_comparison = scaling_analyzer.compare_single_vs_multiple_node_addition()
gradual_scaling = scaling_analyzer.analyze_gradual_capacity_scaling()
```

## Improved Fault Tolerance

Virtual nodes significantly improve system resilience by distributing the impact of node failures across multiple segments.

### Fault Tolerance Analysis

```python
class FaultToleranceAnalysis:
    """Analyze fault tolerance improvements with virtual nodes"""
    
    def __init__(self):
        pass
    
    def demonstrate_failure_impact_distribution(self):
        """Show how virtual nodes distribute failure impact"""
        
        print("Failure Impact Distribution Analysis:")
        print("=" * 45)
        
        # Setup cluster with virtual nodes
        cluster_nodes = ['primary-1', 'primary-2', 'primary-3', 'primary-4', 'primary-5']
        
        system = VirtualNodeConsistentHashing()
        for node in cluster_nodes:
            system.add_physical_node(node, 150)
        
        # Analyze baseline distribution
        baseline_dist = system.analyze_load_distribution()
        print(f"Baseline cluster (5 nodes):")
        print(f"  Imbalance ratio: {baseline_dist['statistics']['imbalance_ratio']:.3f}:1")
        
        # Simulate failure of each node
        failure_impacts = []
        
        for failed_node in cluster_nodes:
            print(f"\nSimulating failure of {failed_node}:")
            
            # Create system without failed node
            surviving_nodes = [n for n in cluster_nodes if n != failed_node]
            
            failed_system = VirtualNodeConsistentHashing()
            for node in surviving_nodes:
                failed_system.add_physical_node(node, 150)
            
            # Analyze post-failure distribution
            post_failure_dist = failed_system.analyze_load_distribution()
            post_failure_stats = post_failure_dist['statistics']
            
            print(f"  Surviving nodes: {len(surviving_nodes)}")
            print(f"  New imbalance ratio: {post_failure_stats['imbalance_ratio']:.3f}:1")
            print(f"  Quality: {post_failure_stats['quality']}")
            
            # Calculate load increase on remaining nodes
            baseline_load_per_node = 100 / len(cluster_nodes)
            post_failure_load_per_node = 100 / len(surviving_nodes)
            theoretical_load_increase = ((post_failure_load_per_node - baseline_load_per_node) / baseline_load_per_node) * 100
            
            print(f"  Theoretical load increase: {theoretical_load_increase:.1f}%")
            
            # Find maximum load increase
            max_load_detail = max(post_failure_dist['load_details'], key=lambda x: x['percentage'])
            max_load_increase = ((max_load_detail['percentage'] - baseline_load_per_node) / baseline_load_per_node) * 100
            
            print(f"  Maximum actual load increase: {max_load_increase:.1f}% on {max_load_detail['node_id']}")
            
            failure_impacts.append({
                'failed_node': failed_node,
                'surviving_nodes': len(surviving_nodes),
                'new_imbalance': post_failure_stats['imbalance_ratio'],
                'theoretical_increase': theoretical_load_increase,
                'max_actual_increase': max_load_increase,
                'quality': post_failure_stats['quality']
            })
        
        # Analyze failure resilience
        print(f"\nFailure Resilience Summary:")
        
        imbalances = [impact['new_imbalance'] for impact in failure_impacts]
        max_increases = [impact['max_actual_increase'] for impact in failure_impacts]
        
        print(f"  Post-failure imbalance range: {min(imbalances):.3f} - {max(imbalances):.3f}")
        print(f"  Maximum load increase range: {min(max_increases):.1f}% - {max(max_increases):.1f}%")
        
        resilience_quality = "Excellent" if max(imbalances) < 1.5 else "Good" if max(imbalances) < 2.0 else "Needs improvement"
        print(f"  Overall resilience: {resilience_quality}")
        
        return failure_impacts
    
    def compare_basic_vs_virtual_failure_impact(self):
        """Compare failure impact between basic and virtual node approaches"""
        
        print("\nBasic vs Virtual Node Failure Impact Comparison:")
        print("=" * 55)
        
        test_nodes = ['node-A', 'node-B', 'node-C', 'node-D']
        
        # Test basic consistent hashing failure impact
        print("Basic Consistent Hashing:")
        basic_system = BasicConsistentHashingFromPrevious()
        
        for node in test_nodes:
            basic_system.add_node(node)
        
        basic_baseline = basic_system.analyze_segment_distribution(test_nodes)
        print(f"  Baseline imbalance: {basic_baseline['statistics']['imbalance_ratio']:.3f}:1")
        
        # Simulate failure in basic system
        basic_after_failure = basic_system.analyze_segment_distribution(['node-A', 'node-B', 'node-C'])
        print(f"  After node failure: {basic_after_failure['statistics']['imbalance_ratio']:.3f}:1")
        
        basic_impact = basic_after_failure['statistics']['imbalance_ratio'] - basic_baseline['statistics']['imbalance_ratio']
        
        # Test virtual node failure impact
        print("\nVirtual Node Consistent Hashing:")
        vnode_system = VirtualNodeConsistentHashing()
        
        for node in test_nodes:
            vnode_system.add_physical_node(node, 150)
        
        vnode_baseline = vnode_system.analyze_load_distribution()
        print(f"  Baseline imbalance: {vnode_baseline['statistics']['imbalance_ratio']:.3f}:1")
        
        # Simulate failure in virtual node system
        vnode_after_failure = VirtualNodeConsistentHashing()
        for node in ['node-A', 'node-B', 'node-C']:
            vnode_after_failure.add_physical_node(node, 150)
        
        vnode_post_failure = vnode_after_failure.analyze_load_distribution()
        print(f"  After node failure: {vnode_post_failure['statistics']['imbalance_ratio']:.3f}:1")
        
        vnode_impact = vnode_post_failure['statistics']['imbalance_ratio'] - vnode_baseline['statistics']['imbalance_ratio']
        
        # Compare impacts
        print(f"\nFailure Impact Comparison:")
        print(f"  Basic system impact: +{basic_impact:.3f} imbalance ratio")
        print(f"  Virtual node impact: +{vnode_impact:.3f} imbalance ratio")
        
        improvement = ((basic_impact - vnode_impact) / basic_impact) * 100 if basic_impact > 0 else 0
        print(f"  Virtual node improvement: {improvement:.1f}% less impact")
        
        return {
            'basic_impact': basic_impact,
            'vnode_impact': vnode_impact,
            'improvement_percent': improvement
        }
    
    def analyze_cascading_failure_resistance(self):
        """Analyze resistance to cascading failures"""
        
        print("\nCascading Failure Resistance Analysis:")
        print("=" * 45)
        
        # Setup larger cluster for cascading failure analysis
        cluster_size = 8
        cluster_nodes = [f"cluster-node-{i:02d}" for i in range(1, cluster_size + 1)]
        
        system = VirtualNodeConsistentHashing()
        for node in cluster_nodes:
            system.add_physical_node(node, 150)
        
        # Baseline
        baseline = system.analyze_load_distribution()
        baseline_max_load = max(detail['percentage'] for detail in baseline['load_details'])
        
        print(f"Baseline cluster ({cluster_size} nodes):")
        print(f"  Maximum node load: {baseline_max_load:.2f}%")
        print(f"  Imbalance ratio: {baseline['statistics']['imbalance_ratio']:.3f}:1")
        
        # Simulate progressive failures
        failure_threshold = 80.0  # Assume node fails if load exceeds 80%
        surviving_nodes = cluster_nodes.copy()
        failure_cascade = []
        
        for failure_round in range(1, 4):  # Test up to 3 rounds of failures
            print(f"\nFailure Round {failure_round}:")
            
            # Remove one node (simulate failure)
            if surviving_nodes:
                failed_node = surviving_nodes[0]  # Remove first node
                surviving_nodes = surviving_nodes[1:]
                
                print(f"  Node failed: {failed_node}")
                print(f"  Surviving nodes: {len(surviving_nodes)}")
                
                if len(surviving_nodes) < 2:
                    print(f"  ⚠️  Too few nodes remaining for analysis")
                    break
                
                # Create system with surviving nodes
                surviving_system = VirtualNodeConsistentHashing()
                for node in surviving_nodes:
                    surviving_system.add_physical_node(node, 150)
                
                # Analyze new distribution
                post_failure_dist = surviving_system.analyze_load_distribution()
                max_load = max(detail['percentage'] for detail in post_failure_dist['load_details'])
                overloaded_nodes = [d for d in post_failure_dist['load_details'] 
                                  if d['percentage'] > failure_threshold]
                
                print(f"  New maximum load: {max_load:.2f}%")
                print(f"  Nodes over threshold ({failure_threshold}%): {len(overloaded_nodes)}")
                print(f"  Imbalance ratio: {post_failure_dist['statistics']['imbalance_ratio']:.3f}:1")
                
                failure_cascade.append({
                    'round': failure_round,
                    'failed_node': failed_node,
                    'surviving_count': len(surviving_nodes),
                    'max_load': max_load,
                    'overloaded_count': len(overloaded_nodes),
                    'imbalance': post_failure_dist['statistics']['imbalance_ratio']
                })
                
                # Check for cascading failure risk
                if len(overloaded_nodes) > 0:
                    print(f"  ⚠️  CASCADING FAILURE RISK: {len(overloaded_nodes)} nodes overloaded")
                else:
                    print(f"  ✅ No cascading failure risk")
        
        # Analyze cascade resistance
        print(f"\nCascade Resistance Summary:")
        
        max_loads = [entry['max_load'] for entry in failure_cascade]
        overload_counts = [entry['overloaded_count'] for entry in failure_cascade]
        
        if any(count > 0 for count in overload_counts):
            cascade_risk_round = next(i+1 for i, count in enumerate(overload_counts) if count > 0)
            print(f"  Cascading failure risk starts at round: {cascade_risk_round}")
        else:
            print(f"  No cascading failure risk detected")
        
        print(f"  Maximum load progression: {' → '.join(f'{load:.1f}%' for load in max_loads)}")
        
        resistance_quality = "Excellent" if not any(count > 0 for count in overload_counts) else "Good" if cascade_risk_round > 2 else "Needs improvement"
        print(f"  Cascade resistance: {resistance_quality}")
        
        return failure_cascade

# Run fault tolerance analysis
fault_analyzer = FaultToleranceAnalysis()
failure_distribution = fault_analyzer.demonstrate_failure_impact_distribution()
failure_comparison = fault_analyzer.compare_basic_vs_virtual_failure_impact()
cascade_resistance = fault_analyzer.analyze_cascading_failure_resistance()
```

## Summary

Virtual nodes solve the fundamental problems of basic consistent hashing through four key mechanisms:

1. **Better Distribution**: Multiple positions per physical node create more uniform load distribution with predictable statistical properties

2. **Smoother Scaling**: Adding nodes affects multiple ring segments simultaneously, providing more effective load relief and predictable scaling behavior

3. **Improved Fault Tolerance**: Node failures are distributed across multiple ring segments, reducing the maximum impact on any single remaining node

4. **Heterogeneous Support**: Different virtual node counts allow nodes with different capacities to receive proportional load, enabling mixed hardware deployments

These improvements make virtual nodes essential for production consistent hashing implementations, transforming the algorithm from a basic partitioning scheme into a robust, scalable distributed system primitive capable of handling real-world operational requirements.​​​​​​​​​​​​​​​​
