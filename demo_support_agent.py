"""
Customer Support Agent Demo
Demonstrates support interactions, refunds, and complaints
"""
import requests

BASE_URL = "http://localhost:8000"

def demonstrate_support():
    """Demonstrate customer support agent capabilities"""
    
    print("=" * 60)
    print("🎧 CUSTOMER SUPPORT AGENT DEMO")
    print("=" * 60)
    
    customer_phone = "+919490362478"
    
    # Create a test order first
    print("\n📦 Step 1: Creating order for support demo...")
    order_data = {
        "customer_phone": customer_phone,
        "items": [
            {"name": "Pasta Alfredo", "price": 279},
            {"name": "Club Sandwich", "price": 179}
        ],
        "address": "789 Indiranagar, Bangalore",
        "payment_method": "Cash on Delivery"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders/order/create", json=order_data)
    if response.status_code != 200:
        print("❌ Failed to create order")
        return
    
    result = response.json()
    order_id = result["order"]["order_id"]
    print(f"✅ Order created: {order_id}")
    print(f"   Total: ₹{result['order']['total']}")
    
    # Scenario 1: Order inquiry ("Where is my order?")
    print("\n🔍 Scenario 1: Customer inquiring about order status")
    print("   Customer: 'Where is my order?'")
    
    inquiry_data = {
        "customer_phone": customer_phone,
        "query": "Where is my order?"
    }
    response = requests.post(f"{BASE_URL}/api/orders/support/inquiry", params=inquiry_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   🤖 Support: {result['response']}")
    
    # Scenario 2: Filing a complaint
    print("\n📝 Scenario 2: Filing a complaint")
    print("   Customer: 'Food was cold when delivered'")
    
    complaint_data = {
        "customer_phone": customer_phone,
        "order_id": order_id,
        "complaint": "Food was cold when delivered"
    }
    response = requests.post(f"{BASE_URL}/api/orders/support/complaint", params=complaint_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Ticket created: {result['ticket_id']}")
        print(f"   📱 Message: {result['message']}")
    
    # Scenario 3: Processing refund
    print("\n💰 Scenario 3: Processing refund request")
    print("   Customer: 'I want a refund for my order'")
    
    refund_params = {
        "order_id": order_id,
        "reason": "Food quality issue"
    }
    response = requests.post(f"{BASE_URL}/api/orders/support/refund", params=refund_params)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Refund processed: {result['refund_id']}")
        print(f"   💵 Amount: ₹{result['amount']}")
        print(f"   📱 Message: {result['message']}")
    
    # Scenario 4: Order cancellation
    print("\n❌ Scenario 4: Cancelling order")
    print("   Customer: 'I want to cancel my order'")
    
    cancel_params = {
        "reason": "Changed my mind"
    }
    response = requests.post(f"{BASE_URL}/api/orders/order/{order_id}/cancel", params=cancel_params)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ {result['message']}")

if __name__ == "__main__":
    demonstrate_support()
    
    print("\n" + "=" * 60)
    print("✅ CUSTOMER SUPPORT AGENT DEMO COMPLETE")
    print("=" * 60)
