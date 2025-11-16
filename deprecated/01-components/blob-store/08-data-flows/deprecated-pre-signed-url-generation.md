# Pre-signed URL Generation

Pre-signed URLs provide temporary, controlled access to blob store objects without requiring the recipient to have permanent credentials, enabling secure sharing and delegated uploads.

## Diagram Overview

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

## Detailed Process Flow

### 1. Client Request Initiation

**Client → API Service**

The process begins with an authenticated client requesting a pre-signed URL:

- Client constructs request specifying:
  - Target object key (existing or future object)
  - Desired operation (GET, PUT, DELETE)
  - Expiration time for the URL
  - Optional restrictions (IP range, content-type)
  - Custom headers to enforce
- Includes their own authentication credentials
- May specify permissions for the URL recipient
- Sends request to the API service

### 2. API Request Processing

**API Service → Auth Check**

The API service processes the pre-signed URL generation request:

- Validates request format and parameters
- Checks for required fields
- Validates expiration timeframe against system limits
- Normalizes parameters for consistent handling
- Prepares context for authentication verification
- Logs pre-signed URL generation request
- Forwards to authentication service

### 3. Authentication and Authorization

**Auth Check → Apply Permissions**

The system verifies the requesting client's permissions:

- Validates caller's credentials
- Confirms caller has permission to:
  - Access the specified object
  - Perform the requested operation
  - Generate pre-signed URLs
- Checks if bucket allows pre-signed URL generation
- Verifies expiration is within allowed maximum
- If authorized, allows request to proceed
- If unauthorized, returns appropriate error

### 4. Permission Application

**Apply Permissions → Generate Signature**

The system prepares the permission scope for the pre-signed URL:

- Constructs temporary permission set based on:
  - Original requestor's permissions (as upper bound)
  - Explicitly requested permissions (narrowed scope)
  - System policies for pre-signed URLs
- Applies time-based constraints
- Incorporates any conditional parameters:
  - IP address restrictions
  - Allowed HTTP methods
  - Required headers
  - Referrer restrictions
- Prepares permission context for signature generation

### 5. Signature Generation

**Generate Signature → Return URL**

The system cryptographically signs the URL parameters:

- Canonicalizes request elements:
  - HTTP verb
  - Resource path
  - Query parameters
  - Selected headers
  - Expiration timestamp
- Applies cryptographic algorithm (typically HMAC-SHA256)
- Uses caller's secret key or system key for signing
- Encodes signature according to URL-safe standards
- Generates full pre-signed URL including:
  - Base endpoint URL
  - Object path
  - Authentication parameters
  - Expiration information
  - Policy constraints
  - Cryptographic signature

### 6. Response Completion

**Return URL → Client**

The system returns the generated pre-signed URL to the client:

- Provides complete pre-signed URL in response
- Includes expiration time in human-readable format
- May include usage instructions
- Logs successful URL generation
- Returns additional metadata about URL capabilities
- Sends response to original client

## Use Case Variations

### Download (GET) Pre-signed URL

For temporary access to download an object:

1. **URL Construction**:
   - Generated URL permits only GET operations
   - May include response-content parameters
   - Often shorter expiration for security

2. **Usage Pattern**:
   - Recipient uses standard HTTP GET with URL
   - No additional authentication required
   - Commonly used for:
     - Temporary file sharing
     - Media content distribution
     - Report downloads
     - CDN origin authentication

### Upload (PUT) Pre-signed URL

For allowing uploads without permanent credentials:

1. **URL Construction**:
   - Generated URL permits PUT operation
   - May enforce content-type, content-length restrictions
   - Can include required metadata as enforced headers

2. **Usage Pattern**:
   - Recipient uses HTTP PUT to specified URL
   - Must include any required headers specified during generation
   - Commonly used for:
     - Direct browser uploads
     - Mobile app content submission
     - Partner data ingestion
     - Distributed upload collection

### Form-Based Upload URL

For browser-based uploads using HTML forms:

1. **Policy Document**:
   - Defines allowed form field values
   - Specifies conditions for the upload
   - Includes expiration time

2. **Form Construction**:
   - URL accompanied by form field values
   - Signature applied to entire policy
   - Fields encoded for HTML form inclusion

3. **Usage Pattern**:
   - Used with standard HTML form submission
   - Supports file input elements
   - Enables direct-to-storage uploads from web applications

## Security Considerations

1. **Expiration Time Management**:
   - Shorter is better for security
   - Balance between usability and security risk
   - Different defaults for different operations

2. **Scope Limitation**:
   - Restrict to minimal necessary permissions
   - Avoid pre-signed URLs for multiple objects when possible
   - Consider using condition parameters to further restrict usage

3. **Access Controls**:
   - IP range restrictions for sensitive operations
   - Referrer checking to prevent URL sharing
   - Required headers to enforce expected behavior
   - Content validation parameters

4. **Audit and Monitoring**:
   - Log all pre-signed URL generations
   - Track usage of pre-signed URLs
   - Alert on unusual patterns
   - Monitor for potential abuse

## Implementation Best Practices

1. **URL Generation Efficiency**:
   - Cache cryptographic operations when possible
   - Optimize canonical request construction
   - Consider dedicated service for high-volume URL generation

2. **User Experience**:
   - Provide clear expiration information
   - Return helpful error messages for misconfigured URLs
   - Offer URL shortening for very long pre-signed URLs
   - Include usage examples when appropriate

3. **Operational Management**:
   - Key rotation handling for long-lived URLs
   - Revocation mechanisms for emergency situations
   - Monitoring for URL generation rate anomalies
   - Quotas for URL generation to prevent abuse

Pre-signed URLs represent a powerful feature for secure, temporary object access without credential sharing, enabling a wide range of integrations and workflows while maintaining the blob store's security model.​​​​​​​​​​​​​​​​
