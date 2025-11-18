# 🚀 SETUP CHECKLIST
## Multi-Agent AI Voice System

Use this checklist to ensure everything is properly set up.

---

## ✅ Prerequisites

### Software Installation
- [ ] Python 3.11+ installed and working
  ```bash
  python --version
  ```
- [ ] Docker Desktop installed and running
- [ ] Git installed (for version control)
- [ ] VS Code or preferred IDE
- [ ] ngrok downloaded (for Twilio webhooks)

### API Accounts Created
- [ ] Twilio account created (https://www.twilio.com/try-twilio)
- [ ] Deepgram account created (https://console.deepgram.com/)
- [ ] ElevenLabs account created (https://elevenlabs.io/)
- [ ] Anthropic account created (https://console.anthropic.com/)
- [ ] OpenAI account created (https://platform.openai.com/)
- [ ] Google Cloud account (for Maps API)
- [ ] Stripe OR Razorpay account

### API Keys Obtained
- [ ] Twilio Account SID & Auth Token
- [ ] Twilio Phone Number purchased
- [ ] Deepgram API Key
- [ ] ElevenLabs API Key
- [ ] Anthropic API Key (Claude)
- [ ] OpenAI API Key
- [ ] Google Maps API Key
- [ ] Payment gateway keys (Stripe or Razorpay)

---

## 🔧 Installation Steps

### 1. Project Setup
- [ ] Navigate to project directory
  ```bash
  cd e:\Clg-PDF\Job
  ```
- [ ] Create virtual environment
  ```bash
  python -m venv venv
  ```
- [ ] Activate virtual environment
  ```bash
  venv\Scripts\activate
  ```
- [ ] Verify activation (should see `(venv)` in prompt)

### 2. Dependencies
- [ ] Upgrade pip
  ```bash
  python -m pip install --upgrade pip
  ```
- [ ] Install requirements (takes 5-10 minutes)
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Verify installation
  ```bash
  pip list | findstr fastapi
  ```

### 3. Environment Configuration
- [ ] Copy .env.example to .env
  ```bash
  copy .env.example .env
  ```
- [ ] Open .env in text editor
- [ ] Add Twilio credentials
  - TWILIO_ACCOUNT_SID
  - TWILIO_AUTH_TOKEN
  - TWILIO_PHONE_NUMBER
- [ ] Add Deepgram API key
- [ ] Add ElevenLabs API key
- [ ] Add Anthropic API key
- [ ] Add OpenAI API key
- [ ] Add Google Maps API key
- [ ] Add payment gateway keys
- [ ] Save .env file

### 4. Docker Infrastructure
- [ ] Start Docker Desktop
- [ ] Pull required images
  ```bash
  docker-compose pull
  ```
- [ ] Start services
  ```bash
  docker-compose up -d postgres redis qdrant rabbitmq
  ```
- [ ] Wait 30 seconds for services to initialize
- [ ] Verify containers are running
  ```bash
  docker ps
  ```
  Should see 4 containers: postgres, redis, qdrant, rabbitmq

### 5. Database Setup
- [ ] Initialize Alembic
  ```bash
  alembic init alembic
  ```
- [ ] Edit alembic.ini - set sqlalchemy.url
  ```
  sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/fooddelivery
  ```
- [ ] Edit alembic/env.py - import Base
  ```python
  from app.db.database import Base
  target_metadata = Base.metadata
  ```
- [ ] Create initial migration
  ```bash
  alembic revision --autogenerate -m "Initial schema"
  ```
- [ ] Apply migration
  ```bash
  alembic upgrade head
  ```
- [ ] Verify database created
  ```bash
  docker exec -it fooddelivery-postgres psql -U postgres -l
  ```

---

## 🧪 Testing Installation

### 1. Start Application
- [ ] Run FastAPI server
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
- [ ] See "Application started successfully" message
- [ ] No error messages in console

### 2. Basic Health Checks
- [ ] Open browser: http://localhost:8000
  - Should see JSON with app info
- [ ] Open API docs: http://localhost:8000/docs
  - Should see Swagger UI with all endpoints
- [ ] Test health endpoint: http://localhost:8000/health
  - Should return: `{"status": "healthy", ...}`
- [ ] Test readiness: http://localhost:8000/api/v1/health/ready
  - Should show database and redis connected

### 3. Database Connection
- [ ] Check PostgreSQL
  ```bash
  docker exec -it fooddelivery-postgres psql -U postgres -d fooddelivery -c "\dt"
  ```
  Should list all tables: customers, restaurants, orders, etc.

### 4. Redis Connection
- [ ] Check Redis
  ```bash
  docker exec -it fooddelivery-redis redis-cli ping
  ```
  Should return: `PONG`

### 5. Qdrant Connection
- [ ] Open Qdrant dashboard: http://localhost:6333/dashboard

---

## 📞 Twilio Integration Setup

### 1. Start ngrok
- [ ] Open new terminal
- [ ] Run ngrok
  ```bash
  ngrok http 8000
  ```
- [ ] Copy HTTPS URL (e.g., https://abc123.ngrok.io)
- [ ] Keep ngrok terminal open

### 2. Update Environment
- [ ] Open .env file
- [ ] Set TWILIO_WEBHOOK_URL to ngrok URL
  ```
  TWILIO_WEBHOOK_URL=https://abc123.ngrok.io
  ```
- [ ] Restart application (Ctrl+C, then uvicorn command again)

### 3. Configure Twilio Phone Number
- [ ] Go to Twilio Console: https://www.twilio.com/console/phone-numbers
- [ ] Click your phone number
- [ ] Under "Voice & Fax":
  - A CALL COMES IN: Webhook
  - URL: `https://your-ngrok-url.ngrok.io/api/v1/twilio/incoming`
  - HTTP: POST
- [ ] Click Save
- [ ] Test by calling your Twilio number

---

## 🎯 Final Verification

### Application Checklist
- [ ] Application starts without errors
- [ ] All Docker containers running
- [ ] Database migrations applied
- [ ] API docs accessible
- [ ] Health checks passing
- [ ] ngrok tunnel active

### API Keys Checklist
- [ ] All required API keys in .env
- [ ] No placeholder values remaining
- [ ] Keys tested and working

### Optional: Test Call
- [ ] Call your Twilio number from mobile
- [ ] Should hear recording consent message
- [ ] Should hear greeting from agent
- [ ] Call should not disconnect immediately

---

## 📊 Monitoring Setup

### Prometheus & Grafana
- [ ] Access Prometheus: http://localhost:9090
- [ ] Access Grafana: http://localhost:3000
  - Default login: admin/admin
- [ ] Import dashboards (when ready)

### RabbitMQ Management
- [ ] Access RabbitMQ UI: http://localhost:15672
  - Default login: guest/guest

---

## 🐛 Troubleshooting

### If application won't start:
- [ ] Check all containers are running: `docker ps`
- [ ] Check .env file has no syntax errors
- [ ] Check database URL is correct
- [ ] Look at error messages carefully

### If database connection fails:
- [ ] Verify PostgreSQL container: `docker logs fooddelivery-postgres`
- [ ] Check DATABASE_URL in .env
- [ ] Try restarting containers: `docker-compose restart postgres`

### If Twilio webhooks fail:
- [ ] Check ngrok is running: http://localhost:4040
- [ ] Verify webhook URL in Twilio console
- [ ] Check application logs for incoming requests
- [ ] Ensure TWILIO_WEBHOOK_URL in .env is correct

### If imports fail:
- [ ] Ensure virtual environment is activated
- [ ] Reinstall requirements: `pip install -r requirements.txt`
- [ ] Check Python version: `python --version`

---

## ✨ Ready to Code!

Once all checks pass, you're ready to implement:

### Next Immediate Tasks:
1. [ ] Implement tool registry (app/tools/)
2. [ ] Create customer order agent
3. [ ] Test end-to-end call flow
4. [ ] Implement remaining 5 agents

### Development Workflow:
```bash
# 1. Activate venv (if not already)
venv\Scripts\activate

# 2. Ensure Docker services running
docker ps

# 3. Start application
uvicorn app.main:app --reload

# 4. Start ngrok (separate terminal)
ngrok http 8000

# 5. Code, test, repeat!
```

---

## 📝 Daily Checklist

At the start of each work session:
- [ ] Virtual environment activated
- [ ] Docker containers running
- [ ] Application starts successfully
- [ ] ngrok tunnel active
- [ ] Git status checked
- [ ] TODO list reviewed

---

## 🎉 Success Criteria

You've successfully completed setup when:
- ✅ Application runs without errors
- ✅ All health checks pass
- ✅ Can access API documentation
- ✅ Database tables created
- ✅ Can make test call to Twilio number
- ✅ Logs show proper message flow

**Congratulations! You're ready to build the multi-agent system!** 🚀

---

**Last Updated**: November 12, 2025  
**Status**: Setup Guide Complete
