# Minutes 1-5: Requirements Clarification - Detailed Breakdown

This is your **most critical phase**. Senior engineers distinguish themselves by asking insightful questions that expose hidden complexity and demonstrate domain expertise. Here’s how to structure it:

-----

## **Minute 1-2: Functional Requirements (Core Features)**

### Questions to Ask:

**“Let me clarify the core functionality we’re building…”**

1. **Feed Types**

- “Are we designing a home feed (content from people you follow), a user profile feed (posts by one user), or both?”
- “Should users see their own posts in their feed?”

1. **Content Creation**

- “What can users post? Text only, or images/videos too?”
- “Are there character limits or file size restrictions we should consider?”
- “Do we support editing or deleting posts after creation?”

1. **Social Interactions**

- “Are we including likes, comments, and shares in this scope?”
- “Do interactions affect feed ranking, or is this purely chronological?”
- “Should users see interactions from their network (e.g., ‘John liked this post’)?”

1. **Following Model**

- “Is it a symmetric follow (mutual friends like Facebook) or asymmetric (Twitter/Instagram style)?”
- “Can users have both followers and friends?”

### What You’re Demonstrating:

- You understand there are multiple types of news feed systems
- You’re scoping the problem to fit 60 minutes
- You won’t make assumptions that derail your design later

-----

## **Minute 2-3: Non-Functional Requirements (Scale & Performance)**

### Questions to Ask:

**“Let me understand the scale we’re operating at…”**

1. **User Scale**

- “How many total users? Daily Active Users (DAU)?”
- “What’s the distribution? Are we dealing with celebrities who have millions of followers?”
- “Geographic distribution - global or specific regions?”

1. **Content Volume**

- “How many posts per day on average?”
- “What’s the average post size?”
- “If supporting media, what’s the mix? 80% images, 15% videos, 5% text?”

1. **Read/Write Patterns**

- “What’s the expected read-to-write ratio?” (Usually 100:1 or higher)
- “How many times does a user check their feed per day?”
- “Should feed updates be real-time or near-real-time?”

1. **Performance Expectations**

- “What’s the acceptable latency for loading a feed? 200ms? 500ms?”
- “How fresh should the feed be? Seconds, minutes, hours?”
- “What about availability? 99.9%? 99.99%?”

### Example Clarification with Interviewer:

**You:** “For scale, are we thinking Facebook-size—billions of users—or something smaller?”

**Interviewer:** “Let’s say 500 million total users, 200 million DAU.”

**You:** “Got it. And for celebrities or influencers with millions of followers, do we need special handling?”

**Interviewer:** “Yes, assume 1% of users have over 1 million followers.”

**You:** *(writes down)* “Perfect, that’ll inform our fan-out strategy.”

-----

## **Minute 3-4: Clarify Scope & Constraints**

### Questions to Ask:

**“To keep this focused, let me confirm what’s in and out of scope…”**

1. **What to Include**

- “Should we design the full end-to-end system, or focus on feed generation?”
- “Are we including the data model, or just the architecture?”
- “Do you want me to cover monitoring and observability?”

1. **What to Exclude**

- “Can we assume authentication is handled by another service?”
- “Should we cover spam detection and content moderation, or is that out of scope?”
- “Are we designing for mobile, web, or both?”
- “Do we need to discuss video encoding/transcoding, or can we assume a CDN handles that?”

1. **Technical Constraints**

- “Are we working with a specific tech stack, or should I propose one?”
- “Any preferences on databases—SQL, NoSQL, or a mix?”
- “Should we assume cloud infrastructure (AWS/GCP) or on-premise?”

### Why This Matters:

- **Senior signal**: You know system design interviews can spiral out of control
- You’re protecting your time budget by setting boundaries
- You’re showing you can prioritize what matters most

-----

## **Minute 4-5: Confirm Assumptions & Prioritize**

### Summarize Your Understanding:

**“Let me summarize what we’re building to make sure I understood correctly…”**

Create a quick verbal or written summary:

### Example Summary:

> **Functional:**
> 
> - Users can create text posts with optional images
> - Users follow others (asymmetric)
> - Home feed shows posts from followed users, ranked by relevance
> - Users can like and comment on posts
> 
> **Non-Functional:**
> 
> - 500M total users, 200M DAU
> - 100M posts/day
> - Read:Write ratio ~100:1
> - Feed latency <500ms
> - Near-real-time updates (minutes, not seconds)
> - Handle celebrity users with 1M+ followers
> 
> **Out of Scope:**
> 
> - Authentication/Authorization
> - Content moderation
> - Notifications
> - Direct messaging
> - Video processing details

**Then ask:** *“Does this align with what you had in mind, or should we adjust anything?”*

-----

## **Senior-Level Signals to Demonstrate:**

### ✅ **Do’s:**

1. **Ask clarifying questions, don’t make assumptions** - “Should I assume X, or would you like me to consider Y?”
1. **Acknowledge trade-offs early** - “If we prioritize real-time updates, that’ll impact our architecture compared to eventual consistency.”
1. **Show you’ve done this before** - “In my experience, read-heavy feeds typically have a 100:1 read-write ratio. Does that match your expectations?”
1. **Write things down** - Keep a running list of requirements visible on the whiteboard
1. **Stay engaged** - Make eye contact (if in-person), show enthusiasm

### ❌ **Don’ts:**

1. **Don’t jump straight to solutions** - Resist the urge to say “We’ll use Redis for caching” before understanding requirements
1. **Don’t ask yes/no questions exclusively** - Ask open-ended questions that invite discussion
1. **Don’t spend more than 5 minutes here** - Watch the clock; you have a lot to cover
1. **Don’t be passive** - Don’t wait for the interviewer to spoon-feed requirements
1. **Don’t over-complicate** - If interviewer says “keep it simple,” listen to them

-----

## **Red Flags Interviewers Watch For:**

- **Jumping to implementation** before understanding the problem
- **Not asking about scale** - This is a distributed systems problem; scale matters
- **Ignoring trade-offs** - Every design decision has costs
- **Being too rigid** - Not adapting when interviewer redirects
- **Analysis paralysis** - Asking 50 questions instead of 10-15 targeted ones

-----

## **Transitioning to Next Phase:**

**At the 5-minute mark, transition smoothly:**

> “Great, I have a clear picture now. Before I dive into the architecture, let me do some quick back-of-the-envelope calculations to size the system. This should take about 3-4 minutes. Sound good?”

This shows you’re:

- Time-conscious
- Structured in your approach
- Moving from requirements → estimation → design (the expected flow)

-----

## **Quick Reference Card (What to Write on Whiteboard):**

```
REQUIREMENTS SUMMARY
====================
Users: 500M total, 200M DAU
Posts: 100M/day (text + images)
Followers: Asymmetric, 1% have >1M followers
Read:Write: 100:1
Latency: <500ms for feed load
Freshness: Minutes (near real-time OK)

IN SCOPE: Post creation, feed generation, follow/unfollow, likes
OUT OF SCOPE: Auth, moderation, notifications, DMs
```

This reference keeps you grounded throughout the interview and shows organizational skills.

-----

**Bottom line**: These 5 minutes set the foundation for everything else. Rush through them and you’ll design the wrong system. Nail them, and you’ll demonstrate the judgment and communication skills of a senior engineer.​​​​​​​​​​​​​​​​
