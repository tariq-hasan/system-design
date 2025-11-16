# Objectives

- Create data repositories for machine learning
- Identify and implement a data-ingestion solution
- Identify and implement a data-transformation solution

# Big Data Solutions

## Amazon Services
- **Amazon Glue**: Crawls over S3 and extracts a schema from data
- **Amazon Athena**: Serverless application that can query S3 using SQL
- **Amazon Redshift**: Data warehouse solution for analytics workloads
- **Redshift Spectrum**: Queries S3 directly without storing data in Redshift

## Design Considerations
- Structure write patterns based on access patterns (e.g., partitioning by date and/or store)
- Design data organization to optimize for most common query patterns
