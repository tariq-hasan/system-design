# Minutes 9-15: High-Level Design

## **Minute 9: Draw the Basic Architecture (60-90 seconds)**

### **Start Simple - Core Components**

*While drawing boxes and arrows on the whiteboard:*

“Let me start with the high-level architecture. I’ll begin simple and then elaborate.”

**Draw these components (in order):**

```
[Clients] → [API Gateway/LB] → [Notification Service] 
                                        ↓
                                [Message Queue]
                                   ↓  ↓  ↓
                    [Email Worker] [SMS Worker] [Push Worker]
                         ↓              ↓            ↓
                    [SendGrid]     [Twilio]    [FCM/APNs]
```

**Narrate as you draw (30 seconds):**

- “Clients send notification requests to our API Gateway”
- “The Notification Service validates and enqueues messages”
- “Channel-specific workers process from the queue”
- “Workers integrate with third-party providers”

**Add supporting services (30 seconds):**

```
[User Preferences DB] ← [Notification Service]
[Template Service] ← [Workers]
[Analytics/Tracking DB] ← [Workers]
```

-----

## **Minute 10-11: Walk Through API & Entry Point (2 minutes)**

### **API Design (60 seconds)**

“Let me define how clients interact with the system.”

**Draw API endpoint on whiteboard:**

```json
POST /api/v1/notifications/send
{
  "userId": "user_12345",
  "notificationType": "order_confirmation",
  "channels": ["email", "push"],
  "priority": "high",
  "templateId": "order_confirm_v2",
  "data": {
    "orderId": "ORD-789",
    "amount": "$99.99",
    "estimatedDelivery": "2024-03-15"
  },
  "metadata": {
    "idempotencyKey": "uuid-here",
    "scheduledTime": "2024-03-10T15:00:00Z" // optional
  }
}
```

**Explain key design choices (30 seconds):**

- **userId**: Who receives the notification
- **channels array**: Multi-channel support in one request
- **templateId**: Separates content from delivery logic
- **priority**: Enables queue prioritization
- **idempotencyKey**: Prevents duplicate sends on retries
- **scheduledTime**: Optional delayed delivery

### **API Gateway Responsibilities (30 seconds)**

“The API Gateway handles:”

- Authentication & authorization (API keys, OAuth)
- Rate limiting (per-client, per-user)
- Request validation
- Load balancing to Notification Service instances

-----

## **Minute 12: Notification Service Deep Dive (60 seconds)**

### **Core Orchestration Logic**

*Point to Notification Service box:*

“This is the brain of the system. Here’s what it does:”

**1. Validation (15 seconds)**

```
- Verify request schema
- Check idempotency (have we seen this key before?)
- Validate templateId exists
- Ensure channels are valid
```

**2. User Preference Check (15 seconds)**

```
- Query User Preferences DB
- Filter channels based on opt-outs
  Example: User opted out of SMS → remove from channels array
- Check do-not-disturb settings
- Apply frequency caps (already sent 10 today? skip low priority)
```

**3. Message Enrichment (15 seconds)**

```
- Add user metadata (email address, phone, device tokens)
- Attach timezone for scheduled sends
- Add tracking IDs for analytics
- Split into channel-specific messages
```

**4. Enqueue (15 seconds)**

```
- Route to appropriate queue(s) based on:
  - Channel type (email_queue, sms_queue, push_queue)
  - Priority (high_priority_queue, normal_queue, low_priority_queue)
- Persist to DB for audit trail
- Return success response to client
```

-----

## **Minute 13: Message Queue Architecture (60 seconds)**

### **Queue Strategy Explanation**

*Draw expanded queue architecture:*

```
                    [Notification Service]
                            ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
[High Priority Queue] [Normal Queue] [Low Priority Queue]
        ↓                  ↓                  ↓
     Partitioned by channel type
   [Email|SMS|Push]  [Email|SMS|Push]  [Email|SMS|Push]
```

**Explain design decisions (60 seconds):**

**Q: “Why use a message queue?”**

- **Decoupling**: Service doesn’t wait for external providers
- **Buffering**: Handle traffic spikes (Black Friday, breaking news)
- **Retry**: Failed messages stay in queue
- **Scalability**: Add more workers independently

**Q: “Why multiple queues?”**

- **Priority separation**: Critical alerts bypass promotional emails
- **Channel isolation**: SMS provider outage doesn’t block emails
- **Rate limiting**: Different consumption rates per channel

**Queue Technology Choice:**

- “For this scale, I’d use **Kafka** or **AWS SQS**”
  - Kafka: Better for high throughput (millions/sec), message replay
  - SQS: Simpler ops, good enough for most cases, managed service
  - Both support dead letter queues

-----

## **Minute 14: Worker Processing Logic (60 seconds)**

### **Worker Responsibilities**

*Point to worker boxes:*

“Each worker type (Email/SMS/Push) follows this pattern:”

**Processing Flow:**

```
1. Poll queue for messages (batch of 10-100)
2. Fetch template from Template Service
3. Render template with user data
4. Apply rate limiting check
   - Token bucket per user
   - Respect provider limits (Twilio: 1000 SMS/sec)
5. Call third-party provider API
6. Handle response:
   ✓ Success → Update tracking DB, acknowledge message
   ✗ Failure → Retry logic (exponential backoff)
   ✗ Permanent failure → Move to dead letter queue
7. Log metrics (latency, success rate, errors)
```

**Worker Scaling Strategy (20 seconds):**

- Horizontally scalable (add more instances)
- Auto-scale based on queue depth
- Each worker processes messages independently
- No shared state between workers

-----

## **Minute 15: End-to-End Flow Example (60 seconds)**

### **Walk Through Complete Example**

“Let me trace a notification from start to finish to validate the design.”

**Scenario: User places an order, system sends confirmation**

```
Step 1: Order Service → POST /api/v1/notifications/send
        {userId: "123", type: "order_confirmation", 
         channels: ["email", "push"]}

Step 2: API Gateway → Authenticates, rate limits, routes to 
        Notification Service

Step 3: Notification Service
        ├─ Check user preferences: User allows email + push ✓
        ├─ Enrich: Add email="user@example.com", deviceToken="xyz"
        ├─ Split into 2 messages (one per channel)
        └─ Enqueue to high_priority_queue

Step 4: Workers poll queue
        ├─ Email Worker: Fetches template, renders, calls SendGrid
        └─ Push Worker: Fetches template, renders, calls FCM

Step 5: Providers deliver
        ├─ SendGrid → User's inbox
        └─ FCM → User's mobile device

Step 6: Workers record delivery
        └─ Update Analytics DB: sent_at, delivered_at, status
```

**Verification Questions (15 seconds):**
*Ask interviewer:*
“Does this flow make sense? Any parts you’d like me to elaborate on before we dive deeper?”

-----

## **What You’ve Accomplished After Minute 15:**

✅ **Visual architecture** drawn on whiteboard  
✅ **API contract** defined  
✅ **Component responsibilities** clearly explained  
✅ **Data flow** demonstrated end-to-end  
✅ **Technology choices** justified (queue, workers)  
✅ **Foundation** ready for deep dives

-----

## **Key Components Summary (Reference)**

|Component               |Purpose                           |Technology Examples              |
|------------------------|----------------------------------|---------------------------------|
|**API Gateway**         |Entry point, auth, rate limiting  |Kong, AWS API Gateway, Nginx     |
|**Notification Service**|Orchestration, validation, routing|Node.js, Go, Java service        |
|**Message Queue**       |Decoupling, buffering, retry      |Kafka, RabbitMQ, AWS SQS         |
|**Workers**             |Channel-specific processing       |Worker pools, Kubernetes pods    |
|**User Preferences DB** |Opt-in/out, settings              |PostgreSQL, MongoDB              |
|**Template Service**    |Content management                |Internal service + S3/DB         |
|**Analytics DB**        |Tracking, audit logs              |Cassandra, PostgreSQL, ClickHouse|
|**Providers**           |Actual delivery                   |SendGrid, Twilio, FCM, APNs      |

-----

## **Common Mistakes to Avoid:**

❌ **Over-engineering too early**: Don’t add every component upfront  
❌ **Skipping the API**: Jumping to queues without showing entry point  
❌ **No concrete example**: Abstract diagrams without a walkthrough  
❌ **Messy whiteboard**: Unclear arrows, overlapping boxes  
❌ **Not explaining “why”**: Drawing without justifying decisions  
❌ **Forgetting data stores**: Where is user data, preferences stored?

## **Pro Tips:**

💡 **Draw incrementally**: Start simple, add complexity  
💡 **Use consistent shapes**: Rectangles for services, cylinders for DBs, queues as trapezoids  
💡 **Label everything**: Don’t assume interviewer knows what box means  
💡 **Color code** (if available): Different colors for sync vs async flows  
💡 **Leave space**: You’ll add more components in deep dives  
💡 **Narrate continuously**: Never draw in silence

-----

## **Transition to Deep Dive:**

*At the end of Minute 15, ask:*

“I’ve outlined the high-level architecture. We have about 40 minutes left. Which areas would you like me to dive deeper into?

Some options:

- Message queue reliability and retry mechanisms
- Scaling strategies for high throughput
- User preference management and filtering
- Template rendering and A/B testing
- Failure scenarios and monitoring

What’s most important for this system in your view?”

**This question:**

- Shows you’re time-aware
- Gives interviewer control
- Demonstrates you know there’s more depth
- Helps prioritize remaining time

You’re now perfectly positioned to go deep on what matters most to the interviewer! 🎯​​​​​​​​​​​​​​​​
