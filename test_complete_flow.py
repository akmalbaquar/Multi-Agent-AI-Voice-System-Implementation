"""
Complete Voice Flow Test Script
Simulates full 6-agent conversation through Twilio outbound call
Tests: Order → Restaurant → Driver → Tracking → Support → Feedback
"""
from twilio.rest import Client
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Twilio Credentials
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
YOUR_PHONE = "+919490362478"
NGROK_URL = "https://drossier-arianna-unpunitive.ngrok-free.dev"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def make_test_call():
    """
    Make outbound call that tests complete agent flow
    """
    print_section("🎯 TESTING COMPLETE 6-AGENT FLOW")
    
    print("\n📞 Initiating call to test all agents...")
    print(f"   From: {TWILIO_NUMBER}")
    print(f"   To: {YOUR_PHONE}")
    print(f"   Webhook: {NGROK_URL}/api/voice/incoming")
    
    try:
        call = client.calls.create(
            to=YOUR_PHONE,
            from_=TWILIO_NUMBER,
            url=f"{NGROK_URL}/api/voice/incoming"
        )
        
        print(f"\n✅ Call initiated successfully!")
        print(f"   Call SID: {call.sid}")
        print(f"   Status: {call.status}")
        
        print_section("📋 CONVERSATION SCRIPT TO FOLLOW")
        
        print("""
When your phone rings, follow this script to test ALL 6 agents:

┌─────────────────────────────────────────────────────────┐
│  PHASE 1: ORDER AGENT (Ordering Food)                   │
└─────────────────────────────────────────────────────────┘
🤖 Robot: "Welcome to AI restaurant. We have Pizza..."
👤 YOU SAY: "I want pizza and fries"

🤖 Robot: "Pizza added for 299 rupees. Anything else?"
👤 YOU SAY: "That's all"

┌─────────────────────────────────────────────────────────┐
│  PHASE 2: ORDER AGENT (Address Collection)              │
└─────────────────────────────────────────────────────────┘
🤖 Robot: "Perfect! 2 items, 398 rupees. Delivery address?"
👤 YOU SAY: "123 MG Road Bangalore Karnataka"

┌─────────────────────────────────────────────────────────┐
│  PHASE 3: ORDER AGENT (Payment Selection)               │
│          → RESTAURANT AGENT (Auto-notified)             │
│          → DRIVER AGENT (Auto-assigned)                 │
└─────────────────────────────────────────────────────────┘
🤖 Robot: "Got it. Cash on delivery or online payment?"
👤 YOU SAY: "Cash on delivery"

🤖 Robot: "Order ORD123ABC confirmed. Delivery in 35 mins.
          Say 'track' for updates or 'support' for help."

┌─────────────────────────────────────────────────────────┐
│  PHASE 4: TRACKING AGENT (Order Status)                 │
└─────────────────────────────────────────────────────────┘
👤 YOU SAY: "Track order"

🤖 Robot: "Your order ORD123ABC is on the way! Driver will 
          arrive in 30 minutes. Say 'support' if you need 
          help or 'rate' to give feedback."

┌─────────────────────────────────────────────────────────┐
│  PHASE 5: SUPPORT AGENT (Issue Resolution)              │
└─────────────────────────────────────────────────────────┘
👤 YOU SAY: "Support"

🤖 Robot: "Connecting to support. What can I help with?"
👤 YOU SAY: "Food was cold"

🤖 Robot: "I apologize for that. Processing 50% refund 
          immediately. Would you like to rate your experience?"

┌─────────────────────────────────────────────────────────┐
│  PHASE 6: FEEDBACK AGENT (Rating & Promotion)           │
└─────────────────────────────────────────────────────────┘
👤 YOU SAY: "2 stars"

🤖 Robot: "We're sorry about your experience. Here's 20% off.
          Code: SAVE20. Support will call you. Goodbye!"

════════════════════════════════════════════════════════════

🎯 WHAT THIS TESTS:
   ✅ Agent 1: Order Agent - Menu ordering, address, payment
   ✅ Agent 2: Restaurant Agent - Auto-notification on payment
   ✅ Agent 3: Driver Agent - Auto-assignment with ETA
   ✅ Agent 4: Tracking Agent - Real-time order status
   ✅ Agent 5: Support Agent - Complaint handling & refunds
   ✅ Agent 6: Feedback Agent - Rating collection & promos

🔥 ALL 6 AGENTS IN ONE SINGLE CALL!
        """)
        
        print_section("⏰ CALL MONITORING")
        print("\n⏳ Waiting for call to complete...")
        print("   (This will take 3-5 minutes)")
        
        # Monitor call status
        time.sleep(5)
        
        for i in range(12):  # Check for 1 minute
            updated_call = client.calls(call.sid).fetch()
            status = updated_call.status
            
            status_icons = {
                "queued": "⏳",
                "ringing": "📞",
                "in-progress": "🗣️",
                "completed": "✅",
                "failed": "❌",
                "busy": "📵",
                "no-answer": "🔇"
            }
            
            icon = status_icons.get(status, "⚪")
            print(f"\r   {icon} Call Status: {status.upper()}", end="", flush=True)
            
            if status in ["completed", "failed", "busy", "no-answer"]:
                break
            
            time.sleep(5)
        
        print("\n\n" + "="*60)
        
        if updated_call.status == "completed":
            print("✅ CALL COMPLETED SUCCESSFULLY!")
            print("\n📊 Call Details:")
            print(f"   Duration: {updated_call.duration} seconds")
            print(f"   Price: {updated_call.price} {updated_call.price_unit}")
        elif updated_call.status == "in-progress":
            print("🗣️ CALL IN PROGRESS")
            print("   Follow the script above and test all 6 agents!")
        else:
            print(f"⚠️ Call Status: {updated_call.status}")
        
        print("\n🎯 Next Steps:")
        print("   1. Check server logs for agent routing")
        print("   2. Verify order created in system")
        print("   3. Test API endpoints at http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error making call: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Is ngrok running? Check: curl {NGROK_URL}")
        print("   2. Is server running? Check: curl http://localhost:8000/api/monitoring/health")
        print("   3. Verify Twilio credentials in .env file")

if __name__ == "__main__":
    make_test_call()
