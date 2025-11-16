# 7.1 Object Key Format

The object key format defines how objects are uniquely identified and addressed within a blob storage system. A well-designed key format enables efficient object retrieval, logical organization, and compatibility with various access patterns.

## Key Structure and Syntax

### Standard Format
```
/<bucket_name>/<optional_prefix>/<object_key>[?versionId=<version>]
```

- **Bucket Name**: The top-level namespace container
  - Globally unique across the entire storage system
  - Usually 3-63 characters, lowercase alphanumeric, hyphens
  - Cannot begin or end with hyphens
  - Cannot contain uppercase, underscores, or special characters
  - Must not be formatted as an IP address

- **Optional Prefix**: Path-like structure for logical organization
  - Simulates a directory hierarchy through naming convention
  - Typically ends with a delimiter character (usually `/`)
  - No actual physical hierarchy or folders in the underlying storage
  - Used for listing, permission grouping, and logical organization
  - Common pattern: `/<year>/<month>/<day>/` or `/<department>/<project>/`

- **Object Key**: The unique identifier for the object within the bucket
  - Can include alphanumeric characters, special characters with some restrictions
  - Length limitations (typically 1-1024 bytes after URL encoding)
  - Case-sensitive identifiers
  - Special characters require URL encoding when accessed via HTTP

- **Version Identifier**: Optional component to access specific versions
  - Provided as a query parameter `?versionId=<version>`
  - System-generated unique identifier for each version
  - Typically UUID or other unique string format
  - Required only when accessing non-current versions

### URL Representation
When accessed via HTTP/HTTPS, the object key is represented as:

```
https://[endpoint]/[bucket_name]/[optional_prefix]/[object_key][?versionId=version]
```

Alternatively, using virtual-hosted style:

```
https://[bucket_name].[endpoint]/[optional_prefix]/[object_key][?versionId=version]
```

## Namespace Characteristics

### Flat Namespace with Logical Hierarchy
- Blob storage uses a **flat namespace** despite the hierarchical appearance
- No actual folder objects exist in the storage backend
- The hierarchy is simulated through key naming conventions and delimiter usage
- Listing operations use prefix filtering and delimiter-based grouping
- Common prefixes are aggregated to simulate folder listings

*Implementation considerations*:
- Design efficient prefix indexing for fast listing
- Implement delimiter-based common prefix aggregation
- Create logical permission boundaries based on prefixes
- Support folder-like operations despite flat architecture
- Design for efficient metadata retrieval by prefix

### Delimiter Usage
- Forward slash (`/`) is the standard delimiter for path-like hierarchies
- Delimiter is used by listing operations to group common prefixes
- Multiple consecutive delimiters are preserved (`/a//b/` is different from `/a/b/`)
- Empty segments between delimiters are valid parts of the key
- Trailing delimiters can be significant (affecting listing operations)

*Implementation considerations*:
- Implement consistent delimiter handling across operations
- Design clear semantics for trailing delimiters
- Create efficient handling for consecutive delimiters
- Support different delimiter characters (while `/` is standard)
- Design for compatibility with file system path conventions

### Version Identification
- Versions are identified through a query parameter rather than in the path
- Current (latest) version is accessed without version parameter
- Historical versions require explicit version identifier
- Delete markers are special version objects marking deletion
- Version chains are maintained per distinct object key

*Implementation considerations*:
- Design efficient version chain lookup
- Implement clear "current version" semantics
- Create intuitive version listing capabilities
- Support version-specific metadata operations
- Design for efficient version garbage collection

## Key Design Best Practices

### Performance Considerations
- **Avoid Sequential Key Patterns**: Sequentially named keys (timestamp prefixes, incrementing numbers) can create storage hotspots
  - Bad: `/logs/2023-04-01/log1.txt`, `/logs/2023-04-01/log2.txt`
  - Better: Add high-cardinality prefix or suffix: `/logs/shard-17/2023-04-01/log1.txt`

- **High-Cardinality Distribution**: Ensure keys distribute evenly across storage partitions
  - Use hash-based prefixes: `/a871/user/profile.jpg` instead of `/user/profile.jpg`
  - Introduce randomness for sequential data: `/logs-${random(0-9)}/2023-04-01/`

- **Key Length Optimization**: Balance between descriptive keys and performance
  - Very long keys increase metadata overhead
  - Very short keys may lack context and organization
  - Target 20-200 characters for most use cases

*Implementation considerations*:
- Design key generation patterns that avoid hotspots
- Implement client-side hashing for high-volume uploads
- Create key naming conventions for common use cases
- Support key renaming/relocation capabilities
- Design for range-based listing efficiency

### Organization Strategies
- **Date-Based Prefixes**: Time-series data organization
  - Standard: `/<year>/<month>/<day>/`
  - Reverse: `/day=01/month=04/year=2023/` (for partition pruning)
  - ISO format: `/2023-04-01/` (for simpler sorting)

- **Resource-Based Paths**: Entity-centric organization
  - Resource type: `/users/profiles/`, `/users/documents/`
  - Resource ID: `/users/123/profile.jpg`, `/users/123/documents/report.pdf`
  - Domain-driven: `/<tenant>/<domain>/<entity>/<id>/`

- **Application-Based Segmentation**: Separate application data
  - By app: `/app-name/environment/resource-type/`
  - By environment: `/prod/app-name/resource-type/`
  - By function: `/static-assets/app-name/`, `/user-data/app-name/`

*Implementation considerations*:
- Design patterns appropriate for data access patterns
- Implement conventions for common data types
- Create documentation for organization standards
- Support easy migration between organization schemes
- Design for appropriate security boundaries

### URL Encoding and Special Characters
- Most special characters require URL encoding in HTTP requests
- Some characters have special handling requirements:
  - Forward slash (`/`) - Used as delimiter, but valid in key names when encoded
  - Ampersand (`&`) - Used for query parameters, must be encoded in keys
  - Question mark (`?`) - Separates query parameters, must be encoded
  - Spaces - Should be encoded as `%20` (not `+` which is ambiguous)
  - Control characters - Generally not allowed even when encoded
  - Non-ASCII Unicode - Supported when properly UTF-8 encoded

- Restricted characters (even with encoding):
  - Control characters (0x00-0x1F, 0x7F)
  - Backslash in some implementations
  - Certain Unicode ranges in some implementations

*Implementation considerations*:
- Design consistent character encoding handling
- Implement proper validation of key names
- Create clear documentation on character restrictions
- Support international character sets where needed
- Design for interoperability with web and file systems

## Implementation Examples

### Path-Style (S3-compatible) Example
```
# Single object
/mybucket/documents/2023/financial-report.pdf

# Versioned object
/mybucket/documents/2023/financial-report.pdf?versionId=3a5c1f82-1d3e-4567-8a4b

# Object with special characters (shown unencoded for readability)
/mybucket/product photos/camera#2-$199.99.jpg

# Same object with proper URL encoding for HTTP access
/mybucket/product%20photos/camera%232-%24199.99.jpg
```

### Virtual-Hosted Style Example
```
# Single object
https://mybucket.blob.example.com/documents/2023/financial-report.pdf

# Versioned object
https://mybucket.blob.example.com/documents/2023/financial-report.pdf?versionId=3a5c1f82-1d3e-4567-8a4b

# Object with URL encoding
https://mybucket.blob.example.com/product%20photos/camera%232-%24199.99.jpg
```

## Common Patterns and Anti-Patterns

### Effective Patterns
- **Low-to-high cardinality**: `/department/project/user/timestamp-uuid.file`
- **Hash distribution**: `/hash-prefix/logical-path/object.file`
- **Consistent naming**: Standardized conventions across applications
- **Semantic paths**: Keys that encode meaning and context
- **Search-friendly**: Keys designed for common prefix queries

### Anti-Patterns to Avoid
- **Timestamp-prefixed keys**: `/2023-04-01-12-30-45-user123.log` creates hotspots
- **Extremely deep hierarchies**: `/a/b/c/d/e/f/g/h/i/j/file.txt` impacts performance
- **Very long key names**: Excessive key length increases metadata overhead
- **Inconsistent delimiters**: Mixing `/`, `:`, `-` as level separators
- **Sequential numerical IDs**: `/user/00000001/profile.jpg`, `/user/00000002/profile.jpg`

## Migration and Evolution

### Renaming Considerations
- No atomic rename operation in most blob stores
- Renaming requires copy-then-delete operations
- Bulk renaming can be resource-intensive
- Version history is typically not preserved during renames
- Permission changes may be needed when restructuring

### Organization Evolution
- Plan for future growth when designing key patterns
- Use key design that allows for non-disruptive reorganization
- Consider using metadata or tagging rather than encoding all information in keys
- Design for potential multi-region or cross-account migration
- Create patterns that support changing business requirements

The object key format is a fundamental design choice that impacts performance, organization, and usability of the blob storage system. A well-designed key structure balances human readability, machine efficiency, and flexibility for evolving requirements.​​​​​​​​​​​​​​​​
