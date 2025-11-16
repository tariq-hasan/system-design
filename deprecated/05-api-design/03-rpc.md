# Remote Procedure Call (RPC)

## 1. Introduction

- **Definition**: A Remote Procedure Call (RPC) enables a client application to execute a subroutine on a remote server.

### Unique Features
- **Location Transparency**: Remote method calls look like local method calls to the developer.
- **Language Interoperability**: RPC frameworks allow applications written in different languages to communicate.

---

## 2. How RPC Works

- APIs and data types are defined using an **Interface Description Language (IDL)**, which varies by RPC framework.
- This schema serves as the contract between the client and server.

### Example IDL Definition
```plaintext
debitAccount(UserInfo userinfo, int32 amount) -> Response

UserInfo {
  String name;
  String lastName;
  String creditCardNumber;
  int32 securityCode;
  ...
}

Response {
  bool success;
  String errorMessage;
}
```

### Code Generation Process
- The IDL is compiled to generate:
  - **Client Stub**: Handles method invocation and request transmission.
  - **Server Stub**: Receives requests and invokes the actual method.

### Data Flow at Runtime
1. Client calls a method: `Response response = debitAccount(userInfo, 100)`
2. Client Stub:
   - Serializes (marshals) data
   - Sends it to the server
3. Server Stub:
   - Deserializes (unmarshals) data
   - Invokes the actual implementation
4. Server returns a response
5. Client Stub:
   - Deserializes the response
   - Returns it to the caller

### DTOs (Data Transfer Objects)
- Custom object types defined in IDL are compiled into classes/structs and used in both client and server.

---

## 3. RPC Over Time
- RPC has existed for decades.
- What changes over time:
  - Frameworks
  - Implementation details
  - Efficiency

---

## 4. Developer Responsibilities
- Choose an RPC framework
- Define APIs and data types using the framework's IDL
- Publish the interface definition

---

## 5. Decoupling Client and Server
- The client and server are fully decoupled via the published API definition.
- A new client can:
  - Use the IDL to generate a stub in their preferred language
  - Communicate with the server without modifying server code

### Multi-language Support
- Some RPC frameworks support multiple languages, allowing more flexibility in system design.

---

## 6. Benefits of RPC
- **Developer Convenience**:
  - Remote methods appear like local method calls
  - Network communication and serialization are abstracted away
  - Errors during communication surface as exceptions or error values

---

## 7. Drawbacks of RPC
1. **Slowness**:
   - Remote calls are slower than local methods
   - Asynchronous versions may help with slow operations
2. **Unreliability**:
   - Failures may occur due to:
     - Lost acknowledgment messages
     - Server crashes
   - Solution: Use idempotent operations when possible

---

## 8. When to Use RPC

### Ideal Use Cases
- Backend-to-backend communication
- APIs provided to other companies
- Internal microservice communication
- When abstraction of network details is preferred

### When Not to Use RPC
- When direct access to HTTP headers/cookies is required
- When communication details should be exposed
- When designing CRUD or data-centric APIs

### Design Characteristics
- RPC emphasizes actions over resources
- Each action is a distinct method with its own name and parameters

---

## 9. Popular RPC Frameworks

### gRPC
- Developed by Google in 2015
- Uses HTTP/2 and Protocol Buffers
- Supported Languages: C#, C++, Dart, Go, Java, Kotlin, Node, Objective-C, PHP, Python, Ruby

### Apache Thrift
- Developed by Facebook
- Supports 28+ programming languages
- Uses its own IDL: Thrift IDL
- Designed for scalable cross-language service development

### Java RMI (Remote Method Invocation)
- Java-only RPC framework
- Allows method calls across JVMs
- Uses Java as its IDL​​​​​​​​​​​​​​​​
