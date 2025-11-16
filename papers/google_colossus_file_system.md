- improves scalability and performance over GFS using a distributed metadata model for better data management and low latency

- Google Colossus system https://cloud.google.com/blog/products/storage-data-transfer/a-peek-behind-colossus-googles-file-system

- The original GFS system used a centralized control plane (in the form of a manager) to keep the design simple.
- GFS designers used interesting approaches so that a single manager does not become a single point of failure.
- However, over the years, while a GFS cluster has been able to grow to a multi-petabytes level, the single manager design was approaching its scalability limits.
- The primary reasons for building Colossus were
  - To scale for data beyond petabytes with good horizontal scalability.
  - To enable more kinds of applications (for example, files with small data, apps that need low latency at the tail, for example, p99, etc.).
  - To enable clients to pick from full replication, Reed-Solomon-based encoding for space-saving, or the use of RAID.

<br/>

- Reed–Solomon codes are a group of error-correcting codes.
- They have numerous uses, one of which is in the mass storage systems to correct the burst errors associated with media defects.

<br/>

- RAID stands for “redundant array of inexpensive disks” or “redundant array of independent disks”.
- It is a data storage virtualization technology that combines multiple physical disk drive components into one or more logical units for the purposes of data redundancy, performance improvement, or both.
