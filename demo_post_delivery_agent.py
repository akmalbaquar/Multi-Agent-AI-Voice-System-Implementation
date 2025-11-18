"""
Post-Delivery Agent Demo
Demonstrates feedback collection and promotions
"""
import requests

BASE_URL = "http://localhost:8000"

def demonstrate_post_delivery():
    """Demonstrate post-delivery interactions"""
    
    print("=" * 60)
    print("⭐ POST-DELIVERY AGENT DEMO")
    print("=" * 60)
    
    customer_phone = "+919490362478"
    
    # Create and complete an order
    print("\n📦 Creating and completing order...")
    order_data = {
        "customer_phone": customer_phone,
        "items": [{"name": "Margherita Pizza", "price": 299}],
        "address": "123 Test Address",
        "payment_method": "Cash on Delivery"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders/order/create", json=order_data)
    if response.status_code != 200:
        print("❌ Failed to create order")
        return
    
    result = response.json()
    order_id = result["order"]["order_id"]
    print(f"✅ Order {order_id} created and delivered")
    
    # Mark as delivered
    requests.post(f"{BASE_URL}/api/orders/order/{order_id}/delivered")
    
    # Scenario 1: Collect positive feedback
    print("\n⭐ Scenario 1: Collecting positive feedback")
    print("   Customer gives 5-star rating")
    
    feedback_data = {
        "order_id": order_id,
        "rating": 5,
        "comments": "Excellent food and fast delivery! Best pizza ever!"
    }
    response = requests.post(f"{BASE_URL}/api/orders/feedback", json=feedback_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Feedback recorded: {result['feedback_id']}")
        print(f"   📱 Response: {result['message']}")
    
    # Scenario 2: Collect negative feedback
    print("\n⭐ Scenario 2: Collecting negative feedback")
    print("   Customer gives 2-star rating")
    
    # Create another order
    response = requests.post(f"{BASE_URL}/api/orders/order/create", json=order_data)
    order_id2 = response.json()["order"]["order_id"]
    requests.post(f"{BASE_URL}/api/orders/order/{order_id2}/delivered")
    
    feedback_data = {
        "order_id": order_id2,
        "rating": 2,
        "comments": "Food was cold and delivery took too long"
    }
    response = requests.post(f"{BASE_URL}/api/orders/feedback", json=feedback_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Feedback recorded: {result['feedback_id']}")
        print(f"   📱 Response: {result['message']}")
        print("   🎧 Support team will contact customer")
    
    # Scenario 3: Get order history
    print("\n📜 Scenario 3: Checking customer order history")
    response = requests.get(f"{BASE_URL}/api/orders/customer/{customer_phone}/orders")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Total orders: {result['count']}")
        print(f"   📦 Orders: {[o['order_id'] for o in result['orders']]}")
        
        # Based on order count, customer gets promotion
        order_count = result['count']
        if order_count >= 5:
            discount = 20
        elif order_count >= 3:
            discount = 15
        else:
            discount = 10
        
        print(f"\n🎁 Scenario 4: Automatic promotion offer")
        print(f"   Customer has {order_count} orders")
        print(f"   🎉 Offering {discount}% discount on next order!")
        print(f"   Promo code: SAVE{discount}")

if __name__ == "__main__":
    demonstrate_post_delivery()
    
    print("\n" + "=" * 60)
    print("✅ POST-DELIVERY AGENT DEMO COMPLETE")
    print("=" * 60)
