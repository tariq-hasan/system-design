# Metadata Service

The Metadata Service forms the "brain" of the blob store system, managing all information about stored objects while separating logical representation from physical storage.

## Level 1: Key Concepts

- **Object Registry**: Maintains authoritative record of all objects in the system
- **Location Mapping**: Translates logical object paths to physical storage locations
- **Index Management**: Provides efficient lookup and listing capabilities
- **Attribute Storage**: Keeps object properties and user-defined metadata
- **Versioning Support**: Tracks multiple versions of the same object

## Level 2: Implementation Details

### Core Metadata Elements

The service maintains several critical data elements for each object:

| Metadata Type | Examples | Purpose |
|---------------|----------|---------|
| System Metadata | Size, creation time, content-type | Core object properties |
| Storage Metadata | Physical location, chunk map, replication status | Enables data retrieval |
| Security Metadata | Owner, ACLs, encryption details | Enforces access control |
| Integrity Metadata | Checksums, ETags, version identifiers | Verifies data integrity |
| User Metadata | Custom key-value pairs, tags | Application-specific attributes |

### Database Technology Choices

The metadata service typically employs different database technologies for different requirements:

- **Primary Object Metadata**: NoSQL databases (DynamoDB, Cassandra)
  - Optimized for key-based lookups and horizontal scaling
  - Provides predictable low-latency regardless of dataset size
  - Handles billions of objects with consistent performance

- **Secondary/Analytics Metadata**: Relational databases (PostgreSQL)
  - Supports complex queries for reporting and management
  - Enables rich indexing for multi-attribute searches
  - Provides ACID transactions for administrative operations

### Indexing Strategies

Efficient metadata retrieval requires specialized indexing approaches:

- **Prefix-Based Indexing**: Using B-trees or LSM-trees to support hierarchical navigation
- **Multi-Attribute Indexing**: For filtering by size, type, or timestamp
- **Inverted Indexes**: For tag-based or content-type searches
- **Composite Key Design**: Optimizing for common query patterns

### Caching Architecture

The service employs multi-level caching to reduce database load:

- **In-Memory Cache**: For hot objects and recent queries
- **Distributed Cache**: For scalable caching across service instances
- **Write-Through Design**: Updates propagate immediately to backing stores
- **Expiration Policies**: Based on access patterns and consistency requirements

## Level 3: Technical Deep Dives

### Consistency Model Design

The metadata service implements a carefully designed consistency model:

- **Strong Consistency**: For single-object operations (GET/PUT/DELETE)
- **Eventual Consistency**: For list operations with high scalability requirements
- **Causal Consistency**: For versioned objects and sequential operations
- **Read-After-Write Consistency**: Guaranteed for object creators

These consistency levels must be balanced against performance, availability, and partition tolerance per the CAP theorem.

### Sharding and Partitioning Strategy

For massive scale, metadata is distributed across multiple database instances:

1. **Bucket-Level Sharding**: Each bucket's metadata on dedicated shards
2. **Key-Based Partitioning**: Within buckets, objects distributed by key hash
3. **Hierarchical Partitioning**: Prefix-aware sharding for balanced distribution
4. **Dynamic Repartitioning**: Automatic adjustment for hot partitions

This approach must handle skewed access patterns and ensure even distribution despite varying object key patterns.

### Versioning Implementation

Object versioning requires specialized data structures:

```
/bucket/key (logical key)
  └── v1 (creation_time=T1, deleted=false)
  └── v2 (creation_time=T2, deleted=false)
  └── v3 (creation_time=T3, deleted=true)  # Deletion marker
  └── v4 (creation_time=T4, deleted=false)
```

The service maintains:
- Version chains with linked-list or tree structures
- Efficient latest-version lookups
- Version pruning capabilities for lifecycle management
- Special handling for deletion markers

### Metadata Synchronization Challenges

In distributed environments, metadata synchronization presents challenges:

- **Multi-Region Replication**: Strategies for cross-region consistency
- **Conflict Resolution**: Handling simultaneous updates to the same object
- **Repair Mechanisms**: Detecting and fixing metadata inconsistencies
- **Background Reconciliation**: Periodic verification against physical storage

These synchronization processes are critical for maintaining system integrity in the face of network partitions, server failures, and concurrent modifications.​​​​​​​​​​​​​​​​
