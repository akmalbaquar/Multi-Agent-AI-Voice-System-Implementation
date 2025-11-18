"""
Twilio Outbound Call Script
Makes a call to your verified Indian number
"""
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your Twilio Credentials
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Replace with your verified Indian number
YOUR_PHONE = "+919490362478"  # <- CHANGE THIS to your number

# Replace with your ngrok URL
NGROK_URL = "https://drossier-arianna-unpunitive.ngrok-free.dev"  # <- Your actual ngrok URL

# Create Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

print("📞 Making outbound call...")
print(f"From: {TWILIO_NUMBER}")
print(f"To: {YOUR_PHONE}")
print(f"Webhook: {NGROK_URL}/api/voice/incoming")

# Make the call
call = client.calls.create(
    to=YOUR_PHONE,
    from_=TWILIO_NUMBER,
    url=f"{NGROK_URL}/api/voice/incoming"
)

print(f"✅ Call Started! Call SID: {call.sid}")
print(f"Status: {call.status}")
print("🔥 Your phone should ring now!")
