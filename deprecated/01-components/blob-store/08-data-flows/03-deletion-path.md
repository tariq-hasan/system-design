# 8.3 Deletion Path

The deletion path defines how objects are removed from the blob storage system. A well-designed deletion flow balances immediate consistency for users with efficient resource reclamation and ensures proper handling of versioning, compliance, and notification requirements.

## End-to-End Flow

The deletion process follows a sequence of operations that safely remove an object while maintaining system integrity.

```
┌──────────┐     ┌──────────┐     ┌────────────┐     ┌───────────────┐     ┌─────────────┐
│  Client  │────►│   API    │────►│ Auth/Auth  │────►│ Delete        │────►│  Metadata   │
│ Request  │     │ Gateway  │     │  Service   │     │   Handler     │     │   Service   │
└──────────┘     └──────────┘     └────────────┘     └───────────────┘     └─────────────┘
                                                                                  │
                                                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌────────────┐     ┌────────────────┐
│ Notification │◄────│    Garbage   │◄────│   Storage  │◄────│   Versioning   │
│   Service    │     │   Collection │     │   Service  │     │   Service      │
└──────────────┘     └──────────────┘     └────────────┘     └────────────────┘
```

### Request Validation

The first step in the deletion path is validating the incoming request to ensure it meets system requirements.

- **Input Validation Checks**:
  - Object key format and length verification
  - Deletion parameter validation (recursive, version-specific)
  - Request signature verification
  - Conditional header validation (If-Match, If-Unmodified-Since)
  - Batch delete request structure

- **Protocol Validation**:
  - HTTP method verification (DELETE)
  - API version compatibility
  - URL format validation
  - Query parameter validation
  - Delete marker handling

- **Resource Validation**:
  - Bucket existence verification
  - Object existence pre-check (optional)
  - Version ID validation (if specified)
  - Deletion eligibility pre-check
  - Legal hold status verification

*Implementation considerations*:
- Design validation for fast rejection of invalid requests
- Implement efficient batch delete validation
- Create clear error messages for validation failures
- Support conditional delete operations
- Design for security-focused validation

### Authentication and Authorization Check

Verification of the requestor's identity and permissions to delete the specific object.

- **Authentication Processing**:
  - Credential validation (API keys, tokens)
  - Signature verification
  - Session validation
  - Authentication context capture
  - Multi-factor requirement checking for sensitive deletions

- **Authorization Evaluation**:
  - Policy resolution and evaluation
  - Delete permission verification
  - Bucket policy checking
  - IAM role/permission resolution
  - Special permission checks (MFA Delete)

- **Safety Controls**:
  - Delete protection verification
  - Compliance mode checking
  - Retention period evaluation
  - Legal hold verification
  - Deletion restriction enforcement

*Implementation considerations*:
- Design efficient permission caching
- Implement fast-path for common delete patterns
- Create comprehensive audit trail for deletion
- Support MFA delete verification
- Design for secure handling of deletion authority

### Versioning Check

The system must handle object versions according to configured versioning policies.

- **Versioning Status Determination**:
  - Bucket versioning state retrieval
  - Object version chain inspection
  - Current version identification
  - Version count verification
  - Delete marker presence check

- **Version-Specific Behavior**:
  - Version-specific delete (with version ID)
  - Delete marker creation (without version ID)
  - Delete marker on delete marker handling
  - Version chain modification
  - Current version pointer updates

- **Special Version Handling**:
  - Latest version restoration after delete
  - Multiple version deletion (batch)
  - Version pruning for lifecycle policies
  - Null version handling
  - Implicit version creation

*Implementation considerations*:
- Design clear versioning semantics for deletion
- Implement efficient version chain management
- Create appropriate delete marker handling
- Support various versioning configurations
- Design for atomic version state updates

### Metadata Update/Removal

Based on versioning status, the system either completely removes metadata or creates a delete marker.

- **Non-Versioned Objects**:
  - Complete metadata removal
  - Index updates for prefix operations
  - Storage location release
  - Reference count updates
  - Permission cache invalidation

- **Versioned Objects**:
  - Delete marker creation
  - Version chain updates
  - Current version pointer updates
  - Previous version preservation
  - Version count maintenance

- **Transaction Handling**:
  - Atomic metadata operations
  - Consistency level selection
  - Optimistic/pessimistic locking
  - Rollback capability for failures
  - Cross-region metadata synchronization

*Implementation considerations*:
- Design transactions appropriate for metadata consistency
- Implement efficient index updates
- Create clear versioning state transitions
- Support high concurrency delete operations
- Design for metadata-only operations in versioned buckets

### Asynchronous Physical Deletion

While metadata operations complete synchronously, physical data removal typically happens asynchronously.

- **Deletion Job Creation**:
  - Storage location identification
  - Deletion job queuing
  - Priority assignment
  - Grouping for batch efficiency
  - Resource impact assessment

- **Data Removal Process**:
  - Chunk identification and mapping
  - Replica coordination
  - Reference count verification
  - Secure deletion requirements
  - Storage space reclamation

- **Safety Mechanisms**:
  - Deletion delay periods
  - Soft delete implementation
  - Recovery window configurations
  - Backup verification before deletion
  - Multi-phase deletion for critical data

*Implementation considerations*:
- Design asynchronous deletion with clear guarantees
- Implement efficient batch processing
- Create appropriate safety mechanisms
- Support configurable deletion delays
- Design for resource-efficient physical deletion

### Garbage Collection Scheduling

Regular processes manage the cleanup of deleted data and associated resources.

- **GC Process Types**:
  - Delete marker cleanup
  - Orphaned chunk removal
  - Version pruning
  - Expired deletion delay processing
  - Incomplete multipart upload cleanup

- **Scheduling Approaches**:
  - Time-based scheduling
  - Space pressure-based triggering
  - Background priority configuration
  - Resource-aware scheduling
  - Maintenance window alignment

- **Resource Management**:
  - I/O throttling during GC
  - CPU/memory constraints
  - Background priority settings
  - Impact monitoring
  - Pause/resume capabilities

*Implementation considerations*:
- Design non-disruptive garbage collection
- Implement resource-aware scheduling
- Create clear metrics for cleanup backlog
- Support emergency cleanup for space recovery
- Design for minimal impact on foreground operations

### Event Notification

The system notifies interested applications about object deletion events.

- **Event Generation**:
  - Object deletion event formatting
  - Delete marker creation events
  - Permanent deletion notifications
  - Version-specific deletion events
  - Batch delete summarization

- **Notification Destinations**:
  - Queue-based notifications (SQS, Kafka)
  - Function triggers (Lambda, Azure Functions)
  - Webhook delivery
  - Internal system notifications
  - Metrics collection systems

- **Delivery Guarantees**:
  - At-least-once delivery semantics
  - Retry policies for failed notifications
  - Dead-letter handling
  - Event ordering preservation
  - Event filtering support

*Implementation considerations*:
- Design lightweight event generation
- Implement asynchronous notification delivery
- Create appropriate event schemas for deletion
- Support filtering at source
- Design for delivery guarantees appropriate to use case

## Special Deletion Scenarios

### Batch Delete Operations

Bulk deletion requests require special handling to manage large-scale removal efficiently.

- **Batch Processing**:
  - Multiple object key validation
  - Parallel permission checking
  - Atomic batch operation semantics
  - Partial success handling
  - Detailed result reporting

- **Optimizations**:
  - Metadata operation batching
  - Storage operation coalescing
  - Common prefix optimizations
  - Multi-phase parallel processing
  - Resource utilization management

- **Error Handling**:
  - Per-object error reporting
  - Continuation after partial failures
  - Retry strategies for transient errors
  - Comprehensive result aggregation
  - Client guidance for failed items

*Implementation considerations*:
- Design efficient parallel processing for batches
- Implement appropriate error aggregation
- Create clear success/failure reporting
- Support resumable batch operations
- Design for minimal impact during large batch processing

### Recursive Prefix Deletion

Deletion of all objects with a common prefix simulates directory removal in a hierarchical system.

- **Prefix Resolution**:
  - Prefix-based object enumeration
  - Pagination through large prefixes
  - Optimization for common patterns
  - Empty result handling
  - Common prefix aggregation

- **Processing Approach**:
  - Chunked processing for large collections
  - Progressive deletion with continuation
  - Parallel deletion operations
  - Progress tracking and reporting
  - Resumable operation support

- **Special Considerations**:
  - Prefix permission verification
  - Version handling for all objects
  - Delete marker creation consistency
  - Directory marker special handling
  - Concurrent modification handling

*Implementation considerations*:
- Design efficient prefix enumeration
- Implement chunked processing for large prefixes
- Create appropriate progress tracking
- Support cancellation of in-progress operations
- Design for consistency across the entire prefix

### Compliance and Retention

Objects under compliance controls or retention policies have special deletion restrictions.

- **Retention Verification**:
  - Retention period validation
  - Governance mode vs. compliance mode
  - Retention override permission checking
  - Extension-only enforcement
  - Time-based retention calculation

- **Legal Hold Processing**:
  - Legal hold presence detection
  - Hold removal authorization
  - Multiple hold coordination
  - Legal hold audit logging
  - Hold removal workflow

- **Compliance Mode Behavior**:
  - Strict immutability enforcement
  - Elevated permission requirements
  - Enhanced audit logging
  - Administrative bypass validation
  - Compliance metadata preservation

*Implementation considerations*:
- Design comprehensive retention enforcement
- Implement proper legal hold mechanisms
- Create detailed audit trails for compliance
- Support proper authorization for overrides
- Design for regulatory requirement satisfaction

## Performance Optimizations

### Metadata Efficiency

- **Index Optimization**:
  - Efficient deletion from indices
  - Minimized lock contention
  - Optimistic concurrency for versions
  - Batched index updates
  - Background cleanup for complex structures

- **Caching Considerations**:
  - Cache invalidation strategies
  - Negative caching for deleted objects
  - Delete propagation through cache layers
  - Cache update batching
  - Cache consistency during deletion

- **Storage Reclamation**:
  - Space reuse strategies
  - Fragmentation management
  - Storage compaction triggering
  - Delayed space reclamation
  - Background space optimization

*Implementation considerations*:
- Design efficient metadata removal processes
- Implement appropriate caching strategies
- Create space reclamation mechanisms
- Support background optimization
- Design for minimal disruption during deletions

### Physical Deletion Optimization

- **Batch Processing**:
  - Similar object coalescing
  - Location-based grouping
  - Storage-tier specific batching
  - I/O pattern optimization
  - Parallel execution management

- **Resource Management**:
  - Throttling and rate limiting
  - Priority-based scheduling
  - Background operation deprioritization
  - Resource constraint awareness
  - Adaptive scheduling based on load

- **Storage-Specific Optimization**:
  - SSD garbage collection coordination
  - HDD seek optimization
  - Archive storage special handling
  - Secure deletion for sensitive data
  - Media-specific deletion techniques

*Implementation considerations*:
- Design storage-appropriate deletion methods
- Implement efficient batch operations
- Create resource-aware scheduling
- Support priority-based execution
- Design for minimal disruption to foreground operations

## Error Handling and Recovery

### Common Failure Scenarios

- **Client-Side Failures**:
  - Connection termination
  - Timeout during batch operations
  - Client cancellation
  - Invalid deletion requests
  - Insufficient permissions

- **Server-Side Failures**:
  - Metadata inconsistency
  - Storage node unavailability
  - Transaction failures
  - Resource exhaustion
  - Internal service errors

- **Compliance Failures**:
  - Retention period violations
  - Legal hold restrictions
  - MFA delete requirement failures
  - Governance mode override failures
  - Compliance mode restriction violations

*Implementation considerations*:
- Design comprehensive error classification
- Implement appropriate error responses
- Create clear client guidance for deletion failures
- Support partial success for batch operations
- Design for proper security and compliance enforcement

### Recovery Mechanisms

- **Retry Strategies**:
  - Idempotent operation design
  - Exponential backoff implementation
  - Partial batch retry
  - Alternative path routing
  - Failure isolation

- **Rollback Capabilities**:
  - Transaction rollback for metadata
  - Soft delete recovery options
  - Delete marker reversal
  - Version restoration
  - Audit trail for recovery operations

- **Administrative Recovery**:
  - Emergency restoration tools
  - Forensic recovery capabilities
  - Compliance override processes
  - Bulk recovery operations
  - Cross-region recovery coordination

*Implementation considerations*:
- Design proper retry mechanisms
- Implement soft delete with recovery options
- Create clear audit trails for all deletions
- Support emergency recovery processes
- Design for compliance-aware recovery

The deletion path, while conceptually simple, involves complex considerations around versioning, physical resource reclamation, compliance, and performance. A well-implemented deletion path ensures reliable object removal while maintaining system integrity, compliance requirements, and operational efficiency.​​​​​​​​​​​​​​​​
