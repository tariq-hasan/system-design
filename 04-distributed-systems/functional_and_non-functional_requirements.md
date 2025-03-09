# Functional and Non-functional Requirements

## Understanding Availability and Redundancy

Effective failover strategies rely on a foundation of infrastructure distribution. Modern cloud platforms organize their resources across:

- **Availability Zones**: Physically separate data centers within a geographic region that provide isolation from localized failures
- **Geographic Regions**: Distinct geographic areas (e.g., US-East, EU-West) that provide protection against regional disasters

Cloud providers offer serverless services that handle failover automatically:
- AWS Lambda (Function-as-a-Service)
- AWS Kinesis (Stream processing)
- AWS Athena (Interactive query service)
