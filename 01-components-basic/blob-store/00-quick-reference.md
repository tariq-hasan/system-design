# Blob Store

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
- Images, videos, audio files
- Documents, PDFs, office files
- Application backups and snapshots
- Log files and application metrics
- Data lake contents
- Machine learning models and datasets

**Key Characteristics:**
- Massive scalability (exabytes+)
- High durability (99.999999999%)
- Simple REST APIs (GET/PUT/DELETE)
- Metadata-rich object storage
- Content-agnostic data handling

**Popular Examples:** 
- Amazon S3 (Simple Storage Service)
- Google Cloud Storage
- Azure Blob Storage
- MinIO (open-source)
- Cloudflare R2
- Backblaze B2

**Distinctions from Other Storage:**
- vs. File Systems: No true hierarchy, immutable objects, HTTP access
- vs. Block Storage: Higher-level abstraction, rich metadata, not mountable
- vs. Databases: No query language, 10-100x cheaper for large data, no transactions

## 2. Use Cases

- **Media Content Delivery**: Store and serve content (videos, images), integrate with CDNs, support byte-range requests for streaming
  
- **Data Backup & Archiving**: Long-term retention with versioning, 80-90% cost reduction vs. block storage, object locking for compliance

- **Log & Metrics Storage**: Scale for unpredictable volume (1+ TB daily), time-based partitioning, compression formats (Parquet/ORC)

- **Data Lakes**: Separate storage from compute, schema-on-read flexibility, integration with analytics tools (Spark, Presto)

- **Static Website Hosting**: Serverless delivery with 99.99% availability, CDN integration, automatic scaling, built-in SSL/TLS

- **Mobile/IoT App Data**: Handle intermittent connectivity, support multipart uploads, client-side buffering, edge preprocessing

- **AI/ML Model Storage**: Version models (1-10GB each) and datasets, centralized management, metadata for lineage tracking

- **Collaborative Workflows**: Share large assets (terabytes) between teams, versioning, fine-grained access controls

## 3. Functional Requirements

- **Object Operations**:
  - Upload objects (PUT): checksumming, content validation, ETag generation, encryption
  - Download objects (GET): conditional requests, byte-range support, streaming optimization
  - Delete objects (DELETE): atomic operations, soft-delete options, bulk operations
  - List objects (LIST): pagination, prefix filtering, delimiter-based hierarchy

- **Metadata Management**:
  - Custom metadata: key-value pairs (2-4KB limit), system metadata, searchable attributes
  - Object tagging: tag-based access policies, cost allocation, bulk tagging (10-50 tags/object)

- **Organization**:
  - Buckets/containers: globally unique names, region specification, policy attachment
  - Hierarchical structure: delimiter-based navigation ('/'), prefix aggregation, path permissions

- **Advanced Features**:
  - Object versioning: version IDs, deletion markers, MFA Delete protection
  - Lifecycle policies: storage class transitions, expiration rules, version pruning
  - Pre-signed URLs: timed access (seconds to days), IP restrictions, operation limitations
  - Multipart uploads: 5MB-5GB parts, resumable transfers, concurrent uploads
  - Event notifications: filterable triggers, messaging integration (SNS, SQS, webhooks)
  - Cross-region replication: selective replication, conflict resolution, metadata sync
  - Batch operations: async job model, operation manifests, completion reports
  - Object locking: WORM storage, governance/compliance modes, legal holds
