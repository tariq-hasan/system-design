# Checksums

Checksums serve as the first line of defense against data corruption, providing a mathematical verification of data integrity throughout the object's lifecycle.

## Level 1: Key Concepts

- **Data Integrity Verification**: Mathematical technique to detect data corruption
- **Upload Validation**: Ensures data is received correctly during upload
- **Storage Validation**: Verifies data hasn't changed while at rest
- **Transfer Validation**: Confirms data is delivered correctly during download
- **Background Verification**: Continuous checking of stored objects

## Level 2: Implementation Details

### Checksum Types and Algorithms

Blob stores typically employ cryptographic hash functions:

| Algorithm | Output Size | Characteristics | Usage |
|-----------|-------------|-----------------|-------|
| **MD5** | 128 bits | Faster computation, less secure cryptographically | Common for ETags and basic integrity |
| **SHA-1** | 160 bits | Legacy algorithm, faster than SHA-256 | Historical usage, being phased out |
| **SHA-256** | 256 bits | Strong security, industry standard | Modern implementations, security-focused systems |
| **CRC32C** | 32 bits | Very fast, hardware acceleration available | Internal integrity checks, not for security |

Many systems use multiple checksums for different purposes:
- Faster algorithms (CRC32C) for internal validation
- Cryptographic hashes (SHA-256) for end-to-end verification

### Checksum Lifecycle

Checksums are employed at multiple stages:

1. **Upload Process**:
   - Client may pre-calculate and provide checksum
   - Server independently calculates checksum upon receipt
   - Checksums compared to verify successful transmission
   - Checksum stored with object metadata

2. **Storage Period**:
   - Background processes periodically recalculate checksums
   - Results compared against stored values
   - Mismatches trigger repair procedures
   - Statistics gathered on error rates

3. **Download Process**:
   - Server includes checksum in response headers
   - Client can validate received data against checksum
   - Optional end-to-end verification

### Metadata Integration

Checksums are stored as core metadata with several potential representations:

- **HTTP ETag**: Used in GET/PUT responses for caching and validation
- **Content-MD5**: Standard HTTP header for MD5 checksums
- **Custom Headers**: x-amz-checksum-sha256, x-goog-hash, etc.
- **Internal Metadata**: Not exposed directly but used for verification

## Level 3: Technical Deep Dives

### Multi-Part Upload Checksum Handling

Large objects uploaded in parts require special checksum processing:

1. **Individual Part Verification**:
   - Each part gets its own checksum (e.g., MD5)
   - Server verifies parts independently

2. **Combined Object Checksum**:
   - Simple approach: Calculate new checksum on complete object
   - Optimized approach: Deterministic algorithm to combine part checksums
   - Example: S3 ETag format for multipart uploads:
     `"a1b2c3d4-5"`
     where a1b2c3d4 is a hash of part hashes and 5 indicates number of parts

3. **Challenges and Solutions**:
   - Varying part sizes affect checksum algorithms
   - Parts may be uploaded in parallel and out of order
   - Resumable uploads need persistent checksum state

### Error Detection and Correction

Different types of data corruption require different approaches:

1. **Bit Flips/Silent Data Corruption**:
   - Random bit changes due to hardware issues or cosmic rays
   - Detected by checksum verification
   - Typically requires repair from replicas/parity
   - Rate of occurrence: ~1 per 10-100TB read

2. **Torn Writes**:
   - Partial updates due to power failures or crashes
   - Checksums may be insufficient (partial write could have valid checksum)
   - Additional protection: write verification, atomic updates, journal/log
   - Mitigated by careful storage implementation

3. **Phantom Writes/Misdirected Writes**:
   - Data written to wrong location
   - Can be detected if checksums include expected location
   - Block address verification in lower storage layers
   - Requires careful end-to-end system design

### Efficiency and Performance Considerations

Several techniques optimize checksum operations:

1. **Incremental Checksumming**:
   - Update checksums incrementally during streaming uploads
   - Avoid buffering entire object in memory
   - Example: Running SHA-256 context updated as data arrives

2. **Hardware Acceleration**:
   - CRC32C instruction in modern CPUs (SSE4.2)
   - AES-NI for cryptographic hashing
   - GPU acceleration for batch operations
   - FPGA offloading in specialized systems

3. **Sampling vs. Complete Verification**:
   - Full verification: Check entire object content
   - Sampling: Verify random portions (faster but less comprehensive)
   - Tiered approach: Frequent sampling with periodic full verification

4. **Checksum Caching**:
   - Cache checksum calculations to avoid redundant work
   - Particularly useful for background verification
   - Requires invalidation on any potential data change

These advanced checksum strategies ensure that the blob store can detect and address data corruption while maintaining performance and efficiency, even at massive scale.​​​​​​​​​​​​​​​​
