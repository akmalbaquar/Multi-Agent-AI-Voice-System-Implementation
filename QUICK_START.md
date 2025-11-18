"""
Quick Start Guide
Multi-Agent AI Voice System for Food Delivery

This guide will help you get the system up and running quickly.
"""

## Prerequisites

### 1. Install Python 3.11+
```bash
python --version  # Should be 3.11 or higher
```

### 2. Install Docker Desktop (for Windows)
Download from: https://www.docker.com/products/docker-desktop/

### 3. Get API Keys

You'll need accounts and API keys for:
- **Twilio**: https://www.twilio.com/console
- **Deepgram**: https://console.deepgram.com/
- **ElevenLabs**: https://elevenlabs.io/
- **Anthropic (Claude)**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/
- **Google Maps**: https://console.cloud.google.com/
- **Stripe** or **Razorpay**: Payment gateway

## Installation Steps

### Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd e:\Clg-PDF\Job

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Verify activation - you should see (venv) in prompt
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take 5-10 minutes. Go get coffee! ☕

### Step 3: Setup Environment Variables

```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your API keys
# Use notepad or any text editor
notepad .env
```

**Critical variables to set:**
```ini
# Twilio (Required for calls)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Deepgram STT (Required)
DEEPGRAM_API_KEY=your_deepgram_key

# ElevenLabs TTS (Required)
ELEVENLABS_API_KEY=your_elevenlabs_key

# Claude LLM (Required)
ANTHROPIC_API_KEY=your_anthropic_key

# OpenAI (Required for embeddings)
OPENAI_API_KEY=your_openai_key

# Google Maps (Required)
GOOGLE_MAPS_API_KEY=your_maps_key

# Stripe or Razorpay (Pick one)
STRIPE_API_KEY=your_stripe_key
# OR
RAZORPAY_KEY_ID=your_razorpay_id
RAZORPAY_KEY_SECRET=your_razorpay_secret

# Database (Use default for local dev)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fooddelivery
REDIS_URL=redis://localhost:6379/0
```

### Step 4: Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, Qdrant, RabbitMQ
docker-compose up -d postgres redis qdrant rabbitmq

# Wait 30 seconds for services to be ready
timeout /t 30

# Check services are running
docker ps
```

You should see 4 containers running.

### Step 5: Setup Database

```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### Step 6: Test the Setup

```bash
# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open browser: http://localhost:8000
- You should see: {"message": "Multi-Agent AI Voice System API", ...}

Open API docs: http://localhost:8000/docs
- Interactive Swagger UI should load

Health check: http://localhost:8000/health
- Should return: {"status": "healthy", ...}

### Step 7: Setup Ngrok for Twilio Webhooks

For testing, you need a public URL for Twilio to send webhooks:

```bash
# Install ngrok: https://ngrok.com/download

# Start ngrok tunnel
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update .env:
TWILIO_WEBHOOK_URL=https://abc123.ngrok.io
```

### Step 8: Configure Twilio Phone Number

1. Go to Twilio Console: https://www.twilio.com/console/phone-numbers
2. Click on your phone number
3. Under "Voice & Fax", set:
   - **A CALL COMES IN**: Webhook
   - **URL**: https://your-ngrok-url.ngrok.io/api/v1/twilio/incoming
   - **HTTP**: POST
4. Click Save

## Testing the System

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Database Connection
```bash
curl http://localhost:8000/api/v1/health/ready
```

### Test 3: Make a Test Call

Call your Twilio phone number from your mobile phone.

You should hear:
1. Recording consent message
2. Welcome greeting from the Customer Order Agent
3. Be able to have a conversation

## What to Do If Things Break

### Problem: Dependencies won't install
**Solution:**
```bash
# Try upgrading pip
python -m pip install --upgrade pip

# Install dependencies one by one to find the culprit
pip install fastapi
pip install uvicorn
# etc...
```

### Problem: Docker containers won't start
**Solution:**
```bash
# Check if ports are already in use
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# Stop all containers and restart
docker-compose down
docker-compose up -d
```

### Problem: Database connection fails
**Solution:**
```bash
# Check PostgreSQL is running
docker logs fooddelivery-postgres

# Test connection
docker exec -it fooddelivery-postgres psql -U postgres
```

### Problem: Twilio webhooks not working
**Solution:**
- Check ngrok is running: http://localhost:4040
- Verify webhook URL in Twilio console
- Check logs in terminal for incoming requests
- Verify .env has correct TWILIO_WEBHOOK_URL

### Problem: "Module not found" errors
**Solution:**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Implement remaining agents** - See `IMPLEMENTATION_STATUS.md`
2. **Add sample data** - Create restaurants, menu items, customers
3. **Test each agent** - Build and test one agent at a time
4. **Load testing** - Use Locust to test concurrent calls
5. **Documentation** - Document your implementation

## Useful Commands

```bash
# Restart application
Ctrl+C  # Stop
uvicorn app.main:app --reload

# View logs
docker-compose logs -f app

# Access PostgreSQL
docker exec -it fooddelivery-postgres psql -U postgres -d fooddelivery

# Access Redis CLI
docker exec -it fooddelivery-redis redis-cli

# Check API endpoints
curl http://localhost:8000/docs

# Run tests
pytest

# Code formatting
black app/

# Type checking
mypy app/
```

## Port Reference

- **8000**: FastAPI application
- **5432**: PostgreSQL
- **6379**: Redis
- **6333**: Qdrant
- **5672**: RabbitMQ
- **15672**: RabbitMQ Management UI
- **9090**: Prometheus
- **3000**: Grafana

## Important Files

- **app/main.py** - Application entry point
- **app/core/config.py** - Configuration
- **app/db/models.py** - Database models
- **app/api/v1/** - API endpoints
- **app/services/** - Business logic
- **app/agents/** - AI agents (to be implemented)
- **.env** - Environment variables (DON'T commit this!)

## Getting Help

- Check `IMPLEMENTATION_STATUS.md` for current progress
- Review API docs at http://localhost:8000/docs
- Check logs in terminal for errors
- Review error messages carefully

## Daily Checklist

- [ ] Virtual environment activated
- [ ] All Docker containers running
- [ ] Application starts without errors
- [ ] Can access /docs endpoint
- [ ] Ngrok tunnel is active (for Twilio testing)
- [ ] Git commits made regularly
- [ ] Tests passing

Good luck with your implementation! 🚀
