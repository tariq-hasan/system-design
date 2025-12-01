# Minutes 1-8: Requirements Gathering & Clarification (Expanded)

## **Minute 1-2: Functional Scope Clarification**

### **Opening Response (30 seconds)**

“Great! Before I jump into the design, let me clarify the requirements. I want to make sure we’re aligned on scope and priorities.”

### **Core Functionality Questions (90 seconds)**

**Q1: “What notification channels are we supporting?”**

- Push notifications (mobile/web)?
- Email?
- SMS?
- In-app notifications?
- *Why ask: Each channel has different infrastructure needs, latency requirements, and cost implications*

**Q2: “Who initiates these notifications?”**

- User-to-user (e.g., social media mentions)?
- System-generated (e.g., order confirmations, alerts)?
- Marketing campaigns (bulk sends)?
- Third-party webhooks/integrations?
- *Why ask: Affects API design, authentication, and rate limiting strategies*

**Q3: “What types of notifications are we handling?”**

- Transactional (critical, immediate)?
- Promotional (can be delayed/batched)?
- Time-sensitive alerts?
- Scheduled notifications?
- *Why ask: Determines priority queuing and delivery guarantees needed*

-----

## **Minute 3-4: Scale & Performance Requirements**

### **Scale Questions (2 minutes)**

**Q4: “What scale are we designing for?”**

- Number of active users? (1M, 10M, 100M+)
- Notifications per day? Per second?
- Expected growth rate over next 1-2 years?
- *Example answer: “Let’s design for 100M users, ~10 notifications per user per day on average”*
- *Why ask: Determines architecture choices (monolith vs microservices, queue technology, database sharding)*

**Q5: “What are the latency requirements?”**

- Real-time delivery (< 1 second)?
- Near real-time (< 10 seconds)?
- Best effort (minutes acceptable)?
- Can we batch certain notification types?
- *Why ask: Affects queue design, worker polling strategies, and batching opportunities*

**Q6: “Are there any geographic considerations?”**

- Global user base or single region?
- Data residency requirements (GDPR, etc.)?
- Multi-region deployment needed?
- *Why ask: Impacts infrastructure deployment and data storage decisions*

-----

## **Minute 5-6: Reliability & Delivery Guarantees**

### **Critical Reliability Questions (2 minutes)**

**Q7: “What delivery guarantees do we need?”**

- At-least-once delivery acceptable? (may get duplicates)
- Exactly-once delivery required? (more complex, more expensive)
- Best-effort delivery okay for some channels?
- *Why ask: Dramatically affects system complexity and storage requirements*

**Q8: “What’s our target availability?”**

- 99.9% (43 min downtime/month)?
- 99.99% (4.3 min downtime/month)?
- Different SLAs for different notification types?
- *Why ask: Determines redundancy, failover strategies, and infrastructure costs*

**Q9: “How should we handle failures?”**

- Retry logic needed? How many retries?
- What happens if a provider (Twilio, SendGrid) is down?
- Should we support fallback providers?
- Dead letter queue for permanent failures?
- *Why ask: Critical for designing robust retry mechanisms and failure handling*

**Q10: “Do we need delivery confirmation/tracking?”**

- Track sent, delivered, opened, clicked?
- Audit trail requirements?
- How long to retain delivery logs?
- *Why ask: Affects storage design and analytics infrastructure*

-----

## **Minute 7-8: User Experience & Advanced Features**

### **UX & Features Questions (2 minutes)**

**Q11: “What user preference controls exist?”**

- Opt-in/opt-out by channel?
- Granular preferences (e.g., “only email for orders, push for messages”)?
- Do-not-disturb hours?
- Frequency capping (max X notifications per day)?
- *Why ask: Requires preference storage and filtering logic before sending*

**Q12: “Do we need notification templates?”**

- Standardized templates with variable substitution?
- Localization/internationalization support?
- A/B testing capabilities?
- *Why ask: Determines if we need a separate template management service*

**Q13: “Are there priority levels?”**

- Critical alerts (always deliver immediately)?
- Normal priority?
- Low priority (can be batched/delayed)?
- *Why ask: Affects queue design (multiple queues vs priority queues)*

**Q14: “Any rate limiting requirements?”**

- Per-user limits (anti-spam)?
- Global system limits?
- Per-provider limits (respecting vendor quotas)?
- *Why ask: Need to implement rate limiting at multiple layers*

-----

## **Minute 8: Scope Agreement & Final Clarifications**

### **Alignment Check (30-45 seconds)**

“Let me summarize what we’re building to make sure I understand correctly:

- **Channels**: Push, Email, SMS notifications
- **Scale**: 100M users, ~1B notifications/day, ~12K/sec average
- **Delivery**: At-least-once delivery, near real-time (< 10 seconds for critical)
- **Features**: User preferences, templates, priority levels, delivery tracking
- **Out of scope** (confirm): UI/frontend implementation, notification content creation tools

Does this align with what you had in mind? Anything I should adjust or prioritize differently?”

### **Interviewer Pivot Points (15-30 seconds)**

Listen for cues:

- “Focus more on reliability” → Deep dive on retry logic, failover
- “We care a lot about cost” → Emphasize batching, rate limiting, vendor management
- “Scale is critical” → Focus on horizontal scaling, partitioning strategies
- “Multi-tenancy is important” → Add tenant isolation to requirements

-----

## **Common Mistakes to Avoid:**

❌ **Spending too long** (>10 minutes) on requirements
❌ **Not writing down** agreed-upon numbers and requirements
❌ **Assuming requirements** without asking
❌ **Asking yes/no questions** instead of open-ended ones
❌ **Not confirming** what’s in/out of scope
❌ **Forgetting to ask about scale** early (it affects everything)

## **What Success Looks Like:**

✅ Clear understanding of functional scope
✅ Concrete numbers for scale (users, QPS, data volume)
✅ Defined latency and reliability requirements
✅ Agreement on must-have vs nice-to-have features
✅ Shared understanding with interviewer (they’re nodding along)
✅ Written notes on whiteboard for reference
✅ Finished in 8 minutes or less, ready to design

-----

**Remember**: This phase sets the foundation. Good clarification prevents wasted time later redesigning based on missed requirements. The interviewer is evaluating your ability to ask the *right* questions, not just any questions.​​​​​​​​​​​​​​​​
