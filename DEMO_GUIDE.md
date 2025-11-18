# Multi-Agent AI Voice System - Quick Start Guide

## 🚀 What's Working Now

### ✅ Complete Voice Ordering System
- Inbound calls via Twilio
- Speech recognition and TTS responses
- Menu browsing (5 items with prices)
- Multi-item ordering
- **Address collection**
- **Payment method selection (COD/Online)**
- Order confirmation with total

### ✅ Backend Services
- **Order Management** - Complete order lifecycle tracking
- **Restaurant Coordination** - Automated notifications & prep time tracking
- **Driver Assignment** - Auto-assignment with ETA calculation
- **Delivery Tracking** - Real-time status updates
- **Customer Support** - Inquiry handling, refunds, complaints
- **Post-Delivery** - Feedback collection & promotions
- **Monitoring** - Health checks and metrics API

### ✅ API Endpoints
All accessible at `http://localhost:8000/docs`

## 📞 Test the Voice System

### Call Flow Example:
```
1. Call: +1 218-496-4536
2. AI: "Welcome to Food Delivery AI! We have..."
3. You: "I want a pizza"
4. AI: "Great! Pizza added. Anything else?"
5. You: "Add a burger"
6. AI: "Burger added. Anything else?"
7. You: "Done"
8. AI: "Please tell me your delivery address..."
9. You: "123 MG Road Bangalore"
10. AI: "For payment, say cash on delivery or online payment"
11. You: "Cash on delivery"
12. AI: "Order confirmed! Delivery in 30-45 mins"
```

## 🔧 Setup Instructions

### Prerequisites
- Python 3.10+
- Twilio account
- Ngrok for local testing

### Environment Variables (.env)
```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+12184964536

# OpenAI (optional - using keyword matching)
OPENAI_API_KEY=your_openai_key

# Server
NGROK_URL=https://your-ngrok-url.ngrok-free.dev
```

### Installation
```bash
# Activate virtual environment
ai-agent\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn app.main:app --reload --port 8000
```

### Start Ngrok
```bash
ngrok http 8000
```

### Configure Twilio Webhook
1. Go to Twilio Console → Phone Numbers
2. Select your number
3. Voice Configuration → Webhook URL:
   `https://your-ngrok-url.ngrok-free.dev/api/voice/incoming`
4. Method: POST

## 📊 API Examples

### Create Order Programmatically
```bash
curl -X POST "http://localhost:8000/api/orders/order/create" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_phone": "+919490362478",
    "items": [
      {"name": "Margherita Pizza", "price": 299},
      {"name": "Chicken Burger", "price": 199}
    ],
    "address": "123 MG Road, Bangalore",
    "payment_method": "Cash on Delivery"
  }'
```

### Track Order
```bash
curl "http://localhost:8000/api/orders/order/ORD12345678/track"
```

### Get System Metrics
```bash
curl "http://localhost:8000/api/monitoring/metrics"
```

### Submit Feedback
```bash
curl -X POST "http://localhost:8000/api/orders/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORD12345678",
    "rating": 5,
    "comments": "Great food and fast delivery!"
  }'
```

## 🏗️ Architecture

```
┌─────────────┐
│   Caller    │
└──────┬──────┘
       │
       ↓
┌─────────────────┐
│  Twilio Voice   │ → Speech-to-Text
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────┐
│      FastAPI Backend            │
│                                 │
│  ┌──────────────────────────┐  │
│  │   Voice Handler          │  │
│  │   (TwiML Responses)      │  │
│  └───────────┬──────────────┘  │
│              ↓                  │
│  ┌──────────────────────────┐  │
│  │   AI Order Handler       │  │
│  │   (Keyword + Workflow)   │  │
│  └───────────┬──────────────┘  │
│              ↓                  │
│  ┌──────────────────────────┐  │
│  │   Order Service          │  │
│  │   Restaurant Service     │  │
│  │   Driver Service         │  │
│  │   Support Agent          │  │
│  │   Tracking Agent         │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```

## 📈 Current Capabilities

| Feature | Status | Notes |
|---------|--------|-------|
| Voice Ordering | ✅ | Fully working |
| Address Collection | ✅ | Added |
| Payment Selection | ✅ | COD/Online |
| Restaurant Notification | ✅ | Mock service |
| Driver Assignment | ✅ | Auto-assignment |
| Order Tracking | ✅ | Status API |
| Customer Support | ✅ | Refunds, complaints |
| Feedback Collection | ✅ | Rating system |
| Monitoring | ✅ | Metrics API |
| Database | ⚠️ | In-memory only |
| LLM Integration | ⚠️ | Keyword-based |

## 🎯 Next Steps (If Time Permits)

1. **Database Integration**
   - PostgreSQL for persistent storage
   - Redis for session management

2. **Real LLM Integration**
   - Replace keyword matching with GPT-4
   - Natural language understanding

3. **Real-time Tracking**
   - WebSocket for live updates
   - Google Maps integration

4. **Testing**
   - Unit tests
   - Integration tests

## 📝 Demo Script

### What to Show:
1. **Voice Call** - Complete ordering flow
2. **API Docs** - Show Swagger UI at `/docs`
3. **Metrics** - Display system health
4. **Order Tracking** - Show order lifecycle
5. **Logs** - Display real-time processing

### Key Points:
- ✅ 6 agent types implemented
- ✅ Complete order workflow
- ✅ Multi-service coordination
- ✅ Real voice interaction
- ✅ Professional API design

## 🐛 Troubleshooting

### Server not starting?
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Restart with different port
python -m uvicorn app.main:app --reload --port 8001
```

### Ngrok expired?
```bash
# Restart ngrok
ngrok http 8000

# Update Twilio webhook URL
```

### Call not working?
1. Check Twilio webhook configuration
2. Verify ngrok is running
3. Check server logs for errors

## 📞 Support

For issues or questions:
- Check logs: Server console output
- API docs: http://localhost:8000/docs
- Monitoring: http://localhost:8000/api/monitoring/status

---

**Built with:** Python 3.10, FastAPI, Twilio, OpenAI
**Status:** Demo-ready MVP with full order lifecycle
