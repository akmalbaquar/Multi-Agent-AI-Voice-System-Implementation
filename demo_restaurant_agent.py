"""
Restaurant Agent Demo
Simulates restaurant receiving and confirming orders
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Restaurant phone (your test number)
RESTAURANT_PHONE = "+919490362478"

def call_restaurant_for_order():
    """Call restaurant to notify about new order"""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Create TwiML for restaurant notification
    twiml_url = f"{os.getenv('NGROK_URL')}/api/voice/restaurant-notify"
    
    call = client.calls.create(
        to=RESTAURANT_PHONE,
        from_=TWILIO_NUMBER,
        url=twiml_url,
        method='POST'
    )
    
    print(f"📞 Calling restaurant...")
    print(f"   Call SID: {call.sid}")
    print(f"   To: {RESTAURANT_PHONE}")
    print(f"   Message: New order notification")
    print("\n✅ Restaurant will receive order details and confirm prep time")

if __name__ == "__main__":
    print("=" * 60)
    print("🍕 RESTAURANT COORDINATION AGENT DEMO")
    print("=" * 60)
    print("\nThis simulates the restaurant receiving order notifications")
    print("and confirming preparation time.\n")
    
    call_restaurant_for_order()
