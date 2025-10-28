# 60-Minute News Feed System Design Interview Structure

Here’s how I’d recommend structuring your time for maximum impact:

## **Minutes 1-5: Requirements Clarification (5 min)**

Ask targeted questions to scope the problem:

- **Functional**: Post creation, feed generation (home/user timeline), following/followers, likes/comments?
- **Scale**: How many users? Daily active users? Posts per day? Average followers per user?
- **Feed type**: Chronological, ranked, or hybrid? Pull (fan-out on read) vs Push (fan-out on write)?
- **Scope boundaries**: Are we including media (images/videos), notifications, or just text posts?

*Goal: Demonstrate you understand ambiguity and can drive requirements gathering*

## **Minutes 6-10: Back-of-Envelope Calculations (4 min)**

Quickly estimate to inform design decisions:

- Storage needs (posts, media, metadata)
- Read vs write ratio (typically 100:1 for social feeds)
- QPS for feed generation
- Bandwidth requirements

*Example: 500M DAU, 100M posts/day → ~1,150 writes/sec, ~115K reads/sec at peak*

## **Minutes 11-25: High-Level Architecture (14 min)**

Draw the core components and data flow:

- **API Gateway** → Load balancers
- **Write Path**: Post Service → Post DB → Fan-out Service → Feed Cache
- **Read Path**: Feed Service → Feed Cache → Ranking Service
- **Key datastores**: User DB, Post DB, Graph DB (followers), Feed Cache (Redis)
- **CDN** for media content
- **Message Queue** for async fan-out

Explain the **hybrid approach**:

- Fan-out on write for users with fewer followers (push model)
- Fan-out on read for celebrities (pull model)
- Cached feeds in Redis with TTL

*This is your core deliverable - make it clean and comprehensive*

## **Minutes 26-40: Deep Dive (14 min)**

Choose 2-3 areas based on interviewer interest:

**Option 1: Feed Generation Algorithm**

- How to merge timelines from multiple followed users
- Ranking signals (recency, engagement, user affinity)
- Personalization with ML models

**Option 2: Scalability & Performance**

- Sharding strategy (user-based for Graph DB, time-based for Posts)
- Cache invalidation strategies
- Hot user problem (celebrities with millions of followers)

**Option 3: Data Models**

- Post schema (id, user_id, content, timestamp, media_urls)
- Feed cache structure (user_id → sorted list of post_ids)
- Graph database for follow relationships

*Be ready to pivot based on what the interviewer probes*

## **Minutes 41-50: Trade-offs & Bottlenecks (9 min)**

Discuss explicitly:

- **Consistency vs Availability**: Eventual consistency for feeds is acceptable
- **Fan-out on write** (faster reads, more writes) vs **fan-out on read** (slower reads, less storage)
- **Hot celebrity problem**: Special handling, separate queue, selective fan-out
- **Real-time vs near-real-time**: Trade latency for consistency
- **Thundering herd**: Cache warming, request coalescing

*This shows senior-level thinking about real-world constraints*

## **Minutes 51-55: Additional Considerations (4 min)**

Briefly touch on:

- **Monitoring**: Feed latency, cache hit rates, queue depth
- **Privacy**: Block lists, private accounts
- **Content moderation**: Async filtering pipeline
- **Disaster recovery**: Multi-region replication, backup strategies
- **A/B testing**: Infrastructure for feed algorithm experiments

## **Minutes 56-60: Q&A and Wrap-up (4 min)**

- Answer any remaining questions
- Summarize key design decisions
- Mention what you’d improve with more time

-----

## **Pro Tips:**

1. **Time management**: Glance at the clock at 20, 40 minutes to stay on track
1. **Think aloud**: Narrate your reasoning as you draw
1. **Ask for feedback**: “Does this approach make sense?” or “Would you like me to dive deeper here?”
1. **Be flexible**: If interviewer wants to skip calculations and jump to architecture, adapt
1. **Draw continuously**: Keep building on your diagram throughout the interview
1. **Senior signals**: Proactively discuss trade-offs, mention monitoring/observability, acknowledge what you’re deliberately omitting

The key is balancing breadth (covering all major components) with depth (showing expertise in critical areas) while demonstrating clear communication and senior-level judgment.​​​​​​​​​​​​​​​​
