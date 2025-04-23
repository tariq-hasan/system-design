# Blob Store System Design

## Table of Contents
- [1. Overview](#1-overview)
- [2. Use Cases](#2-use-cases)
- [3. Functional Requirements](#3-functional-requirements)
- [4. Non-Functional Requirements](#4-non-functional-requirements)
- [5. High-Level Architecture](#5-high-level-architecture)
- [6. Core Components](#6-core-components)
  - [6.1 API Service](#61-api-service)
  - [6.2 Metadata Service](#62-metadata-service)
  - [6.3 Object Storage Layer](#63-object-storage-layer)
  - [6.4 Authentication & Authorization](#64-authentication--authorization)
  - [6.5 Optional Components](#65-optional-components)
- [7. Storage Design](#7-storage-design)
  - [7.1 Object Key Format](#71-object-key-format)
  - [7.2 Physical Storage Options](#72-physical-storage-options)
  - [7.3 Data Organization](#73-data-organization)
- [8. Data Integrity & Durability](#8-data-integrity--durability)
  - [8.1 Checksums](#81-checksums)
  - [8.2 Replication Strategies](#82-replication-strategies)
  - [8.3 Failure Recovery](#83-failure-recovery)
- [9. Performance Optimization](#9-performance-optimization)
  - [9.1 Write Path](#91-write-path)
  - [9.2 Read Path](#92-read-path)
  - [9.3 Metadata Optimization](#93-metadata-optimization)
- [10. Access Control & Security](#10-access-control--security)
  - [10.1 Authentication Methods](#101-authentication-methods)
  - [10.2 Authorization Models](#102-authorization-models)
  - [10.3 Data Protection](#103-data-protection)
  - [10.4 Security Features](#104-security-features)
- [11. Scalability Approaches](#11-scalability-approaches)
  - [11.1 Horizontal Scaling](#111-horizontal-scaling)
  - [11.2 Capacity Planning](#112-capacity-planning)
  - [11.3 Hot Spot Mitigation](#113-hot-spot-mitigation)
- [12. Operational Aspects](#12-operational-aspects)
  - [12.1 Monitoring & Alerting](#121-monitoring--alerting)
  - [12.2 Maintenance Operations](#122-maintenance-operations)
  - [12.3 Failure Handling](#123-failure-handling)
- [13. Lifecycle Management](#13-lifecycle-management)
  - [13.1 Data Lifecycle Policies](#131-data-lifecycle-policies)
  - [13.2 Storage Classes](#132-storage-classes)
- [14. Advanced Features](#14-advanced-features)
  - [14.1 Versioning](#141-versioning)
  - [14.2 Object Locking](#142-object-locking)
  - [14.3 Event Notifications](#143-event-notifications)
  - [14.4 Static Website Hosting](#144-static-website-hosting)
- [15. Challenges and Considerations](#15-challenges-and-considerations)
  - [15.1 Consistency Models](#151-consistency-models)
  - [15.2 Global Distribution](#152-global-distribution)
  - [15.3 Cost Optimization](#153-cost-optimization)
- [16. Interview Discussion Points](#16-interview-discussion-points)
- [17. System Design Diagrams](#17-system-design-diagrams)
  - [17.1 Upload Flow](#171-upload-flow)
  - [17.2 Download Flow](#172-download-flow)
  - [17.3 Pre-signed URL Generation](#173-pre-signed-url-generation)
  - [17.4 Data Placement and Replication](#174-data-placement-and-replication)
- [18. Specific Implementations](#18-specific-implementations)

## 1. Overview

A **Blob Store** (Binary Large Object Store) is a distributed storage service optimized for storing and retrieving large, unstructured data objects such as:
- Images and videos
- Audio files
- Documents and PDFs
- Application backups
- Log files
- Data lake contents

**Popular Examples:** 
- Amazon S3 (Simple Storage Service)
- Google Cloud Storage
- Azure Blob Storage
- MinIO (open-source)

## 2. Use Cases

- **Media Content Delivery**: Store user-generated content, streaming media
- **Data Backup & Archiving**: Long-term retention of application backups
- **Log & Metrics Storage**: Collect and analyze application/system logs
- **Data Lakes**: Store raw data for analytics processing
- **Static Website Hosting**: Serve HTML, CSS, and JavaScript files
- **Mobile/IoT App Data**: Store data generated from mobile/IoT devices

## 3. Functional Requirements

- **Object Operations**:
  - Upload objects (PUT)
  - Download objects (GET)
  - Delete objects (DELETE)
  - List objects by prefix/bucket
- **Metadata Management**:
  - Store and retrieve custom metadata
  - Object tags for organization
- **Organization**:
  - Group objects into buckets/containers
  - Support for folder-like hierarchies
- **Advanced Features**:
  - Object versioning
  - Lifecycle policies (automatic deletion, archival)
  - Pre-signed URLs for temporary access
  - Multipart uploads for large files

## 4. Non-Functional Requirements

- **Durability**: 99.999999999% (11 9's) - virtually no data loss
- **Availability**: 99.99% uptime (four 9's)
- **Scalability**: Support for billions of objects and exabytes of data
- **Performance**:
  - Low latency for frequent access patterns
  - High throughput for batch operations
- **Security**:
  - Data encryption (at rest and in transit)
  - Fine-grained access control
  - Audit logging
- **Cost Efficiency**: Optimize storage and bandwidth costs

## 5. High-Level Architecture

```
┌─────────────────────┐
│                     │
│    Client Apps      │
│                     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│                     │
│  Load Balancer /    │
│   API Gateway       │
│                     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│                     │
│   API Service       │◄──────┐
│                     │       │
└──────────┬──────────┘       │
           │                  │
           ▼                  │
┌──────────┴──────────┐       │
│                     │       │
│  Metadata Service   │       │
│                     │       │
└──────────┬──────────┘       │
           │                  │
           ├───────────┬──────┘
           │           │
           ▼           ▼
┌─────────────┐ ┌─────────────┐
│             │ │             │
│ Object      │ │ Auth &      │
│ Storage     │ │ Security    │
│             │ │             │
└──────┬──────┘ └──────┬──────┘
       │               │
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│             │ │             │
│ CDN         │ │ Monitoring  │
│ (Optional)  │ │ & Logging   │
│             │ │             │
└─────────────┘ └─────────────┘
```

## 6. Core Components

### 6.1 API Service
- Handles RESTful API endpoints (PUT, GET, DELETE, LIST)
- Authenticates and authorizes requests
- Implements rate limiting and throttling
- Generates pre-signed URLs for temporary access
- Orchestrates storage operations across components

### 6.2 Metadata Service
- Stores object metadata:
  - Object name, size, content type
  - Creation/modification timestamps
  - Checksums and version IDs
  - Custom user metadata
- Maps logical object paths to physical storage locations
- Implements indexing for fast lookups and prefix searches
- **Database Options**:
  - NoSQL (DynamoDB, Cassandra): For horizontal scalability
  - Relational (PostgreSQL): For complex queries and relationships

### 6.3 Object Storage Layer
- Stores actual binary data of objects
- Breaks large files into multiple chunks
- Implements data placement policies
- Handles replication across availability zones/regions
- Manages garbage collection for deleted objects
- **Implementation Options**:
  - Custom distributed file system
  - Block storage with custom metadata layer
  - Commodity hardware with erasure coding

### 6.4 Authentication & Authorization
- Validates access credentials
- Enforces bucket and object-level permissions
- Integrates with identity providers (OIDC, SAML)
- Implements security policies (CORS, bucket policies)

### 6.5 Optional Components
- **Content Delivery Network (CDN)**:
  - Caches frequently accessed objects at edge locations
  - Reduces latency for global users
- **Chunking Service**:
  - Splits large objects into manageable pieces
  - Enables parallel uploads/downloads
  - Facilitates deduplication
- **Event Notification Service**:
  - Publishes events for object operations
  - Enables serverless workflows

## 7. Storage Design

### 7.1 Object Key Format
```
/<bucket_name>/<optional_prefix>/<object_key>[?versionId=<version>]
```

### 7.2 Physical Storage Options
- **Direct Filesystem**: Simple but limited scalability
- **Distributed File System**: HDFS, GlusterFS, Ceph
- **Cloud Provider Storage**: S3, GCS, Azure Blob
- **Custom Solution**: 
  - Data nodes with local storage
  - Object splitting and distribution

### 7.3 Data Organization
- **Flat Namespace per Bucket**: 
  - No actual "folders" (just key prefixes)
  - Avoids hierarchical bottlenecks
- **Sharding Strategy**:
  - Hash-based partitioning by object key
  - Consistent hashing for balanced distribution
  - Geographic partitioning for locality

## 8. Data Integrity & Durability

### 8.1 Checksums
- Compute cryptographic hashes (MD5, SHA-256) during upload
- Verify integrity on download and during background checks
- Store checksums with metadata

### 8.2 Replication Strategies
- **Simple Replication**:
  - Store multiple copies (typically 3+) across failure domains
  - Synchronous vs. asynchronous replication tradeoffs
- **Erasure Coding**:
  - Split data into k data chunks and m parity chunks
  - Reconstruct data from any k chunks (out of k+m)
  - Better storage efficiency than replication
  - Example: 10+4 coding (40% overhead vs. 200% for 3x replication)

### 8.3 Failure Recovery
- Continuous background verification processes
- Automatic repair of corrupted/lost chunks
- Cross-region replication for disaster recovery

## 9. Performance Optimization

### 9.1 Write Path
- **Multipart Uploads**:
  - Break large files into smaller parts (e.g., 5MB-5GB)
  - Enable parallel uploads and resumability
- **Write Buffering**:
  - Accept writes to memory/SSD buffer first
  - Asynchronously persist to permanent storage
- **Content-Based Deduplication**:
  - Detect identical chunks using checksums
  - Store single copy and update reference counts

### 9.2 Read Path
- **Read-Ahead**: Prefetch subsequent chunks
- **Caching**:
  - In-memory cache for hot objects
  - SSD cache tier for warm objects
  - CDN for globally distributed access
- **Range Requests**:
  - Support partial content retrieval (HTTP Range header)
  - Especially important for video streaming

### 9.3 Metadata Optimization
- **Denormalization**: Store frequently accessed metadata together
- **Caching**: In-memory caching of popular object metadata
- **Indexing**: B-tree or LSM-tree indexes for prefix queries

## 10. Access Control & Security

### 10.1 Authentication Methods
- **API Keys**: Simple access/secret key pairs
- **OAuth/OIDC**: Integration with identity providers
- **STS**: Temporary credentials with limited permissions

### 10.2 Authorization Models
- **IAM Policies**: JSON documents defining permissions
- **ACLs**: Per-object access control lists
- **Bucket Policies**: Rules applied at the bucket level

### 10.3 Data Protection
- **Encryption at Rest**:
  - Server-side encryption with service-managed keys
  - Server-side encryption with customer-managed keys
  - Client-side encryption (zero knowledge)
- **Encryption in Transit**:
  - TLS for all API connections
  - Secure transfer protocols

### 10.4 Security Features
- **Object Lock**: Prevent deletion for compliance
- **Versioning**: Protect against accidental overwrites
- **Access Logs**: Track all access to objects
- **VPC Endpoints**: Private connectivity without internet

## 11. Scalability Approaches

### 11.1 Horizontal Scaling
- **Stateless API Tier**: Add more API servers as needed
- **Metadata Tier**: 
  - Database sharding/partitioning
  - Read replicas for query scaling
- **Storage Tier**: 
  - Add more storage nodes
  - Auto-rebalancing when adding capacity

### 11.2 Capacity Planning
- **Overprovisioning**: Maintain headroom for traffic spikes
- **Auto-Scaling**: Dynamically adjust resources based on load
- **Storage Expansion**: Seamless addition of new storage nodes

### 11.3 Hot Spot Mitigation
- **Key Space Partitioning**: Avoid sequential keys causing hotspots
- **Load-Based Routing**: Direct traffic based on node capacity
- **Caching Popular Objects**: Reduce pressure on storage nodes

## 12. Operational Aspects

### 12.1 Monitoring & Alerting
- **Metrics to Track**:
  - Request latency (p50, p90, p99)
  - Error rates
  - Storage utilization
  - Node health
- **Alerting**: Proactive notification of anomalies

### 12.2 Maintenance Operations
- **Rebalancing**: Redistribute data when adding/removing nodes
- **Garbage Collection**: Clean up deleted and orphaned objects
- **Compaction**: Consolidate fragmented storage space

### 12.3 Failure Handling
- **Retry Logic**: Exponential backoff for transient failures
- **Circuit Breakers**: Prevent cascading failures
- **Degraded Operation Modes**: Continue service with reduced functionality

## 13. Lifecycle Management

### 13.1 Data Lifecycle Policies
- **Transition Rules**: Move data between storage tiers
  - Hot → Warm → Cold → Archive
- **Expiration Rules**: Automatically delete data
- **Versioning Policies**: Prune old versions

### 13.2 Storage Classes
- **Standard**: Frequent access, highest availability
- **Infrequent Access**: Lower cost, slight retrieval penalty
- **Archival**: Lowest cost, high retrieval latency

## 14. Advanced Features

### 14.1 Versioning
- Keep multiple versions of objects
- Automatic version number assignment
- Version-specific operations (retrieve, delete)

### 14.2 Object Locking
- WORM (Write Once Read Many) capabilities
- Legal hold and retention settings
- Compliance with regulations (SEC, FINRA)

### 14.3 Event Notifications
- Generate events on object operations
- Integrate with message queues (SQS, Kafka)
- Trigger serverless functions (Lambda)

### 14.4 Static Website Hosting
- Serve HTML, CSS, JS directly from blob store
- Custom domains and routing rules
- Index document and error page configuration

## 15. Challenges and Considerations

### 15.1 Consistency Models
- **Strong Consistency**: All reads reflect latest writes
  - Higher latency, more coordination required
- **Eventual Consistency**: Reads may not reflect recent writes
  - Better performance, simpler implementation
- **Read-After-Write Consistency**: Compromise approach

### 15.2 Global Distribution
- **Geo-Replication**: Copy data across regions
- **Latency Challenges**: Speed of light limitations
- **Regulatory Compliance**: Data residency requirements

### 15.3 Cost Optimization
- **Storage Tiering**: Match access patterns to storage class
- **Compression**: Reduce storage footprint
- **Traffic Management**: Reduce egress costs

## 16. Interview Discussion Points

- How would you handle very large files (100GB+)?
- What are the trade-offs between replication and erasure coding?
- How would you implement consistent listing operations?
- What strategies would you use to prevent data corruption?
- How would you design the system to recover from major outages?
- How would you optimize for cost vs. performance?
- How would you implement global access with low latency?
- What security measures would you implement?

## 17. System Design Diagrams

### 17.1 Upload Flow

```
┌──────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│  Client  │────▶│ API Service│────▶│ Auth Check │────▶│ Validation │
└──────────┘     └────────────┘     └────────────┘     └──────┬─────┘
                                                              │
                                                              ▼
┌──────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│ Complete │◀────│ Update     │◀────│ Store Data │◀────│ Generate   │
│ Response │     │ Metadata   │     │ Chunks     │     │ Checksums  │
└──────────┘     └────────────┘     └────────────┘     └────────────┘
```

### 17.2 Download Flow

```
┌──────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│  Client  │────▶│ API Service│────▶│ Auth Check │────▶│ Metadata   │
└──────────┘     └────────────┘     └────────────┘     │ Lookup     │
                                                       └──────┬─────┘
                                                              │
                                                              ▼
┌──────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│  Return  │◀────│ Verify     │◀────│ Retrieve   │◀────│ Locate     │
│  Object  │     │ Checksums  │     │ Data Chunks│     │ Chunks     │
└──────────┘     └────────────┘     └────────────┘     └────────────┘
```

### 17.3 Pre-signed URL Generation

```
┌──────────┐     ┌────────────┐     ┌────────────┐
│  Client  │────▶│ API Service│────▶│ Auth Check │
└──────────┘     └────────────┘     └────────────┘
                                          │
                                          ▼
┌──────────┐     ┌────────────┐     ┌────────────┐
│  Return  │◀────│ Generate   │◀────│ Apply      │
│  URL     │     │ Signature  │     │ Permissions│
└──────────┘     └────────────┘     └────────────┘
```

### 17.4 Data Placement and Replication

```
                  ┌────────────────────────────┐
                  │      Object Key Hash       │
                  └──────────────┬─────────────┘
                                 │
                                 ▼
           ┌───────────────────────────────────────┐
           │        Consistent Hash Ring          │
           └───────────────────┬───────────────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
         ┌───────────┐  ┌───────────┐  ┌───────────┐
         │ Data Node │  │ Data Node │  │ Data Node │
         │    # 1    │  │    # 2    │  │    # 3    │
         └───────────┘  └───────────┘  └───────────┘
```

## 18. Specific Implementations

| Feature           | AWS S3             | Google Cloud Storage | Azure Blob Storage     |
|-------------------|--------------------|-----------------------|------------------------|
| Storage Classes   | Standard, IA, Glacier | Standard, Nearline, Coldline | Hot, Cool, Archive |
| Consistency       | Strong             | Strong                | Strong                |
| Max Object Size   | 5TB                | 5TB                   | 4.75TB                |
| Versioning        | Yes                | Yes                   | Yes                   |
| Encryption        | SSE-S3, SSE-KMS, SSE-C | Google-managed, Customer-managed | Azure-managed, Customer-managed |
| Event Notifications | SNS, SQS, Lambda  | Pub/Sub, Cloud Functions | Event Grid, Functions |
| Pricing Model     | Storage + Requests + Data Transfer | Storage + Requests + Data Transfer | Storage + Requests + Data Transfer |
