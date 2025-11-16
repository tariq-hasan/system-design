# Object Key Format

The blob store's object key format defines how objects are uniquely identified and addressed within the system.

## Level 1: Key Concepts

- **Hierarchical Naming Structure**: Logical organization of objects
- **URI-Compatible Format**: Enables RESTful addressing
- **Versioning Support**: Optional identification of specific object versions
- **Flat Namespace with Prefix Illusion**: Creates folder-like organization without actual folders

## Level 2: Implementation Details

### Standard Format Structure

```
/<bucket_name>/<optional_prefix>/<object_key>[?versionId=<version>]
```

#### Components Explained:

| Component | Description | Example |
|-----------|-------------|---------|
| **bucket_name** | Top-level container for objects | `user-uploads` |
| **optional_prefix** | Path-like segments for organization | `images/2023/vacation/` |
| **object_key** | Unique identifier for the object within prefix | `beach-sunrise.jpg` |
| **versionId** | Optional parameter identifying a specific version | `v2` or `a1b2c3d4` |

### Key Format Constraints

- **Bucket Names**:
  - Globally unique across the system
  - 3-63 characters (typically)
  - DNS-compatible naming (lowercase, no special characters except hyphens)
  - Cannot be IP address formatted

- **Key Names**:
  - Maximum length: Typically 1024-4096 characters
  - UTF-8 encoding support
  - Special character handling (URL encoding for special characters)
  - Case-sensitive

- **Prefixes**:
  - Not structurally different from object keys
  - Delimited by forward slashes (/)
  - Create virtual folder hierarchy
  - No formal definition or creation step required

### Versioning Format

When versioning is enabled:
- Each object can have multiple versions
- Latest version is returned by default
- Specific versions accessed via versionId parameter
- Special version designations may include:
  - `null` - for pre-versioning objects
  - `latest` - explicit request for current version
  - System-generated unique identifiers (UUID, timestamp-based)

## Level 3: Technical Deep Dives

### Virtual Hierarchies Without Folders

Unlike traditional file systems, blob stores don't have actual folder objects or inode structures:

```
Traditional filesystem:
├── Documents (folder)
│   ├── Work (folder)
│   │   └── report.pdf (file)
│   └── Personal (folder)
│       └── budget.xlsx (file)

Blob store:
└── documents/work/report.pdf (object)
└── documents/personal/budget.xlsx (object)
```

This approach eliminates:
- Directory size limitations
- Directory listing performance bottlenecks
- Inode exhaustion issues
- Directory lock contention

But requires efficient prefix-based querying mechanisms.

### Performance Implications of Key Design

Different key naming strategies have significant performance implications:

1. **Sequential Keys** (e.g., timestamp-based):
   - Potential for write hotspots on specific partitions
   - Better read locality for time-series data
   - Good for time-ordered access patterns

2. **Randomized Keys** (e.g., UUID-based):
   - Better write distribution
   - Worse locality for related objects
   - Less efficient caching behavior

3. **Hybrid Approaches**:
   - Timestamp prefixes with random suffixes
   - Shard indicators in prefixes
   - Reverse timestamp elements for better distribution

The choice significantly impacts scalability and requires careful consideration based on workload characteristics.

### Prefix Optimization for Common Access Patterns

Strategic prefix design enhances performance for specific use cases:

```
// Multi-tenant isolation
/tenant123/data/...

// Time-series data with reverse timestamps for distribution
/logs/2023-04-28/region-west/...

// User data with balanced sharding
/user_data/shard042/user123456/...

// Media with format-based organization
/images/original/2023/04/image123.jpg
/images/thumbnails/2023/04/image123.jpg
```

Advanced designs consider:
- Expected query patterns
- Cache efficiency
- Data lifecycle management
- Access control boundaries
- Potential for hotspots

The right prefix strategy can significantly improve system performance while providing intuitive organization for users.​​​​​​​​​​​​​​​​
