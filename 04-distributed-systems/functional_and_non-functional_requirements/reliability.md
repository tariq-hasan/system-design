# Resiliency

## Understanding Failure Scenarios

When designing large-scale systems, you must anticipate and plan for failures. With hundreds or thousands of servers, failures become inevitable rather than exceptional events. A comprehensive system design must account for various failure scenarios:

### Failure Hierarchy

1. **Individual Component Failures**
   - Hard drive failures
   - Memory failures
   - CPU burnout
   - Network interface issues

2. **Server-Level Failures**
   - Complete server outages
   - Operating system crashes
   - Power supply failures

3. **Rack-Level Failures**
   - Power distribution problems
   - Network switch failures
   - Physical accidents (disconnected cables)
   - Power surges affecting entire racks

4. **Data Center/Availability Zone Failures**
   - Power outages
   - Cooling system failures
   - Natural disasters (hurricanes, floods)
   - Limited backup power duration

5. **Regional Failures**
   - Network disruptions (undersea cable cuts)
   - Large-scale power grid issues
   - Regional internet outages
   - Regional natural disasters

6. **Continental or Global Failures**
   - Major natural disasters
   - Significant geopolitical events
   - (Outside the scope of standard system design)

## Resiliency Strategies

### Data Redundancy

Database systems like MongoDB implement redundancy through replication:
- Primary instances handle writes
- Secondary instances maintain synchronized copies
- Automatic failover mechanisms

### Geographic Distribution

Implement geo-routing to direct traffic based on user location:
- North American traffic routes to North American data centers
- European traffic routes to European data centers
- Traffic from India routes to Indian data centers

This approach provides:
- Lower latency during normal operations
- Fallback options during regional failures
- Ability to reroute traffic when regions become unavailable

### Capacity Planning for Resilience

To maintain service during failures, systems need excess capacity:
- Calculate normal operating capacity
- Add buffer for handling redirected traffic from failed regions
- Ensure remaining regions can absorb traffic if any single region fails

### Multi-Level Distribution

Distribute critical system components across:
- Multiple racks within data centers
- Multiple availability zones within regions
- Multiple geographic regions globally

This ensures that no single failure point can bring down the entire system.

## Cost-Benefit Considerations

Implementing full resiliency has significant cost implications:
- Over-provisioning servers and infrastructure
- Maintaining redundant systems that may rarely be used
- Higher operational complexity and management overhead

When designing systems, consider:
- Application criticality and downtime tolerance
- Acceptable recovery time objectives (RTOs)
- Budget constraints and business priorities
- Regulatory or contractual uptime requirements

### Industry Context

Large tech companies like Amazon, Google, and Facebook typically prioritize maximum resiliency:
- They have substantial financial resources
- Their business models cannot tolerate significant downtime
- The cost of failure exceeds the cost of over-provisioning

For other organizations, it's important to find the appropriate balance between resiliency and cost based on business requirements.

## Designing for Resiliency in Interviews

When approaching system design interviews:
1. Ask explicit questions about resiliency requirements
2. Demonstrate understanding of different failure scenarios
3. Present multiple approaches with their trade-offs
4. Show awareness of cost implications
5. Recommend solutions proportional to the system's criticality

Resiliency planning demonstrates mature engineering thinking and an understanding that real-world systems must operate reliably even when components fail.
