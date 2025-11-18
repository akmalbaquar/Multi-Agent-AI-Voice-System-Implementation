"""
API Router
Main router that includes all API endpoints
"""
from fastapi import APIRouter

# Removed old imports that require database
# from app.api.v1 import twilio, orders, customers, agents, health

router = APIRouter()

# Router setup will be done in main.py directly
# Include sub-routers when modules are ready
