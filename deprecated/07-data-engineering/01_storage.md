# Storage

## S3

### Features
- **Scalable Storage**: Infinite capacity with no provisioning required.  
- **Decoupled from Compute**: Works with EC2, Athena, Redshift Spectrum, Rekognition, Glue, and more.  
- **Centralized Architecture**: Provides a unified data management solution.  
- **Flexible Object Storage**: Supports multiple file formats, including CSV, JSON, Parquet, ORC, Avro, and Protobuf.  

### Buckets and Objects
- **Globally Unique Buckets**: Each bucket name must be globally unique.  
- **Object Keys**: Objects are identified by a key (full path), e.g.:  
  - `s3://my_bucket/my_file.txt`  
  - `s3://my_bucket/my_folder1/another_folder/my_file.txt`  
- **Size Limit**: Maximum object size is **5 TB**.  
- **Object Tags**: Up to **10 key-value pairs** per object, useful for security and lifecycle management.  

### Data Partitioning
- **Improves Query Performance**: Helps optimize range queries, especially for Athena.  
- **Partitioning Strategies**:  
  - **By Date**: `s3://bucket/my-data-set/year/month/day/hour/data_00.csv`  
  - **By Product**: `s3://bucket/my-data-set/product-id/data_32.csv`  
- **Partitioning Tools**: Managed via AWS Glue and other ETL tools.  

### Durability
- **Industry-Leading Reliability**: S3 provides **99.999999999% durability** (11 nines).  
- **Minimal Data Loss Risk**:  
  - On average, for every **10 million objects**, only **one object is lost every 10,000 years**.  
- **Consistent Across Storage Classes**: All S3 storage classes offer the same level of durability.  

### Availability
- **Measures Accessibility**: Indicates how readily available the service is.  
- **Varies by Storage Class**:  
  - **S3 Standard**: **99.99% availability** (~53 minutes of downtime per year).  
  - Other storage classes may have different availability guarantees.  

## Data Lakes

## DynamoDB
