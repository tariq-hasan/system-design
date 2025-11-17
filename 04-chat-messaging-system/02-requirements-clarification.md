# Minutes 0-5: Requirements Clarification (5 min)

This is arguably the **most critical phase** of the interview. Senior engineers distinguish themselves by asking the right questions and defining clear boundaries. Here’s how to execute this perfectly:

-----

## **Minute 0-1: Initial Framing (1 min)**

### **Your Opening Statement:**

*“Great! Before I jump into the design, I want to make sure I understand the problem correctly. Let me start by clarifying the scope and requirements. I’m thinking of this as a general-purpose chat system like WhatsApp or Slack—is that the right mental model, or are there specific characteristics you want me to focus on?”*

**Why this works:**

- Shows you don’t jump straight to solutions
- Demonstrates collaborative approach
- Sets expectations for a conversation, not a monologue

### **Listen for Interviewer’s Response:**

They might say:

- “Yes, think WhatsApp-scale” → Consumer focus, massive scale
- “More like Slack for teams” → Enterprise focus, features over scale
- “Your choice, but justify it” → You need to pick and be explicit

-----

## **Minute 1-3: Functional Requirements (2 min)**

### **Core Features (Must-Haves):**

**Present these as assumptions, then confirm:**

*“I’m assuming we need to support:*

- *1-on-1 messaging and group chats*
- *Text messages as the primary medium*
- *Basic message history and persistence*
- *Online/offline status*
- *Message delivery confirmation*

*Is that correct, or should I adjust priorities?”*

### **Follow-up Questions to Ask:**

**On Group Chats:**

- *“For group chats, what’s the maximum group size we need to support? Are we talking 10 people, 1000, or unlimited like Telegram channels?”*
  - **Why this matters:** Dramatically affects fanout strategy and architecture
  - **Expected answer:** Usually 100-500 for interview purposes
  - **If 10K+:** You’ll need read-time fanout, different storage model

**On Message Types:**

- *“Beyond text, do we need to support rich media—images, videos, files? And if so, what size limits?”*
  - **Why this matters:** Affects storage strategy, CDN requirements
  - **Expected answer:** “Yes, support images up to 10MB, files up to 100MB”
  - **Follow-up:** “Should we handle media compression and thumbnail generation?”

**On Message History:**

- *“How far back should message history go? Indefinitely, or can we archive old messages after, say, a year?”*
  - **Why this matters:** Storage costs, query patterns, hot vs cold data
  - **Expected answer:** Usually “indefinitely for now” or “1 year retention”

**On Read Receipts:**

- *“Do we need read receipts and typing indicators? These are common but not always required.”*
  - **Why this matters:** Adds complexity to the real-time system
  - **Expected answer:** “Yes, include them” (shows you understand real-time challenges)

**On Message Ordering:**

- *“For group chats, is strict message ordering critical, or is eventual consistency acceptable?”*
  - **Why this matters:** Determines whether you need consensus protocols
  - **Expected answer:** Usually “best effort ordering is fine”

### **Features to Explicitly Scope Out (Unless Asked):**

*“For time constraints, I’m assuming we’re NOT covering:*

- *End-to-end encryption details*
- *Voice and video calling*
- *Message search (or should we include basic search?)*
- *Bot integrations and slash commands*
- *Message threading*
- *Screen sharing or file collaboration”*

**Pro tip:** Mention these shows you know what a complete system needs, but you’re being smart about scope.

-----

## **Minute 3-4: Non-Functional Requirements (1 min)**

### **Scale Estimation:**

**Proactively propose numbers:**

*“Let me confirm the scale we’re targeting:*

- *Daily Active Users: 500 million?*
- *Concurrent online users: 100 million?*
- *Average messages per user per day: 50?*
- *Peak concurrent connections: Should I design for 2-3x normal for spikes?”*

**Quick Math (show on whiteboard):**

- Total messages/day: 500M × 50 = **25 billion messages/day**
- Messages/second average: 25B / 86,400 ≈ **290K messages/sec**
- Peak: 870K messages/sec (3x)

**Storage Estimation:**

- Average message size: 100 bytes (text) + metadata
- Daily storage: 25B × 100 bytes = **2.5 TB/day**
- Annual: ~900 TB
- With media (10% of messages): +5-10 TB/day

*“Does this scale sound about right, or should I adjust?”*

### **Latency Requirements:**

*“For latency, I’m thinking:*

- *Message delivery: <200ms end-to-end*
- *Online status updates: <1 second*
- *Message history load: <500ms*

*Are these acceptable targets?”*

### **Availability & Consistency:**

**Ask explicitly:**
*“On the CAP theorem spectrum, I’m assuming we prioritize Availability and Partition Tolerance over strict Consistency—meaning if there’s a network partition, users can still send messages, and we’ll resolve conflicts later. Is that the right trade-off?”*

**Expected answer:** “Yes, availability is more important”

**If they say consistency is critical:** Your design needs to change—maybe you need stronger guarantees for certain operations.

### **Geographic Distribution:**

*“Should this be globally distributed across multiple regions, or can we assume a single region for now?”*

- **If global:** Adds complexity with cross-region replication, CDN
- **If single region:** Simplifies initial design

-----

## **Minute 4-5: Final Clarifications & Prioritization (1 min)**

### **Confirm What You’ll Focus On:**

*“Perfect. Let me summarize what I’ll be designing:*

**In Scope:**

- *1-on-1 and group messaging (up to 500 people per group)*
- *Text and media support (images/files)*
- *Real-time delivery with <200ms latency*
- *Online status and typing indicators*
- *Read receipts*
- *Message persistence and history*
- *500M DAU, 100M concurrent, 290K messages/sec average*
- *High availability over strict consistency*

**Out of Scope:**

- *E2E encryption implementation details*
- *Voice/video calls*
- *Advanced search (or basic search only)*

*Does this align with what you’re looking for, or should I adjust anything?”*

### **Ask About Deep Dive Preferences:**

*“Also, are there specific areas you’d like me to focus on during the design? For example:*

- *Real-time message delivery architecture?*
- *Storage and data modeling?*
- *Scaling WebSocket connections?*
- *Or should I give balanced coverage?”*

**Why ask this:**

- Shows you’re flexible and collaborative
- Helps you allocate time in the next 55 minutes
- Interviewer might reveal what they care about most

-----

## **Common Mistakes to Avoid in This Phase:**

❌ **Spending too long here (>7 min):** You need time for actual design
❌ **Not proposing numbers:** Waiting for interviewer to give you everything shows passivity
❌ **Asking yes/no questions:** Ask open-ended questions that show expertise
❌ **Not writing anything down:** Capture requirements on the whiteboard
❌ **Ignoring non-functional requirements:** Scale/latency are as important as features
❌ **Being too deferential:** You should guide this conversation, not just ask questions

-----

## **What a Strong Candidate’s Whiteboard Looks Like After 5 Minutes:**

```
REQUIREMENTS
============

Functional:
✓ 1-on-1 + group chat (max 500/group)
✓ Text + media (images <10MB, files <100MB)
✓ Message history (1 year retention)
✓ Online status, typing, read receipts
✓ Push notifications for offline users
✗ E2E encryption (out of scope)
✗ Voice/video calls (out of scope)

Non-Functional:
• Scale: 500M DAU, 100M concurrent
• Throughput: 290K msg/sec avg, 870K peak
• Latency: <200ms delivery
• Availability: 99.99%
• Storage: ~3TB/day (with media)
• Global distribution (3 regions)
• CAP: AP (eventual consistency OK)
```

-----

## **Time Check:**

At the 5-minute mark, you should:

- ✅ Have clear functional scope
- ✅ Have quantitative scale targets
- ✅ Understand key trade-offs (consistency vs availability)
- ✅ Know what the interviewer cares about most
- ✅ Have requirements written on whiteboard
- 🎯 **Be ready to transition:** *“Great! Let me start with a high-level architecture…”*

This sets you up to nail the next 55 minutes with confidence and clarity.​​​​​​​​​​​​​​​​
