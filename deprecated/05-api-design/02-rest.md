# REST API: A Comprehensive Guide

## Introduction to REST API
REST (Representational State Transfer) is an architectural style for defining APIs for the web, introduced by Roy Fielding in his 2000 dissertation. It is not a standard or protocol, but rather a set of architectural constraints and best practices that enable:
- APIs that are easy for clients to use and understand
- Systems with quality attributes like scalability, high availability, and performance

An API that follows the REST architectural constraints is called a RESTful API.

## RPC vs REST API: Different Approaches

### RPC API Style
- Revolves around **methods** exposed to the client
- Methods are organized in interfaces
- System is abstracted through a set of callable methods
- API expansion occurs by adding more methods

### REST API Style
- Takes a **resource-oriented** approach
- Main abstraction is a named resource
- Resources encapsulate different entities in the system
- Client manipulates resources through a small number of standard methods

## Core Concepts of REST APIs

### Representation in REST API
A client requests a named resource, and the system responds with a representation of that resource's state. The representation is separate from how the resource is actually implemented in the system:

- The client receives only the representation of the resource state
- The resource implementation can be completely different and transparent to the client
- HTTP is commonly used as the protocol for requesting resources

#### Example of Representational State Transfer
For an online news magazine:
- The resource provided to the client is the homepage
- When requested, the client receives a webpage with a title, articles, and pictures
- This is just the representation of the current state of the homepage resource
- Internally, the system might implement this resource using many entities spread across multiple database tables, files, or external services

### HATEOAS: Hypermedia as the Engine of Application State
REST APIs are dynamic in nature through HATEOAS:
- In RPC, actions are statically defined by Interface Description Language
- In RESTful APIs, the interface is more dynamic

HATEOAS is achieved by accompanying state representation responses with hypermedia links, allowing clients to follow links and progress their internal state.

Example:
```http
GET /users/john-smith

Response:
{
    "accounts_status": {
        "user_id": 123,
        "total_incoming_messages": 1003,
        "unread_messages": 5,
        "total_sent_messages": 567
    },
    "links": {
        "messages": "/users/123/messages",
        "profile": "/users/123/profile",
        "threads": "/users/123/threads"
    }
}
```

## REST API Quality Attributes

### Statelessness
- Server is stateless and maintains no session information about the client
- Each request is served in isolation without information about previous requests
- Benefits:
  - Enables high availability and scalability
  - Allows load distribution across multiple servers transparent to clients

### Cacheability
- Server must explicitly or implicitly define each response as cacheable or non-cacheable
- Benefits:
  - Eliminates potential roundtrips to servers when responses are cached
  - Reduces load on the system

### Named Resources
In a RESTful API, resources are organized hierarchically:
- Each resource is addressed using a URI (Uniform Resource Identifier)
- Resources are organized in a hierarchy represented using forward slashes
- Two types of resources:
  - Simple resource: Has a state and optionally contains sub-resources
  - Collection resource: Contains a list of resources of the same type

Example hierarchy for a movie streaming service:
- `http://best-movies-service/movies` (collection resource)
- `http://best-movies-service/movies/movie-01` (simple resource)
- `http://best-movies-service/movies/movie-01/directors` (collection sub-resource)
- `http://best-movies-service/movies/movie-01/actors` (collection sub-resource)
- `http://best-movies-service/movies/movie-01/actors/john-smith` (simple resource)
- `http://best-movies-service/movies/movie-01/actors/john-smith/profile-picture` (sub-resource)

### Representation of Resources
Resource states can be represented in various formats:
- Images
- Links to media streams
- Objects
- HTML pages
- Binary blobs
- Executable code (e.g., JavaScript)

## Best Practices for REST APIs

### Resource Naming Best Practices
1. **Use nouns for resources**
   - Makes a clear distinction from actions (verbs)
   - Use verbs only for actions on resources

2. **Distinguish between collection and simple resources**
   - Use plural names for collections (e.g., `/movies`)
   - Use singular names for simple resources (e.g., `/movies/movie-01`)

3. **Use clear and meaningful names**
   - Makes the API easy to use
   - Prevents incorrect usage and mistakes
   - Avoid overly generic collection names (elements, entities, items, instances, values, objects)

4. **Ensure resource identifiers are unique and URL-friendly**
   - Allows for safe and easy use on the web

### REST API Operations
Unlike RPC, REST API limits operations on resources to a few predefined actions:
- Creating a new resource
- Updating an existing resource
- Deleting an existing resource
- Getting the current state of a resource (or listing sub-resources for collections)

### Mapping REST Operations to HTTP Methods
RESTful APIs commonly use HTTP methods:
- **POST**: Create a new resource
- **PUT**: Update an existing resource
- **DELETE**: Delete an existing resource
- **GET**: Retrieve the state of a resource or list sub-resources of a collection

### HTTP Methods Guarantees
1. **Safety and Idempotence**:
   - GET is safe (doesn't change resource state)
   - GET, PUT, and DELETE are idempotent (applying multiple times gives same result as applying once)

2. **Cacheability**:
   - GET requests are cacheable by default
   - POST responses can be made cacheable with appropriate HTTP headers

### Data Formats
When clients need to send additional information (in POST or PUT):
- JSON format is most common
- XML and other formats are also acceptable

## Defining a REST API: Step-by-Step Process

### Step 1: Identify System Entities
Identify the different entities in your system that will serve as API resources.
Example (movie streaming service): users, movies, reviews, actors

### Step 2: Map Entities to URIs
Define resources based on entities and organize them in a hierarchy:
- Independent collections:
  - `/users`, `/users/{user-id}`
  - `/movies`, `/movies/{movie-id}`
  - `/actors`, `/actors/{actor-id}`
- Sub-resources:
  - `/movies/{movie-id}/reviews`, `/movies/{movie-id}/reviews/{review-id}`

### Step 3: Choose Resource Representations
Most commonly JSON format is used to represent resources.

Example for movies collection:
```json
{
    "movies": [
        {
            "name": "Pirates of the Caribbean",
            "id": "movie-123"
        },
        {
            "name": "Lord of the Rings",
            "id": "movie-456"
        }
    ]
}
```

Example for a single movie resource:
```json
{
    "movie-info": {
        "name": "Pirates of the Caribbean",
        "id": "movie-123"
    },
    "links": {
        "movie-stream": "...",
        "reviews": "/movies/movie-123/reviews",
        "actors": "/actors?movie-id=movie-123"
    }
}
```

### Step 4: Assign HTTP Methods to Actions
Define operations for each resource:

**User operations:**
- `POST /users` → Create new user
- `GET /users/{user-id}` → Get user information
- `PUT /users/{user-id}` → Update user information
- `DELETE /users/{user-id}` → Delete existing user

Repeat this process for all resources in the system to complete the API design.
