# To-Do List

- [ ] [Facebook System Design Interview: Design an Analytics Platform (Metrics & Logging)](https://www.youtube.com/watch?v=kIcq1_pBQSY)
- [ ] [Distributed Metrics/Logging Design Deep Dive with Google SWE! | Systems Design Interview Question 14](https://www.youtube.com/watch?v=_KoiMoZZ3C8)

# Logging

- Logging is an I/O intensive operation that is time-consuming and slow.

<br/>

- A log file records details of events occurring in a software application.
- The details may consist of microservices, transactions, service actions, or anything helpful to debug the flow of an event in the system.

<br/>

- Logging is essential in understanding the flow of an event in a distributed system.
- It seems like a tedious task, but upon facing a failure or a security breach, logging helps pinpoint when and how the system failed or was compromised.
- It can also aid in finding out the root cause of the failure or breach.
- It decreases the meantime to repair a system.
  - Mean time to repair (MTTR) is a basic measure of the maintainability of repairable items.
    It represents the average time required to repair a failed component or device.

## Restrain the log size

- The number of logs increases over time.
- At a time, perhaps hundreds of concurrent messages need to be logged.
- But the question is, are they all important enough to be logged?
- To solve this, logs have to be structured.
- We need to decide what to log into the system on the application or logging level.

### Use sampling

- We’ll determine which messages we should log into the system in this approach.
- Consider a situation where we have lots of messages from the same set of events.
- For example, there are people commenting on a post, where Person X commented on Person Y’s post, then Person Z commented on Person Y’s post, and so on.
- Instead of logging all the information, we can use a sampler service that only logs a smaller set of messages from a larger chunk.
- This way, we can decide on the most important messages to be logged.

- For large systems like Facebook, where billions of events happen per second, it is not viable to log them all.
- An appropriate sampling threshold and strategy are necessary to selectively pick a representative data set.

- We can also categorize the types of messages and apply a filter that identifies the important messages and only logs them to the system.

- A scenario where the sampling approach will not work
  - Let’s consider an application that processes a financial ATM transaction.
  - It runs various services like fraud detection, expiration time checking, card validation, and many more.
  - If we start to miss out logging of any service, we cannot identify an end-to-end flow that affects the debugging in case an error occurs.
  - Using sampling, in this case, is not ideal and results in the loss of useful data.

### Use categorization

- The following severity levels are commonly used in logging: DEBUG, INFO, WARNING, ERROR, FATAL/CRITICAL
- Usually, the production logs are set to print messages with the severity of WARNING and above.
- But for more detailed flow, the severity levels can be set to DEBUG and INFO levels too.

## Structure the logs

- Applications have the liberty to choose the structure of their log data.
- For example, an application is free to write to log as binary or text data, but it is often helpful to enforce some structure on the logs.
- The first benefit of structured logs is better interoperability between log writers and readers.
-  Second, the structure can make the job of a log processing system easier.

- [PhD thesis by Ryan Braud titled "Query-based debugging of distributed systems."](https://escholarship.org/uc/item/2p06d5sv)

## Points to consider while logging

- The logging information should only contain the relevant information and not breach security concerns.
- For secure data, we should log encrypted data.
- We should consider the following few points while logging:
  - Avoid logging personally identifiable information (PII), such as names, addresses, emails, and so on.
  - Avoid logging sensitive information like credit card numbers, passwords, and so on.
  - Avoid excessive information. Logging all information is unnecessary. It only takes up more space and affects performance. Logging, being an I/O-heavy operation, has its performance penalties.
  - The logging mechanism should be secure and not vulnerable because logs contain the application’s flow, and an insecure logging mechanism is vulnerable to hackers.

### Vulnerability in logging infrastructure

- A zero-day vulnerability in Log4j, a famous logging framework for Java, has been identified as of November 2021.
- Log4j has contained the hidden vulnerability, Log4Shell (CVE-2021-44228), since 2013.
- Apache gave the highest available score, a CVSS severity rating of 10, to Log4Shell. 
- The exploit is simple to execute and affects hundreds of millions of devices.
- Security experts are convinced that this vulnerability can allow devastating cyberattacks internationally because it can enable attackers to run malicious code and take control of the machine.

# Design of a Distributed Logging Service

- We will design a system that allows services in a distributed system to log their events efficiently.

## Requirements

### Functional requirements

### Non-functional requirements

## Building blocks we will use

## API design

## Initial design

## Logging at various levels

### In a server

### At datacenter level

## Conclusion
