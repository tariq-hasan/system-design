# Node Placement in Consistent Hashing

Node placement is the process of positioning physical and virtual nodes on the hash ring to achieve optimal load distribution and system performance. The placement strategy directly impacts load balance, fault tolerance, and operational complexity. Understanding the nuances of node placement is crucial for building production systems that can scale gracefully while maintaining predictable performance characteristics.

## Node Placement Algorithm

The core node placement algorithm transforms node identifiers into ring positions through a deterministic hashing process that ensures consistent placement across all system components.

### Basic Placement Process

```python
import hashlib
import bisect
from typing import List, Dict, Set, Tuple, Optional
import uuid
import ipaddress

class NodePlacement:
    """Comprehensive node placement implementation"""
    
    def __init__(self, hash_function: str = 'sha1'):
        self.hash_function = hash_function
        self.ring = {}  # position -> node_id mapping
        self.sorted_positions = []  # Sorted list for efficient lookups
        self.node_positions = {}  # node_id -> [positions] mapping
        
        # Setup hash function
        self._setup_hash_function()
    
    def _setup_hash_function(self):
        """Configure hash function and space size"""
        hash_configs = {
            'sha1': {'func': hashlib.sha1, 'space_size': 2**160},
            'sha256': {'func': hashlib.sha256, 'space_size': 2**256},
            'md5': {'func': hashlib.md5, 'space_size': 2**128},
        }
        
        if self.hash_function not in hash_configs:
            raise ValueError(f"Unsupported hash function: {self.hash_function}")
        
        config = hash_configs[self.hash_function]
        self.hasher = config['func']
        self.space_size = config['space_size']
    
    def compute_node_position(self, node_identifier: str) -> int:
        """
        Compute hash ring position for a node identifier
        
        Args:
            node_identifier: Unique identifier for the node
            
        Returns:
            Integer position on the hash ring
        """
        if not isinstance(node_identifier, str):
            raise TypeError("Node identifier must be a string")
        
        if not node_identifier.strip():
            raise ValueError("Node identifier cannot be empty")
        
        # Convert to bytes and hash
        identifier_bytes = node_identifier.encode('utf-8')
        hash_obj = self.hasher(identifier_bytes)
        hash_hex = hash_obj.hexdigest()
        
        # Convert to ring position
        hash_int = int(hash_hex, 16)
        position = hash_int % self.space_size
        
        return position
    
    def place_node(self, node_id: str, virtual_node_count: int = 1) -> Dict:
        """
        Place a node on the ring with specified number of virtual nodes
        
        Args:
            node_id: Unique identifier for the physical node
            virtual_node_count: Number of virtual nodes to create
            
        Returns:
            Dictionary with placement results
        """
        if node_id in self.node_positions:
            raise ValueError(f"Node {node_id} is already placed on the ring")
        
        placed_positions = []
        collision_count = 0
        
        for i in range(virtual_node_count):
            # Create virtual node identifier
            virtual_id = f"{node_id}:vnode_{i}"
            position = self.compute_node_position(virtual_id)
            
            # Handle position collisions
            original_position = position
            collision_attempts = 0
            max_collision_attempts = 1000
            
            while position in self.ring and collision_attempts < max_collision_attempts:
                collision_count += 1
                collision_attempts += 1
                # Create new identifier with collision suffix
                collision_virtual_id = f"{virtual_id}_collision_{collision_attempts}"
                position = self.compute_node_position(collision_virtual_id)
            
            if collision_attempts >= max_collision_attempts:
                raise RuntimeError(f"Unable to resolve position collision for {virtual_id}")
            
            # Place virtual node
            self.ring[position] = node_id
            placed_positions.append(position)
        
        # Update node tracking
        self.node_positions[node_id] = placed_positions
        
        # Update sorted positions for efficient lookups
        self.sorted_positions = sorted(self.ring.keys())
        
        return {
            'node_id': node_id,
            'virtual_nodes_placed': len(placed_positions),
            'positions': placed_positions,
            'collisions_resolved': collision_count,
            'ring_size': len(self.ring)
        }
    
    def remove_node(self, node_id: str) -> Dict:
        """Remove a node and all its virtual nodes from the ring"""
        if node_id not in self.node_positions:
            raise ValueError(f"Node {node_id} is not on the ring")
        
        positions_to_remove = self.node_positions[node_id]
        
        # Remove all positions for this node
        for position in positions_to_remove:
            if position in self.ring:
                del self.ring[position]
        
        # Remove from node tracking
        del self.node_positions[node_id]
        
        # Update sorted positions
        self.sorted_positions = sorted(self.ring.keys())
        
        return {
            'node_id': node_id,
            'virtual_nodes_removed': len(positions_to_remove),
            'positions': positions_to_remove,
            'ring_size': len(self.ring)
        }
    
    def demonstrate_placement_process(self):
        """Demonstrate the step-by-step node placement process"""
        
        print("Node Placement Process Demonstration:")
        print("=" * 45)
        
        # Example nodes with different identifier types
        test_nodes = [
            'server-001',
            'cache-node-alpha',
            'db-primary-east',
            'storage-tier1-01'
        ]
        
        for node_id in test_nodes:
            print(f"\nPlacing node: {node_id}")
            
            # Show position computation
            position = self.compute_node_position(node_id)
            percentage = (position / self.space_size) * 100
            
            print(f"  Step 1: Compute hash({node_id})")
            print(f"  Step 2: Position = {position:,} ({percentage:.6f}% around ring)")
            
            # Place node with multiple virtual nodes
            result = self.place_node(node_id, virtual_node_count=3)
            
            print(f"  Step 3: Placed {result['virtual_nodes_placed']} virtual nodes")
            print(f"  Positions: {[f'{p:,}' for p in result['positions'][:3]}...")
            print(f"  Ring size now: {result['ring_size']}")
            
            if result['collisions_resolved'] > 0:
                print(f"  Collisions resolved: {result['collisions_resolved']}")
        
        # Show final ring state
        print(f"\nFinal ring state:")
        print(f"  Total positions: {len(self.ring)}")
        print(f"  Physical nodes: {len(self.node_positions)}")
        print(f"  Average virtual nodes per physical: {len(self.ring) / len(self.node_positions):.1f}")

# Demonstrate basic node placement
placement_demo = NodePlacement('sha1')
placement_demo.demonstrate_placement_process()
```

### Advanced Placement with Virtual Nodes

```python
class VirtualNodePlacement:
    """Advanced virtual node placement strategies"""
    
    def __init__(self, hash_function: str = 'sha1'):
        self.hash_function = hash_function
        self.placement = NodePlacement(hash_function)
        
    def analyze_virtual_node_distribution(self, node_id: str, virtual_counts: List[int]):
        """Analyze how different virtual node counts affect distribution"""
        
        print(f"Virtual Node Distribution Analysis for {node_id}:")
        print("=" * 55)
        
        for vnode_count in virtual_counts:
            print(f"\nTesting {vnode_count} virtual nodes:")
            
            # Create temporary ring for testing
            temp_placement = NodePlacement(self.hash_function)
            result = temp_placement.place_node(node_id, vnode_count)
            
            positions = result['positions']
            
            # Analyze position distribution
            position_gaps = []
            sorted_positions = sorted(positions)
            
            for i in range(len(sorted_positions)):
                current_pos = sorted_positions[i]
                next_pos = sorted_positions[(i + 1) % len(sorted_positions)]
                
                if next_pos > current_pos:
                    gap = next_pos - current_pos
                else:
                    # Wrap-around case
                    gap = (temp_placement.space_size - current_pos) + next_pos
                
                position_gaps.append(gap)
            
            # Calculate distribution metrics
            avg_gap = sum(position_gaps) / len(position_gaps)
            min_gap = min(position_gaps)
            max_gap = max(position_gaps)
            gap_variance = sum((gap - avg_gap) ** 2 for gap in position_gaps) / len(position_gaps)
            gap_std_dev = gap_variance ** 0.5
            
            print(f"  Average gap: {avg_gap:,.0f}")
            print(f"  Gap range: {min_gap:,.0f} - {max_gap:,.0f}")
            print(f"  Gap std deviation: {gap_std_dev:,.0f}")
            print(f"  Distribution quality: {self._assess_distribution_quality(gap_std_dev, avg_gap)}")
    
    def _assess_distribution_quality(self, std_dev: float, mean: float) -> str:
        """Assess the quality of virtual node distribution"""
        coefficient_of_variation = std_dev / mean if mean > 0 else float('inf')
        
        if coefficient_of_variation < 0.2:
            return "Excellent"
        elif coefficient_of_variation < 0.4:
            return "Good"
        elif coefficient_of_variation < 0.6:
            return "Acceptable"
        else:
            return "Poor"
    
    def optimal_virtual_node_recommendation(self, cluster_size: int, target_balance: float = 0.1):
        """Recommend optimal virtual node count based on cluster size"""
        
        print(f"Optimal Virtual Node Recommendation:")
        print(f"Cluster size: {cluster_size} nodes")
        print(f"Target balance coefficient: {target_balance}")
        print("=" * 40)
        
        # Theoretical calculation
        # For good load balance, we want coefficient of variation < target_balance
        # CV ≈ 1/sqrt(virtual_nodes_per_physical)
        min_virtual_nodes = int((1 / target_balance) ** 2)
        
        # Practical recommendations based on cluster size
        if cluster_size <= 10:
            recommended = max(50, min_virtual_nodes)
            reasoning = "Small cluster needs more virtual nodes for balance"
        elif cluster_size <= 100:
            recommended = max(100, min_virtual_nodes)
            reasoning = "Medium cluster balances virtual nodes with complexity"
        elif cluster_size <= 1000:
            recommended = max(150, min_virtual_nodes)
            reasoning = "Large cluster can use more virtual nodes efficiently"
        else:
            recommended = max(200, min_virtual_nodes)
            reasoning = "Very large cluster benefits from many virtual nodes"
        
        print(f"Theoretical minimum: {min_virtual_nodes}")
        print(f"Recommended: {recommended}")
        print(f"Reasoning: {reasoning}")
        
        # Calculate expected performance
        expected_cv = 1 / (recommended ** 0.5)
        total_virtual_nodes = cluster_size * recommended
        
        print(f"\nExpected performance:")
        print(f"  Total virtual nodes: {total_virtual_nodes:,}")
        print(f"  Expected balance CV: {expected_cv:.3f}")
        print(f"  Memory overhead: ~{total_virtual_nodes * 64} bytes")
        
        return recommended

# Demonstrate virtual node analysis
virtual_demo = VirtualNodePlacement('sha1')
virtual_demo.analyze_virtual_node_distribution('test-node', [10, 50, 100, 200])
virtual_demo.optimal_virtual_node_recommendation(100)
```

## Node Identification Strategies

The choice of node identifier format significantly impacts system operability, debugging capabilities, and geographic distribution strategies.

### Identification Format Analysis

```python
class NodeIdentificationStrategies:
    """Compare different node identification strategies"""
    
    def __init__(self):
        self.placement = NodePlacement('sha1')
    
    def demonstrate_ip_port_strategy(self):
        """Demonstrate IP:Port identification strategy"""
        
        print("IP:Port Identification Strategy:")
        print("=" * 35)
        
        # Example server configurations
        servers = [
            ('192.168.1.100', 6379),  # Redis cache
            ('192.168.1.101', 6379),  # Redis cache
            ('10.0.1.50', 3306),      # MySQL database
            ('10.0.1.51', 3306),      # MySQL database
            ('172.16.0.10', 8080),    # Web server
        ]
        
        positions = []
        for ip, port in servers:
            node_id = f"{ip}:{port}"
            position = self.placement.compute_node_position(node_id)
            positions.append((node_id, position))
            
            print(f"  {node_id:<20} → {position:>15,}")
        
        # Analyze distribution
        self._analyze_position_distribution(positions, "IP:Port strategy")
        
        print("\nAdvantages:")
        print("  + Natural mapping to network endpoints")
        print("  + Easy debugging and operational correlation")
        print("  + Automatic uniqueness within network")
        
        print("\nDisadvantages:")
        print("  - Tied to network configuration")
        print("  - Changes with IP address updates")
        print("  - May cluster in certain IP ranges")
        
        return positions
    
    def demonstrate_uuid_strategy(self):
        """Demonstrate UUID identification strategy"""
        
        print("\nUUID Identification Strategy:")
        print("=" * 35)
        
        # Generate example UUIDs
        servers = []
        for i in range(5):
            node_uuid = str(uuid.uuid4())
            servers.append(node_uuid)
        
        positions = []
        for node_id in servers:
            position = self.placement.compute_node_position(node_id)
            positions.append((node_id, position))
            
            print(f"  {node_id} → {position:>15,}")
        
        # Analyze distribution
        self._analyze_position_distribution(positions, "UUID strategy")
        
        print("\nAdvantages:")
        print("  + Guaranteed uniqueness")
        print("  + Excellent hash distribution")
        print("  + Independent of network configuration")
        print("  + Stable across infrastructure changes")
        
        print("\nDisadvantages:")
        print("  - No semantic meaning")
        print("  - Difficult debugging without mapping")
        print("  - Requires persistent identifier storage")
        
        return positions
    
    def demonstrate_composite_strategy(self):
        """Demonstrate composite identification strategy"""
        
        print("\nComposite Identification Strategy:")
        print("=" * 40)
        
        # Example composite identifiers
        servers = [
            'us-east-1a-rack01-server05',
            'us-east-1b-rack03-server12',
            'us-west-2a-rack02-server08',
            'eu-west-1a-rack01-server03',
            'ap-south-1b-rack04-server15',
        ]
        
        positions = []
        for node_id in servers:
            position = self.placement.compute_node_position(node_id)
            positions.append((node_id, position))
            
            print(f"  {node_id:<25} → {position:>15,}")
        
        # Analyze distribution
        self._analyze_position_distribution(positions, "Composite strategy")
        
        # Analyze geographic clustering
        self._analyze_geographic_distribution(positions)
        
        print("\nAdvantages:")
        print("  + Rich semantic information")
        print("  + Hierarchical organization")
        print("  + Easy operational reasoning")
        print("  + Supports geographic policies")
        
        print("\nDisadvantages:")
        print("  - May create geographic clustering")
        print("  - Longer identifiers")
        print("  - Requires naming conventions")
        
        return positions
    
    def _analyze_position_distribution(self, positions: List[Tuple[str, int]], strategy_name: str):
        """Analyze how well positions are distributed"""
        
        if len(positions) < 2:
            return
        
        sorted_positions = sorted([pos for _, pos in positions])
        gaps = []
        
        for i in range(len(sorted_positions)):
            current = sorted_positions[i]
            next_pos = sorted_positions[(i + 1) % len(sorted_positions)]
            
            if next_pos > current:
                gap = next_pos - current
            else:
                # Wrap around
                gap = (self.placement.space_size - current) + next_pos
            
            gaps.append(gap)
        
        avg_gap = sum(gaps) / len(gaps)
        min_gap = min(gaps)
        max_gap = max(gaps)
        
        print(f"\nDistribution analysis for {strategy_name}:")
        print(f"  Average gap: {avg_gap:,.0f}")
        print(f"  Gap range: {min_gap:,.0f} - {max_gap:,.0f}")
        print(f"  Gap ratio: {max_gap / min_gap:.2f}:1")
    
    def _analyze_geographic_distribution(self, positions: List[Tuple[str, int]]):
        """Analyze geographic clustering in composite identifiers"""
        
        # Extract regions from composite identifiers
        regions = {}
        for node_id, position in positions:
            # Assume format: region-az-rack-server
            parts = node_id.split('-')
            if len(parts) >= 2:
                region = f"{parts[0]}-{parts[1]}"
                if region not in regions:
                    regions[region] = []
                regions[region].append(position)
        
        print(f"\nGeographic distribution:")
        for region, positions_in_region in regions.items():
            avg_position = sum(positions_in_region) / len(positions_in_region)
            print(f"  {region}: {len(positions_in_region)} nodes, avg position: {avg_position:,.0f}")

# Demonstrate identification strategies
id_strategies = NodeIdentificationStrategies()
ip_positions = id_strategies.demonstrate_ip_port_strategy()
uuid_positions = id_strategies.demonstrate_uuid_strategy()
composite_positions = id_strategies.demonstrate_composite_strategy()
```

### Advanced Identification Patterns

```python
class AdvancedIdentificationPatterns:
    """Advanced patterns for node identification"""
    
    def __init__(self):
        self.placement = NodePlacement('sha1')
    
    def hierarchical_identification(self):
        """Demonstrate hierarchical identification for large deployments"""
        
        print("Hierarchical Identification Pattern:")
        print("=" * 40)
        
        # Multi-level hierarchy: region.datacenter.rack.server.service
        services = [
            'us-east.dc1.rack01.srv001.redis',
            'us-east.dc1.rack01.srv002.mysql',
            'us-east.dc1.rack02.srv001.redis',
            'us-east.dc2.rack01.srv001.redis',
            'us-west.dc1.rack01.srv001.redis',
        ]
        
        hierarchy_analysis = {}
        
        for service_id in services:
            position = self.placement.compute_node_position(service_id)
            
            # Parse hierarchy levels
            parts = service_id.split('.')
            levels = {
                'region': parts[0],
                'datacenter': f"{parts[0]}.{parts[1]}",
                'rack': f"{parts[0]}.{parts[1]}.{parts[2]}",
                'server': f"{parts[0]}.{parts[1]}.{parts[2]}.{parts[3]}",
                'service': service_id
            }
            
            # Track positions by hierarchy level
            for level, identifier in levels.items():
                if level not in hierarchy_analysis:
                    hierarchy_analysis[level] = {}
                if identifier not in hierarchy_analysis[level]:
                    hierarchy_analysis[level][identifier] = []
                hierarchy_analysis[level][identifier].append(position)
            
            print(f"  {service_id:<35} → {position:>15,}")
        
        # Analyze clustering at each level
        print(f"\nHierarchy clustering analysis:")
        for level in ['region', 'datacenter', 'rack', 'server']:
            identifiers_at_level = hierarchy_analysis[level]
            print(f"  {level.capitalize()} level: {len(identifiers_at_level)} unique identifiers")
            
            # Calculate clustering coefficient
            all_positions = []
            for positions in identifiers_at_level.values():
                all_positions.extend(positions)
            
            if len(all_positions) > 1:
                gaps = self._calculate_position_gaps(all_positions)
                clustering_coefficient = max(gaps) / min(gaps) if min(gaps) > 0 else float('inf')
                print(f"    Clustering coefficient: {clustering_coefficient:.2f}")
    
    def service_aware_identification(self):
        """Demonstrate service-aware identification"""
        
        print("\nService-Aware Identification:")
        print("=" * 35)
        
        # Include service type in identifier for different hash distributions
        services = [
            ('cache', 'redis-cluster-01'),
            ('cache', 'redis-cluster-02'),
            ('database', 'postgres-primary'),
            ('database', 'postgres-replica-01'),
            ('web', 'nginx-frontend-01'),
            ('web', 'nginx-frontend-02'),
            ('api', 'app-server-01'),
            ('api', 'app-server-02'),
        ]
        
        service_distributions = {}
        
        for service_type, instance_id in services:
            # Create service-aware identifier
            node_id = f"{service_type}:{instance_id}"
            position = self.placement.compute_node_position(node_id)
            
            if service_type not in service_distributions:
                service_distributions[service_type] = []
            service_distributions[service_type].append(position)
            
            print(f"  {node_id:<25} → {position:>15,}")
        
        # Analyze per-service distribution
        print(f"\nPer-service distribution analysis:")
        for service_type, positions in service_distributions.items():
            if len(positions) > 1:
                gaps = self._calculate_position_gaps(positions)
                avg_gap = sum(gaps) / len(gaps)
                print(f"  {service_type}: {len(positions)} instances, avg gap: {avg_gap:,.0f}")
    
    def _calculate_position_gaps(self, positions: List[int]) -> List[int]:
        """Calculate gaps between sorted positions"""
        sorted_positions = sorted(positions)
        gaps = []
        
        for i in range(len(sorted_positions)):
            current = sorted_positions[i]
            next_pos = sorted_positions[(i + 1) % len(sorted_positions)]
            
            if next_pos > current:
                gap = next_pos - current
            else:
                gap = (self.placement.space_size - current) + next_pos
            
            gaps.append(gap)
        
        return gaps

# Demonstrate advanced identification patterns
advanced_patterns = AdvancedIdentificationPatterns()
advanced_patterns.hierarchical_identification()
advanced_patterns.service_aware_identification()
```

## Placement Considerations

Several critical factors must be considered when designing node placement strategies for production systems.

### Deterministic Placement Validation

```python
class PlacementValidation:
    """Validate deterministic placement properties"""
    
    def __init__(self):
        self.placement = NodePlacement('sha1')
    
    def validate_deterministic_placement(self):
        """Verify that placement is truly deterministic"""
        
        print("Deterministic Placement Validation:")
        print("=" * 40)
        
        test_nodes = ['server-001', 'cache-alpha', 'db-primary']
        
        for node_id in test_nodes:
            print(f"\nTesting node: {node_id}")
            
            # Compute position multiple times
            positions = []
            for attempt in range(5):
                position = self.placement.compute_node_position(node_id)
                positions.append(position)
            
            # Check consistency
            all_same = all(pos == positions[0] for pos in positions)
            print(f"  5 consecutive computations: {positions}")
            print(f"  Deterministic: {'✅ YES' if all_same else '❌ NO'}")
            
            # Test across different instances
            other_placement = NodePlacement('sha1')
            other_position = other_placement.compute_node_position(node_id)
            cross_instance_consistent = other_position == positions[0]
            
            print(f"  Cross-instance consistent: {'✅ YES' if cross_instance_consistent else '❌ NO'}")
    
    def validate_collision_handling(self):
        """Test collision detection and resolution"""
        
        print("\nCollision Handling Validation:")
        print("=" * 35)
        
        # Force collisions by using predictable identifiers
        collision_test_nodes = [
            'collision-test-base',
            'collision-test-base:vnode_0_collision_1',  # Simulate collision resolution
            'collision-test-base:vnode_0_collision_2',
        ]
        
        positions = {}
        collisions_detected = 0
        
        for node_id in collision_test_nodes:
            position = self.placement.compute_node_position(node_id)
            
            if position in positions:
                collisions_detected += 1
                print(f"  Collision detected: {node_id} → {position} (same as {positions[position]})")
            else:
                positions[position] = node_id
                print(f"  Unique position: {node_id} → {position}")
        
        print(f"\nCollision summary:")
        print(f"  Nodes tested: {len(collision_test_nodes)}")
        print(f"  Collisions detected: {collisions_detected}")
        print(f"  Unique positions: {len(positions)}")
    
    def validate_distribution_quality(self, num_nodes: int = 100):
        """Validate that nodes distribute well across the ring"""
        
        print(f"\nDistribution Quality Validation ({num_nodes} nodes):")
        print("=" * 50)
        
        # Generate test nodes
        test_nodes = [f"node-{i:03d}" for i in range(num_nodes)]
        positions = []
        
        for node_id in test_nodes:
            position = self.placement.compute_node_position(node_id)
            positions.append(position)
        
        # Analyze distribution
        sorted_positions = sorted(positions)
        gaps = []
        
        for i in range(len(sorted_positions)):
            current = sorted_positions[i]
            next_pos = sorted_positions[(i + 1) % len(sorted_positions)]
            
            if next_pos > current:
                gap = next_pos - current
            else:
                gap = (self.placement.space_size - current) + next_pos
            
            gaps.append(gap)
        
        # Calculate statistics
        avg_gap = sum(gaps) / len(gaps)
        min_gap = min(gaps)
        max_gap = max(gaps)
        gap_variance = sum((gap - avg_gap) ** 2 for gap in gaps) / len(gaps)
        gap_std_dev = gap_variance ** 0.5
        coefficient_of_variation = gap_std_dev / avg_gap
        
        print(f"  Average gap: {avg_gap:,.0f}")
        print(f"  Gap range: {min_gap:,.0f} - {max_gap:,.0f}")
        print(f"  Standard deviation: {gap_std_dev:,.0f}")
        print(f"  Coefficient of variation: {coefficient_of_variation:.3f}")
        
        # Quality assessment
        if coefficient_of_variation < 0.3:
            quality = "Excellent"
        elif coefficient_of_variation < 0.5:
            quality = "Good"
        elif coefficient_of_variation < 0.8:
            quality = "Acceptable"
        else:
            quality = "Poor"
        
        print(f"  Distribution quality: {quality}")
        
        # Chi-squared test for uniformity
        num_bins = 20
        bin_size = self.placement.space_size // num_bins
        bin_counts = [0] * num_bins
        
        for position in positions:
            bin_index = min(position // bin_size, num_bins - 1)
            bin_counts[bin_index] += 1
        
        expected_per_bin = num_nodes / num_bins
        chi_squared = sum((count - expected_per_bin) ** 2 / expected_per_bin 
                         for count in bin_counts)
        
        print(f"  Chi-squared statistic: {chi_squared:.2f}")
        print(f"  Expected (uniform): ~{num_bins:.0f}")
        
        return {
            'coefficient_of_variation': coefficient_of_variation,
            'chi_squared': chi_squared,
            'quality': quality
        }

# Run placement validation
validation = PlacementValidation()
validation.validate_deterministic_placement()
validation.validate_collision_handling()
validation.validate_distribution_quality(50)
```

### Production Placement Guidelines

```python
class ProductionPlacementGuidelines:
    """Production deployment guidelines for node placement"""
    
    def __init__(self):
        pass
    
    def recommend_placement_strategy(self, deployment_scenario: Dict) -> Dict:
        """Recommend placement strategy based on deployment scenario"""
        
        cluster_size = deployment_scenario.get('cluster_size', 10)
        geographic_distribution = deployment_scenario.get('geographic', False)
        service_types = deployment_scenario.get('service_types', 1)
        operational_complexity = deployment_scenario.get('ops_complexity', 'medium')
        
        print("Production Placement Strategy Recommendation:")
        print("=" * 50)
        print(f"Scenario: {deployment_scenario}")
        
        # Identifier strategy recommendation
        if geographic_distribution and cluster_size > 50:
            id_strategy = "Hierarchical composite (region.dc.rack.server.service)"
            id_benefits = ["Geographic awareness", "Operational clarity", "Policy support"]
            id_considerations = ["Naming convention enforcement", "Potential clustering"]
        elif operational_complexity == 'low' and cluster_size <= 20:
            id_strategy = "IP:Port based"
            id_benefits = ["Simple implementation", "Natural debugging", "Network correlation"]
            id_considerations = ["IP address stability", "Limited scalability"]
        else:
            id_strategy = "UUID with metadata mapping"
            id_benefits = ["Guaranteed uniqueness", "Excellent distribution", "Infrastructure independence"]
            id_considerations = ["Requires identifier mapping", "Less intuitive debugging"]
        
        # Virtual node count recommendation
        if cluster_size <= 10:
            virtual_nodes = 150
            vnode_reasoning = "Small clusters need more virtual nodes for balance"
        elif cluster_size <= 100:
            virtual_nodes = 100
            vnode_reasoning = "Medium clusters balance efficiency with complexity"
        else:
            virtual_nodes = 75
            vnode_reasoning = "Large clusters can use fewer virtual nodes per physical node"
        
        # Hash function recommendation
        if deployment_scenario.get('security_requirements', 'medium') == 'high':
            hash_function = "SHA-256"
            hash_reasoning = "High security requirements need cryptographically secure hash"
        elif cluster_size > 1000:
            hash_function = "SHA-1"
            hash_reasoning = "Large clusters benefit from SHA-1 performance"
        else:
            hash_function = "SHA-1"
            hash_reasoning = "SHA-1 provides good balance of security and performance"
        
        recommendation = {
            'identifier_strategy': id_strategy,
            'virtual_nodes_per_physical': virtual_nodes,
            'hash_function': hash_function,
            'benefits': id_benefits,
            'considerations': id_considerations,
            'reasoning': {
                'virtual_nodes': vnode_reasoning,
                'hash_function': hash_reasoning
            }
        }
        
        print(f"\nRecommendations:")
        print(f"  Identifier strategy: {recommendation['identifier_strategy']}")
        print(f"  Virtual nodes per physical: {recommendation['virtual_nodes_per_physical']}")
        print(f"  Hash function: {recommendation['hash_function']}")
        
        print(f"\nBenefits:")
        for benefit in recommendation['benefits']:
            print(f"  + {benefit}")
        
        print(f"\nConsiderations:")
        for consideration in recommendation['considerations']:
            print(f"  - {consideration}")
        
        return recommendation
    
    def deployment_checklist(self):
        """Provide deployment checklist for node placement"""
        
        print("\nNode Placement Deployment Checklist:")
        print("=" * 40)
        
        checklist_items = [
            ("Identifier Strategy", [
                "Choose appropriate identifier format for operational needs",
                "Ensure identifiers are stable across restarts",
                "Validate identifier uniqueness across entire system",
                "Document identifier format and conventions"
            ]),
            ("Hash Function Configuration", [
                "Select hash function based on security and performance needs",
                "Ensure all system components use same hash function",
                "Validate hash function produces uniform distribution",
                "Consider hash function upgrade path for future"
            ]),
            ("Virtual Node Configuration", [
                "Determine optimal virtual node count for cluster size",
                "Test load balance with chosen virtual node count",
                "Configure virtual node collision handling",
                "Monitor virtual node distribution after deployment"
            ]),
            ("Operational Considerations", [
                "Implement deterministic placement validation",
                "Create node placement monitoring and alerting",
                "Document node addition/removal procedures",
                "Test placement behavior during failure scenarios"
            ]),
            ("Performance Validation", [
                "Benchmark placement computation performance",
                "Validate lookup performance with expected load",
                "Test memory usage with maximum expected nodes",
                "Profile placement algorithm under stress conditions"
            ])
        ]
        
        for category, items in checklist_items:
            print(f"\n{category}:")
            for item in items:
                print(f"  ☐ {item}")

# Demonstrate production guidelines
production_guidelines = ProductionPlacementGuidelines()

# Test different deployment scenarios
scenarios = [
    {
        'cluster_size': 5,
        'geographic': False,
        'service_types': 1,
        'ops_complexity': 'low',
        'security_requirements': 'medium'
    },
    {
        'cluster_size': 100,
        'geographic': True,
        'service_types': 3,
        'ops_complexity': 'medium',
        'security_requirements': 'high'
    },
    {
        'cluster_size': 1000,
        'geographic': True,
        'service_types': 5,
        'ops_complexity': 'high',
        'security_requirements': 'medium'
    }
]

for i, scenario in enumerate(scenarios, 1):
    print(f"\nScenario {i}:")
    recommendation = production_guidelines.recommend_placement_strategy(scenario)

production_guidelines.deployment_checklist()
```

## Summary

Node placement in consistent hashing involves three critical design decisions:

1. **Identifier Strategy**: Choose between IP:Port (operational simplicity), UUID (guaranteed uniqueness), or composite identifiers (semantic richness) based on deployment requirements

2. **Placement Algorithm**: Implement deterministic hashing with collision resolution, virtual node support, and efficient data structures for O(log n) lookups

3. **Production Considerations**: Ensure deterministic behavior, handle collisions gracefully, validate distribution quality, and implement comprehensive monitoring

The placement strategy significantly impacts system operability, debugging capabilities, and load distribution. Production implementations should include thorough validation, monitoring, and documentation to ensure reliable operation at scale.​​​​​​​​​​​​​​​​
