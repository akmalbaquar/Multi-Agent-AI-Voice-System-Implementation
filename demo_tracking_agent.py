"""
Tracking Agent Demo
Demonstrates real-time order tracking
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def demonstrate_tracking():
    """Demonstrate order tracking throughout delivery"""
    
    print("=" * 60)
    print("📍 DELIVERY TRACKING AGENT DEMO")
    print("=" * 60)
    
    # Create order
    print("\n📦 Creating test order...")
    order_data = {
        "customer_phone": "+919490362478",
        "items": [{"name": "Chicken Burger", "price": 199}],
        "address": "456 Brigade Road, Bangalore",
        "payment_method": "Online Payment"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders/order/create", json=order_data)
    if response.status_code != 200:
        print("❌ Failed to create order")
        return
    
    result = response.json()
    order_id = result["order"]["order_id"]
    print(f"✅ Order created: {order_id}")
    
    # Simulate tracking at different stages
    stages = [
        ("Order placed", 0),
        ("Restaurant preparing", 2),
        ("Driver assigned", 4),
        ("Driver picking up", 6),
        ("Out for delivery", 8),
        ("Delivered", 10)
    ]
    
    print(f"\n🔄 Tracking order lifecycle...\n")
    
    for stage_name, delay in stages:
        time.sleep(delay)
        
        print(f"\n📍 {stage_name}...")
        track_response = requests.get(f"{BASE_URL}/api/orders/order/{order_id}/track")
        
        if track_response.status_code == 200:
            tracking = track_response.json()
            print(f"   Status: {tracking.get('status', 'N/A')}")
            if 'driver_name' in tracking:
                print(f"   Driver: {tracking['driver_name']}")
                print(f"   ETA: {tracking['eta_minutes']} minutes")
            print(f"   📱 Message: {tracking['message']}")
        
        # Update status for demo
        if stage_name == "Driver picking up":
            requests.post(f"{BASE_URL}/api/orders/order/{order_id}/picked-up")
        elif stage_name == "Delivered":
            requests.post(f"{BASE_URL}/api/orders/order/{order_id}/delivered")
    
    print("\n✅ Order tracking complete!")

if __name__ == "__main__":
    demonstrate_tracking()
    
    print("\n" + "=" * 60)
    print("✅ TRACKING AGENT DEMO COMPLETE")
    print("=" * 60)
