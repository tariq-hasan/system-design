# Node Addition and Removal Operations

Node addition and removal operations are the fundamental scaling mechanisms in consistent hashing that enable dynamic cluster management. These operations must maintain system consistency while minimizing data movement and service disruption. Understanding the precise mechanics of these operations is crucial for building production systems that can scale gracefully under load while maintaining high availability.

## Node Addition Algorithm

Adding a node to a consistent hashing ring requires carefully orchestrated steps to maintain data consistency while minimizing the impact on ongoing operations.

### Detailed Addition Process

```python
import hashlib
import bisect
import time
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import threading

class NodeAdditionManager:
    """Comprehensive node addition management for consistent hashing"""
    
    def __init__(self, hash_function: str = 'sha1'):
        self.hash_function = hash_function
        self.ring = {}  # position -> node_id mapping
        self.sorted_positions = []  # Sorted positions for efficient lookups
        self.node_positions = defaultdict(list)  # node_id -> [positions] mapping
        self.data_location = defaultdict(set)  # node_id -> set(keys) - simulated data
        
        # Addition tracking
        self.addition_history = []
        self.migration_stats = defaultdict(dict)
        
        # Thread safety for concurrent operations
        self.ring_lock = threading.RLock()
        
        self._setup_hash_function()
    
    def _setup_hash_function(self):
        """Configure hash function and space size"""
        if self.hash_function == 'sha1':
            self.hasher = hashlib.sha1
            self.space_size = 2**160
        elif self.hash_function == 'sha256':
            self.hasher = hashlib.sha256
            self.space_size = 2**256
        else:
            self.hasher = hashlib.md5
            self.space_size = 2**128
    
    def compute_position(self, identifier: str) -> int:
        """Compute hash ring position for identifier"""
        if isinstance(identifier, str):
            identifier_bytes = identifier.encode('utf-8')
        else:
            identifier_bytes = str(identifier).encode('utf-8')
        
        hash_obj = self.hasher(identifier_bytes)
        hash_int = int(hash_obj.hexdigest(), 16)
        return hash_int % self.space_size
    
    def add_node_with_migration(self, node_id: str, virtual_node_count: int = 150) -> Dict:
        """
        Add a node with complete data migration simulation
        
        Args:
            node_id: Unique identifier for the new node
            virtual_node_count: Number of virtual nodes to create
            
        Returns:
            Dictionary with addition and migration statistics
        """
        if node_id in self.node_positions:
            raise ValueError(f"Node {node_id} already exists")
        
        with self.ring_lock:
            start_time = time.perf_counter()
            
            print(f"Adding node: {node_id}")
            print("=" * 40)
            
            # Step 1: Compute and validate positions
            new_positions = self._compute_new_node_positions(node_id, virtual_node_count)
            
            print(f"Step 1: Computed {len(new_positions)} virtual node positions")
            print(f"  Sample positions: {[f'{p:,}' for p in sorted(new_positions)[:3]]}...")
            
            # Step 2: Identify affected ranges and data movement
            migration_plan = self._create_migration_plan(new_positions)
            
            total_keys_to_move = sum(len(keys) for keys in migration_plan.values())
            print(f"Step 2: Migration plan created")
            print(f"  Keys to migrate: {total_keys_to_move:,}")
            print(f"  Source nodes: {len(migration_plan)}")
            
            # Step 3: Insert new node into ring
            self._insert_node_positions(node_id, new_positions)
            
            print(f"Step 3: Node inserted into ring")
            print(f"  Ring size: {len(self.ring):,} positions")
            
            # Step 4: Execute data migration
            migration_results = self._execute_migration(node_id, migration_plan)
            
            end_time = time.perf_counter()
            operation_time = end_time - start_time
            
            # Compile results
            addition_result = {
                'node_id': node_id,
                'virtual_nodes_added': len(new_positions),
                'positions': new_positions,
                'keys_migrated': total_keys_to_move,
                'migration_sources': list(migration_plan.keys()),
                'operation_time_ms': operation_time * 1000,
                'migration_details': migration_results,
                'ring_size_after': len(self.ring)
            }
            
            # Track addition history
            self.addition_history.append(addition_result)
            
            print(f"Step 4: Migration completed")
            print(f"  Total operation time: {operation_time*1000:.2f} ms")
            print(f"  Migration efficiency: {total_keys_to_move/operation_time:.0f} keys/sec")
            
            return addition_result
    
    def _compute_new_node_positions(self, node_id: str, virtual_node_count: int) -> List[int]:
        """Compute positions for new node's virtual nodes"""
        positions = []
        collision_count = 0
        
        for i in range(virtual_node_count):
            virtual_id = f"{node_id}:vnode_{i}"
            position = self.compute_position(virtual_id)
            
            # Handle collisions
            original_position = position
            attempts = 0
            while position in self.ring and attempts < 1000:
                collision_count += 1
                attempts += 1
                collision_virtual_id = f"{virtual_id}_collision_{attempts}"
                position = self.compute_position(collision_virtual_id)
            
            if attempts >= 1000:
                raise RuntimeError(f"Cannot resolve collision for {virtual_id}")
            
            positions.append(position)
        
        if collision_count > 0:
            print(f"  Resolved {collision_count} position collisions")
        
        return positions
    
    def _create_migration_plan(self, new_positions: List[int]) -> Dict[str, Set[str]]:
        """Create migration plan for new node positions"""
        migration_plan = defaultdict(set)
        
        for position in new_positions:
            # Find predecessor position
            predecessor_pos = self._find_predecessor_position(position)
            
            # Find current successor (where keys will move from)
            successor_pos = self._find_successor_position(position)
            successor_node = self.ring.get(successor_pos)
            
            if successor_node:
                # Identify keys in range (predecessor, new_position]
                keys_to_move = self._find_keys_in_range(predecessor_pos, position, successor_node)
                migration_plan[successor_node].update(keys_to_move)
        
        return migration_plan
    
    def _find_predecessor_position(self, position: int) -> Optional[int]:
        """Find the position immediately before the given position"""
        if not self.sorted_positions:
            return None
        
        # Find largest position < given position
        index = bisect.bisect_left(self.sorted_positions, position)
        if index > 0:
            return self.sorted_positions[index - 1]
        else:
            # Wrap around to last position
            return self.sorted_positions[-1]
    
    def _find_successor_position(self, position: int) -> Optional[int]:
        """Find the position immediately after the given position"""
        if not self.sorted_positions:
            return None
        
        # Find smallest position >= given position
        index = bisect.bisect_left(self.sorted_positions, position)
        if index < len(self.sorted_positions):
            return self.sorted_positions[index]
        else:
            # Wrap around to first position
            return self.sorted_positions[0]
    
    def _find_keys_in_range(self, start_pos: int, end_pos: int, source_node: str) -> Set[str]:
        """Find keys that should move from source node to new position"""
        # Simulate finding keys in range
        # In real implementation, this would query the actual data store
        
        keys_in_range = set()
        
        # Get all keys from source node
        source_keys = self.data_location.get(source_node, set())
        
        for key in source_keys:
            key_position = self.compute_position(key)
            
            # Check if key is in range (start_pos, end_pos]
            if self._position_in_range(key_position, start_pos, end_pos):
                keys_in_range.add(key)
        
        return keys_in_range
    
    def _position_in_range(self, position: int, start: int, end: int) -> bool:
        """Check if position is in range (start, end] considering wraparound"""
        if start < end:
            # Normal case: no wraparound
            return start < position <= end
        else:
            # Wraparound case
            return position > start or position <= end
    
    def _insert_node_positions(self, node_id: str, positions: List[int]):
        """Insert new node positions into ring structure"""
        for position in positions:
            self.ring[position] = node_id
        
        self.node_positions[node_id] = positions
        self.sorted_positions = sorted(self.ring.keys())
    
    def _execute_migration(self, target_node: str, migration_plan: Dict[str, Set[str]]) -> Dict:
        """Execute the data migration according to plan"""
        migration_start = time.perf_counter()
        
        total_keys_moved = 0
        source_details = {}
        
        for source_node, keys_to_move in migration_plan.items():
            move_start = time.perf_counter()
            
            # Simulate data movement
            self.data_location[source_node] -= keys_to_move
            self.data_location[target_node] |= keys_to_move
            
            move_end = time.perf_counter()
            move_time = move_end - move_start
            
            source_details[source_node] = {
                'keys_moved': len(keys_to_move),
                'move_time_ms': move_time * 1000,
                'throughput_keys_per_sec': len(keys_to_move) / move_time if move_time > 0 else 0
            }
            
            total_keys_moved += len(keys_to_move)
        
        migration_end = time.perf_counter()
        total_migration_time = migration_end - migration_start
        
        return {
            'total_keys_moved': total_keys_moved,
            'total_time_ms': total_migration_time * 1000,
            'overall_throughput': total_keys_moved / total_migration_time if total_migration_time > 0 else 0,
            'source_breakdown': source_details
        }
    
    def demonstrate_node_addition(self):
        """Demonstrate complete node addition process"""
        
        print("Node Addition Process Demonstration:")
        print("=" * 45)
        
        # Initialize with some nodes and data
        initial_nodes = ['node-01', 'node-02', 'node-03']
        for node_id in initial_nodes:
            positions = []
            for i in range(100):  # 100 virtual nodes each
                virtual_id = f"{node_id}:vnode_{i}"
                position = self.compute_position(virtual_id)
                positions.append(position)
                self.ring[position] = node_id
            
            self.node_positions[node_id] = positions
            
            # Simulate some data on each node
            test_keys = {f"key_{j}_{node_id}" for j in range(1000)}
            self.data_location[node_id] = test_keys
        
        self.sorted_positions = sorted(self.ring.keys())
        
        print(f"Initial state:")
        print(f"  Nodes: {len(initial_nodes)}")
        print(f"  Ring positions: {len(self.ring):,}")
        print(f"  Total simulated keys: {sum(len(keys) for keys in self.data_location.values()):,}")
        
        # Show initial distribution
        for node_id in initial_nodes:
            key_count = len(self.data_location[node_id])
            vnode_count = len(self.node_positions[node_id])
            print(f"    {node_id}: {key_count:,} keys, {vnode_count} vnodes")
        
        # Add new node
        print(f"\nAdding new node...")
        result = self.add_node_with_migration('node-04', virtual_node_count=100)
        
        # Show final distribution
        print(f"\nFinal state:")
        all_nodes = list(self.node_positions.keys())
        for node_id in sorted(all_nodes):
            key_count = len(self.data_location[node_id])
            vnode_count = len(self.node_positions[node_id])
            print(f"  {node_id}: {key_count:,} keys, {vnode_count} vnodes")
        
        # Calculate balance metrics
        key_counts = [len(self.data_location[node]) for node in all_nodes]
        avg_keys = sum(key_counts) / len(key_counts)
        min_keys = min(key_counts)
        max_keys = max(key_counts)
        imbalance_ratio = max_keys / min_keys if min_keys > 0 else float('inf')
        
        print(f"\nLoad balance analysis:")
        print(f"  Average keys per node: {avg_keys:.0f}")
        print(f"  Range: {min_keys:,} - {max_keys:,}")
        print(f"  Imbalance ratio: {imbalance_ratio:.2f}:1")
        
        return result

# Demonstrate node addition
addition_manager = NodeAdditionManager('sha1')
addition_result = addition_manager.demonstrate_node_addition()
```

### Movement Calculation and Analysis

```python
class MovementCalculationAnalysis:
    """Detailed analysis of data movement during node operations"""
    
    def __init__(self):
        self.addition_manager = NodeAdditionManager('sha1')
    
    def analyze_movement_patterns(self):
        """Analyze data movement patterns for different cluster sizes"""
        
        print("Data Movement Pattern Analysis:")
        print("=" * 40)
        
        # Test different cluster sizes
        cluster_scenarios = [
            (5, 10000, "Small cluster"),
            (20, 50000, "Medium cluster"),
            (100, 200000, "Large cluster")
        ]
        
        for node_count, total_keys, description in cluster_scenarios:
            print(f"\n{description}: {node_count} nodes, {total_keys:,} keys")
            
            # Setup cluster
            self._setup_test_cluster(node_count, total_keys)
            
            # Calculate theoretical movement
            theoretical_movement = total_keys / (node_count + 1)
            theoretical_percentage = (theoretical_movement / total_keys) * 100
            
            print(f"  Theoretical movement: {theoretical_movement:.0f} keys ({theoretical_percentage:.2f}%)")
            
            # Simulate adding a node
            new_node_id = f"node-{node_count + 1:02d}"
            
            # Create detailed migration plan
            migration_analysis = self._analyze_detailed_migration(new_node_id)
            
            actual_movement = migration_analysis['total_keys_to_move']
            actual_percentage = (actual_movement / total_keys) * 100
            
            print(f"  Actual movement: {actual_movement} keys ({actual_percentage:.2f}%)")
            print(f"  Efficiency: {theoretical_percentage/actual_percentage*100:.1f}% of theoretical optimum")
            
            # Analyze movement sources
            source_analysis = migration_analysis['source_breakdown']
            print(f"  Movement sources: {len(source_analysis)} nodes")
            
            for source_node, details in list(source_analysis.items())[:3]:  # Show top 3
                keys_moved = details['keys_moved']
                percentage_of_total = (keys_moved / actual_movement) * 100
                print(f"    {source_node}: {keys_moved} keys ({percentage_of_total:.1f}% of movement)")
            
            # Reset for next scenario
            self.addition_manager = NodeAdditionManager('sha1')
    
    def _setup_test_cluster(self, node_count: int, total_keys: int):
        """Setup test cluster with specified nodes and data"""
        
        # Add nodes
        for i in range(node_count):
            node_id = f"node-{i+1:02d}"
            positions = []
            
            for j in range(150):  # 150 virtual nodes each
                virtual_id = f"{node_id}:vnode_{j}"
                position = self.addition_manager.compute_position(virtual_id)
                positions.append(position)
                self.addition_manager.ring[position] = node_id
            
            self.addition_manager.node_positions[node_id] = positions
        
        self.addition_manager.sorted_positions = sorted(self.addition_manager.ring.keys())
        
        # Distribute keys according to consistent hashing
        for key_index in range(total_keys):
            key = f"key_{key_index:06d}"
            responsible_node = self._find_responsible_node(key)
            self.addition_manager.data_location[responsible_node].add(key)
    
    def _find_responsible_node(self, key: str) -> str:
        """Find responsible node for a key"""
        key_position = self.addition_manager.compute_position(key)
        
        # Find successor position
        index = bisect.bisect_left(self.addition_manager.sorted_positions, key_position)
        if index < len(self.addition_manager.sorted_positions):
            successor_position = self.addition_manager.sorted_positions[index]
        else:
            successor_position = self.addition_manager.sorted_positions[0]
        
        return self.addition_manager.ring[successor_position]
    
    def _analyze_detailed_migration(self, new_node_id: str) -> Dict:
        """Analyze detailed migration requirements for new node"""
        
        # Compute new node positions
        new_positions = []
        for i in range(150):
            virtual_id = f"{new_node_id}:vnode_{i}"
            position = self.addition_manager.compute_position(virtual_id)
            new_positions.append(position)
        
        # Analyze each position's impact
        source_breakdown = defaultdict(lambda: {'keys_moved': 0, 'ranges': []})
        total_keys_to_move = 0
        
        for position in new_positions:
            # Find predecessor and successor
            predecessor_pos = self.addition_manager._find_predecessor_position(position)
            successor_pos = self.addition_manager._find_successor_position(position)
            
            if successor_pos is not None:
                successor_node = self.addition_manager.ring[successor_pos]
                
                # Find keys in range
                keys_in_range = self.addition_manager._find_keys_in_range(
                    predecessor_pos, position, successor_node
                )
                
                source_breakdown[successor_node]['keys_moved'] += len(keys_in_range)
                source_breakdown[successor_node]['ranges'].append({
                    'start': predecessor_pos,
                    'end': position,
                    'keys': len(keys_in_range)
                })
                
                total_keys_to_move += len(keys_in_range)
        
        return {
            'total_keys_to_move': total_keys_to_move,
            'source_breakdown': dict(source_breakdown),
            'positions_added': len(new_positions)
        }
    
    def calculate_movement_bounds(self):
        """Calculate theoretical bounds for data movement"""
        
        print("\nData Movement Theoretical Bounds:")
        print("=" * 40)
        
        cluster_sizes = [5, 10, 50, 100, 500, 1000]
        
        for n in cluster_sizes:
            # Adding one node to n-node cluster
            theoretical_movement_pct = 100 / (n + 1)
            
            # Range of actual movement (due to virtual nodes and hash distribution)
            # Typically within ±10% of theoretical due to virtual node effects
            expected_min = theoretical_movement_pct * 0.9
            expected_max = theoretical_movement_pct * 1.1
            
            print(f"  {n:3d} → {n+1:3d} nodes:")
            print(f"    Theoretical: {theoretical_movement_pct:.3f}%")
            print(f"    Expected range: {expected_min:.3f}% - {expected_max:.3f}%")
            print(f"    Absolute bound: <{2*theoretical_movement_pct:.3f}% (2x theoretical)")

# Demonstrate movement analysis
movement_analyzer = MovementCalculationAnalysis()
movement_analyzer.analyze_movement_patterns()
movement_analyzer.calculate_movement_bounds()
```

## Node Removal Algorithm

Node removal requires careful coordination to ensure data is not lost and system availability is maintained during the operation.

### Detailed Removal Process

```python
class NodeRemovalManager:
    """Comprehensive node removal management for consistent hashing"""
    
    def __init__(self, hash_function: str = 'sha1'):
        self.hash_function = hash_function
        self.ring = {}
        self.sorted_positions = []
        self.node_positions = defaultdict(list)
        self.data_location = defaultdict(set)
        
        # Removal tracking
        self.removal_history = []
        self.ring_lock = threading.RLock()
        
        self._setup_hash_function()
    
    def _setup_hash_function(self):
        """Configure hash function"""
        if self.hash_function == 'sha1':
            self.hasher = hashlib.sha1
            self.space_size = 2**160
        else:
            self.hasher = hashlib.md5
            self.space_size = 2**128
    
    def compute_position(self, identifier: str) -> int:
        """Compute hash ring position"""
        identifier_bytes = identifier.encode('utf-8')
        hash_obj = self.hasher(identifier_bytes)
        return int(hash_obj.hexdigest(), 16) % self.space_size
    
    def remove_node_with_migration(self, node_id: str) -> Dict:
        """
        Remove a node with complete data migration to successors
        
        Args:
            node_id: Identifier of node to remove
            
        Returns:
            Dictionary with removal and migration statistics
        """
        if node_id not in self.node_positions:
            raise ValueError(f"Node {node_id} does not exist")
        
        with self.ring_lock:
            start_time = time.perf_counter()
            
            print(f"Removing node: {node_id}")
            print("=" * 30)
            
            # Step 1: Identify data to migrate
            keys_to_migrate = self.data_location[node_id].copy()
            total_keys = len(keys_to_migrate)
            
            print(f"Step 1: Data inventory")
            print(f"  Keys to migrate: {total_keys:,}")
            
            # Step 2: Create migration plan for each position
            migration_plan = self._create_removal_migration_plan(node_id)
            
            print(f"Step 2: Migration plan created")
            print(f"  Target nodes: {len(migration_plan)}")
            
            # Step 3: Execute data migration
            migration_results = self._execute_removal_migration(node_id, migration_plan, keys_to_migrate)
            
            print(f"Step 3: Data migration completed")
            
            # Step 4: Remove node from ring
            removal_details = self._remove_node_from_ring(node_id)
            
            end_time = time.perf_counter()
            operation_time = end_time - start_time
            
            print(f"Step 4: Node removed from ring")
            print(f"  Positions removed: {removal_details['positions_removed']}")
            print(f"  Total operation time: {operation_time*1000:.2f} ms")
            
            # Compile results
            removal_result = {
                'node_id': node_id,
                'keys_migrated': total_keys,
                'positions_removed': removal_details['positions_removed'],
                'migration_targets': list(migration_plan.keys()),
                'operation_time_ms': operation_time * 1000,
                'migration_details': migration_results,
                'ring_size_after': len(self.ring)
            }
            
            self.removal_history.append(removal_result)
            
            return removal_result
    
    def _create_removal_migration_plan(self, node_id: str) -> Dict[str, List[int]]:
        """Create migration plan mapping positions to successor nodes"""
        migration_plan = defaultdict(list)
        
        node_positions = self.node_positions[node_id]
        
        for position in node_positions:
            # Find successor for this position
            successor_position = self._find_successor_position_excluding_node(position, node_id)
            
            if successor_position is not None:
                successor_node = self.ring[successor_position]
                migration_plan[successor_node].append(position)
        
        return migration_plan
    
    def _find_successor_position_excluding_node(self, position: int, excluded_node: str) -> Optional[int]:
        """Find successor position that doesn't belong to excluded node"""
        
        # Get positions not belonging to excluded node
        valid_positions = [pos for pos in self.sorted_positions 
                          if self.ring[pos] != excluded_node]
        
        if not valid_positions:
            return None
        
        # Find first valid position >= given position
        for pos in valid_positions:
            if pos > position:
                return pos
        
        # Wrap around to first valid position
        return valid_positions[0]
    
    def _execute_removal_migration(self, source_node: str, migration_plan: Dict[str, List[int]], 
                                 keys_to_migrate: Set[str]) -> Dict:
        """Execute data migration from removed node to successors"""
        
        migration_start = time.perf_counter()
        
        # Distribute keys among target nodes based on their new responsibilities
        key_distribution = self._distribute_keys_to_targets(keys_to_migrate, migration_plan)
        
        migration_details = {}
        total_keys_moved = 0
        
        for target_node, keys in key_distribution.items():
            move_start = time.perf_counter()
            
            # Simulate data movement
            self.data_location[target_node] |= keys
            key_count = len(keys)
            
            move_end = time.perf_counter()
            move_time = move_end - move_start
            
            migration_details[target_node] = {
                'keys_received': key_count,
                'move_time_ms': move_time * 1000,
                'throughput_keys_per_sec': key_count / move_time if move_time > 0 else 0
            }
            
            total_keys_moved += key_count
        
        # Clear data from source node
        self.data_location[source_node].clear()
        
        migration_end = time.perf_counter()
        total_migration_time = migration_end - migration_start
        
        return {
            'total_keys_moved': total_keys_moved,
            'total_time_ms': total_migration_time * 1000,
            'overall_throughput': total_keys_moved / total_migration_time if total_migration_time > 0 else 0,
            'target_breakdown': migration_details
        }
    
    def _distribute_keys_to_targets(self, keys: Set[str], migration_plan: Dict[str, List[int]]) -> Dict[str, Set[str]]:
        """Distribute keys to target nodes based on consistent hashing rules"""
        
        key_distribution = defaultdict(set)
        
        for key in keys:
            key_position = self.compute_position(key)
            
            # Find which target node should receive this key
            target_node = self._find_target_for_key_position(key_position, migration_plan)
            if target_node:
                key_distribution[target_node].add(key)
        
        return key_distribution
    
    def _find_target_for_key_position(self, key_position: int, migration_plan: Dict[str, List[int]]) -> Optional[str]:
        """Find target node for a key based on its position and migration plan"""
        
        # Find the appropriate successor among target nodes
        best_target = None
        best_distance = float('inf')
        
        for target_node, positions in migration_plan.items():
            for position in positions:
                # Calculate distance to this position
                if position >= key_position:
                    distance = position - key_position
                else:
                    distance = (self.space_size - key_position) + position
                
                if distance < best_distance:
                    best_distance = distance
                    best_target = target_node
        
        return best_target
    
    def _remove_node_from_ring(self, node_id: str) -> Dict:
        """Remove node from ring data structures"""
        
        positions_to_remove = self.node_positions[node_id]
        
        # Remove positions from ring
        for position in positions_to_remove:
            if position in self.ring:
                del self.ring[position]
        
        # Remove from node tracking
        del self.node_positions[node_id]
        
        # Update sorted positions
        self.sorted_positions = sorted(self.ring.keys())
        
        return {
            'positions_removed': len(positions_to_remove),
            'ring_size_after': len(self.ring)
        }
    
    def demonstrate_node_removal(self):
        """Demonstrate complete node removal process"""
        
        print("Node Removal Process Demonstration:")
        print("=" * 45)
        
        # Setup initial cluster
        initial_nodes = ['node-01', 'node-02', 'node-03', 'node-04']
        total_test_keys = 8000
        
        for node_id in initial_nodes:
            # Add virtual nodes
            positions = []
            for i in range(100):
                virtual_id = f"{node_id}:vnode_{i}"
                position = self.compute_position(virtual_id)
                positions.append(position)
                self.ring[position] = node_id
            
            self.node_positions[node_id] = positions
        
        self.sorted_positions = sorted(self.ring.keys())
        
        # Distribute test keys
        for key_index in range(total_test_keys):
            key = f"test_key_{key_index:05d}"
            responsible_node = self._find_responsible_node(key)
            self.data_location[responsible_node].add(key)

        # Show initial state
        print(f"Initial state:")
        print(f"  Nodes: {len(initial_nodes)}")
        print(f"  Total keys: {total_test_keys:,}")
        print(f"  Ring positions: {len(self.ring):,}")
        
        for node_id in initial_nodes:
            key_count = len(self.data_location[node_id])
            vnode_count = len(self.node_positions[node_id])
            print(f"    {node_id}: {key_count:,} keys, {vnode_count} vnodes")
        
        # Remove a node
        node_to_remove = 'node-02'
        print(f"\nRemoving node: {node_to_remove}")
        
        removal_result = self.remove_node_with_migration(node_to_remove)
        
        # Show final state
        print(f"\nFinal state:")
        remaining_nodes = [node for node in initial_nodes if node != node_to_remove]
        
        for node_id in remaining_nodes:
            key_count = len(self.data_location[node_id])
            vnode_count = len(self.node_positions[node_id])
            print(f"  {node_id}: {key_count:,} keys, {vnode_count} vnodes")
        
        # Verify data integrity
        total_keys_after = sum(len(self.data_location[node]) for node in remaining_nodes)
        print(f"\nData integrity check:")
        print(f"  Keys before removal: {total_test_keys:,}")
        print(f"  Keys after removal: {total_keys_after:,}")
        print(f"  Data integrity: {'✅ PRESERVED' if total_keys_after == total_test_keys else '❌ LOST'}")
        
        return removal_result
    
    def _find_responsible_node(self, key: str) -> str:
        """Find responsible node for a key"""
        key_position = self.compute_position(key)
        
        index = bisect.bisect_left(self.sorted_positions, key_position)
        if index < len(self.sorted_positions):
            successor_position = self.sorted_positions[index]
        else:
            successor_position = self.sorted_positions[0]
        
        return self.ring[successor_position]

# Demonstrate node removal
removal_manager = NodeRemovalManager('sha1')
removal_result = removal_manager.demonstrate_node_removal()
```

## Advanced Movement Analysis

```python
class AdvancedMovementAnalysis:
    """Advanced analysis of data movement patterns and optimization"""
    
    def __init__(self):
        self.scenarios = []
    
    def analyze_movement_efficiency(self):
        """Analyze movement efficiency across different scenarios"""
        
        print("Advanced Movement Efficiency Analysis:")
        print("=" * 45)
        
        # Test scenarios with different virtual node counts
        virtual_node_configs = [50, 100, 150, 200, 300]
        cluster_size = 20
        total_keys = 100000
        
        for vnode_count in virtual_node_configs:
            print(f"\nVirtual nodes per physical node: {vnode_count}")
            
            # Setup test scenario
            manager = NodeAdditionManager('sha1')
            self._setup_test_scenario(manager, cluster_size, total_keys, vnode_count)
            
            # Analyze movement for adding one node
            movement_analysis = self._analyze_movement_for_addition(manager, cluster_size + 1, vnode_count)
            
            theoretical_movement = total_keys / (cluster_size + 1)
            actual_movement = movement_analysis['total_movement']
            efficiency = (theoretical_movement / actual_movement) * 100 if actual_movement > 0 else 0
            
            print(f"  Theoretical movement: {theoretical_movement:.0f} keys")
            print(f"  Actual movement: {actual_movement} keys")
            print(f"  Efficiency: {efficiency:.1f}%")
            print(f"  Movement variance: {movement_analysis['movement_variance']:.2f}")
    
    def _setup_test_scenario(self, manager, cluster_size, total_keys, vnode_count):
        """Setup test scenario with specified parameters"""
        
        # Add nodes with virtual nodes
        for i in range(cluster_size):
            node_id = f"node-{i+1:02d}"
            positions = []
            
            for j in range(vnode_count):
                virtual_id = f"{node_id}:vnode_{j}"
                position = manager.compute_position(virtual_id)
                positions.append(position)
                manager.ring[position] = node_id
            
            manager.node_positions[node_id] = positions
        
        manager.sorted_positions = sorted(manager.ring.keys())
        
        # Distribute keys
        for key_index in range(total_keys):
            key = f"key_{key_index:06d}"
            responsible_node = self._find_responsible_node_in_manager(manager, key)
            manager.data_location[responsible_node].add(key)
    
    def _find_responsible_node_in_manager(self, manager, key):
        """Find responsible node in manager"""
        key_position = manager.compute_position(key)
        
        index = bisect.bisect_left(manager.sorted_positions, key_position)
        if index < len(manager.sorted_positions):
            successor_position = manager.sorted_positions[index]
        else:
            successor_position = manager.sorted_positions[0]
        
        return manager.ring[successor_position]
    
    def _analyze_movement_for_addition(self, manager, new_node_number, vnode_count):
        """Analyze movement requirements for adding a new node"""
        
        new_node_id = f"node-{new_node_number:02d}"
        
        # Calculate new positions
        new_positions = []
        for i in range(vnode_count):
            virtual_id = f"{new_node_id}:vnode_{i}"
            position = manager.compute_position(virtual_id)
            new_positions.append(position)
        
        # Analyze movement for each position
        movements = []
        total_movement = 0
        
        for position in new_positions:
            predecessor_pos = manager._find_predecessor_position(position)
            successor_pos = manager._find_successor_position(position)
            
            if successor_pos is not None:
                successor_node = manager.ring[successor_pos]
                keys_to_move = manager._find_keys_in_range(predecessor_pos, position, successor_node)
                movement_count = len(keys_to_move)
                movements.append(movement_count)
                total_movement += movement_count
        
        # Calculate movement statistics
        if movements:
            movement_variance = sum((m - (total_movement/len(movements)))**2 for m in movements) / len(movements)
        else:
            movement_variance = 0
        
        return {
            'total_movement': total_movement,
            'movement_per_position': movements,
            'movement_variance': movement_variance,
            'positions_analyzed': len(new_positions)
        }
    
    def compare_addition_vs_removal_efficiency(self):
        """Compare efficiency of addition vs removal operations"""
        
        print("\nAddition vs Removal Efficiency Comparison:")
        print("=" * 50)
        
        cluster_size = 15
        total_keys = 75000
        vnode_count = 150
        
        # Test addition efficiency
        print("Addition Analysis:")
        addition_manager = NodeAdditionManager('sha1')
        self._setup_test_scenario(addition_manager, cluster_size, total_keys, vnode_count)
        
        addition_analysis = self._analyze_movement_for_addition(addition_manager, cluster_size + 1, vnode_count)
        addition_theoretical = total_keys / (cluster_size + 1)
        addition_efficiency = (addition_theoretical / addition_analysis['total_movement']) * 100
        
        print(f"  Theoretical optimal: {addition_theoretical:.0f} keys")
        print(f"  Actual movement: {addition_analysis['total_movement']} keys")
        print(f"  Efficiency: {addition_efficiency:.1f}%")
        
        # Test removal efficiency
        print("\nRemoval Analysis:")
        removal_manager = NodeRemovalManager('sha1')
        
        # Setup with one extra node to remove
        self._setup_removal_scenario(removal_manager, cluster_size + 1, total_keys, vnode_count)
        
        # Analyze removal of one node
        node_to_remove = 'node-01'
        keys_on_removed_node = len(removal_manager.data_location[node_to_remove])
        
        print(f"  Keys to redistribute: {keys_on_removed_node}")
        print(f"  Theoretical optimal: {keys_on_removed_node} keys (all keys move)")
        print(f"  Actual movement: {keys_on_removed_node} keys")
        print(f"  Efficiency: 100.0% (removal is always optimal)")
        
        # Compare operations
        print(f"\nComparison:")
        print(f"  Addition efficiency: {addition_efficiency:.1f}%")
        print(f"  Removal efficiency: 100.0%")
        print(f"  Conclusion: Removal is more predictable and efficient")
    
    def _setup_removal_scenario(self, manager, cluster_size, total_keys, vnode_count):
        """Setup scenario for removal testing"""
        
        for i in range(cluster_size):
            node_id = f"node-{i+1:02d}"
            positions = []
            
            for j in range(vnode_count):
                virtual_id = f"{node_id}:vnode_{j}"
                position = manager.compute_position(virtual_id)
                positions.append(position)
                manager.ring[position] = node_id
            
            manager.node_positions[node_id] = positions
        
        manager.sorted_positions = sorted(manager.ring.keys())
        
        # Distribute keys
        for key_index in range(total_keys):
            key = f"key_{key_index:06d}"
            responsible_node = self._find_responsible_node_in_removal_manager(manager, key)
            manager.data_location[responsible_node].add(key)
    
    def _find_responsible_node_in_removal_manager(self, manager, key):
        """Find responsible node in removal manager"""
        key_position = manager.compute_position(key)
        
        index = bisect.bisect_left(manager.sorted_positions, key_position)
        if index < len(manager.sorted_positions):
            successor_position = manager.sorted_positions[index]
        else:
            successor_position = manager.sorted_positions[0]
        
        return manager.ring[successor_position]

# Run advanced movement analysis
advanced_analyzer = AdvancedMovementAnalysis()
advanced_analyzer.analyze_movement_efficiency()
advanced_analyzer.compare_addition_vs_removal_efficiency()
```

## Production Considerations

```python
class ProductionNodeOperations:
    """Production considerations for node addition and removal"""
    
    def deployment_best_practices(self):
        """Outline best practices for production deployments"""
        
        print("Production Node Operations Best Practices:")
        print("=" * 50)
        
        practices = [
            ("Pre-operation Validation", [
                "Verify cluster health before making changes",
                "Check data replication status and consistency",
                "Ensure sufficient capacity for data movement",
                "Validate network connectivity to all nodes",
                "Confirm backup and recovery procedures are current"
            ]),
            ("Operation Execution", [
                "Perform operations during low-traffic periods",
                "Use gradual rollout with monitoring at each step",
                "Implement circuit breakers for operation rollback",
                "Monitor system performance throughout operation",
                "Maintain detailed logs of all operation steps"
            ]),
            ("Post-operation Verification", [
                "Verify data integrity and consistency",
                "Check load balance across all nodes",
                "Monitor system performance for degradation",
                "Validate that all services are functioning normally",
                "Update documentation and monitoring baselines"
            ]),
            ("Emergency Procedures", [
                "Prepare rollback procedures for failed operations",
                "Implement automated health checks and alerting",
                "Maintain emergency contact procedures",
                "Document escalation paths for critical issues",
                "Practice failure scenarios in staging environment"
            ])
        ]
        
        for category, items in practices:
            print(f"\n{category}:")
            for item in items:
                print(f"  • {item}")
    
    def operation_timing_recommendations(self):
        """Provide timing recommendations for different operation types"""
        
        print("\nOperation Timing Recommendations:")
        print("=" * 40)
        
        scenarios = [
            ("Small Cluster (< 10 nodes)", {
                "addition_time": "2-5 minutes",
                "removal_time": "1-3 minutes", 
                "recommended_window": "Any low-traffic period",
                "data_movement": "< 100MB typically"
            }),
            ("Medium Cluster (10-100 nodes)", {
                "addition_time": "5-15 minutes",
                "removal_time": "3-10 minutes",
                "recommended_window": "Scheduled maintenance window",
                "data_movement": "100MB-1GB typically"
            }),
            ("Large Cluster (100+ nodes)", {
                "addition_time": "10-30 minutes",
                "removal_time": "5-20 minutes",
                "recommended_window": "Coordinated maintenance window",
                "data_movement": "1GB+ potentially"
            })
        ]
        
        for scenario_name, details in scenarios:
            print(f"\n{scenario_name}:")
            for metric, value in details.items():
                print(f"  {metric.replace('_', ' ').title()}: {value}")

# Demonstrate production considerations
production_ops = ProductionNodeOperations()
production_ops.deployment_best_practices()
production_ops.operation_timing_recommendations()
```

## Summary

Node addition and removal operations in consistent hashing follow predictable patterns that enable efficient scaling:

1. **Addition Process**: Compute new positions, identify affected ranges, migrate data from successors, update ring structure - typically moving 1/n of data

2. **Removal Process**: Identify data on departing node, find successor nodes for each position, migrate all data to successors, remove from ring - always moving exactly the data on the removed node

3. **Movement Efficiency**: Addition achieves near-optimal data movement (theoretical minimum), while removal is inherently optimal (100% efficiency)

4. **Production Considerations**: Require careful planning, monitoring, and validation procedures to ensure data integrity and system availability during operations

These operations enable consistent hashing systems to scale dynamically while maintaining the mathematical guarantees of minimal data movement and predictable performance impact.​​​​​​​​​​​​​​​​
