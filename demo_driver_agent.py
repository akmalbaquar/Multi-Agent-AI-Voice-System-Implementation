"""
Driver Agent Demo
Simulates driver assignment and delivery coordination
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def demonstrate_driver_flow():
    """Demonstrate complete driver coordination flow"""
    
    print("=" * 60)
    print("🚗 DRIVER ASSIGNMENT AGENT DEMO")
    print("=" * 60)
    
    # Step 1: Create an order first
    print("\n📦 Step 1: Creating order...")
    order_data = {
        "customer_phone": "+919490362478",
        "items": [
            {"name": "Margherita Pizza", "price": 299},
            {"name": "French Fries", "price": 99}
        ],
        "address": "123 MG Road, Koramangala, Bangalore",
        "payment_method": "Cash on Delivery"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders/order/create", json=order_data)
    if response.status_code == 200:
        result = response.json()
        order_id = result["order"]["order_id"]
        print(f"✅ Order created: {order_id}")
        print(f"   Total: ₹{result['order']['total']}")
        print(f"   Driver: {result['driver']['driver']['name']}")
        print(f"   Vehicle: {result['driver']['driver']['vehicle']}")
        print(f"   Rating: {result['driver']['driver']['rating']}⭐")
        print(f"   Pickup ETA: {result['driver']['pickup_eta_minutes']} mins")
        print(f"   Delivery ETA: {result['driver']['delivery_eta_minutes']} mins")
        
        # Step 2: Track delivery
        print(f"\n📍 Step 2: Tracking delivery...")
        track_response = requests.get(f"{BASE_URL}/api/orders/order/{order_id}/track")
        if track_response.status_code == 200:
            tracking = track_response.json()
            print(f"✅ Current status: {tracking['status']}")
            print(f"   Driver: {tracking['driver_name']}")
            print(f"   Phone: {tracking['driver_phone']}")
            print(f"   ETA: {tracking['eta_minutes']} minutes")
            print(f"   Message: {tracking['message']}")
        
        # Step 3: Simulate pickup
        print(f"\n📦 Step 3: Marking order as picked up...")
        pickup_response = requests.post(f"{BASE_URL}/api/orders/order/{order_id}/picked-up")
        if pickup_response.status_code == 200:
            print("✅ Order picked up from restaurant")
            print("   Driver is now heading to customer")
        
        # Step 4: Track again after pickup
        print(f"\n📍 Step 4: Tracking after pickup...")
        track_response = requests.get(f"{BASE_URL}/api/orders/order/{order_id}/track")
        if track_response.status_code == 200:
            tracking = track_response.json()
            print(f"✅ Current status: {tracking['delivery_status']}")
            print(f"   Message: {tracking['message']}")
            print(f"   ETA to customer: {tracking['eta_minutes']} minutes")
        
        # Step 5: Simulate delivery
        print(f"\n✅ Step 5: Marking order as delivered...")
        delivery_response = requests.post(f"{BASE_URL}/api/orders/order/{order_id}/delivered")
        if delivery_response.status_code == 200:
            print("✅ Order delivered successfully!")
            print("   Driver is now available for next order")
        
        return order_id
    else:
        print(f"❌ Error creating order: {response.status_code}")
        return None

if __name__ == "__main__":
    demonstrate_driver_flow()
    
    print("\n" + "=" * 60)
    print("✅ DRIVER AGENT DEMO COMPLETE")
    print("=" * 60)
