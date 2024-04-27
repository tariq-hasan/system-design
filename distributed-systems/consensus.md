- Consensus algorithms are used to gain consensus between nodes in distributed systems.

<br/>

- Properties of consensus algorithms:
  - agreement : every correct process must agree on the same value
  - validity: the value agreed upon must have been proposed by another process
  - termination: a value will eventually be decided by every correct process

<br/>

Failures a consensus algorithm might have to deal with:
- Fail-stop
- Network partition
- Fail-recover
- Byzantine failure

<br/>

Consensus algorithms:
- Paxos
- Chandra-Toueg
- Raft (Replicated and Fault Tolerant)
