# Domain Name System

- Computers are uniquely identified by IP addresses - for example, 104.18.2.119 is an IP address.
- We use IP addresses to visit a website hosted on a machine.
- Humans cannot easily remember IP addresses to visit domain names (an example domain name being educative.io), so we need a phone book-like repository that can maintain all mappings of domain names to IP addresses.
- DNS is the Internet’s naming service that maps human-friendly domain names to machine-readable IP addresses.

<br/>

- The service of DNS is transparent to users.
- When a user enters a domain name in the browser, the browser has to translate the domain name to IP address by asking the DNS infrastructure.
- Once the desired IP address is obtained, the user’s request is forwarded to the destination web server.

<br/>

- DNS focuses on how to design hierarchical and distributed naming systems for computers connected to the Internet via different Internet protocols.
- When you navigate to twitter.com, your web browser will send an HTTP request to Twitter’s servers to download the latest content.
- It will then render that content.
- In order to send this HTTP request, your browser will need the IP address of Twitter’s web server (or Twitter’s load balancer).
- DNS is the technology that makes this possible.
- It serves as the phonebook of the Internet, where it maps between the human-readable web URL (www.twitter.com) and the machine-readable, most up-to-date IP address (104.244.42.193).

# Forwarding Query

![DNS execution flow](images/domain_name_system_forwarding_query.png)

- The user requests to visit a website by entering its URL in the browser
- The browser requests the ISP to forward the DNS query to resolve the request for the IP address
- The ISP forwards the DNS query to the DNS infrastructure
- The DNS infrastructure responds with a list of IP addresses against the domain name
- The IP address(es) reach the browser
- The browser sends an HTTP request on the received IP address
- The ISP forwards the HTTP request to the web server

# Resource Records

- DNS records are pieces of information hosted on DNS servers that provide details about domains.

<br/>

- The DNS database stores domain name to IP address mappings in the form of resource records.
- The RR is the smallest unit of information that users request from the name servers.
- There are different types of RRs.
  - Type: NS (name server)
    - Description: Provides the hostname that is the authoritative DNS for a domain name
    - Name: Domain name
    - Value: Hostname
    - Example (Type, Name, Value): (NS, educative.io, dns.educative.io)
  - Type: A (address) for IPv4; AAAA for IPv6
    - Description: Provides the hostname to IP address mapping
    - Name: Hostname
    - Value: IP address
    - Example (Type, Name, Value): (A, relay1.main.educative.io, 104.18.2.119)
  - Type: CNAME (canonical name)
    - Description: Provides the mapping from alias to canonical hostname
    - Name: Hostname
    - Value: Canonical name
    - Example (Type, Name, Value): (CNAME, educative.io, server1.primary.educative.io)
  - Type: MX (mail exchange)
    - Description: Provides the mapping of mail server from alias to canonical hostname
    - Name: Hostname
    - Value: Canonical name
    - Example (Type, Name, Value): (MX, mail.educative.io, mailserver1.backup.educative.io)

## A Record

## CNAME Record

# DNS Hierarchy

## Iterative versus recursive query resolution

# Caching

# GeoDNS

# Dynamic IP Addresses

# Domain Forwarding

# Non-functional Requirements

## Scalability

## Reliability

## Consistency

## Security

# Test it out

## The nslookup output

## The dig output

