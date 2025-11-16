# Resources for Intermediate-Level Components

This repository contains a collection of markdown files covering various intermediate-level components.

- [WIP] [Auto/Typeahead Suggestion](auto_typeahead_suggestion.md)
- [WIP] [Code Editor](code_editor.md)
- [WIP] [Collaborative Document Editing: Google Docs](collaborative_document_editing.md)
- [WIP] [Google Calendar](google_calendar.md)
- [WIP] [Cricbuzz](cricbuzz.md)
- [WIP] [Dating App](dating_app.md)
- [WIP] [E-Commerce](e-commerce.md)
- [WIP] [Email Service](email_service.md)
- [WIP] [Games System](games_system.md)
- [WIP] [IRCTC](irctc.md)
- [WIP] [Judge for Coding Contests](judge_for_coding_contests.md)
- [WIP] [Location Based Service: Food Delivery (DoorDash, Uber Eats, Swiggy)](location_based_service_food_delivery.md)
- [WIP] [Location Based Service: Maps (Google Maps)](location_based_service_maps.md)
- [WIP] [Location Based Service: Online Review Sites (FourSquare, Google Places, TripAdvisor, Yelp)](location_based_service_online_review_sites.md)
- [WIP] [Location Based Service: Taxi Services (Lyft, Grab, Ola, Uber)](location_based_service_taxi_services.md)
- [WIP] [Messaging Service](messaging_service.md)
- [WIP] [Notification Service](notification_service.md)
- [WIP] [Paste Bin](paste_bin.md)
- [WIP] [Payment System](payment_system.md)
- [WIP] [Pinterest](pinterest.md)
- [WIP] [Practo](practo.md)
- [WIP] [Real Estate: Zillow](real_estate.md)
- [WIP] [Scan To Pay Process for Dynamic QR code](scan_to_pay_process_dynamic_qr_code.md)
- [WIP] [Social Media: Instagram](social_media_instagram.md)
- [WIP] [Social Media: Twitter](social_media_twitter.md)
- [WIP] [Social Media: News Feed](social_media_news_feed.md)
- [WIP] [Stack Overflow](stack_overflow.md)
- [WIP] [Stock Exchange](stock_exchange.md)
- [WIP] [Hotel/Ticket Booking](hotel_ticket_booking.md)
- [WIP] [URL Shortening Service: TinyURL](url_shortening_service.md)
- [WIP] [Storage: Dropbox, Google Drive](storage.md)
- [WIP] [Video Streaming Service: Amazon Prime Video/Netflix/Youtube](video_streaming_service.md)
- [WIP] [Video: Calling (Google Hangouts, Facebook, Webex, Whatsapp, Zoom)](video_calling.md)
- [WIP] [Video: Live Streaming](video_live_streaming.md)
- [WIP] [Web Crawler / Spider / Spider Bot](web_crawler_spider_bot.md)
- [WIP] [Live Commenting](live_commenting.md)
- [WIP] [Leaderboard](leaderboard.md)
- [WIP] [Miscellaneous](miscellaneous.md)
- [WIP] [Case Studies](case_studies.md)



## 🚀 Intermediate Components
* A/B Testing Platform
* Analytics System (Clickstream)
* Auction Systems (Real-time bidding)
* Authentication and Authorization Service
* Auto/Typeahead Suggestion
* CI/CD Pipeline
* Code Editor
* Collaborative Document Editing: Google Docs
* Content Moderation Systems
* Cricbuzz
* Customer Support Ticketing System
* Dark Launch System
* Dating App
* E-Commerce
* Email Service
* Feature Flag Service
* Fraud Detection Service
* Games System
* Google Calendar
* Hotel/Ticket Booking
* Inventory Management System
* IRCTC
* Judge for Coding Contests
* Leaderboard
* Live Commenting
* Location Based Service: Food Delivery
* Location Based Service: Maps
* Location Based Service: Online Review Sites
* Location Based Service: Taxi Services
* Messaging Service
* Miscellaneous
* Notification Service
* Paste Bin
* Payment System
* Pinterest
* Practo
* Pricing Engine
* Real Estate: Zillow
* Recommendation Systems
* Scan To Pay Process for Dynamic QR code
* Search Autocomplete Ranking System
* Social Media: Instagram
* Social Media: News Feed
* Social Media: Twitter
* Stack Overflow
* Stock Exchange
* Storage: Dropbox, Google Drive
* Unified Search Service
* URL Shortening Service: TinyURL
* User Segmentation Service
* Video: Calling
* Video: Live Streaming
* Video Streaming Service: Netflix, YouTube
* Web Crawler / Spider / Spider Bot
* Webhook System

















# System Design Interview Topics: Application Focus

This repository complements the "System Design Components" list by providing a detailed categorization of application-oriented system design topics. While the Components list focuses on the building blocks, this list focuses on end-to-end applications and services commonly discussed in interviews.

## Table of Contents

- [Tier 1: High-Frequency Interview Systems](#tier-1-high-frequency-interview-systems)
- [Tier 2: Common Industry Applications](#tier-2-common-industry-applications)
- [Tier 3: Specialized Applications](#tier-3-specialized-applications)
- [Tier 4: Platform Services](#tier-4-platform-services)

## Tier 1: High-Frequency Interview Systems

These systems appear most frequently in system design interviews and effectively test a candidate's understanding of distributed systems principles.

| System | Description | Key Components | Design Challenges | Component Integration |
|--------|-------------|----------------|-------------------|----------------------|
| URL Shortening Service | Converts long URLs to short aliases | Database, Cache, Web Server, Analytics | High availability, URL collision handling, Analytics | Shows integration of rate limiters, distributed caching, and database sharding |
| Rate Limiter Service | Controls request rates to APIs | Counter storage, Rule engine, Decision service | Distributed counting, Minimal latency impact, Fairness | Demonstrates token bucket algorithms, distributed counters, and request processing |
| Chat Messaging System | Real-time communication platform | WebSockets, Message broker, Presence system, Storage | Real-time delivery, Offline messages, Group chat scaling | Showcases WebSockets, Pub/Sub patterns, and eventual consistency |
| News Feed System | Personalized content aggregation | Content ingestion, Ranking service, Cache, Fan-out service | Content freshness, Personalization, Read vs. write optimization | Illustrates fan-out strategies, cache invalidation, and content delivery |
| Video/Audio Streaming | Media content delivery platform | Transcoding pipeline, CDN, Media servers, Metadata service | Adaptive bitrate, Content protection, Latency reduction | Combines CDNs, caching hierarchies, and metadata management |
| Distributed File Storage | Cloud file storage and sharing | Blob storage, Metadata DB, Synchronization service | Consistency, Versioning, Large file handling | Demonstrates chunking strategies, metadata separation, and synchronization models |
| Type-ahead Suggestion | Real-time search predictions | Prefix trie, Query analyzer, Ranking system | Ultra-low latency, Data structure efficiency, Personalization | Shows trie implementations, caching strategies, and query processing |
| Distributed Key-Value Store | Scalable data storage service | Partition manager, Replication engine, Consistency service | High throughput, Availability vs. consistency, Failure handling | Illustrates consistent hashing, replication strategies, and conflict resolution |

## Tier 2: Common Industry Applications

These systems test broader distributed system principles and real-world design considerations.

| System | Description | Key Components | Design Challenges | Component Integration |
|--------|-------------|----------------|-------------------|----------------------|
| Ride-Sharing Platform | On-demand transportation | Matching engine, Location service, ETA calculator, Payment | Geographic partitioning, Real-time matching, Dispatch efficiency | Shows geospatial indexing, real-time processing, and marketplace dynamics |
| E-Commerce Platform | Online shopping system | Product catalog, Order management, Checkout, Recommendations | Inventory consistency, Flash sale handling, Search relevance | Demonstrates inventory systems, order pipelines, and catalog management |
| Hotel/Ticket Booking | Reservation system | Inventory DB, Booking workflow, Payment processing | Concurrency control, Consistent reservations, Overbooking strategy | Illustrates transaction patterns, inventory locking, and quota management |
| Collaborative Editor | Multi-user document system | OT/CRDT engine, Conflict resolution, Version control | Concurrent editing, Real-time synchronization, History management | Shows conflict-free data types, versioning, and synchronization protocols |
| Video Conferencing | Real-time A/V communication | Media servers, Signaling service, Network adaptation | Quality optimization, NAT traversal, Scalable broadcasting | Demonstrates media relay vs. SFU models, connection negotiation |
| Web Crawler | Content discovery and indexing | URL frontier, Content processor, Indexing service | Politeness, URL prioritization, Duplicate detection | Shows URL processing, distributed crawling, and resource management |
| Payment Processing | Financial transaction system | Payment gateway, Fraud detection, Ledger | Idempotency, Security, Audit trails | Illustrates idempotent APIs, transaction patterns, and security practices |
| Notification Service | Multi-channel alerts | Message prioritization, Channel manager, Delivery tracking | Delivery guarantees, Channel optimization, Batching strategies | Demonstrates queue management, delivery patterns, and failure handling |

## Tier 3: Specialized Applications

These systems test deeper technical knowledge in specialized domains and novel architectural patterns.

| System | Description | Key Components | Design Challenges | Component Integration |
|--------|-------------|----------------|-------------------|----------------------|
| Recommendation Engine | Personalized content selection | Feature extraction, Model serving, A/B testing | Real-time inference, Cold start problem, Feedback loops | Shows model serving architecture, feature storage, and ranking systems |
| Stock Exchange | High-throughput trading | Order matching engine, Market data feed, Risk control | Ultra-low latency, Fairness, Transaction integrity | Demonstrates LMAX architecture, memory optimization, and distributed matching |
| Code Execution Engine | Secure code runner | Container orchestration, Test harness, Resource governor | Security isolation, Resource constraints, Fair scheduling | Shows containerization, resource allocation, and secure execution |
| Real-time Analytics | Event processing and aggregation | Event ingestion, Stream processor, Aggregation service | High throughput, Low-latency queries, Approximation accuracy | Illustrates stream processing, time-windowing, and distributed aggregation |
| Content Moderation | Automated content filtering | Classification service, Review workflow, Policy engine | Accuracy vs. scale, Multi-media support, Policy enforcement | Shows ML system integration, human-in-loop design, and rule enforcement |
| Live Streaming Platform | User broadcast service | Ingest servers, Transcoding, Distribution, Chat | Low latency delivery, Viewer scaling, Interactive elements | Demonstrates media protocols, CDN integration, and real-time engagement |
| Distributed Leaderboard | High-throughput ranking | Score processor, Ranking service, Anti-fraud, Caching | Real-time updates, Global consistency, Score validation | Shows Top-K algorithms, sharding approaches, and materialized views |
| Ad Serving System | Real-time ad delivery | Bidding service, Ad selection, Performance tracking | Sub-millisecond decisions, Targeting accuracy, Budget adherence | Illustrates real-time auctions, targeting algorithms, and budget management |

## Tier 4: Platform Services

These systems represent critical infrastructure services that modern applications rely on.

| System | Description | Key Components | Design Challenges | Component Integration |
|--------|-------------|----------------|-------------------|----------------------|
| Identity & Access Control | Authentication and authorization | Identity providers, Token service, Permission store | Security, SSO integration, Permission granularity | Shows OAuth flows, token management, and permission models |
| Feature Management | Feature flag and experimentation | Flag configuration, Targeting service, SDK, Analytics | Consistent assignment, Performance impact, Metrics collection | Demonstrates configuration distribution, targeting logic, experiment design |
| Distributed Search | Cross-application content discovery | Indexing pipeline, Query processor, Relevance engine | Index freshness, Query understanding, Result relevance | Shows inverted index architecture, query parsing, and relevance algorithms |
| Distributed Task Scheduler | Reliable job execution | Task definition, Scheduler, Worker management | Execution guarantees, Prioritization, Failure recovery | Illustrates scheduling algorithms, failure handling, and state management |
| Distributed Tracing | Request flow visualization | Trace collection, Storage, Visualization | Low overhead, Sampling strategy, Correlation | Shows trace propagation, correlation IDs, and sampling techniques |
| API Gateway | Unified service access | Routing, Authentication, Rate limiting, Transformation | API composition, Protocol translation, Client management | Demonstrates BFF pattern, API versioning, and traffic management |
| Service Mesh | Service communication control | Sidecar proxies, Control plane, Policy enforcement | Transparent integration, Failure handling, Traffic control | Shows sidecar architecture, circuit breaking, and traffic policies |
| Event Streaming Platform | Real-time data pipeline | Event ingestion, Stream storage, Processing framework | Ordering guarantees, Exactly-once processing, Backpressure | Demonstrates log-based messaging, stream processing, and state management |

## Critical System Design Application Trends (2025)

1. **AI-enhanced Applications**: System designs increasingly incorporate AI components for personalization, recommendation, and automation.

2. **Real-time Distributed Systems**: Growing emphasis on systems with stringent real-time requirements at scale.

3. **Global Consistency Challenges**: Systems that manage consistency across geo-distributed deployments.

4. **Resilience and Observability**: Greater focus on failure modes, fault injection, and comprehensive monitoring.

5. **Sustainability Considerations**: Energy efficiency and resource optimization in large-scale systems.

## Complementary Skills for System Design Interviews

1. **Trade-off Analysis**: Ability to analyze and communicate the pros and cons of different architectural decisions.

2. **Capacity Estimation**: Skills in calculating and estimating storage, memory, and throughput requirements.

3. **Data Modeling**: Expertise in designing appropriate data schemas for different use cases.

4. **API Design**: Knowledge of RESTful, gRPC, GraphQL, and event-driven API patterns.

5. **Back-of-envelope Calculations**: Quick calculation of system constraints and requirements.

## How This List Complements the Components List

This application-focused list demonstrates how components from the "System Design Components" repository work together to create complete systems. In interviews, candidates should:

1. Identify the appropriate components needed for the application
2. Explain how these components interact and integrate
3. Discuss trade-offs in component selection and configuration
4. Address specific application requirements using appropriate components

For maximum preparation, study both lists and practice mapping components to applications and vice versa.



























# System Design Interview Topics

This repository contains detailed categorization of the most common system design topics that appear in interviews. Topics are organized by frequency of appearance in interviews and their fundamental importance to real-world systems.

## Table of Contents

- [Tier 1: Fundamental Systems](#tier-1-fundamental-systems)
- [Tier 2: Common Applications](#tier-2-common-applications)
- [Tier 3: Specialized Systems](#tier-3-specialized-systems)
- [Tier 4: Infrastructure & Platform Services](#tier-4-infrastructure--platform-services)

## Tier 1: Fundamental Systems

These systems appear in almost every system design interview and represent core platforms that many engineers are familiar with.

| System | Description | Key Components | Design Challenges |
|--------|-------------|----------------|-------------------|
| URL Shortening Service | Converts long URLs to short aliases | Hash functions, Database, Cache | High availability, URL collision handling, Analytics |
| Notification Service | Delivers alerts across multiple channels | Message queue, Push servers, Priority handling | Scalability, Delivery guarantees, Multi-channel support |
| Messaging Service | Enables real-time chat and communication | WebSockets, Presence system, Message store | Real-time delivery, Offline message handling, E2E encryption |
| Social Media: News Feed | Aggregates and displays content from connections | Content ranking, Cache, CDN | Personalization, Content freshness, Feed composition |
| Video Streaming Service | Delivers video content to users | Transcoding pipeline, CDN, Recommendation system | Adaptive bitrate, Content protection, Viewing analytics |
| E-Commerce | Online shopping platform | Product catalog, Cart system, Payment processing | Inventory management, Recommendations, Search optimization |
| Storage Services | Cloud file storage and sharing | Blob storage, Metadata DB, Synchronization | Consistency, Versioning, Permissions management |
| Hotel/Ticket Booking | Reservation systems for accommodations/events | Inventory management, Booking workflow, Payment processing | Concurrency control, Availability management, Pricing optimization |

## Tier 2: Common Applications

These systems appear frequently in interviews and represent popular applications that require significant distributed systems knowledge.

| System | Description | Key Components | Design Challenges |
|--------|-------------|----------------|-------------------|
| Location-Based Service: Maps | Geographic information and navigation | Geospatial database, Routing engine, Tile rendering | Real-time traffic, Path optimization, Spatial indexing |
| Location-Based Service: Taxi | On-demand ride services | Driver/rider matching, Location tracking, Payment | Surge pricing, ETA calculation, Dispatch optimization |
| Location-Based Service: Food Delivery | Restaurant ordering and delivery | Restaurant catalog, Order tracking, Delivery assignment | Delivery time estimation, Batching, Driver efficiency |
| Auto/Typeahead Suggestion | Real-time search predictions | Prefix trie, Query analyzer, Ranking | Latency requirements, Personalization, Language handling |
| Payment System | Financial transaction processing | Payment gateway, Fraud detection, Ledger | Security, Compliance, Transaction atomicity |
| Collaborative Document Editing | Real-time multi-user document systems | Operational transforms, Conflict resolution, Version control | Concurrency handling, Real-time sync, Undo/redo |
| Social Media: Twitter/Instagram | Content sharing and social interaction | Content store, Timeline generator, Graph database | Content distribution, Viral amplification, Engagement optimization |
| Video Calling | Real-time audio/video communication | WebRTC, Media servers, Signaling | Quality adaptation, NAT traversal, Connection management |
| Web Crawler | Automated content discovery and indexing | URL frontier, Content extractor, Link analyzer | Politeness, Duplicate detection, Content prioritization |

## Tier 3: Specialized Systems

These systems address specific needs and often combine elements from fundamental systems with specialized requirements.

| System | Description | Key Components | Design Challenges |
|--------|-------------|----------------|-------------------|
| Recommendation Systems | Personalized content/product suggestions | Feature extraction, Ranking models, A/B testing | Cold start problem, Diversity vs. relevance, Feedback loops |
| Paste Bin | Text storage and sharing service | Content store, Expiration handling, Access control | Content moderation, Storage optimization, Link generation |
| Stock Exchange | Financial market trading platform | Order matching engine, Market data feed, Settlement | Ultra-low latency, Transaction integrity, Regulatory compliance |
| Judge for Coding Contests | Automated code evaluation platform | Sandboxed execution, Test case runner, Plagiarism detection | Security isolation, Performance measurement, Scale during contests |
| Leaderboard | Ranking and competition tracking | Score aggregation, Ranking algorithm, Anti-cheat | Real-time updates, Partition tolerance, Global consistency |
| Live Commenting | Real-time discussion on live content | Comment stream, Moderation queue, Notification system | Message ordering, Spam prevention, Peak load handling |
| Live Streaming | User-generated broadcast video | Ingestion servers, Transcoding, Distribution | Low latency, Quality adaptation, Viewer scaling |
| Content Moderation Systems | Automated inappropriate content detection | ML classifiers, Human review queue, Reporting system | False positive handling, Emergent abuse, Scale |
| Auction Systems | Real-time bidding platforms | Bid processor, Clearing price calculator, Settlement | Time-bounded operations, Sniping prevention, Fraud detection |

## Tier 4: Infrastructure & Platform Services

These represent platform-level services that support other applications and are increasingly important in modern system design.

| System | Description | Key Components | Design Challenges |
|--------|-------------|----------------|-------------------|
| Authentication and Authorization | Identity and access management | Identity providers, Token service, Permission store | Security, Single sign-on, Scalability |
| A/B Testing Platform | Controlled feature experimentation | Experiment configuration, User assignment, Analytics | Statistical significance, Isolation, Metrics collection |
| Analytics System | User behavior and metrics tracking | Event collection, Processing pipeline, Data warehouse | High throughput ingestion, Real-time vs batch, Data integrity |
| CI/CD Pipeline | Automated build and deployment | Source control hooks, Build servers, Deployment automation | Testing reliability, Artifact management, Rollback capability |
| Feature Flag Service | Dynamic feature enablement | Flag configuration, User targeting, SDK | Consistency, Performance impact, Gradual rollout |
| Unified Search Service | Cross-application content discovery | Content indexing, Query processing, Relevance ranking | Index freshness, Query understanding, Federated search |
| User Segmentation Service | User categorization for targeting | Attribute store, Rule engine, Integration APIs | Real-time evaluation, Complex conditions, Scale |
| Webhook System | Event-based HTTP callbacks | Event broker, Delivery service, Retry mechanisms | Delivery guarantees, Timeout handling, Idempotency |
| Dark Launch System | Hidden feature deployment | Traffic shadowing, Result comparison, Configuration | Production testing, Performance impact, Isolation |
