# Comprehensive List of Object-Oriented Design (OOD) Problems for Tech Interviews

## 🔝 **Top Categories of OOD Problems (Ranked by Popularity)**

| Rank | Category                          | Est. % Popularity | Description |
|------|----------------------------------|-------------------|-------------|
| 1    | Real-world Systems Modeling       | 30%               | Model complex real-world objects and their interactions |
| 2    | Game Design                       | 15%               | Design mechanics for games using OOP principles |
| 3    | In-Memory Storage & Cache Systems | 15%               | Implement efficient data storage and retrieval mechanisms |
| 4    | Online Platforms & Services       | 12%               | Model user-facing platforms with rich interaction models |
| 5    | Machine Design & State Systems    | 10%               | Simulate systems with well-defined states and transitions |
| 6    | Custom Data Structures            | 8%                | Implement specialized data structures with OO principles |
| 7    | Event-driven & Messaging Systems  | 5%                | Model asynchronous communication between components |
| 8    | Scheduling & Resource Management  | 5%                | Design systems for time-based allocation and conflict resolution |

---

## 📦 **1. Real-World Systems Modeling (30%)**

| Problem                                         | Keywords | Design Patterns |
|------------------------------------------------|----------|-----------------|
| 🔹 **Parking Lot System**                       | spaces, vehicles, tickets, payments, capacity | Factory, Strategy, Observer |
| 🔹 **Elevator System**                          | floors, direction, request queue, scheduling algorithm | State, Command, Singleton |
| 🔹 **Library Management System**                | books, members, borrowing, returns, reservations | Repository, Observer |
| 🔹 **ATM System**                               | card validation, transactions, balance, dispensing | State, Command, Template |
| 🔹 **Vending Machine**                          | inventory, payment processing, product selection | State, Factory, Strategy |
| 🔹 **Airline/Hotel Reservation System**         | booking, cancellation, seat assignment, pricing | Strategy, Observer, Template |
| 🔹 **E-commerce Platform**                      | products, cart, checkout, payment, shipping | Factory, Observer, Strategy |
| 🔹 **Ride-sharing System**                      | riders, drivers, matching, routes, pricing | Strategy, Observer, Factory |
| 🔹 **Smart Home System**                        | devices, automation, triggers, scenes | Command, Observer, Composite |
| 🔹 **Restaurant Management System**             | tables, orders, kitchen, billing | Command, Observer |

---

## 🎮 **2. Game Design (15%)**

| Problem                                         | Keywords | Design Patterns |
|------------------------------------------------|----------|-----------------|
| 🔹 **Chess / Checkers**                         | board, pieces, moves, rules, validation | Strategy, State, Factory |
| 🔹 **Card Games (Blackjack, Poker)**            | deck, hands, rules, scoring, betting | Factory, Strategy, Command |
| 🔹 **Tic-Tac-Toe / Connect Four**              | board, player turns, win conditions | State, Strategy |
| 🔹 **Snake / Tetris / Pac-Man**                | game loop, collision, scoring | State, Command, Observer |
| 🔹 **Sudoku Solver/Generator**                 | grid, validation, difficulty levels | Strategy, Factory |
| 🔹 **Minesweeper**                             | grid, mines, revealing, flagging | Command, State |
| 🔹 **RPG Character System**                     | attributes, skills, inventory, progression | Decorator, Factory, Strategy |
| 🔹 **Turn-based Strategy Game**                | units, actions, resources, map | Strategy, Command, Composite |

---

## 🧠 **3. In-Memory Storage & Cache Systems (15%)**

| Problem                                         | Keywords | Design Patterns |
|------------------------------------------------|----------|-----------------|
| 🔹 **LRU/LFU Cache Implementation**            | eviction policy, capacity, O(1) operations | Strategy, Singleton |
| 🔹 **In-memory Key-Value Store**               | CRUD operations, TTL, persistence | Proxy, Factory |
| 🔹 **Trie for Autocomplete System**            | prefix search, word suggestion, ranking | Composite |
| 🔹 **File System Simulation**                  | directories, files, permissions, operations | Composite, Proxy |
| 🔹 **Distributed Cache**                       | sharding, replication, consistency | Proxy, Strategy |
| 🔹 **Rate Limiter**                            | algorithms, window tracking, throttling | Strategy, Singleton |
| 🔹 **In-memory Database**                      | indexing, querying, transactions | Repository, Factory |
| 🔹 **Log Aggregation System**                  | collection, storage, search, rotation | Observer, Strategy |

---

## 🌐 **4. Online Platforms & Services (12%)**

| Problem                                         | Keywords | Design Patterns |
|------------------------------------------------|----------|-----------------|
| 🔹 **Social Media Platform**                   | profiles, posts, connections, feed | Observer, Factory, Proxy |
| 🔹 **Content Management System**               | articles, media, workflow, permissions | Composite, Command, Strategy |
| 🔹 **Online Movie Streaming Service**          | catalog, playback, recommendations | Strategy, Factory, Observer |
| 🔹 **Food Delivery System**                    | restaurants, orders, delivery, tracking | Observer, State, Strategy |
| 🔹 **Job Portal / Applicant Tracking**         | listings, applications, workflow | State, Observer |
| 🔹 **Chat Application**                        | messages, groups, status, notifications | Observer, State, Mediator |
| 🔹 **Online Learning Platform**                | courses, lessons, progress tracking | Composite, Observer, State |
| 🔹 **Payment Processing System**               | methods, transactions, security | Strategy, Chain of Responsibility |

---

## ⚙️ **5. Machine Design & State Systems (10%)**

| Problem                                         | Keywords | Design Patterns |
|------------------------------------------------|----------|-----------------|
| 🔹 **Traffic Light Controller**                | states, timing, sequences | State, Command |
| 🔹 **Washing Machine Simulator**               | cycles, programs, sensors | State, Command, Strategy |
| 🔹 **Turnstile / Access Control System**       | entry/exit, authentication | State, Observer |
| 🔹 **Automated Teller Machine (ATM)**          | transaction flow, error handling | State, Command |
| 🔹 **Workflow Engine**                         | tasks, transitions, conditions | State, Command, Chain of Responsibility |
| 🔹 **IoT Device Management**                   | device states, commands, telemetry | Observer, Command, State |
| 🔹 **Finite State Machine Implementation**     | states, events, transitions, actions | State, Command, Observer |
| 🔹 **Multi-step Form Processor**               | validation, navigation, submission | State, Command, Template |

---

## 🧱 **6. Custom Data Structures (8%)**

| Problem                                         | Keywords | Design Patterns |
|------------------------------------------------|----------|-----------------|
| 🔹 **Enhanced Stack (MinStack, MaxStack)**     | custom operations, O(1) complexity | Decorator, Adapter |
| 🔹 **Circular Buffer / Ring Buffer**           | fixed size, FIFO with wraparound | Iterator, Adapter |
| 🔹 **Interval Tree / Range Query Structure**   | overlapping intervals, range operations | Composite |
| 🔹 **Sparse Matrix Implementation**            | efficient storage, operations | Proxy, Flyweight |
| 🔹 **Multi-dimensional Array**                 | indexing, traversal, operations | Iterator, Adapter |
| 🔹 **Custom HashMap with Load Balancing**      | hashing, collision resolution, resizing | Strategy |
| 🔹 **Excel-like Cell Reference System**        | cell dependencies, formula evaluation | Observer, Composite |
| 🔹 **Prefix/Suffix Data Structure**            | pattern matching, string operations | Strategy, Composite |

---

## 📣 **7. Event-driven & Messaging Systems (5%)**

| Problem                                         | Keywords | Design Patterns |
|------------------------------------------------|----------|-----------------|
| 🔹 **Publish-Subscribe System**                | topics, subscribers, message delivery | Observer, Mediator |
| 🔹 **Event Bus / Message Broker**              | routing, persistence, delivery guarantees | Observer, Mediator, Strategy |
| 🔹 **Notification Service**                    | channels, preferences, delivery | Observer, Strategy, Template |
| 🔹 **Chat Server**                             | real-time messaging, presence | Observer, Mediator |
| 🔹 **Webhook Management System**               | registration, dispatch, retries | Observer, Strategy |
| 🔹 **Real-time Collaboration Tool**            | document sharing, conflict resolution | Observer, Command |
| 🔹 **Reactive Programming Framework**          | streams, operators, subscription | Observer, Strategy, Iterator |
| 🔹 **IoT Message Processing Pipeline**         | ingestion, transformation, routing | Chain of Responsibility, Strategy |

---

## 📅 **8. Scheduling & Resource Management (5%)**

| Problem                                         | Keywords | Design Patterns |
|------------------------------------------------|----------|-----------------|
| 🔹 **Meeting Room Scheduler**                  | availability, bookings, conflicts | Strategy, Observer |
| 🔹 **Calendar System**                         | events, recurrence, notifications | Strategy, Observer, Composite |
| 🔹 **Task Scheduler with Dependencies**        | DAG, priorities, execution | Strategy, Observer |
| 🔹 **Resource Allocation System**              | reservation, optimization | Strategy, Command |
| 🔹 **Job Queue / Worker Pool**                 | priorities, retries, throttling | Command, Strategy |
| 🔹 **Time-slot Booking System**                | availability, reservation, cancellation | Strategy, Command |
| 🔹 **Distributed Task Execution Framework**    | assignment, monitoring, load balancing | Command, Observer, Strategy |
| 🔹 **CPU Scheduler Simulation**                | algorithms, process management | Strategy, State |

---

## 🔄 **Design Patterns Frequently Used in OOD Problems**

| Pattern | Description | Example Applications |
|---------|-------------|----------------------|
| **Strategy** | Defines family of algorithms that are interchangeable | Pricing strategies, sorting algorithms, validation rules |
| **Factory** | Creates objects without specifying exact class | User types, payment methods, document types |
| **Observer** | Notifies dependents when object changes | UI updates, event handling, notifications |
| **Singleton** | Ensures only one instance of a class | Configuration, connection pools, loggers |
| **Command** | Encapsulates request as an object | Undo/redo, queueing tasks, transactions |
| **State** | Alters object behavior when state changes | Order processing, game states, workflow |
| **Decorator** | Adds responsibilities to objects dynamically | UI components, buffered streams, permission layers |
| **Composite** | Treats individual and compositions uniformly | File systems, UI hierarchies, organizational structures |
| **Proxy** | Represents another object | Remote services, lazy loading, access control |
| **Template Method** | Defines algorithm skeleton, deferring steps | Document generation, data processing pipelines |
| **Chain of Responsibility** | Passes request along chain of handlers | Error handling, event processing, filters |
| **Mediator** | Coordinates interaction between objects | Chat rooms, air traffic control, device communication |
| **Flyweight** | Shares objects to support large numbers | Character rendering, particle systems, cached objects |
| **Iterator** | Accesses elements sequentially | Custom collections, data streams, pagination |
| **Adapter** | Converts interface to another | Legacy system integration, third-party libraries |

---

## 📝 **Interview Approach Tips**

1. **Clarify Requirements**: Ask questions to understand the problem scope and constraints
2. **Identify Key Objects**: Determine the main entities and their relationships
3. **Define Class Hierarchy**: Establish inheritance structures and abstractions
4. **Outline Interfaces**: Define how classes will interact with each other
5. **Apply Design Patterns**: Identify where patterns can solve specific challenges
6. **Consider Edge Cases**: Address boundary conditions and error scenarios
7. **Evaluate Extensibility**: Ensure your design can accommodate future requirements
8. **Implement Core Methods**: Code key methods to demonstrate your design works

---

## 🚀 **Recent Trends in OOD Interview Questions**

- **Microservices Architecture**: Designing bounded contexts and service interactions
- **Domain-Driven Design**: Focusing on core domain models and ubiquitous language
- **Event-Sourcing**: Modeling systems around events rather than current state
- **CQRS Pattern**: Separating read and write operations for scalability
- **Reactive Systems**: Building responsive, resilient, elastic, and message-driven applications
- **Immutable Objects**: Designing with immutability for thread safety and simpler reasoning
- **Functional Design Elements**: Incorporating functional concepts within OO designs
