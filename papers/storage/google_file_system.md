# [WIP] Table of Contents

1. [To-Do List](#to-do-list)
2. [Motivation](#motivation)
   - [Single-Node File System](#single-node-file-system)
   - [NAS System](#nas-system)
   - [SAN System](#san-system)
3. [Functional Requirements](#functional-requirements)
4. [Non-Functional Requirements](#non-functional-requirements)
5. [Bird’s Eye View](#birds-eye-view)
6. [File Operations](#file-operations)
7. [Design](#design)
8. [Workflow of Create and Read File Operations in GFS](#workflow-of-create-and-read-file-operations-in-gfs)
9. [Workflow of Write Operations in GFS](#workflow-of-write-operations-in-gfs)
10. [Workflow of Delete and Snapshot Operations in GFS](#workflow-of-delete-and-snapshot-operations-in-gfs)
11. [Relaxed Data Consistency Model](#relaxed-data-consistency-model)
12. [Dealing with Data Inconsistencies in GFS](#dealing-with-data-inconsistencies-in-gfs)
13. [Metadata Consistency Model of GFS](#metadata-consistency-model-of-gfs)
14. [Evaluation of GFS](#evaluation-of-gfs)

# To-Do List

- [ ] [Sanjay Ghemawat, Howard Gobioff, and Shun-Tak Leung. 2003. The Google file system. In Proceedings of the nineteenth ACM symposium on Operating systems principles (SOSP '03). Association for Computing Machinery, New York, NY, USA, 29–43.](https://dl.acm.org/doi/10.1145/945445.945450)

# Motivation

- GFS is an example of co-designing where GFS was purpose-built on commodity hardware and, for specific use cases, write and read-heavy workloads with a lot of concurrent activity.

## Single-Node File System

- A single-node file system is a system that runs on a single computer and manages the storage attached to it.
- A single server has limited resources like storage space, processing power, as well as I/O operations that can be performed on a storage disk per second.
- We can attach substantial storage capacity to a single server, increase the RAM, and upgrade the processor, but there are limits to this type of vertical scaling.
- A single server also has limitations regarding the number of data reads and writes, and how quickly data is stored and accessed.
- These limitations restrict the system's ability to process large datasets and serve a large number of clients simultaneously.
- A single-node system is also a single point of failure where the system becomes unavailable to the users.
- The focus should be on high throughput rather than low latency for applications requiring processing of large datasets.

## NAS System

- The network-attached storage system consists of a file-level storage server with multiple clients connected to it over a network running the network file system (NFS) protocol.
- Clients can store and access the files on this remote storage server like the local files.
- The NAS system has the same limitations as a single-node file system.
- Setting up and managing a NAS system is easy but expensive to scale.
- This system can also suffer from throughput issues while accessing large files from a single server.

## SAN System

- The storage area network system consists of a cluster of commodity storage devices connected to each other, providing block-level data storage to the clients over the network.
- SAN systems are easy to scale by adding more storage devices.
- However, these systems are difficult to manage because of the complexity of the second network — the Fiber Channel (FC).
- To set up the Fiber Channel, we need dedicated host bus adapters (HBAs) to be deployed on each host server, switches, and specialized cabling.
- It is difficult to monitor where failure has occurred in this complex system.
- Data inconsistency issues among replicas may appear in this case.
- Rebalancing the load on the storage devices might also be difficult to handle with this architecture.

<br/>

- SAN deployments are special-purpose networks apart from the usual Ethernet networks.
- This duplicate network, while good for segregating storage traffic, is expensive in terms of dollar cost.

<br/>

![Traditional Networked File Systems](images/traditional_networked_file_systems.png)
*Caption: The traditional networked file systems*

# Functional Requirements

- Data storage: The system should allow users to store their data on GFS.
- Data retrieval: The system should be able to give data back to users when they request it.

# Non-Functional Requirements

- Scalability
  - The system should be able to store an increasing amount of data (hundreds of terabytes and beyond), and handle a large number of clients concurrently.
- Availability
  - A file system is one of the main building blocks of many large systems used for data storage and retrieval.
  - The unavailability of such a system disrupts the operation of the systems that rely on it.
  - Therefore, the file system should be able to respond to the client’s requests all the time.
- Fault tolerance
  - The system’s availability and data integrity shouldn’t be compromised by component failures that are common in large clusters consisting of commodity hardware.
- Durability
  - Once the system has acknowledged to the user that its data has been stored, the data shouldn’t be lost unless the user deletes the data themselves.
- Easy operational management
  - The system should easily be able to store multi-GB files and beyond.
  - It should be easy for the system to handle data replication, re-replication, garbage collection, taking snapshots, and other system-wide management activities.
  - If some data becomes stale, there should be an easy mechanism to detect and fix it.
  - The system should allow multiple independent tenants to use GFS for safe data storage and retrieval.
- Performance optimization
  - The focus should be on high throughput rather than low latency for applications that require processing for large datasets.
  - Additionally, Google’s applications, for which the system was being built, most often append data to the files instead of overwriting the existing data.
  - So, the system should be optimized for append operations.
  - For example, a logging application appends log files with new log entries.
  - Instead of overwriting existing copies of the crawled data within a file, a web crawler appends new web crawl data to a crawl file.
  - All MapReduce outputs write a file from beginning to end by appending key/value pairs to the file(s).
- Relaxed consistency model
  - GFS does not need to comply with POSIX standards because of the unique characteristics of the use cases/applications that it targets to serve.
  - A file system must implement a strong consistency model in order to be POSIX compatible.
  - In POSIX, random write is one of the fundamental operations.
  - In GFS, there are more append operations and very few random writes.
  - That’s why GFS doesn’t comply with POSIX and provides a relaxed consistency model that is optimized for append operations.
  - Data consistency in a distributed setting is hard, and GFS carefully opts for a custom-consistency model for better scalability and performance.

<br/>

- The Portable Operating System Interface (POSIX) is a set of standards set out by the IEEE Computer Society to support compatibility between operating systems.
- It defines system and user-level application programming interfaces (API), command line shells, and utility interfaces for software portability among operating system variants.
- Both application and system developers are encouraged to use POSIX.

# Architecture

- A GFS cluster consists of two major types of components – a manager node and a large number of chunk servers.
- It stores a file’s data in the form of chunks.
- A chunk is a unit of data storage in GFS.

<br/>

![Architecture of GFS](images/gfs_architecture.png)
*Caption: Architecture of GFS*

<br/>

- The client is a GFS application program interface through which the end users perform the directory or the file operations.

<br/>

- Each file is split into fixed-size chunks.
- The manager assigns each chunk a 64-bit globally unique ID and assigns chunkservers where the chunk is stored and replicated.
- A manager is like an administrator that manages the file system metadata, including namespaces, file-to-chunk mapping, and chunk location.
- The metadata is stored in the manager’s memory for good performance.
- For a persistent record of the metadata, the manager logs the metadata changes in an operation log placed on the manager’s hard disk so that it can recover its state after the restart by replaying the operation log.
- Besides managing metadata, the manager also handles the following tasks:
  - Data replication and rebalancing
  - Operational locks to ensure data consistency
  - Garbage collection of the deleted data

<br/>

- Chunkservers are commodity storage servers that store chunks as plain Linux files.

<br/>

- The client requests the manager node for metadata information, such as the location of the requested chunks.
- The manager looks into its metadata and responds to the client with the location of the requested chunks.
- The client then asks the chunkservers for the data operations.
- It is important to note that the data doesn't flow through the manager but directly between the client and the chunkserver.
- Note: The largest GFS cluster can store up to tens of petabytes of data and can be accessed by hundreds of clients concurrently.

<br/>

How does a single manager suffice to handle requests from hundreds of clients?
- According to the architecture of GFS, the manager appears to have a tremendous amount of work to do and this could act as a bottleneck.
- For the simplicity a single manager offers, making it lighter weight is worthwhile instead of switching to a distributed manager.
- GFS optimizes the single manager by:
  - Minimizing manager involvement in read/write operations. First, it separates the data and the control flow, so the data doesn’t need to pass through the manager. The client has to interact with the manager only for the metadata. Secondly, the chunk size is kept large to reduce the metadata requests on the manager.
  - Keeping the metadata in memory and serving the clients from there.
  - Caching the metadata on the client side

<br/>

Does the in-memory approach for storing metadata put a limitation on the amount of data we can store? The more data, the more the metadata would be.
- Practically, it’s not a big issue as the space required to store metadata per file is small.
- Less than 64 bytes are needed to store file-specific information such as the file name, and less than 64 bytes are required to keep each chunk’s metadata.
- Moreover, the cost of adding additional memory to a single manager is negligible compared to the gains in performance and simplicity a single manager architecture provides.

<br/>

How can we reduce the amount of time required to replay the growing operation log to rebuild the manager state?
- Checkpoint the manager state when the log grows beyond a certain size.
- Load the latest checkpoint and replay the logs that are recorded after the last saved checkpoint.

# Bird’s Eye View

![GFS Concept Map](images/gfs_concept_map.png)
*Caption: GFS Concept Map*

# File Operations

- GFS client API
  - create - file, directory
  - read - file
  - write - file
  - delete - file, directory
  - open - file
  - close - file
  - list - directory
  - snapshot - file, directory
  - record append

<br/>

- Delete directory
    - This operation does not leave dangling data on the chunkservers.
    - All the files in the directory are deleted before deleting the directory itself.
    - If the directory contains files, GFS asks the client to delete those files first.

<br/>

- List directory
    - GFS does not have a inode-like data structure for representing namespaces.
    - GFS represents a file with its full pathname.
    - A lookup table is maintained that maps the full pathname of a file to its metadata.
    - This table logically represents the namespace.
    - The last component in the path can be a file or a directory.
    - The rest of the path is all about directories.
    - Listing a directory with a path should list the path names that are one name longer than it.

<br/>

- Index node
  - The inode is a data structure in a Unix-style file system that defines file system object (FSO) model like files or directories.
  - Each inode stores the attributes and disk block locations of the object's data.
  - Attributes of a file or a directory object may include metadata like times of last change, access, and modification, with owner and permission data.
  - A directory is a list of inodes with their assigned names.
  - The list includes an entry for itself, its parent, and each of its children.

<br/>

- Create a file
    - The operation is performed atomically.
    - Multiple users can concurrently create files in the same directory.
    - If there are N concurrent requests to create a file with the same name in the same directory, only one of the request is successful, while other N-1 clients will receive an error.
    - The directory where one user creates a file is not deleted by another user who has access to that directory.

<br/>


# Design

# Workflow of Create and Read File Operations in GFS

# Workflow of Write Operations in GFS

# Workflow of Delete and Snapshot Operations in GFS

# Relaxed Data Consistency Model

# Dealing with Data Inconsistencies in GFS

# Metadata Consistency Model of GFS

# Evaluation of GFS



GFS allows operations such as appending data to a file to be performed concurrently by multiple clients. Explain.
The Atomic Record Append operation ensures that when multiple clients append data to a file, their writes are atomically executed without interference, preserving the integrity of each append operation. Explain.
GFS is designed to support a high degree of concurrency, meaning multiple clients can read from and write to the file system simultaneously without significant performance degradation. Explain.
GFS provides an atomic record append operation that allows multiple clients to append data to the same file concurrently. This feature is crucial for workloads where multiple processes need to write to a shared log or data file, ensuring that the system can handle concurrent writes without sacrificing performance. Explain.
Without atomic record append, coordinating these writes would be challenging, potentially leading to race conditions where one process's logs could overwrite another's. Explain.
The operation is designed to handle high levels of concurrency, allowing multiple clients to append data to the file simultaneously. GFS manages this concurrency by coordinating the appends at the chunk level, ensuring that all data is appended in the correct order, even when multiple clients are writing at the same time. Explain.
If an error occurs during an append operation, GFS ensures that the error is reported to the client, and the operation does not leave the file in an inconsistent state. This reliability is crucial for applications that depend on the integrity of the appended data, such as transactional logs or audit trails. Explain.

The design decisions, such as large chunk size and distributed architecture, contribute to high throughput. Explain.
By allowing multiple clients to operate on different chunks of a file simultaneously, GFS achieves high data throughput, which is crucial for large-scale data processing tasks like indexing and map-reduce jobs. Explain.
Write and Read-Heavy Workloads: GFS was purpose-built for large files, frequent reads and writes, and the need for high throughput. This includes operations like web indexing, map-reduce jobs, and log processing.
GFS is optimized for large, sequential reads and writes rather than small, random I/O operations. Explain.
GFS stores files in large chunks (typically 64 MB), which reduces the overhead of metadata management and allows for efficient handling of large files. Explain.
GFS is particularly well-suited for workloads that involve large files and sequential access patterns, which are common in data processing tasks like MapReduce. In these scenarios, multiple clients or processes often need to read large amounts of data simultaneously. GFS's architecture is optimized to handle such concurrent access efficiently. Explain.

GFS is designed to handle server failures gracefully. Explain.
How does GFS detect and recover from hardware failures?
Explain the difference between disk failure and server crash.
GFS includes robust mechanisms for fault detection, data replication, and recovery. Explain.
GFS's architecture supports distributed operations, where different parts of the data are handled by different servers, reducing bottlenecks. Explain.

GFS uses a relaxed consistency model that fits Google's specific needs, such as eventual consistency with strong guarantees for certain operations like atomic record append. Explain.
GFS uses a relaxed consistency model that provides strong guarantees for specific operations, such as atomic record appends, while allowing for eventual consistency in other cases. This model is sufficient for many of Google's applications and allows the system to remain highly available and performant even under heavy loads. Explain.

By dividing files into large chunks, GFS can efficiently manage and store very large files, which are common in data-intensive applications. The chunk size is optimized to reduce the overhead of metadata and to enable efficient handling of large sequential reads and writes. Explain.

Since chunks of a file are distributed across multiple servers, GFS can read and write data in parallel, greatly increasing the throughput. Multiple clients can access different chunks of the same file simultaneously, leading to significant performance gains in large-scale data processing tasks. Explain.

GFS is particularly well-suited for applications that deal with large files and require high throughput, such as web indexing, data mining, and large-scale scientific computations. The system's design focuses on optimizing performance for these types of workloads. Explain.

The master server provides a single point of control for managing the file system, simplifying tasks such as data replication, garbage collection, and load balancing. Explain.

What is a large sequential read or write?
What is a sequential access pattern?
Why is this common in big data processing such as such as batch processing, data mining, and log processing?

Why are fewer disk seeks when data is read or written sequentially?
Why does fewer disk seeks significantly improve performance?

How does GFS detect a sequential read pattern?
What does it mean for GFS to prefetch data from the next sequential chunks when it detects a sequential read pattern?
Why is it necessary to split or reallocate chunks when writing to GFS?

GFS is optimized for workloads where files are written once and then read multiple times. Explain.
