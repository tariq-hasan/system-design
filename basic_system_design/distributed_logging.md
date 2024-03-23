# To-Do List

- [ ] [Facebook System Design Interview: Design an Analytics Platform (Metrics & Logging)](https://www.youtube.com/watch?v=kIcq1_pBQSY)
- [ ] [Distributed Metrics/Logging Design Deep Dive with Google SWE! | Systems Design Interview Question 14](https://www.youtube.com/watch?v=_KoiMoZZ3C8)

# Logging

- A log file records details of events occurring in a software application.
- The details may consist of microservices, transactions, service actions, etc. to debug the flow of an event in the system.

<br/>

- Use cases
  - understand the flow of an event in a distributed system
  - pinpoint when and how a system failed or was compromised and find out the root cause of the failure or breach
  - decrease the meantime to repair a system

<br/>

- Logging is an I/O intensive operation (time-consuming and slow).

## Restrain the log size

- The number of logs increases over time.
- At a time, perhaps hundreds of concurrent messages need to be logged.
- But the question is, are they all important enough to be logged?
- To solve this, logs have to be structured.
- We need to decide what to log into the system on the application or logging level.

### Use sampling

- Scenario where the sampling approach works:
  - e.g. large systems like Facebook where billions of events happen per second
  - e.g. situation where we have lots of messages from the same set of events
  - e.g. people commenting on a post, where Person X commented on Person Y’s post, then Person Z commented on Person Y’s post, etc.
  - Use a sampler service (with a sampling threshold and strategy) that logs only a smaller and representative set of messages from a larger chunk
  - Categorize the types of messages and apply a filter that identifies the important messages and logs only those messages to the system

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
- Avoid excessive information. Logging all information is unnecessary. It only takes up more space and affects performance. Logging, being an I/O-heavy operation, has its performance penalties.
- The logging mechanism should be secure and not vulnerable because logs contain the application’s flow, and an insecure logging mechanism is vulnerable to hackers.

### Vulnerability in logging infrastructure

- A zero-day vulnerability in Log4j, a famous logging framework for Java, has been identified as of November 2021.
- Log4j has contained the hidden vulnerability, Log4Shell (CVE-2021-44228), since 2013.
- Apache gave the highest available score, a CVSS severity rating of 10, to Log4Shell. 
- The exploit is simple to execute and affects hundreds of millions of devices.
- This vulnerability can allow devastating cyberattacks because it can enable attackers to run malicious code and take control of the machine.

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
