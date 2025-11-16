# Authorization Models

Authorization determines what authenticated users and applications can do within the blob store, controlling access to resources at various levels of granularity.

## Level 1: Key Concepts

- **Permission Management**: Mechanisms to define allowed operations
- **Policy Evaluation**: How access decisions are made
- **Granularity Levels**: Different scopes of access control
- **Inheritance Patterns**: How permissions flow through the resource hierarchy
- **Default Protections**: Baseline security without explicit configuration

## Level 2: Implementation Details

### IAM Policies

Comprehensive permission documents attached to identities:

- **Structure and Format**:
  - JSON documents with standardized schema
  - Explicit Allow/Deny statements
  - Resource patterns for matching
  - Condition expressions for contextual access
  - Action lists defining permitted operations

- **Policy Attachment Points**:
  - **User Policies**: Directly attached to user identities
  - **Group Policies**: Applied to all members of a group
  - **Role Policies**: Assumed temporarily by users/applications
  - **Service Policies**: Applied to service accounts

- **Key Components**:
  ```json
  {
    "Version": "2023-04-01",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": ["s3:GetObject", "s3:PutObject"],
        "Resource": "arn:aws:s3:::example-bucket/user/${aws:username}/*",
        "Condition": {
          "IpAddress": {"aws:SourceIp": "192.0.2.0/24"}
        }
      }
    ]
  }
  ```

- **Evaluation Logic**:
  - Default implicit deny
  - Explicit deny overrides any allows
  - At least one allow required for access
  - Policies evaluated in aggregate

### Access Control Lists (ACLs)

Fine-grained, object-level permissions:

- **Implementation Approach**:
  - Metadata associated directly with objects
  - Lists of grantees and their permissions
  - Simple permission sets (READ, WRITE, FULL_CONTROL)
  - Independent of identity policies
  - Evaluated in addition to IAM policies

- **Grantee Types**:
  - Individual users
  - Predefined groups (All Users, Authenticated Users)
  - Other accounts
  - Service principals

- **Common Use Cases**:
  - Public access to specific objects
  - Cross-account permissions
  - Legacy application support
  - Simple sharing scenarios
  - Per-object permission variations

- **Limitations**:
  - Less expressive than policy language
  - Management overhead at scale
  - No condition support
  - Limited audit visibility

### Bucket Policies

Container-level rules that apply to all contained objects:

- **Implementation Approach**:
  - JSON policies similar to IAM format
  - Attached directly to bucket resources
  - Apply to all objects within the bucket
  - Can restrict or expand access relative to IAM policies

- **Key Use Cases**:
  - Enforcing encryption requirements
  - Implementing VPC-only access
  - Setting up cross-account access
  - Enforcing object ownership on upload
  - Implementing compliance controls

- **Policy Scope**:
  - Control object operations (GET, PUT, DELETE)
  - Manage bucket configuration
  - Govern bucket metadata
  - Restrict based on request properties
  - Enforce object characteristics

- **Example Elements**:
  ```json
  {
    "Version": "2023-04-01",
    "Statement": [
      {
        "Effect": "Deny",
        "Principal": "*",
        "Action": "s3:*",
        "Resource": [
          "arn:aws:s3:::example-bucket",
          "arn:aws:s3:::example-bucket/*"
        ],
        "Condition": {
          "Bool": {"aws:SecureTransport": "false"}
        }
      }
    ]
  }
  ```

## Level 3: Technical Deep Dives

### Policy Evaluation Pipeline

Authorization decisions involve sophisticated processing:

1. **Request Context Assembly**:
   - Authentication principal information
   - Requested resource identification
   - Operation type and parameters
   - Request metadata (time, IP, TLS details)
   - Special context attributes

2. **Policy Collection**:
   - Gather applicable identity policies
   - Retrieve resource policies (bucket, object)
   - Include organization-wide policies
   - Process any session policies
   - Assemble ACL entries

3. **Evaluation Algorithm**:
   ```
   Explicit DENY in any policy? → Deny Access
            │
            ↓ (No)
   Request context matches    → Allow Access
   an ALLOW in any policy?
            │
            ↓ (No)
        Deny Access (default)
   ```

4. **Optimization Techniques**:
   - Policy indexing for fast retrieval
   - Cached evaluation results
   - Common pattern optimization
   - Principle of least privilege checks
   - Evaluation short-circuits

### Conditional Access Controls

Advanced authorization uses rich contextual information:

1. **Condition Operators**:
   - **String Conditions**: Exact, prefix, wildcard matching
   - **Numeric Conditions**: Range comparisons
   - **Date Conditions**: Time-based access windows
   - **Boolean Conditions**: Flag-based controls
   - **IP Address Conditions**: CIDR range membership
   - **Existence Conditions**: Presence of specific attributes

2. **Advanced Condition Examples**:
   - Restrict access to business hours
   - Require multi-factor authentication for sensitive operations
   - Limit access to specific geographic regions
   - Enforce minimum TLS version
   - Require specific HTTP headers
   - Validate resource tags match principal tags

3. **Condition Resolution**:
   - Multiple values handled with set operators (ForAnyValue, ForAllValues)
   - Nested condition blocks with logical operators
   - Key attribute existence checking
   - Null value handling
   - Case-sensitivity controls

### Cross-Account Authorization

Enterprise environments implement sophisticated cross-boundary access:

1. **Trust Relationship Model**:
   ```
   Account A                      Account B
   ┌───────────┐  Trust Policy   ┌───────────┐
   │ Resource  │ ◄──────────────►│ Principal │
   └───────────┘                 └───────────┘
         │                             │
   Bucket Policy                     Role
         │                             │
         ▼                             ▼
   Object Access ◄─────────────── Assumed Role
                    Operations
   ```

2. **Role Assumption Flow**:
   - Principal in Account B assumes role through STS
   - STS verifies trust policy allows assumption
   - STS issues temporary credentials for the role
   - Principal uses role credentials to access resources
   - Access evaluated against role permissions and resource policies

3. **Security Considerations**:
   - Privilege escalation prevention
   - External ID verification
   - Role session tagging
   - Access chain analysis
   - Least privilege principle enforcement

4. **Multi-Factor Authentication Integration**:
   - MFA requirement for role assumption
   - MFA condition in resource policies
   - MFA validity period management
   - Device binding options
   - Step-up authentication for sensitive operations

These advanced authorization models enable organizations to implement sophisticated access control strategies that balance security requirements with operational needs, while maintaining robust auditability and compliance.​​​​​​​​​​​​​​​​
