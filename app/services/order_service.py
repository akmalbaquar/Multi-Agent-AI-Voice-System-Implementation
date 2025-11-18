"""
Order Management Service
Handles complete order lifecycle
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class OrderStatus:
    """Order status constants"""
    CART = "cart"
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderService:
    """Manages order lifecycle"""
    
    def __init__(self):
        self.orders = {}
    
    def create_order(self, customer_phone: str, items: list, address: str, payment_method: str) -> Dict[str, Any]:
        """
        Create new order
        
        Args:
            customer_phone: Customer phone number
            items: List of order items
            address: Delivery address
            payment_method: Payment method
        
        Returns:
            Created order details
        """
        order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total
        total = sum(item['price'] for item in items)
        
        order = {
            "order_id": order_id,
            "customer_phone": customer_phone,
            "items": items,
            "total": total,
            "delivery_address": address,
            "payment_method": payment_method,
            "status": OrderStatus.PLACED,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status_history": [
                {"status": OrderStatus.PLACED, "timestamp": datetime.now().isoformat()}
            ]
        }
        
        self.orders[order_id] = order
        logger.info(f"✅ Order created: {order_id} - Total: ₹{total}")
        
        return order
    
    def update_status(self, order_id: str, new_status: str, notes: Optional[str] = None) -> bool:
        """
        Update order status
        
        Args:
            order_id: Order identifier
            new_status: New status
            notes: Optional notes
        
        Returns:
            Success status
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        old_status = order["status"]
        order["status"] = new_status
        order["updated_at"] = datetime.now().isoformat()
        
        # Add to status history
        history_entry = {
            "status": new_status,
            "timestamp": datetime.now().isoformat()
        }
        if notes:
            history_entry["notes"] = notes
        
        order["status_history"].append(history_entry)
        
        logger.info(f"📦 Order {order_id}: {old_status} → {new_status}")
        
        return True
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def cancel_order(self, order_id: str, reason: str) -> bool:
        """Cancel order"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        # Only allow cancellation before picked up
        if order["status"] in [OrderStatus.PICKED_UP, OrderStatus.IN_TRANSIT, OrderStatus.DELIVERED]:
            logger.warning(f"Cannot cancel order {order_id} - already {order['status']}")
            return False
        
        self.update_status(order_id, OrderStatus.CANCELLED, reason)
        logger.info(f"❌ Order {order_id} cancelled: {reason}")
        
        return True
    
    def get_customer_orders(self, customer_phone: str) -> list:
        """Get all orders for a customer"""
        return [o for o in self.orders.values() if o["customer_phone"] == customer_phone]
