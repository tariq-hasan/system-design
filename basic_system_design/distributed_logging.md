# To-Do List

- [ ] [Facebook System Design Interview: Design an Analytics Platform (Metrics & Logging)](https://www.youtube.com/watch?v=kIcq1_pBQSY)
- [ ] [Distributed Metrics/Logging Design Deep Dive with Google SWE! | Systems Design Interview Question 14](https://www.youtube.com/watch?v=_KoiMoZZ3C8)

# Logging

- A log file records details of events occurring in a software application.
- The details may consist of microservices, transactions, service actions, etc. to debug the flow of an event in the system.

<br/>

- Use cases
  - Understand the flow of an event in a distributed system.
  - Pinpoint when and how a system failed or was compromised and find out the root cause of the failure or breach.
  - Decrease the meantime to repair a system.

<br/>

- Logging is an I/O intensive operation (time-consuming and slow).

## Restrain the log size

- Problem
  - The number of logs increases over time.
  - At a time, hundreds of concurrent messages need to be logged.
  - But not all are important enough to be logged.
Solution
- Structure logs to help decide what to log into the system on the application or logging level.

### Use sampling

- Scenario where the sampling approach works:
  - e.g. large systems like Facebook where billions of events happen per second
  - e.g. situation where we have lots of messages from the same set of events
  - e.g. people commenting on a post, where Person X commented on Person Y’s post, then Person Z commented on Person Y’s post, etc.
  - Use a sampler service (with a sampling threshold and strategy) that logs only a smaller and representative set of messages from a larger chunk.
  - Categorize the types of messages and apply a filter that identifies the important messages and logs only those messages to the system.

<br/>

- Scenario where the sampling approach does not work:
  - e.g. application that processes a financial ATM transaction and runs services like fraud detection, expiration time checking, card validation, etc.
  - If logging of any service is missed out, end-to-end flow of events cannot be identified when debugging errors.

### Use categorization

- Severity levels used in logging: DEBUG, INFO, WARNING, ERROR, FATAL/CRITICAL.
- Production logs are set to print messages with the severity of WARNING and above.
- For more detailed flow, severity levels can be set to DEBUG and INFO levels.

## Structure the logs

- Applications have the liberty to choose the structure of their log data.
- For example, an application is free to write to log as binary or text data, but it is often helpful to enforce some structure on the logs.
- Benefits of structured logs:
  - better interoperability between log writers and readers
  - make the job of a log processing system easier

<br/>

- [PhD thesis by Ryan Braud titled "Query-based debugging of distributed systems."](https://escholarship.org/uc/item/2p06d5sv)

## Points to consider while logging

- For secure data log encrypted data.
- Avoid logging personally identifiable information (PII), such as names, addresses, emails, and so on.
- Avoid logging sensitive information like credit card numbers, passwords, and so on.
- Avoid excessive information. Logging all information is unnecessary and only takes up more space and affects performance (logging is an I/O-heavy operation).
- The logging mechanism should be secure and not vulnerable because logs contain the application’s flow, and an insecure logging mechanism is vulnerable to hackers.

### Vulnerability in logging infrastructure

- A zero-day vulnerability in Log4j, a famous logging framework for Java, has been identified as of November 2021.
- Log4j has contained the hidden vulnerability, Log4Shell (CVE-2021-44228), since 2013.
- Apache gave the highest available score, a CVSS severity rating of 10, to Log4Shell. 
- The exploit is simple to execute and affects hundreds of millions of devices.
- This vulnerability can allow devastating cyberattacks because it can enable attackers to run malicious code and take control of the machine.

# Design of a Distributed Logging Service

- System that allows services in a distributed system to log their events efficiently
- System should log all activities or messages (without incorporating sampling ability)

## Requirements

### Functional requirements

- Writing logs: The services of the distributed system must be able to write into the logging system.
- Searchable logs: It should be effortless for a system to find logs. Similarly, the application’s flow from end-to-end should also be effortless.
- Storing logging: The logs should reside in distributed storage for easy access.
- Centralized logging visualizer: The system should provide a unified view of globally separated services.

### Non-functional requirements

- Low latency: Logging is an I/O-intensive operation that is often much slower than CPU operations. We need to design the system so that logging is not on an application’s critical path.
- Scalability: We want our logging system to be scalable. It should be able to handle the increasing amounts of logs over time and a growing number of concurrent users.
- Availability: The logging system should be highly available to log the data.

## Building blocks we will use

- Pub-sub system to handle the huge size of logs
- Distributed search to query the logs efficiently

## API design

- Write a message
  - write(unique_ID, message_to_be_logged)
  - unique_ID is a numeric ID containing application-id, service-id, and a time stamp.
  - message_to_be_logged is the log message stored against a unique key.

- Search log
  - searching(keyword)
  - keyword is used for finding logs containing the keyword.

## Initial design

In a distributed system, clients across the globe generate events by requesting services from different serving nodes. The nodes generate logs while handling each of the requests. These logs are accumulated on the respective nodes.

In addition to the building blocks, let’s list the major components of our system:
- Log accumulator: An agent that collects logs from each node and dumps them into storage. So, if we want to know about a particular event, we don’t need to visit each node, and we can fetch them from our storage.
- Storage: The logs need to be stored somewhere after accumulation. We’ll choose blob storage to save our logs.
- Log indexer: The growing number of log files affects the searching ability. The log indexer will use the distributed search to search efficiently.
- Visualizer: The visualizer is used to provide a unified view of all the logs.





## Logging at various levels

### In a server

### At datacenter level

## Conclusion
