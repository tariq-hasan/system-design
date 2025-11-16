# Redistribution Efficiency in Consistent Hashing

The redistribution efficiency of consistent hashing represents one of its most significant advantages over traditional partitioning schemes. This efficiency stems from the mathematical properties of the hash ring and the clockwise assignment rule, which together ensure that topology changes require minimal data movement. Understanding redistribution efficiency is crucial for system architects because it directly impacts operational costs, service availability, and system scalability.

## Optimal Movement Mathematics

The cornerstone of consistent hashing's efficiency is that it achieves theoretically optimal data movement during topology changes. This optimality is not just a practical benefit but a mathematical guarantee that emerges from the algorithm's design.

### Theoretical Foundation

**Optimal Movement Theorem**: When adding or removing a node in a consistent hashing system with K total keys and n existing nodes, exactly K/(n+1) keys need to move (for addition) or K/n keys need to move (for removal), representing the theoretical minimum required for balanced redistribution.

### Mathematical Proof and Analysis

```python
import math
import random
from collections import defaultdict

class RedistributionAnalysis:
    def __init__(self):
        self.ring = {}
        self.sorted_positions = []
        
    def _hash_value(self, key):
        """Hash function for ring positions"""
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
    
    def remove_node(self, node_id):
        """Remove a node from the ring"""
        position = self._hash_value(node_id)
        if position in self.ring:
            del self.ring[position]
            self.sorted_positions = sorted(self.ring.keys())
        return position
    
    def get_node_for_key(self, key):
        """Find responsible node for key"""
        if not self.sorted_positions:
            return None
        
        key_position = self._hash_value(key)
        
        # Find first node position >= key position
        for node_position in self.sorted_positions:
            if node_position >= key_position:
                return self.ring[node_position]
        
        # Wrap around to first node
        return self.ring[self.sorted_positions[0]]
    
    def analyze_optimal_movement(self, initial_nodes, num_keys):
        """Analyze data movement optimality"""
        
        print("Optimal Movement Analysis:")
        print("=" * 30)
        
        # Set up initial ring
        for node in initial_nodes:
            self.add_node(node)
        
        # Generate test keys and record initial assignments
        test_keys = [f"key_{i}" for i in range(num_keys)]
        initial_assignments = {}
        initial_distribution = defaultdict(int)
        
        for key in test_keys:
            node = self.get_node_for_key(key)
            initial_assignments[key] = node
            initial_distribution[node] += 1
        
        print(f"Initial state: {len(initial_nodes)} nodes, {num_keys:,} keys")
        print(f"Average keys per node: {num_keys / len(initial_nodes):.1f}")
        
        # Show initial distribution
        print("Initial distribution:")
        for node in sorted(initial_distribution.keys()):
            percentage = (initial_distribution[node] / num_keys) * 100
            print(f"  {node}: {initial_distribution[node]:,} keys ({percentage:.1f}%)")
        
        # Test node addition
        new_node = f"node_{len(initial_nodes)}"
        print(f"\nAdding {new_node}:")
        
        self.add_node(new_node)
        
        # Analyze movement after addition
        moved_keys = []
        new_assignments = {}
        new_distribution = defaultdict(int)
        
        for key in test_keys:
            new_node_assignment = self.get_node_for_key(key)
            new_assignments[key] = new_node_assignment
            new_distribution[new_node_assignment] += 1
            
            if initial_assignments[key] != new_node_assignment:
                moved_keys.append({
                    'key': key,
                    'from': initial_assignments[key],
                    'to': new_node_assignment,
                    'position': self._hash_value(key)
                })
        
        # Calculate movement metrics
        num_moved = len(moved_keys)
        total_nodes_after = len(initial_nodes) + 1
        theoretical_optimal = num_keys / total_nodes_after
        actual_movement_percentage = (num_moved / num_keys) * 100
        theoretical_percentage = (theoretical_optimal / num_keys) * 100
        
        print(f"  Theoretical optimal movement: {theoretical_optimal:.1f} keys ({theoretical_percentage:.2f}%)")
        print(f"  Actual movement: {num_moved} keys ({actual_movement_percentage:.2f}%)")
        print(f"  Efficiency: {(theoretical_percentage / actual_movement_percentage * 100):.1f}% of theoretical optimum")
        
        # Verify all moved keys went to new node
        moved_to_new_node = sum(1 for mk in moved_keys if mk['to'] == new_node)
        print(f"  Keys moved to new node: {moved_to_new_node} ({moved_to_new_node / num_moved * 100:.1f}% of moved keys)")
        
        # Show new distribution
        print("\nDistribution after addition:")
        for node in sorted(new_distribution.keys()):
            percentage = (new_distribution[node] / num_keys) * 100
            change = new_distribution[node] - initial_distribution.get(node, 0)
            change_str = f"({change:+d})" if change != 0 else ""
            print(f"  {node}: {new_distribution[node]:,} keys ({percentage:.1f}%) {change_str}")
        
        return {
            'theoretical_optimal': theoretical_optimal,
            'actual_moved': num_moved,
            'efficiency_percentage': (theoretical_percentage / actual_movement_percentage * 100) if actual_movement_percentage > 0 else 100,
            'moved_to_correct_node': moved_to_new_node == num_moved
        }

# Demonstrate optimal movement
analysis = RedistributionAnalysis()
initial_nodes = ['node_0', 'node_1', 'node_2', 'node_3']
result = analysis.analyze_optimal_movement(initial_nodes, 10000)
```

### Comparative Analysis with Traditional Methods

```python
class ComparativeRedistribution:
    def compare_redistribution_methods(self):
        """Compare redistribution efficiency across different methods"""
        
        print("\nRedistribution Method Comparison:")
        print("=" * 40)
        
        scenarios = [
            (5, 10000, "Small system"),
            (50, 100000, "Medium system"),
            (500, 1000000, "Large system")
        ]
        
        for num_nodes, num_keys, description in scenarios:
            print(f"\n{description}: {num_nodes} → {num_nodes + 1} nodes, {num_keys:,} keys")
            
            # Consistent hashing movement
            ch_theoretical = num_keys / (num_nodes + 1)
            ch_percentage = (ch_theoretical / num_keys) * 100
            
            # Traditional modulo hashing movement
            modulo_affected = num_keys * 0.8  # Approximately 80% typically affected
            modulo_percentage = (modulo_affected / num_keys) * 100
            
            # Range-based partitioning (varies widely)
            range_affected = num_keys * 0.25  # Approximately 25% for hot spot split
            range_percentage = (range_affected / num_keys) * 100
            
            print(f"  Consistent Hashing:")
            print(f"    Keys moved: {ch_theoretical:.0f} ({ch_percentage:.2f}%)")
            print(f"    Network transfer: {ch_theoretical * 2:.0f} KB (assuming 2KB/key)")
            
            print(f"  Modulo Hashing:")
            print(f"    Keys moved: {modulo_affected:.0f} ({modulo_percentage:.1f}%)")
            print(f"    Network transfer: {modulo_affected * 2 / 1024:.0f} MB")
            
            print(f"  Range-Based:")
            print(f"    Keys moved: {range_affected:.0f} ({range_percentage:.1f}%)")
            print(f"    Network transfer: {range_affected * 2 / 1024:.0f} MB")
            
            # Calculate improvements
            modulo_improvement = modulo_percentage / ch_percentage
            range_improvement = range_percentage / ch_percentage
            
            print(f"  Consistent Hashing Advantage:")
            print(f"    vs Modulo: {modulo_improvement:.1f}x less data movement")
            print(f"    vs Range-based: {range_improvement:.1f}x less data movement")

# Run comparative analysis
comparative = ComparativeRedistribution()
comparative.compare_redistribution_methods()
```

## Localized Impact Analysis

The localized impact property ensures that topology changes only affect keys in specific, predictable regions of the hash ring, making the system's behavior deterministic and debuggable.

### Mathematical Characterization of Impact Zones

```python
class LocalizedImpactAnalysis:
    def __init__(self):
        self.ring = {}
        self.sorted_positions = []
    
    def _hash_value(self, key):
        import hashlib
        if isinstance(key, str):
            key = key.encode('utf-8')
        return int(hashlib.md5(key).hexdigest(), 16) % (2**32)
    
    def setup_ring(self, nodes):
        """Set up ring with given nodes"""
        self.ring = {}
        for node in nodes:
            position = self._hash_value(node)
            self.ring[position] = node
        self.sorted_positions = sorted(self.ring.keys())
    
    def find_predecessor(self, position):
        """Find the predecessor position on the ring"""
        if not self.sorted_positions:
            return None
        
        # Find largest position < given position
        for i in range(len(self.sorted_positions) - 1, -1, -1):
            if self.sorted_positions[i] < position:
                return self.sorted_positions[i]
        
        # If no predecessor found, wrap around to last position
        return self.sorted_positions[-1]
    
    def find_successor(self, position):
        """Find the successor position on the ring"""
        if not self.sorted_positions:
            return None
        
        # Find smallest position > given position
        for pos in self.sorted_positions:
            if pos > position:
                return pos
        
        # If no successor found, wrap around to first position
        return self.sorted_positions[0]
    
    def analyze_impact_zone(self, nodes, operation, target_node):
        """Analyze the exact impact zone of a topology change"""
        
        print(f"Localized Impact Analysis: {operation} {target_node}")
        print("=" * 50)
        
        # Set up initial ring
        self.setup_ring(nodes)
        
        if operation == 'add':
            new_position = self._hash_value(target_node)
            predecessor_position = self.find_predecessor(new_position)
            
            # Impact zone: keys between predecessor and new node
            impact_start = predecessor_position if predecessor_position is not None else 0
            impact_end = new_position
            
            # Calculate impact zone size
            if impact_end >= impact_start:
                impact_size = impact_end - impact_start
            else:
                # Wrap-around case
                impact_size = (2**32 - impact_start) + impact_end
            
            impact_percentage = (impact_size / (2**32)) * 100
            
            print(f"Adding node at position: {new_position}")
            print(f"Predecessor position: {impact_start}")
            print(f"Impact zone: ({impact_start}, {impact_end}]")
            print(f"Impact zone size: {impact_size:,} ({impact_percentage:.4f}% of ring)")
            
            # Theoretical vs actual
            expected_percentage = 100 / (len(nodes) + 1)
            print(f"Expected impact: {expected_percentage:.2f}% (1/{len(nodes) + 1})")
            print(f"Actual impact: {impact_percentage:.4f}%")
            
        elif operation == 'remove':
            removed_position = self._hash_value(target_node)
            predecessor_position = self.find_predecessor(removed_position)
            successor_position = self.find_successor(removed_position)
            
            # Impact zone: keys between predecessor and removed node
            impact_start = predecessor_position if predecessor_position is not None else 0
            impact_end = removed_position
            
            if impact_end >= impact_start:
                impact_size = impact_end - impact_start
            else:
                impact_size = (2**32 - impact_start) + impact_end
            
            impact_percentage = (impact_size / (2**32)) * 100
            
            print(f"Removing node at position: {removed_position}")
            print(f"Predecessor position: {impact_start}")
            print(f"Successor position: {successor_position}")
            print(f"Impact zone: ({impact_start}, {impact_end}]")
            print(f"Impact zone size: {impact_size:,} ({impact_percentage:.4f}% of ring)")
            print(f"Keys will move to successor at: {successor_position}")
        
        return {
            'impact_size': impact_size,
            'impact_percentage': impact_percentage,
            'ring_size': 2**32
        }
    
    def demonstrate_localization_property(self):
        """Demonstrate that impact is truly localized"""
        
        print("\nLocalization Property Demonstration:")
        print("=" * 40)
        
        # Test with different ring sizes
        test_scenarios = [
            (['A', 'B', 'C'], 'D'),
            (['A', 'B', 'C', 'D', 'E'], 'F'),
            ([f'Node{i}' for i in range(10)], 'Node10'),
            ([f'Node{i}' for i in range(100)], 'Node100')
        ]
        
        for nodes, new_node in test_scenarios:
            print(f"\nScenario: {len(nodes)} → {len(nodes) + 1} nodes")
            result = self.analyze_impact_zone(nodes, 'add', new_node)
            
            # Verify localization
            theoretical_impact = 100 / (len(nodes) + 1)
            actual_impact = result['impact_percentage']
            localization_ratio = actual_impact / theoretical_impact
            
            print(f"Localization ratio: {localization_ratio:.3f} (closer to 1.0 is better)")
            
            if 0.5 <= localization_ratio <= 2.0:
                quality = "Good localization"
            elif 0.25 <= localization_ratio <= 4.0:
                quality = "Acceptable localization"
            else:
                quality = "Poor localization"
            
            print(f"Quality assessment: {quality}")

# Demonstrate localized impact
impact_analysis = LocalizedImpactAnalysis()
impact_analysis.demonstrate_localization_property()
```

### Real-World Impact Scenarios

```python
class RealWorldImpactScenarios:
    def simulate_production_scenarios(self):
        """Simulate real-world redistribution scenarios"""
        
        print("\nReal-World Redistribution Scenarios:")
        print("=" * 40)
        
        scenarios = [
            {
                'name': 'E-commerce Peak Traffic Scaling',
                'initial_nodes': 50,
                'keys': 10000000,  # 10M products/sessions
                'key_size_kb': 2,   # 2KB average
                'network_speed_gbps': 10,
                'description': 'Adding capacity during Black Friday'
            },
            {
                'name': 'Social Media Cache Expansion', 
                'initial_nodes': 200,
                'keys': 100000000,  # 100M cache entries
                'key_size_kb': 1,    # 1KB average
                'network_speed_gbps': 40,
                'description': 'Expanding global cache infrastructure'
            },
            {
                'name': 'Gaming Session Storage',
                'initial_nodes': 20,
                'keys': 1000000,   # 1M active sessions
                'key_size_kb': 5,   # 5KB session data
                'network_speed_gbps': 25,
                'description': 'Adding server during launch event'
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{scenario['name']}:")
            print(f"  {scenario['description']}")
            
            # Calculate redistribution requirements
            initial_nodes = scenario['initial_nodes']
            total_keys = scenario['keys']
            key_size_kb = scenario['key_size_kb']
            network_speed_gbps = scenario['network_speed_gbps']
            
            # Consistent hashing movement
            keys_to_move = total_keys / (initial_nodes + 1)
            data_to_move_gb = (keys_to_move * key_size_kb) / (1024 * 1024)
            
            # Network transfer time
            network_speed_gbps_effective = network_speed_gbps * 0.7  # 70% efficiency
            transfer_time_minutes = (data_to_move_gb / network_speed_gbps_effective) / 60
            
            print(f"  Initial configuration: {initial_nodes} nodes, {total_keys:,} keys")
            print(f"  Keys to redistribute: {keys_to_move:,.0f} ({keys_to_move/total_keys*100:.2f}%)")
            print(f"  Data volume: {data_to_move_gb:.1f} GB")
            print(f"  Transfer time: {transfer_time_minutes:.1f} minutes")
            
            # Service impact assessment
            if transfer_time_minutes < 5:
                impact = "Minimal impact - can be done online"
            elif transfer_time_minutes < 15:
                impact = "Low impact - brief performance degradation"
            elif transfer_time_minutes < 60:
                impact = "Moderate impact - maintenance window recommended"
            else:
                impact = "High impact - extended maintenance required"
            
            print(f"  Service impact: {impact}")
            
            # Compare with traditional methods
            traditional_movement_percentage = 80  # 80% typical for modulo hashing
            traditional_data_gb = (total_keys * traditional_movement_percentage / 100 * key_size_kb) / (1024 * 1024)
            traditional_time_minutes = (traditional_data_gb / network_speed_gbps_effective) / 60
            
            improvement_factor = traditional_time_minutes / transfer_time_minutes if transfer_time_minutes > 0 else float('inf')
            
            print(f"  Traditional method would require:")
            print(f"    Data movement: {traditional_data_gb:.1f} GB")
            print(f"    Transfer time: {traditional_time_minutes:.1f} minutes")
            print(f"  Improvement: {improvement_factor:.1f}x faster with consistent hashing")

# Simulate real-world scenarios
real_world = RealWorldImpactScenarios()
real_world.simulate_production_scenarios()
```

## Incremental Updates

One of the most operationally valuable aspects of consistent hashing is its support for incremental updates, allowing systems to gradually redistribute data rather than requiring atomic bulk operations.

### Incremental Update Strategies

```python
class IncrementalUpdateDemo:
    def __init__(self):
        self.ring = {}
        self.sorted_positions = []
        self.migration_state = {}  # Track ongoing migrations
    
    def _hash_value(self, key):
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
    
    def get_affected_keys_for_new_node(self, new_node, all_keys):
        """Identify which keys need to move to a new node"""
        new_position = self._hash_value(new_node)
        
        # Find predecessor
        predecessor_position = None
        for pos in reversed(self.sorted_positions):
            if pos < new_position:
                predecessor_position = pos
                break
        
        if predecessor_position is None:
            predecessor_position = self.sorted_positions[-1] if self.sorted_positions else 0
        
        # Find keys that should move
        affected_keys = []
        for key in all_keys:
            key_position = self._hash_value(key)
            
            # Check if key is in the range that should move to new node
            if predecessor_position < new_position:
                # Normal case: check if key is between predecessor and new node
                if predecessor_position < key_position <= new_position:
                    affected_keys.append(key)
            else:
                # Wrap-around case
                if key_position > predecessor_position or key_position <= new_position:
                    affected_keys.append(key)
        
        return affected_keys
    
    def simulate_incremental_migration(self, initial_nodes, new_node, total_keys, batch_size=1000):
        """Simulate incremental migration process"""
        
        print("Incremental Migration Simulation:")
        print("=" * 35)
        
        # Set up initial ring
        for node in initial_nodes:
            self.add_node(node)
        
        # Generate test keys
        all_keys = [f"key_{i}" for i in range(total_keys)]
        
        # Add new node and identify affected keys
        self.add_node(new_node)
        affected_keys = self.get_affected_keys_for_new_node(new_node, all_keys)
        
        print(f"Migration plan:")
        print(f"  Total keys: {total_keys:,}")
        print(f"  Keys to migrate: {len(affected_keys):,} ({len(affected_keys)/total_keys*100:.2f}%)")
        print(f"  Batch size: {batch_size:,}")
        print(f"  Estimated batches: {math.ceil(len(affected_keys) / batch_size)}")
        
        # Simulate batch migration
        migrated = 0
        batch_number = 0
        migration_timeline = []
        
        while migrated < len(affected_keys):
            batch_number += 1
            batch_end = min(migrated + batch_size, len(affected_keys))
            batch_keys = affected_keys[migrated:batch_end]
            
            # Simulate migration time (assuming 1ms per key + network overhead)
            migration_time_ms = len(batch_keys) * 1 + 100  # 100ms overhead per batch
            
            migration_timeline.append({
                'batch': batch_number,
                'keys_in_batch': len(batch_keys),
                'total_migrated': batch_end,
                'completion_percentage': (batch_end / len(affected_keys)) * 100,
                'time_ms': migration_time_ms
            })
            
            migrated = batch_end
        
        # Show migration timeline
        print(f"\nMigration timeline:")
        total_time = 0
        for milestone in migration_timeline[::max(1, len(migration_timeline)//5)]:  # Show 5 key milestones
            total_time += milestone['time_ms']
            print(f"  Batch {milestone['batch']}: {milestone['total_migrated']:,} keys migrated "
                  f"({milestone['completion_percentage']:.1f}%) - {total_time/1000:.1f}s elapsed")
        
        # Calculate total migration time
        total_migration_time = sum(m['time_ms'] for m in migration_timeline) / 1000
        
        print(f"\nMigration summary:")
        print(f"  Total migration time: {total_migration_time:.1f} seconds")
        print(f"  Migration throughput: {len(affected_keys)/total_migration_time:.0f} keys/second")
        print(f"  Service availability: Maintained throughout migration")
        print(f"  Rollback capability: Available at any batch boundary")
        
        return migration_timeline
    
    def demonstrate_migration_strategies(self):
        """Demonstrate different incremental migration strategies"""
        
        print("\nIncremental Migration Strategies:")
        print("=" * 40)
        
        strategies = [
            {
                'name': 'Conservative (Small Batches)',
                'batch_size': 100,
                'description': 'Minimal service impact, longer total time'
            },
            {
                'name': 'Balanced (Medium Batches)', 
                'batch_size': 1000,
                'description': 'Balance between speed and stability'
            },
            {
                'name': 'Aggressive (Large Batches)',
                'batch_size': 10000,
                'description': 'Faster completion, higher service impact'
            }
        ]
        
        # Test scenario
        initial_nodes = ['node_0', 'node_1', 'node_2', 'node_3']
        new_node = 'node_4'
        total_keys = 100000
        
        for strategy in strategies:
            print(f"\n{strategy['name']} Strategy:")
            print(f"  {strategy['description']}")
            
            # Simulate migration
            demo = IncrementalUpdateDemo()
            timeline = demo.simulate_incremental_migration(
                initial_nodes, new_node, total_keys, strategy['batch_size']
            )
            
            # Calculate metrics
            total_batches = len(timeline)
            total_time = sum(m['time_ms'] for m in timeline) / 1000
            
            print(f"  Results:")
            print(f"    Total batches: {total_batches}")
            print(f"    Total time: {total_time:.1f} seconds")
            print(f"    Average batch time: {total_time/total_batches:.2f} seconds")

# Demonstrate incremental updates
incremental_demo = IncrementalUpdateDemo()
incremental_demo.demonstrate_migration_strategies()
```

### Live Migration Patterns

```python
class LiveMigrationPatterns:
    def demonstrate_live_migration_benefits(self):
        """Show benefits of live migration with consistent hashing"""
        
        print("\nLive Migration Benefits:")
        print("=" * 25)
        
        print("1. ZERO-DOWNTIME SCALING:")
        print("   • New node joins ring and starts receiving new assignments")
        print("   • Existing data gradually migrates in background")
        print("   • Service remains available throughout process")
        
        print("\n2. GRADUAL LOAD TRANSFER:")
        print("   • Load shifts incrementally from old nodes to new node")
        print("   • Performance impact is distributed over time")
        print("   • No sudden spikes in resource usage")
        
        print("\n3. ROLLBACK CAPABILITY:")
        print("   • Migration can be paused or reversed at any point")
        print("   • Failed migrations don't leave system in inconsistent state")
        print("   • Easy to abort if issues are detected")
        
        print("\n4. MONITORING AND CONTROL:")
        print("   • Migration progress can be monitored in real-time")
        print("   • Rate limiting prevents overwhelming source/target nodes")
        print("   • Automated health checks can pause migration if needed")
        
        # Quantitative example
        print("\n5. QUANTITATIVE EXAMPLE:")
        print("   Scenario: Adding 1 node to 10-node cluster with 1M keys")
        print("   • Keys to migrate: ~100,000 (10%)")
        print("   • Batch size: 1,000 keys")
        print("   • Migration batches: 100")
        print("   • Time per batch: 2 seconds")
        print("   • Total migration time: 200 seconds (3.3 minutes)")
        print("   • Service downtime: 0 seconds")
        print("   • Peak performance impact: <5%")
    
    def compare_migration_approaches(self):
        """Compare different migration approaches"""
        
        print("\nMigration Approach Comparison:")
        print("=" * 35)
        
        approaches = [
            {
                'name': 'Atomic Migration',
                'downtime': '30-120 minutes',
                'complexity': 'Low',
                'risk': 'High',
                'rollback': 'Difficult'
            },
            {
                'name': 'Blue-Green Deployment',
                'downtime': '5-15 minutes', 
                'complexity': 'High',
                'risk': 'Medium',
                'rollback': 'Moderate'
            },
            {
                'name': 'Consistent Hashing Live Migration',
                'downtime': '0 minutes',
                'complexity': 'Medium',
                'risk': 'Low', 
                'rollback': 'Easy'
            }
        ]
        
        for approach in approaches:
            print(f"\n{approach['name']}:")
            for metric, value in approach.items():
                if metric != 'name':
                    print(f"  {metric.capitalize()}: {value}")

# Demonstrate live migration patterns
live_migration = LiveMigrationPatterns()
live_migration.demonstrate_live_migration_benefits()
live_migration.compare_migration_approaches()
```

## Performance Impact Analysis

Understanding the performance implications of redistribution helps in planning and optimizing migration operations.

```python
class PerformanceImpactAnalysis:
    def analyze_redistribution_performance(self):
        """Analyze performance impact of redistribution operations"""
        
        print("Redistribution Performance Impact Analysis:")
        print("=" * 45)
        
        # Performance scenarios
        scenarios = [
            {
                'name': 'Low-Impact Migration',
                'keys_per_second': 1000,
                'network_utilization': 10,  # %
                'cpu_overhead': 5,  # %
                'description': 'Conservative migration during low traffic'
            },
            {
                'name': 'Standard Migration',
                'keys_per_second': 5000,
                'network_utilization': 25,  # %
                'cpu_overhead': 15,  # %
                'description': 'Balanced migration during normal traffic'
            },
            {
                'name': 'Aggressive Migration',
                'keys_per_second': 20000,
                'network_utilization': 60,  # %
                'cpu_overhead': 35,  # %
                'description': 'Fast migration during maintenance window'
            }
        ]
        
        total_keys_to_migrate = 100000  # Example: 100K keys need migration
        
        for scenario in scenarios:
            print(f"\n{scenario['name']}:")
            print(f"  {scenario['description']}")
            
            migration_time_seconds = total_keys_to_migrate / scenario['keys_per_second']
            migration_time_minutes = migration_time_seconds / 60
            
            print(f"  Migration rate: {scenario['keys_per_second']:,} keys/second")
            print(f"  Total time: {migration_time_minutes:.1f} minutes")
            print(f"  Network utilization: {scenario['network_utilization']}%")
            print(f"  CPU overhead: {scenario['cpu_overhead']}%")
            
            # Service impact assessment
            if scenario['cpu_overhead'] < 10:
                impact = "Negligible impact on user requests"
            elif scenario['cpu_overhead'] < 25:
                impact = "Minor impact, <5% latency increase"
            elif scenario['cpu_overhead'] < 40:
                impact = "Moderate impact, 5-15% latency increase"
            else:
                impact = "Significant impact, >15% latency increase"
            
            print(f"  Service impact: {impact}")
    
    def demonstrate_efficiency_gains(self):
        """Demonstrate overall efficiency gains of consistent hashing"""
        
        print("\nOverall Efficiency Gains:")
        print("=" * 30)
        
        # Compare total cost of ownership
        system_sizes = [
            (100, 1000000, "Small-Medium System"),
            (1000, 100000000, "Large System"),  
            (10000, 10000000000, "Internet Scale")
        ]
        
        for nodes, keys, description in system_sizes:
            print(f"\n{description}: {nodes:,} nodes, {keys:,} keys")
            
            # Consistent hashing efficiency
            ch_keys_moved = keys / (nodes + 1)  # Adding 1 node
            ch_efficiency = ch_keys_moved / keys * 100
            
            # Traditional method efficiency
            traditional_keys_moved = keys * 0.8  # 80% typically move
            traditional_efficiency = traditional_keys_moved / keys * 100
            
            # Calculate savings
            data_savings_ratio = traditional_keys_moved / ch_keys_moved
            time_savings_ratio = traditional_keys_moved / ch_keys_moved  # Proportional to data
            
            print(f"  Consistent hashing: {ch_efficiency:.3f}% of keys move")
            print(f"  Traditional method: {traditional_efficiency:.1f}% of keys move")
            print(f"  Data movement savings: {data_savings_ratio:.0f}x less")
            print(f"  Time savings: {time_savings_ratio:.0f}x faster")
            
            # Operational impact
            if nodes <= 100:
                operational_benefit = "Enables automated scaling"
            elif nodes <= 1000:
                operational_benefit = "Eliminates manual intervention"
            else:
                operational_benefit = "Makes large-scale operation feasible"
            
            print(f"  Operational benefit: {operational_benefit}")

# Demonstrate performance impact
performance_analysis = PerformanceImpactAnalysis()
performance_analysis.analyze_redistribution_performance()
performance_analysis.demonstrate_efficiency_gains()
```

## Summary

The redistribution efficiency of consistent hashing provides three key advantages:

1. **Optimal Movement**: Theoretical minimum data movement (K/n keys) with mathematical guarantees
2. **Localized Impact**: Changes affect only specific, predictable regions of the hash ring
3. **Incremental Updates**: Support for gradual, zero-downtime migrations with rollback capability

These properties combine to make consistent hashing uniquely suitable for production systems that require:
- Frequent scaling operations
- High availability requirements  
- Predictable operational costs
- Automated infrastructure management

The efficiency gains become more pronounced at larger scales, making consistent hashing essential for internet-scale distributed systems where traditional approaches become operationally infeasible.​​​​​​​​​​​​​​​​
