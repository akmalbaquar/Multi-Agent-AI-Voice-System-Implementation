# Multi-Agent System Demo Scripts

## 🎯 Overview

This system has **6 specialized agents** working together:

1. **Customer Order Agent** - Voice ordering (Twilio call)
2. **Restaurant Coordination Agent** - Order notifications
3. **Driver Assignment Agent** - Auto-assignment with ETA
4. **Delivery Tracking Agent** - Real-time tracking
5. **Customer Support Agent** - Inquiries, refunds, complaints
6. **Post-Delivery Agent** - Feedback & promotions

## 📞 Demo Scripts

### 1. Voice Ordering (Customer Order Agent)
```bash
# Make a real phone call
python call_me.py

# Call: +1 218-496-4536
# Follow voice prompts to order
```

### 2. Complete Multi-Agent Demo
```bash
# Demonstrates all 6 agents working together
python demo_all_agents.py
```
This will:
- Create an order
- Notify restaurant
- Assign driver
- Track delivery
- Handle support inquiry
- Collect feedback

### 3. Driver Agent Demo
```bash
# Demonstrates driver coordination
python demo_driver_agent.py
```
Shows:
- Driver assignment
- ETA calculation
- Pickup confirmation
- Delivery tracking
- Delivery completion

### 4. Tracking Agent Demo
```bash
# Demonstrates order tracking
python demo_tracking_agent.py
```
Shows real-time tracking through:
- Order placed
- Preparing
- Driver assigned
- Picked up
- Out for delivery
- Delivered

### 5. Support Agent Demo
```bash
# Demonstrates customer support
python demo_support_agent.py
```
Handles:
- Order status inquiries
- Filing complaints
- Processing refunds
- Order cancellations

### 6. Post-Delivery Agent Demo
```bash
# Demonstrates feedback collection
python demo_post_delivery_agent.py
```
Shows:
- Feedback collection (1-5 stars)
- Automatic promotions
- Order history tracking
- Customer retention

## 🔧 Setup

Make sure server is running:
```bash
# Terminal 1: Start server
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start ngrok (for voice calls)
ngrok http 8000

# Terminal 3: Run demos
python demo_all_agents.py
```

## 📊 Agent Coordination Flow

```
Customer Call → Order Agent
                    ↓
            Restaurant Agent (notify)
                    ↓
            Driver Agent (assign)
                    ↓
            Tracking Agent (real-time)
                    ↓
            Support Agent (if needed)
                    ↓
            Post-Delivery Agent (feedback)
```

## 🎮 Interactive Testing

### Via API (Postman/cURL)
```bash
# Create order
curl -X POST "http://localhost:8000/api/orders/order/create" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_phone": "+919490362478",
    "items": [{"name": "Pizza", "price": 299}],
    "address": "123 MG Road",
    "payment_method": "COD"
  }'

# Track order (replace ORDER_ID)
curl "http://localhost:8000/api/orders/order/ORDER_ID/track"

# Submit feedback
curl -X POST "http://localhost:8000/api/orders/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORDER_ID",
    "rating": 5,
    "comments": "Great!"
  }'
```

### Via Swagger UI
Open: http://localhost:8000/docs

Interactive documentation for all endpoints!

## 📈 Monitoring

Check system health:
```bash
# Health check
curl "http://localhost:8000/api/monitoring/health"

# System metrics
curl "http://localhost:8000/api/monitoring/metrics"

# Component status
curl "http://localhost:8000/api/monitoring/status"
```

## 🎬 Demo Video Script

1. **Start** - Show API docs at /docs
2. **Voice Call** - Demonstrate ordering via phone
3. **API Demo** - Run demo_all_agents.py
4. **Monitoring** - Show metrics endpoint
5. **Code** - Quick architecture walkthrough

## 🚀 What to Demonstrate

### For Exam Submission:
1. ✅ Voice ordering end-to-end
2. ✅ All 6 agents implemented
3. ✅ Order orchestration working
4. ✅ Real-time tracking
5. ✅ Customer support flows
6. ✅ Feedback collection
7. ✅ Professional API structure
8. ✅ Monitoring & health checks

### Key Talking Points:
- "6 specialized agents coordinate automatically"
- "Real-time order tracking from restaurant to delivery"
- "Complete customer journey handled by AI"
- "Production-ready API with 25+ endpoints"
- "Professional architecture with service separation"

## 📝 Notes

- Voice calls require Twilio + ngrok setup
- Other demos work with just the API server
- All demos use test data (mock restaurants/drivers)
- Real integrations ready for production (just need API keys)

---

**Quick Start:** `python demo_all_agents.py` to see everything! 🎉
