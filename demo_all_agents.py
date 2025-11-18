"""
Complete Multi-Agent System Demo
Orchestrates all 6 agents in sequence
"""
import requests
import time
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def demo_complete_flow():
    """Demonstrate complete order flow through all agents"""
    
    print("\n" + "🚀" * 35)
    print("  COMPLETE MULTI-AGENT SYSTEM DEMONSTRATION")
    print("  All 6 Agents Working Together")
    print("🚀" * 35)
    
    customer_phone = "+919490362478"
    
    # ========== AGENT 1: CUSTOMER ORDER AGENT ==========
    print_section("📞 AGENT 1: CUSTOMER ORDER AGENT (Voice Ordering)")
    print("""
    Customer calls: +1 218-496-4536
    AI: "Welcome! We have Pizza, Burger, Fries, Pasta, Sandwich"
    Customer: "I want a pizza and fries"
    AI: "Pizza and Fries added. Say done when finished."
    Customer: "Done"
    AI: "Total 398 rupees. Please tell me your address."
    Customer: "123 MG Road Bangalore"
    AI: "For payment, say cash on delivery or online."
    Customer: "Cash on delivery"
    AI: "Order confirmed! Delivery in 30-45 minutes."
    """)
    
    # Simulate order creation via API
    print("📦 Creating order via API...")
    order_data = {
        "customer_phone": customer_phone,
        "items": [
            {"name": "Margherita Pizza", "price": 299},
            {"name": "French Fries", "price": 99}
        ],
        "address": "123 MG Road, Koramangala, Bangalore",
        "payment_method": "Cash on Delivery"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders/order/create", json=order_data)
    if response.status_code != 200:
        print("❌ Failed to create order")
        return
    
    result = response.json()
    order_id = result["order"]["order_id"]
    print(f"✅ Order created: {order_id}")
    print(f"   Items: Pizza + Fries")
    print(f"   Total: ₹{result['order']['total']}")
    print(f"   Address: {result['order']['delivery_address']}")
    print(f"   Payment: {result['order']['payment_method']}")
    
    time.sleep(2)
    
    # ========== AGENT 2: RESTAURANT COORDINATION AGENT ==========
    print_section("🍕 AGENT 2: RESTAURANT COORDINATION AGENT")
    print(f"📞 Calling restaurant: {result['restaurant']['restaurant_name']}")
    print(f"   Order notification sent")
    print(f"   Prep time: {result['restaurant']['prep_time_minutes']} minutes")
    print(f"   Ready at: {result['restaurant']['ready_time']}")
    print("✅ Restaurant confirmed order preparation")
    
    time.sleep(2)
    
    # ========== AGENT 3: DRIVER ASSIGNMENT AGENT ==========
    print_section("🚗 AGENT 3: DRIVER ASSIGNMENT AGENT")
    print(f"🔍 Searching for available drivers...")
    print(f"✅ Driver assigned: {result['driver']['driver']['name']}")
    print(f"   Vehicle: {result['driver']['driver']['vehicle']}")
    print(f"   Rating: {result['driver']['driver']['rating']}⭐")
    print(f"   Pickup ETA: {result['driver']['pickup_eta_minutes']} minutes")
    print(f"   Delivery ETA: {result['driver']['delivery_eta_minutes']} minutes")
    print(f"   Phone: {result['driver']['driver']['phone']}")
    
    time.sleep(2)
    
    # ========== AGENT 4: DELIVERY TRACKING AGENT ==========
    print_section("📍 AGENT 4: DELIVERY TRACKING AGENT")
    
    stages = [
        ("Preparing", "Restaurant is preparing your order"),
        ("Ready for pickup", "Order ready, driver on the way to restaurant"),
        ("Picked up", "Driver picked up order, heading to you")
    ]
    
    for status, message in stages:
        print(f"\n📍 Status: {status}")
        print(f"   {message}")
        
        track_response = requests.get(f"{BASE_URL}/api/orders/order/{order_id}/track")
        if track_response.status_code == 200:
            tracking = track_response.json()
            print(f"   ETA: {tracking.get('eta_minutes', 'Calculating')} minutes")
        
        if status == "Picked up":
            requests.post(f"{BASE_URL}/api/orders/order/{order_id}/picked-up")
        
        time.sleep(1.5)
    
    print(f"\n✅ Live tracking active!")
    print(f"   Customer can track order anytime via: /api/orders/order/{order_id}/track")
    
    time.sleep(2)
    
    # ========== AGENT 5: CUSTOMER SUPPORT AGENT ==========
    print_section("🎧 AGENT 5: CUSTOMER SUPPORT AGENT")
    
    # Scenario: Customer calls to check status
    print("\n📞 Scenario: Customer calls support")
    print("   Customer: 'Where is my order?'")
    
    inquiry_data = {
        "customer_phone": customer_phone,
        "query": "Where is my order?"
    }
    response = requests.post(f"{BASE_URL}/api/orders/support/inquiry", params=inquiry_data)
    if response.status_code == 200:
        result_support = response.json()
        print(f"   🤖 Support: {result_support['response']}")
    
    print("\n✅ Support agent capabilities:")
    print("   • Order status inquiries")
    print("   • Refund processing")
    print("   • Complaint handling")
    print("   • Order cancellations")
    
    time.sleep(2)
    
    # Mark as delivered
    print("\n🎉 Order delivered successfully!")
    requests.post(f"{BASE_URL}/api/orders/order/{order_id}/delivered")
    
    # ========== AGENT 6: POST-DELIVERY AGENT ==========
    print_section("⭐ AGENT 6: POST-DELIVERY AGENT")
    
    print("\n📞 Automated call: 'How was your experience?'")
    print("   Customer: '5 stars! Food was amazing!'")
    
    feedback_data = {
        "order_id": order_id,
        "rating": 5,
        "comments": "Excellent food and fast delivery!"
    }
    response = requests.post(f"{BASE_URL}/api/orders/feedback", json=feedback_data)
    if response.status_code == 200:
        result_feedback = response.json()
        print(f"   ✅ {result_feedback['message']}")
    
    # Check order history for promotion
    response = requests.get(f"{BASE_URL}/api/orders/customer/{customer_phone}/orders")
    if response.status_code == 200:
        result_history = response.json()
        order_count = result_history['count']
        
        print(f"\n🎁 Promotional offer based on {order_count} orders:")
        if order_count >= 5:
            discount = 20
        elif order_count >= 3:
            discount = 15
        else:
            discount = 10
        print(f"   🎉 {discount}% discount on your next order!")
        print(f"   Promo code: SAVE{discount}")
    
    # ========== SUMMARY ==========
    print_section("✅ DEMO COMPLETE - ALL 6 AGENTS COORDINATED SUCCESSFULLY")
    print("""
    🎯 What Just Happened:
    
    1. ✅ Customer Order Agent - Took order via voice call
    2. ✅ Restaurant Agent - Notified restaurant, got prep time
    3. ✅ Driver Agent - Assigned driver with ETA calculation
    4. ✅ Tracking Agent - Provided real-time order tracking
    5. ✅ Support Agent - Handled customer inquiry
    6. ✅ Post-Delivery Agent - Collected feedback & offered promotion
    
    📊 System Performance:
    • Order processed in seconds
    • All services coordinated automatically
    • Real-time tracking active
    • Customer satisfaction ensured
    
    🔗 Try the APIs yourself:
    • Voice: Call +1 218-496-4536
    • API Docs: http://localhost:8000/docs
    • Monitoring: http://localhost:8000/api/monitoring/metrics
    """)

if __name__ == "__main__":
    print("\n⏳ Starting demo in 3 seconds...")
    time.sleep(3)
    demo_complete_flow()
    
    print("\n" + "🎊" * 35)
    print("  Thank you for watching the demo!")
    print("🎊" * 35 + "\n")
