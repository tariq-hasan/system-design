# [WIP] To-Do List

- [ ] [System Design Interview Channel Introduction](https://www.youtube.com/watch?v=OOKpXfneQ9Q)
- [ ] [System Design Interview – Step By Step Guide](https://www.youtube.com/watch?v=bUHFg8CZFws)
- [ ] [Golden Rules to answer in a System Design Interview](https://drive.google.com/file/d/1aoXt1zful7unuw2HuNXHLf6c_l8ja960/view)
- [ ] [System Design Interview Cheat Sheet](https://systemdesign.one/system-design-interview-cheatsheet/)

# Table of Contents

1. [Understanding Requirements](#understanding-requirements)
2. [Capacity Estimation](#capacity-estimation)
3. [High-level Design](#high-level-design)
4. [Design Deep Dive](#design-deep-dive)
5. [Wrap-up](#​​wrap-up)
6. [Example: Designing an E-commerce System](#example-designing-an-e-commerce-system)
7. [Miscellaneous](#miscellaneous)

# Understanding Requirements

- Ask the right questions to solidify the requirements.
  - Design questions are open ended, and they’re intentionally vague to start with.
  - Such vagueness mimics the reality of modern day business.

</br>

- Scope the problem.
  - Interviewers often ask about a well-known problem, for example, designing WhatsApp.
  - Now, a real WhatsApp application has numerous features, and including all of them as requirements for our WhatApp clone might not be a wise idea because
    - we have limited time during the interview, and
    - working with some core functionalities of the system should be enough to exhibit our problem-solving skills.
  - We can tell the interviewer that there are many other things that a real WhatsApp does that we do not intend to include in our design.
  - If the interviewer has any objections, we can change our plan of action accordingly.

</br>

- Key aspects:
  - Functional requirements e.g., an e-commerce platform might include user registration, product search, and order processing
    - Customer and actors of the system e.g., for a cab booking app are you designing from the rider’s perspective or the driver’s perspective? for a food delivery app are you designing from the eater’s perspective or the restaurant’s perspective?
    - Features/modules to consider e.g., for a food delivery app the module that gives the list of nearby restaurants or the module that detects the geolocation to determine the fastest route to deliver the food
  - Non-functional requirements e.g., scalability, performance, reliability, availability, security
  - Constraints e.g., technical (e.g., using a specific technology stack), regulatory (e.g., GDPR compliance), or resource-related (e.g., budget, time)
  - Cost considerations
  - Performance considerations
  - Scalability considerations
  - Availability vs. consistency considerations (which informs the choice of datastore and the implementation of resiliency) e.g., banking systems need to be highly consistent

# Capacity Estimation

- Ask whether capacity planning, API design, or database schema design is necessary

</br>

- Define the scale of the system in terms of
  - the number of users (which can be used for capacity estimation in order to determine the correct datastore to use)
  - whether the users are national or international (which can be used to determine if content delivery networks are needed)
- Discuss latency/throughput expectations, QPS and read/write ratio, traffic estimates, storage estimates and memory estimates.

# High-level Design

- Propose high-level design and get buy-in.
- Sketch out high-level components of the system and reach an agreement with the interviewer on the design.
    - Components
      - Databases: relational databases, NoSQL databases, or even in-memory databases.
      - Servers: application servers, web servers, or microservices. Each server or service handles specific business logic or functionalities.
      - Client Applications: Web, mobile, or desktop clients that interact with users and send requests to servers.
      - Third-Party Services: Sometimes it makes sense to integrate external services (e.g., payment gateways, email services).
    - High-level communication protocols (for interaction of system components)
      - APIs (RESTful APIs, GraphQL, gRPC, or websockets) for communication between clients and servers or between different services
      - Message queues for handling asynchronous communication and decoupling components
      - Proxy / reverse proxy
      - Load balancers to distribute incoming requests across multiple servers to ensure no single server becomes a bottleneck
      - Caching Systems to reduce load on databases and improve performance e.g., content delivery network, client-side, server-side, application-level, database-level

  - Read-heavy system: Use caching, content delivery network, database indexing, database replication and load balancing
  - Write-heavy system: Use message queues for asynchronous processing

  - IP resolution and domain name query: Use domain name system
  - Server load management and preventing DoS attacks: Use a rate limiter
  - Complex pre-computation: Use message queue and cache
  - Cache eviction policy: Use LRU cache
  - Global data delivery: Use content delivery network

  - User-to-user fast communication: Use websockets
  - Microservices architecture: Use API gateway
  - Loosely coupled system: Use event-driven architecture
  - Large data in network requests: Implement compression and pagination
  - Large-scale simultaneous connections: Use connection pooling and Protobuf to minimize data payload

- Identify and understand data and its characteristics in order to look for appropriate data storage systems and data processing components.
- Questions to ask when searching for the right systems and components:
  - Size of the data
  - Rate at which the data is expected to grow over time
  - How the data will be consumed by other subsystems or end users
  - If the data is read-heavy or write-heavy
  - Consistency model e.g., strict consistency or eventual consistency
  - Durability target for the data
  - Privacy and regulatory requirements for storing or transmitting user data

</br>

  - Clarify your assumptions before jumping into the solution

  - Communicate with the interviewer to finalize the scope. “What if the interviewer does not respond as expected?”
  - “What if the interviewer does not seem to pay attention?”: Try to control the interview flow by asking specific questions, like “for now, can we assume no data storage is needed; if we have time, we can expand on the storage part”.
  - “What if the interviewer asks a generic question like data consistency?”: Try to ask back the interviewer’s purpose and narrow down the scope of the question: “do you want me to analyze if the current design has consistency issues? What is the consistency requirement?”

  - Make it a discussion by sharing assumptions and admitting knowledge gaps
  - Keep getting feedback during the discussion rather than waiting till the end

  - Manage your time
    - System design interviews can range from 45 to 60 minutes, which is a really short time to design a large-scale distributed application.
    - Drive the conversations and avoid going into the details of a specific design component if it results in the loss of the bigger picture.
  - Communicate
    - Interviewers are interested in knowing a candidate’s thought process instead of getting a boilerplate solution.
    - Asking good questions will send hireable signals to the interviewer.
    - Be open to feedback and have the capacity to collaborate with the interviewer.
  - Ask questions
    - The interviewer may withhold some information to see if the candidate is able to identify and ask those questions to curate the design expected from them.

</br>

  - Define the entire sequence of events that a user goes through when using the app.
  - Define the events that occur within the module you decide to focus on.
  - Example
    -  you open a food delivery app → you get a list of restaurants which you can filter based on geolocation → you select certain food and add it to your cart → payment processing happens → delivery person is assigned to you → food is prepared and delivered
    - if you only focus on delivery module then talk about when the delivery guy will be assigned, when your food will be marked as being prepared, when your food will be marked as delivered, etc.

</br>

  - Define the API you will design in detail by writing them out.
    - request API
    - response API
    - who is going to request it
    - who is going to fulfill it

</br>

  - Define which microservice will be responsible for which API by drawing the architectural diagram.

</br>

  - Define how the communication will occur.
    - HTTP/HTTPS (client-to-server)
    - polling
    - web sockets (server-to-client)

</br>

  - Define the exact data needed in the system.

</br>

  - Define the data flow.
  - Define which microservice will be aware of which data in your architectural diagram.

</br>

  - Define the datastore (SQL or NoSQL) to be used based on capacity estimation (which gives you the size of the data to store).
  - Determine whether you prioritize consistency or availability (which determines whether you need to optimize for read or write).

  - Database Partitioning: methods (Horizontal Partitioning, Vertical Partitioning, Directory-Based Partitioning), Criteria (Range-Based Partitioning, Hash-Based Partitioning (Consistent Hashing), Round Robin)
  - Databases: SQL (sharding, indexes, master-master, master-slave, denormalization), NoSQL (key-value, document, wide-column, graph)

  - ACID-compliant database: Use SQL database
  - Unstructured data: Use NoSQL database
  - Complex data (videos, images, files): Use blob/object storage
  - Graph data: Use graph database
  - High-volume data search: Use search index, tries or search engine
  - Database performance: Use database indexes
  - Scalability of write requests and SQL databases: Implement database sharding

</br>

  - Define whether you need vertical scaling or horizontal scaling of your datastore in order to fulfill the requirements of the capacity estimation.
    - Scaling individual components: Horizontal and Vertical Scaling

</br>

  - Determine whether you need a separate datastore for other countries.
  - Determine whether you need cross-versions.
  - Determine which unique ID to use to shard your datastore (using consistent hashing) if using a relational database.
  - Discuss caching and content delivery network.

</br>

  - Discuss resiliency, failure and fault tolerance.
    - How will you handle failure of your microservices or datastores
    - Are you using master-slave, peer-to-peer, or other architecture?
    - How will you ensure that the data is durable?
    - How will you ensure that you are consistent or available?

  - Replication and Redundancy: Redundancy (Primary & Secondary Server), Replication (Data replication from active to mirrored database)

  - Low latency: Use caching and content delivery network
  - Scalability: Implement horizontal scaling
  - Traffic spikes: Implement autoscaling
  - Availability, performance and throughput: Use a load balancer
  - Fault-tolerance and durability: Implement data replication, redundancy and isolation

  - Availability and consistency trade-off: Use a consistency model
  - Failure detection: Use a heartbeat
  - Decentralized data transfer: Use Gossip protocol
  - Efficient server scaling: Use consistent hashing
  - Data integrity: Use checksum algorithm

</br>

  - Discuss how to check the health of all the microservices and datastores of the system e.g. using heartbeats.

</br>

  - Discuss if you will use a separate logging and monitoring service.
  - Discuss how the data will be sent, stored and parsed for analysis in the logger and monitor.

</br>

  - Discuss security issues in your system.
    - HTTP/HTTPS comes with an overhead.
    - If two microservices are communicating without any sensitive data flow then no need for HTTPS and can simply send/receive binary data.

</br>

  - Discuss data structures and algorithms used in the modules.
  - Example: for the module that determines the fastest route for food delivery using geolocation what is the algorithm to use?
  - Identification of algorithms/data structures and ways to scale them

</br>

- Long-running tasks: Use asynchronous processing and background processes
- Bulk job processing: Use batch processing and message queues
- Analytics and audit trails: Use data lakes or append-only databases

</br>

- Automated builds and deployments - Use CI/CD pipelines
- Independent deployments of various parts of the system - Use microservices architecture

</br>

- Location-based functionality: Use Geohash, Quadtree, etc.

</br>

- Discuss tradeoffs behind each design decision
- Validate the design against the requirements
- Avoid buzzwords and know alternative tech

</br>

- Strategies of System Design
  - Design For Failure
    - Any component that can fail will eventually fail, so it is important to design the service in a way that allows it to recover from failures gracefully.
    - The service should also be able to survive failures without the need for human intervention.
  - Redundancy And Fault Recovery
    - To ensure the reliability and robustness of the service, it is important to document all possible failure modes of each component, as well as combinations of those failure modes.
    - Redundancy should also be built into any component that has the potential to fail.
    - Additionally, it is important to be able to take down any server in the service without disrupting the workload.
  - Single-Version Software
    - Aim to have only one version of your software.
    - This is simpler to manage and cost-effective.
    - It may be easier to achieve this for consumer-based services compared to enterprise software services.
    - For enterprise software services, try to use a single version or consider outsourcing the service to a host or application service provider.
  - Multi-tenancy
    - Aim to have multiple tenants within the same service.
    - This is more efficient and cost-effective compared to having separate services for each tenant, which can be more difficult to manage.
  - Quick Service Health Check
    - It is important for services to have a simple and fast health check endpoint.
    - While it is not possible to test for all possible scenarios, a quick health check can help speed up the process of merging new code and quickly detect any failures.
  - Develop In The Full Environment
    - It is important for development to happen in an environment that is similar to production.
    - This way, developers can test all aspects of production scenarios on their own machines and ensure that their code will work properly in a live production environment.
  - Zero Trust in Underlying Components
    - Expect that underlying components may fail at some point.
    - Some recovery techniques that can be used in these situations include operating in read-only mode using cached data, or continuing to provide service to most users while a redundant copy of the failed component is accessed.
  - Do Not Build the Same Functionality in Multiple Components
    - It is important to avoid code redundancy, similar to the DRY (Don't Repeat Yourself) principle.
    - If redundancy is allowed to creep into the code, fixes will need to be made in multiple parts of the system, which can be time consuming and error-prone.
    - Without proper care, the code base can quickly become difficult to maintain.
  - One Cluster Should Not Affect Another Cluster
    - Clusters should be as independent as possible, with minimally correlated failures.
    - Global services, even with redundancy, can be a central point of failure, so it is best to avoid them whenever possible.
    - Instead, try to include everything that a cluster needs within the cluster itself.
    - This can help to reduce the risk of failures and improve the reliability of the system.
  - Allow (rare) Emergency Human Intervention.
    - Design the system to operate without human intervention, but have a plan in place for rare events that may require human intervention due to combined or unanticipated failures.
    - Test troubleshooting steps as scripts in production to ensure they work and periodically conduct "fire drills" to test the readiness of the operations team.
  - Keep Things Simple And Robust
    - It is generally better to use simple and straightforward solutions instead of complicated algorithms and complex interactions between services.
    - As a general rule, it is worth considering optimizations that bring about an order of magnitude improvement, but smaller gains in performance, such as percentage or small factor improvements, may not be worth the additional complexity.
  - Enforce Admission Control At All Levels
    - A well-designed system should have admission control in place at the entry point to prevent overloading.
    - This follows the principle that it is better to prevent more work from entering an already overloaded system rather than accepting more work and causing thrashing.
    - As a general rule, it is better to degrade gracefully rather than failing completely and providing poor service to all users.
    - To avoid this, it is important to block access to the service before it becomes overwhelmed.

# Design Deep Dive

- Identify and prioritize components in the architecture.
- Go deep on two to three components.
- Lay out multiple solutions and consider trade-offs of all solutions to determine a final solution.

## ​​Wrap-up

- If time allows, give the interviewer a recap of your design.
- This is particularly important if you have suggested a few solutions.
- Refreshing your interviewer’s memory can be helpful after a long session.

## Example: Designing an E-commerce System

- Requirements:
  - Functional:
    - User Authentication
    - Product Catalog
    - Shopping Cart
    - Order Processing
    - Payment Handling
    - User Reviews
  - Non-Functional:
    - Scalability to handle thousands of users
    - High availability with minimal downtime
    - Secure payment transactions
    - Fast response times

</br>

- Mapping to Components:
  - Databases:
    - Relational Database (e.g., PostgreSQL) for transactional data (orders, users).
    - NoSQL Database (e.g., MongoDB) for flexible product catalog storage.
  - Servers:
    - Authentication Service for user login and registration.
    - Product Service for managing the product catalog.
    - Cart Service for handling shopping carts.
    - Order Service for processing orders.
    - Payment Service for integrating with payment gateways.
  - Client Applications:
    - Web and mobile clients for user interaction.

</br>

- Communication Protocols:
  - APIs: RESTful APIs for communication between clients and backend services.
  - Message Queues: Using RabbitMQ for handling asynchronous tasks like order processing and notifications.
  - Load Balancers: AWS Elastic Load Balancer to distribute requests among application servers.
  - Caching Systems: Redis for caching frequently accessed data like product details and user sessions.

## Miscellaneous

- Do mock interviews.

</br>

- Possible questions
  - How a design might evolve over time as some aspect of the system increases by some order of magnitude — for example, the number of users, the number of queries per second, and so on.
    - It is commonly believed that when some aspect of the system increases by a factor of ten or more, the same design might not hold and might require change.
    - Designing and operating a bigger system requires careful thinking because designs often do not linearly scale with increasing demands on the system.
  - Why we do not design a system that is already capable of handling more work than necessary or predicted.
    - The dollar cost associated with complex projects is a major reason why we do not do that.

</br>

- The design evolution of Google
  - The design of the early version of Google Search may seem simplistic today, but it was quite sophisticated for its time.
  - It also kept costs down, which was necessary for a startup like Google to stay afloat.
  - The upshot is that whatever we do as designers have implications for the business and its customers.
  - We need to meet or exceed customer needs by efficiently utilizing resources.
- Design challenges
  - Things will change, and things will break over time because of the following:
    - There’s no single correct approach or solution to a design problem.
    - A lot is predicated on the assumptions we make.
- The responsibility of the designer
  - As designers, we need to provide fault tolerance at the design level because almost all modern systems use off-the-shelf components, and there are millions of such components.
  - So, something will always be breaking down, and we need to hide this undesirable reality from our customers.

</br>

- Distributed systems give us guideposts for mature software principles.
- These include the following:
  - Robustness (the ability to maintain operations during a crisis)
  - Scalability
  - Availability
  - Performance
  - Extensibility
  - Resiliency (the ability to return to normal operations over an acceptable period of time post disruption)
- As an example, we might say that we need to make a trade-off between availability and consistency when network components fail because the CAP theorem indicates that we can’t have both under network partitions.
