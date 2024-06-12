# To-Do List

- [ ] [System Design Interview Channel Introduction](https://www.youtube.com/watch?v=OOKpXfneQ9Q)
- [ ] [System Design Interview – Step By Step Guide](https://www.youtube.com/watch?v=bUHFg8CZFws)
- [ ] [Golden Rules to answer in a System Design Interview](https://drive.google.com/file/d/1aoXt1zful7unuw2HuNXHLf6c_l8ja960/view)
- [ ] [System Design Interview Cheat Sheet](https://systemdesign.one/system-design-interview-cheatsheet/)

# Methodology

- Do mock interviews and keep track of time
- Ask clarifying questions to understand the functional and non-functional requirements
- Ask whether capacity planning, API design, or database schema design is necessary
- Clarify your assumptions before jumping into the solution
- Make it a discussion by sharing assumptions and admitting knowledge gaps
- Keep getting feedback during the discussion rather than waiting till the end
- Discuss tradeoffs behind each design decision
- Validate the design against the requirements
- Avoid buzzwords and know alternative tech

## Understanding Requirements

- Design questions are open ended, and they’re intentionally vague to start with.
- Such vagueness mimics the reality of modern day business.
- Interviewers often ask about a well-known problem, for example, designing WhatsApp.
- Now, a real WhatsApp application has numerous features, and including all of them as requirements for our WhatApp clone might not be a wise idea due to the following reasons:
  - First, we’ll have limited time during the interview.
  - Second, working with some core functionalities of the system should be enough to exhibit our problem-solving skills.
- We can tell the interviewer that there are many other things that a real WhatsApp does that we don’t intend to include in our design.
- If the interviewer has any objections, we can change our plan of action accordingly.
- Here are some best practices that we should follow during a system design interview:
  - An applicant should ask the right questions to solidify the requirements.
  - Applicants also need to scope the problem so that they’re able to make a good attempt at solving it within the limited time frame of the interview.
  - Communication with the interviewer is critical. We should engage with the interviewer to ensure that they understand our thought process.
- The first step in a system design interview is to gather and clarify the requirements.
- This involves understanding the problem you are trying to solve and the constraints you need to work within.
- Key aspects include:
  - Functional Requirements: What the system should do. For example, if you're designing an e-commerce platform, functional requirements might include user registration, product search, and order processing.
  - Non-Functional Requirements: How the system should perform. This includes scalability, performance, reliability, availability, and security.
  - Constraints: These could be technical (e.g., using a specific technology stack), regulatory (e.g., GDPR compliance), or resource-related (e.g., budget, time).

- Understand the problem and establish the design scope. Ask clarification questions to understand the requirements. The purpose of this step is to translate an ambiguous and open-ended question into exact requirements.

- Requirement Gathering
  - Functional requirements
  - Non-functional requirements
  - Cost considerations
  - Performance considerations
  - Do you want a highly scalable system?
  - Do you want a highly available system?
  - Do you want a highly consistent system?

- Define the customer and actors of the system e.g. for a cab booking app are you designing from the rider’s perspective or the driver’s perspective? for a food delivery app are you designing from the eater’s perspective or the restaurant’s perspective?

- Define the features/modules to consider e.g. for a food delivery app 1. the module that gives the list of nearby restaurants 2. the module that detects the geolocation to determine the fastest route to deliver the food.

- Determine if you need high availability or high consistency (which will inform your choice of datastore and how you implement resiliency) e.g. banking systems need to be highly consistent.

## Capacity Estimation

- We need to identify and understand data and its characteristics in order to look for appropriate data storage systems and data processing components for the system design.
- Some important questions to ask ourselves when searching for the right systems and components include the following:
  - What’s the size of the data right now?
  - At what rate is the data expected to grow over time?
  - How will the data be consumed by other subsystems or end users?
  - Is the data read-heavy or write-heavy?
  - Do we need strict consistency of data, or will eventual consistency work?
  - What’s the durability target of the data?
  - What privacy and regulatory requirements do we require for storing or transmitting user data?

- Define the scale of the system in terms of the number of users (which can be used for capacity estimation in order to determine the correct datastore to use) and whether the users are national or international (which can be used to determine if CDNs are needed).

- Capacity estimation discussion would include latency/throughput expectations, QPS and read/write ratio, traffic estimates, storage estimates and memory estimates.

## Mapping Requirements to Computational Components

- Once the requirements are understood, the next step is to map these requirements onto computational components.
- This involves identifying the major parts of the system and defining their roles.
- Components could include:
  - Databases: For storing data. You might choose between relational databases, NoSQL databases, or even in-memory databases based on requirements.
  - Servers: These could be application servers, web servers, or microservices. Each server or service handles specific business logic or functionalities.
  - Client Applications: Web, mobile, or desktop clients that interact with users and send requests to servers.
  - Third-Party Services: Sometimes it makes sense to integrate external services (e.g., payment gateways, email services).

</br>

1. Read-heavy system: use a cache, content delivery network, database indexing, database replication and load balancing
2. Write-heavy system: use message queues for asynchronous processing
3. Requirement for low latency: use a cache and content delivery network
4. Requirement for ACID-compliant database: use RDBMS/SQL database
5. Have unstructured data: use NoSQL database
6. Have complex data (videos, images, files): use blob/object storage
7. Complex pre-computation: use message queue and cache
8. High-volume data search: Consider search index, tries or search engine
9. Scaling SQL database: Implement database sharding
10. High availability, performance and throughput: Use a load balancer
11. Global data delivery: Consider using a content delivery network
12. Graph data (data with nodes, edges, and relationships): Utilize graph database
13. Scaling various components: Implement horizontal scaling
14. High-performing database queries: Use database indexes
15. Bulk job processing: Use batch processing and message queues
16. Server load management and preventing DOS attacks: Use a rate limiter
17. Microservices architecture: Use an API Gateway
18. failure: Implement redundancy and isolation
19. Fault-tolerance and durability: Implement data replication
20. User-to-user fast communication: Use websockets
21. Failure detection in distributed systems: Implement a heartbeat
22. Data integrity: Use checksum algorithm
23. Efficient server scaling: Implement consistent hashing
24. Decentralized data transfer: Consider Gossip protocol
25. Location-based functionality: Use Quadtree, Geohash, etc.
26. High availability and consistency trade-Off: Eventual consistency
27. For IP resolution and domain name query: Mention DNS
28. Handling large data in network requests: Implement compression and pagination
29. Cache eviction policy: Preferred is LRU (Least Recently Used) cache
30. To handle traffic spikes: Implement autoscaling to manage resources dynamically
31. Need analytics and audit trails: Consider using data lakes or append-only databases
32. Handling large-scale simultaneous connections: Use connection pooling and consider using Protobuf to minimize data payload
33. If the system needs to execute long-running tasks, use asynchronous processing and background processes
34. To build a loosely coupled system, consider the use of event-driven architecture
35. For automated builds and deployments, consider implementing CI/CD pipelines
36. If you want to achieve independent deployments of various parts of the system, consider microservices architecture
[9] To scale write requests, consider Database Sharding

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

</br>

- High-level communication protocols define how different components of the system interact with each other.
- This includes:
  - APIs: RESTful APIs, GraphQL, or gRPC for communication between clients and servers or between different services.
  - Message Queues: For handling asynchronous communication and decoupling components (e.g., RabbitMQ, Apache Kafka).
  - Load Balancers: To distribute incoming requests across multiple servers to ensure no single server becomes a bottleneck.
  - Caching Systems: To reduce load on databases and improve performance (e.g., Redis, Memcached).

</br>

Propose high-level design and get buy-in. Sketch out high-level components of the system and reach an agreement with the interviewer on the design.

Communicate with the interviewer to finalize the scope. “What if the interviewer does not respond as expected?”

“What if the interviewer does not seem to pay attention?” 
- Try to control the interview flow by asking specific questions, like “for now, can we assume no data storage is needed; if we have time, we can expand on the storage part”. 

“What if the interviewer asks a generic question like data consistency?” 
- Try to ask back the interviewer’s purpose and narrow down the scope of the question: “do you want me to analyze if the current design has consistency issues? What is the consistency requirement?”

Define the entire sequence of events that a user goes through when using the app and also define the events that occur within the module you decide to focus on e.g you open a food delivery app → you get a list of restaurants which you can filter based on geolocation → you select certain food and add it to your cart → payment processing happens → delivery person is assigned to you → food is prepared and delivered; if you only focus on delivery module then talk about when the delivery guy will be assigned, when your food will be marked as being prepared, when your food will be marked as delivered, etc.

Define the API you will design in detail by writing them out - exact request API, exact response API, who is going to request it, and who is going to fulfill it.

Define which microservice will be responsible for which API by drawing the architectural diagram.

Define how the communication will occur. Do you require HTTP/HTTPS (client-to-server), polling or web sockets (server-to-client)?

Define the exact data needed in the system.

Define the data flow and define which microservice will be aware of which data in your architectural diagram.

Define the datastore (SQL or NoSQL) to be used based on capacity estimation (which gives you the size of the data to store) and whether you prioritize consistency or availability (which determines whether you need to optimize for read or write).

Define whether you need vertical scaling or horizontal scaling of your datastore in order to fulfill the requirements of the capacity estimation.

Determine whether you need a separate datastore for other countries, whether you need cross-versions, and which unique ID to use to shard your datastore (using consistent hashing) if using a relational database. Also discuss caching and CDN.

Discuss resiliency, failure and fault tolerance - 1. how will you handle failure of your microservices or datastores 2. are you using master-slave, peer-to-peer, or other architecture? 3. how will you ensure that the data is durable? 4. how will you ensure that you are consistent or available?

Discuss how to check the health of all the microservices and datastores of the system e.g. using heartbeats.
Discuss if you will use a separate logging and monitoring service and how the data will be sent, stored and parsed for analysis in the logger and monitor.

Discuss security issues in your system - HTTP/HTTPS comes with an overhead; if two microservices are communicating without any sensitive data flow then no need for HTTPS and can simply send/receive binary data.

Discuss data structures and algorithms used in the modules e.g. for the module that determines the fastest route for food delivery using geolocation what is the algorithm to use?

Components: client (mobile, browser), DNS, CDN, load balancers, web / application servers, microservices, blob/object storage, proxy/reverse proxy, database (SQL or NoSQL), cache at various levels (client side, CDN, server side, database side, application level caching), messaging queues for asynchronous communication
Identification of algorithm/data structures and way to scale them
Scaling individual components: Horizontal and Vertical Scaling
Database Partitioning: methods (Horizontal Partitioning, Vertical Partitioning, Directory-Based Partitioning), Criteria (Range-Based Partitioning, Hash-Based Partitioning (Consistent Hashing), Round Robin)
Replication and Redundancy: Redundancy (Primary & Secondary Server), Replication (Data replication from active to mirrored database)
Databases: SQL (Sharding, Indexes, master-slave, master-master, Denormalization), NoSQL (Key-Value, Document, Wide-Column, Graph)
Communication Protocols and standards like - IP, TCP, UDP, HTTP/S, RPC, REST, Web Sockets

## Design deep dive.

- Identify and prioritize components in the architecture.
- Go deep on 2-3 components. Talk about trade-offs and why you choose this approach over others.

- Lay out multiple solutions and consider trade-offs of all solutions to determine a final solution.

</br>

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

- Possible questions
  - Interviews often include questions related to how a design might evolve over time as some aspect of the system increases by some order of magnitude — for example, the number of users, the number of queries per second, and so on.
  - It’s commonly believed in the systems community that when some aspect of the system increases by a factor of ten or more, the same design might not hold and might require change.
  - Designing and operating a bigger system requires careful thinking because designs often don’t linearly scale with increasing demands on the system.
  - Another question might be related to why we don’t design a system that’s already capable of handling more work than necessary or predicted. The dollar cost associated with complex projects is a major reason why we don’t do that.

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
