# System Architecture
Multi-Agent AI Voice System for Food Delivery Platform

## Overview

This system implements a production-ready multi-agent AI voice calling platform that handles the complete food delivery workflow from order placement to post-delivery follow-up.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                        │
├─────────────────────────────────────────────────────────────────┤
│ Twilio Voice │ Deepgram STT │ ElevenLabs TTS │ Claude LLM      │
│ Google Maps  │ Stripe/Razorpay │ OpenAI Embeddings              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (FastAPI)                       │
├─────────────────────────────────────────────────────────────────┤
│  /twilio/*  │  /orders/*  │  /customers/*  │  /agents/*        │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Call Service │    │Audio Processor│   │ LLM Service  │
│              │    │              │    │              │
│ - Inbound    │    │ - STT Stream │    │ - Claude API │
│ - Outbound   │    │ - TTS Stream │    │ - GPT-4o API │
│ - Recording  │    │ - Interrupt  │    │ - Embeddings │
│ - Compliance │    │ - VAD        │    │ - Functions  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                   ┌──────────────────┐
                   │Agent Orchestrator│
                   │                  │
                   │ - Routing        │
                   │ - Context Mgmt   │
                   │ - Handoffs       │
                   └──────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Customer Order│    │  Restaurant  │    │    Driver    │
│    Agent     │    │Coordination  │    │  Assignment  │
│              │    │    Agent     │    │    Agent     │
└──────────────┘    └──────────────┘    └──────────────┘
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Delivery   │    │   Customer   │    │Post-Delivery │
│   Tracking   │    │   Support    │    │    Agent     │
│    Agent     │    │    Agent     │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │  Tool Registry   │
                   │                  │
                   │ - Customer Tools │
                   │ - Restaurant     │
                   │ - Driver Tools   │
                   │ - Payment        │
                   │ - Maps/Location  │
                   └──────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │    │   Qdrant     │
│              │    │              │    │              │
│ - Customers  │    │ - Sessions   │    │ - Menu Items │
│ - Orders     │    │ - Context    │    │ - FAQs       │
│ - Restaurants│    │ - Cache      │    │ - Semantic   │
│ - Drivers    │    │ - Metrics    │    │   Search     │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Component Details

### 1. Voice Infrastructure Layer

#### Twilio Integration
- **Inbound Calls**: Webhook endpoint receives calls, creates sessions
- **Outbound Calls**: Programmatic dialing with machine detection
- **Media Streaming**: WebSocket for real-time bidirectional audio
- **Call Recording**: Automatic recording with consent
- **Status Callbacks**: Track call lifecycle events

#### Audio Processing
- **Deepgram STT**: Real-time speech-to-text with <300ms latency
- **ElevenLabs TTS**: Natural text-to-speech with streaming
- **VAD**: Voice Activity Detection for turn-taking
- **Interrupt Handling**: Barge-in support with <200ms detection
- **Audio Buffering**: Efficient streaming to minimize latency

### 2. Agent Framework

#### Agent Orchestrator
- **Intent Classification**: Determines which agent should handle request
- **Routing Logic**: Dynamic agent selection based on context
- **Handoff Management**: Seamless transitions between agents
- **Context Preservation**: Maintains conversation state during transfers
- **Load Balancing**: Distributes load across agent instances

#### 6 Specialized Agents

**1. Customer Order Agent**
- Primary agent for order placement
- Menu search with semantic understanding
- Item customization handling
- Address verification with Google Maps
- Payment processing integration
- Upselling and recommendations

**2. Restaurant Coordination Agent**
- Automated order notifications
- Preparation time confirmation
- Inventory management (out-of-stock handling)
- Order modifications
- Pickup reminders

**3. Driver Assignment Agent**
- Available driver search
- Route optimization with Google Maps
- Acceptance confirmation
- Incentive calculation
- Reassignment logic

**4. Delivery Tracking Agent**
- Real-time location updates
- ETA calculations
- Proactive delay notifications
- Address correction
- Delivery confirmation

**5. Customer Support Agent**
- Order status inquiries
- Modification/cancellation requests
- Refund processing
- Complaint resolution
- FAQ knowledge base (RAG)

**6. Post-Delivery Agent**
- Delivery confirmation
- Feedback collection
- Rating capture
- Issue resolution
- Promotional offers

### 3. LLM Integration

#### Claude Sonnet 4.5 (Primary)
- **Function Calling**: Executes tools based on conversation
- **Streaming Responses**: Lower latency with progressive output
- **Context Window**: 200K tokens for long conversations
- **Cost**: $3/1M input, $15/1M output tokens

#### GPT-4o-mini (Fallback)
- **Backup**: Activates if Claude fails
- **Cost Optimization**: Cheaper for simple queries
- **Embeddings**: OpenAI ada-002 for semantic search

### 4. State Management

#### Redis Session Store
- **Active Sessions**: In-memory storage with TTL
- **Conversation History**: Message-by-message tracking
- **Order State**: Real-time cart and order data
- **Customer Context**: Profile and preferences
- **Agent Transitions**: Track handoffs for analytics

### 5. Data Layer

#### PostgreSQL (Primary Database)
- **Customers**: Profile, addresses, payment methods
- **Restaurants**: Menu, operating hours, location
- **Orders**: Complete order lifecycle
- **Drivers**: Status, location, ratings
- **Call Sessions**: Transcripts, metrics, costs
- **Agent Transitions**: Handoff tracking

#### Qdrant (Vector Database)
- **Menu Items**: Semantic search ("something spicy")
- **FAQs**: Support agent knowledge base
- **Hybrid Search**: Combines semantic + filters

### 6. Tool Registry

#### Customer-Facing Tools
```python
- get_customer_profile(phone_number)
- search_menu(restaurant_id, query, filters)
- add_to_order(item_id, quantity, customizations)
- verify_address(address)
- calculate_total(apply_promotions)
- place_order(payment_method_id)
- get_order_status(order_id)
- process_refund(order_id, reason, amount)
```

#### Restaurant Tools
```python
- notify_restaurant(restaurant_id, order_details)
- confirm_preparation_time(order_id, minutes)
- handle_unavailable_item(order_id, item_id)
```

#### Driver Tools
```python
- find_available_drivers(location, radius)
- assign_driver(driver_id, order_id)
- update_driver_location(driver_id, coordinates)
- confirm_delivery(order_id)
```

## Data Flow

### Order Placement Flow

```
1. Customer calls Twilio number
   ↓
2. Twilio webhook → FastAPI → Call Service
   ↓
3. WebSocket established → Audio Processor
   ↓
4. Customer speaks → Deepgram STT
   ↓
5. Text → Agent Orchestrator → Customer Order Agent
   ↓
6. Agent generates response via Claude
   ↓
7. Claude returns text + tool calls
   ↓
8. Execute tools (search_menu, add_to_order, etc.)
   ↓
9. Response → ElevenLabs TTS → Audio
   ↓
10. Audio → Twilio → Customer
```

### Agent Handoff Flow

```
1. Customer Order Agent detects issue
   ↓
2. Agent returns {transfer_to: "customer_support"}
   ↓
3. Orchestrator:
   - Saves current context
   - Logs transition
   - Loads Support Agent
   ↓
4. Support Agent:
   - Receives context summary
   - Continues conversation
   - Has access to all history
```

## Performance Optimizations

### Latency Reduction
- **Streaming TTS**: Start playing audio before complete generation
- **Parallel Processing**: STT, LLM, TTS run concurrently where possible
- **Connection Pooling**: Reuse database and API connections
- **Redis Caching**: Cache frequent queries (customer profiles, menu)

### Cost Optimization
- **Cheap TTS**: Use Deepgram Aura for confirmations
- **Smart LLM Selection**: GPT-4o-mini for simple queries
- **Response Caching**: Cache common LLM responses
- **Prompt Optimization**: Minimize token usage

### Scalability
- **Async I/O**: FastAPI with asyncio for high concurrency
- **Horizontal Scaling**: Stateless application servers
- **Database Connection Pooling**: Efficient connection management
- **Message Queue**: RabbitMQ for background tasks

## Security & Compliance

### TRAI Compliance (India)
- DND registry check before outbound calls
- Calling hours: 9 AM - 9 PM IST only
- Recording consent at call start
- Opt-out mechanism in every call

### TCPA Compliance (USA)
- Prior express consent verification
- Calling hours: 8 AM - 9 PM local time
- Opt-out honored immediately

### GDPR Compliance (EU)
- PII encryption at rest and in transit
- Right to access and delete data
- Consent management
- Data minimization

### Security Measures
- API rate limiting
- Webhook signature verification
- SQL injection prevention
- PII anonymization in logs
- Secure session tokens

## Monitoring & Observability

### Metrics (Prometheus)
- Calls per minute
- Average call duration
- Agent success rates
- STT/TTS/LLM latency
- Order completion rate
- Cost per call

### Logging (Structlog)
- Structured JSON logs in production
- Request/response tracking
- Error tracking with Sentry
- Audit trail for sensitive operations

### Dashboards (Grafana)
- Real-time call metrics
- System health monitoring
- Cost tracking
- Agent performance

## Deployment Architecture

### Development
```
Local Machine
├── FastAPI (port 8000)
├── PostgreSQL (Docker)
├── Redis (Docker)
├── Qdrant (Docker)
└── Ngrok (for Twilio webhooks)
```

### Production
```
Kubernetes Cluster
├── API Pods (3+ replicas)
├── Worker Pods (background tasks)
├── PostgreSQL (managed service)
├── Redis (managed service)
├── Qdrant (managed service)
├── Load Balancer (HTTPS)
├── Prometheus (monitoring)
└── Grafana (dashboards)
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Voice | Twilio | Call handling & media streaming |
| STT | Deepgram Nova-2 | Speech-to-text |
| TTS | ElevenLabs / Deepgram Aura | Text-to-speech |
| LLM | Claude Sonnet 4.5 / GPT-4o-mini | Conversation AI |
| Backend | Python 3.11 + FastAPI | Async API server |
| Database | PostgreSQL 15 | Primary data store |
| Cache | Redis | Session & cache |
| Vector DB | Qdrant | Semantic search |
| Queue | RabbitMQ | Background jobs |
| Monitoring | Prometheus + Grafana | Metrics & dashboards |
| Deployment | Docker + Kubernetes | Container orchestration |

## Cost Breakdown (Per Call)

Assuming 5-minute average call:

| Service | Cost |
|---------|------|
| Twilio (inbound) | $0.0425 |
| Deepgram STT | $0.0215 |
| ElevenLabs TTS | ~$0.03 |
| Claude LLM | ~$0.05 |
| Infrastructure | ~$0.01 |
| **Total** | **~$0.15 per call** |

Target: <$0.25 per call ✅

## Next Steps for Implementation

1. ✅ Complete base infrastructure
2. 🚧 Implement all 6 agents
3. ⏳ Build tool registry
4. ⏳ Integrate payment processing
5. ⏳ Add vector search
6. ⏳ Implement monitoring
7. ⏳ Write tests
8. ⏳ Deploy to production

---

**Status**: Foundation Complete (15%)  
**Next Milestone**: All agents operational (Day 5)  
**Target**: Production-ready system (Day 8)
