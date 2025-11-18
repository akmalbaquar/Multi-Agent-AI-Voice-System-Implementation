# Multi-Agent AI Voice System - Food Delivery Platform

## Project Overview
Production-ready multi-agent AI voice calling system for DoorDash-style food delivery platform.

**Timeline**: 8 Days (Nov 12-18, 2025)  
**Company**: Aminuteman Technologies Pvt Ltd

## Features
- ✅ 6 Specialized AI Voice Agents
- ✅ Real-time Voice Processing (STT/TTS)
- ✅ CRM Integration & Order Management
- ✅ Payment Processing (Stripe/Razorpay)
- ✅ Multi-language Support (English/Hindi/Tamil)
- ✅ Real-time Order Tracking
- ✅ Compliance (TRAI/TCPA/GDPR)

## Architecture

### Agents
1. **Customer Order Agent** - Menu search, order placement, customization
2. **Restaurant Coordination Agent** - Order notification, preparation time
3. **Driver Assignment Agent** - Driver search, route optimization
4. **Delivery Tracking Agent** - Real-time updates, delay notifications
5. **Customer Support Agent** - Refunds, complaints, issue resolution
6. **Post-Delivery Agent** - Feedback collection, promotions

### Tech Stack
- **Backend**: Python 3.11+, FastAPI
- **Voice**: Twilio Programmable Voice
- **STT**: Deepgram Nova-2
- **TTS**: ElevenLabs (Primary), Deepgram Aura (Fallback)
- **LLM**: Claude Sonnet 4.5, GPT-4o-mini (Fallback)
- **Databases**: PostgreSQL 15, Redis, Qdrant
- **Message Queue**: RabbitMQ
- **Monitoring**: Prometheus, Grafana, Sentry
- **Deployment**: Docker, Kubernetes, GitHub Actions

## Quick Start

### Prerequisites
```bash
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15
- Redis
```

### Installation
```bash
# Clone repository
git clone <repository-url>
cd Job

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start services
docker-compose up -d

# Run application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables
```
# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Deepgram
DEEPGRAM_API_KEY=

# ElevenLabs
ELEVENLABS_API_KEY=

# Claude
ANTHROPIC_API_KEY=

# OpenAI (for embeddings and fallback)
OPENAI_API_KEY=

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/fooddelivery
REDIS_URL=redis://localhost:6379/0

# Payment
STRIPE_API_KEY=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=

# Google Maps
GOOGLE_MAPS_API_KEY=

# Qdrant
QDRANT_URL=http://localhost:6333
```

## API Documentation
Access Swagger UI at: http://localhost:8000/docs

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Load testing
locust -f tests/load/locustfile.py
```

## Deployment
```bash
# Build Docker image
docker build -t voice-ai-system .

# Deploy to Kubernetes
kubectl apply -f k8s/

# Deploy with Helm
helm install voice-ai ./helm-chart
```

## Performance Targets
- ✅ Total response time: <2.5s
- ✅ STT latency: <300ms
- ✅ TTS latency: <500ms
- ✅ Concurrent calls: 100+
- ✅ Call success rate: >95%
- ✅ Cost per call: <$0.25

## Compliance
- TRAI (India) - DND registry, calling hours, consent
- TCPA (USA) - Express consent, opt-out mechanism
- GDPR (EU) - PII encryption, right to deletion

## Project Structure
```
Job/
├── app/
│   ├── agents/           # AI agent implementations
│   ├── api/              # FastAPI routes
│   ├── core/             # Core configurations
│   ├── db/               # Database models & migrations
│   ├── llm/              # LLM integrations
│   ├── services/         # Business logic services
│   ├── tools/            # Agent tools/functions
│   ├── voice/            # Voice processing (STT/TTS)
│   └── main.py           # Application entry point
├── tests/                # Test suite
├── docs/                 # Documentation
├── k8s/                  # Kubernetes manifests
├── docker-compose.yml    # Local development
├── Dockerfile            # Container image
└── requirements.txt      # Python dependencies
```

## License
Proprietary - Aminuteman Technologies Pvt Ltd

## Contact
For issues and questions, contact the development team.
"# Multi-Agent-AI-Voice-System-Implementation" 
