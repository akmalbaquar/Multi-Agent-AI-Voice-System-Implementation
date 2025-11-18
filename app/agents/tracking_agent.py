"""
Tracking Agent
Handles delivery tracking and real-time updates
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from app.services.driver_service import DriverService
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)


class TrackingAgent:
    """Handles order tracking and delivery updates"""
    
    def __init__(self):
        self.driver_service = DriverService()
        self.order_service = OrderService()
    
    def get_order_tracking(self, order_id: str) -> Dict[str, Any]:
        """
        Get real-time tracking information
        
        Args:
            order_id: Order identifier
        
        Returns:
            Tracking information with ETA
        """
        order = self.order_service.get_order(order_id)
        if not order:
            return {"error": "Order not found"}
        
        delivery = self.driver_service.get_delivery_status(order_id)
        
        if not delivery:
            return {
                "order_id": order_id,
                "status": order["status"],
                "message": "Order is being prepared"
            }
        
        # Calculate current ETA
        if delivery["status"] == "assigned":
            eta = delivery["delivery_eta_minutes"]
            message = f"Driver {delivery['driver_name']} is on the way to pickup your order"
        elif delivery["status"] == "picked_up":
            eta = delivery["delivery_eta_minutes"] - delivery["pickup_eta_minutes"]
            message = f"Driver {delivery['driver_name']} picked up your order and is heading to you"
        else:
            eta = 0
            message = "Order delivered successfully"
        
        return {
            "order_id": order_id,
            "status": order["status"],
            "driver_name": delivery["driver_name"],
            "driver_phone": delivery["driver_phone"],
            "driver_rating": delivery["driver_rating"],
            "vehicle": delivery["vehicle"],
            "eta_minutes": eta,
            "delivery_status": delivery["status"],
            "message": message
        }
    
    def send_delay_notification(self, order_id: str, delay_minutes: int, reason: str) -> bool:
        """
        Notify customer about delivery delay
        
        Args:
            order_id: Order identifier
            delay_minutes: Delay duration
            reason: Delay reason
        
        Returns:
            Success status
        """
        order = self.order_service.get_order(order_id)
        if not order:
            return False
        
        logger.info(f"📢 Delay notification sent for order {order_id}")
        logger.info(f"   Delay: {delay_minutes} mins, Reason: {reason}")
        
        # In production, send SMS/push notification here
        return True
    
    def confirm_delivery(self, order_id: str, delivery_proof: Dict = None) -> bool:
        """
        Confirm order delivery
        
        Args:
            order_id: Order identifier
            delivery_proof: Optional delivery proof (photo, signature)
        
        Returns:
            Success status
        """
        # Mark as delivered in driver service
        if not self.driver_service.mark_delivered(order_id):
            return False
        
        # Update order status
        self.order_service.update_status(order_id, "delivered")
        
        logger.info(f"✅ Delivery confirmed for order {order_id}")
        
        return True
