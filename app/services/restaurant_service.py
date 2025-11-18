"""
Restaurant Coordination Service
Handles order notifications and restaurant communication
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Mock restaurant database
RESTAURANTS = {
    "rest_001": {
        "id": "rest_001",
        "name": "Pizza Paradise",
        "phone": "+919876543210",
        "avg_prep_time": 20,
        "status": "open"
    },
    "rest_002": {
        "id": "rest_002",
        "name": "Burger Hub",
        "phone": "+919876543211",
        "avg_prep_time": 15,
        "status": "open"
    }
}


class RestaurantService:
    """Handles restaurant order coordination"""
    
    def __init__(self):
        self.pending_orders = {}
    
    def notify_restaurant(self, order_id: str, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notify restaurant about new order
        
        Args:
            order_id: Unique order identifier
            order_details: Order information
        
        Returns:
            Notification result with prep time
        """
        logger.info(f"📞 Notifying restaurant for order {order_id}")
        
        # Simulate restaurant notification
        restaurant_id = "rest_001"  # Default restaurant
        restaurant = RESTAURANTS.get(restaurant_id)
        
        if not restaurant:
            return {
                "success": False,
                "error": "Restaurant not found"
            }
        
        # Calculate prep time
        prep_time = restaurant["avg_prep_time"]
        ready_time = datetime.now() + timedelta(minutes=prep_time)
        
        # Store order
        self.pending_orders[order_id] = {
            "restaurant_id": restaurant_id,
            "order_details": order_details,
            "prep_time": prep_time,
            "ready_time": ready_time.isoformat(),
            "status": "preparing"
        }
        
        logger.info(f"✅ Restaurant notified. Prep time: {prep_time} mins")
        
        return {
            "success": True,
            "restaurant_name": restaurant["name"],
            "prep_time_minutes": prep_time,
            "ready_time": ready_time.isoformat(),
            "status": "preparing"
        }
    
    def confirm_preparation_time(self, order_id: str, confirmed_time: int) -> bool:
        """
        Restaurant confirms actual preparation time
        
        Args:
            order_id: Order identifier
            confirmed_time: Confirmed prep time in minutes
        
        Returns:
            Success status
        """
        if order_id in self.pending_orders:
            self.pending_orders[order_id]["prep_time"] = confirmed_time
            ready_time = datetime.now() + timedelta(minutes=confirmed_time)
            self.pending_orders[order_id]["ready_time"] = ready_time.isoformat()
            logger.info(f"✅ Prep time confirmed: {confirmed_time} mins for order {order_id}")
            return True
        return False
    
    def mark_order_ready(self, order_id: str) -> bool:
        """
        Mark order as ready for pickup
        
        Args:
            order_id: Order identifier
        
        Returns:
            Success status
        """
        if order_id in self.pending_orders:
            self.pending_orders[order_id]["status"] = "ready"
            logger.info(f"✅ Order {order_id} marked as ready for pickup")
            return True
        return False
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get current order status from restaurant"""
        return self.pending_orders.get(order_id, {})
