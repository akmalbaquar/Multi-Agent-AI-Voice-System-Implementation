"""
Customer Support Agent
Handles customer inquiries, complaints, and refunds
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.order_service import OrderService

logger = logging.getLogger(__name__)


class SupportAgent:
    """Handles customer support interactions"""
    
    def __init__(self):
        self.order_service = OrderService()
        self.support_tickets = {}
    
    def handle_order_inquiry(self, customer_phone: str, query: str) -> str:
        """
        Handle 'where is my order' queries
        
        Args:
            customer_phone: Customer phone number
            query: Customer query
        
        Returns:
            Response message
        """
        orders = self.order_service.get_customer_orders(customer_phone)
        
        if not orders:
            return "I don't see any recent orders for your number. Can you provide your order ID?"
        
        # Get latest active order
        active_orders = [o for o in orders if o["status"] not in ["delivered", "completed", "cancelled"]]
        
        if not active_orders:
            return "Your last order was delivered successfully. Is there anything else I can help with?"
        
        order = active_orders[0]
        order_id = order["order_id"]
        status = order["status"]
        
        status_messages = {
            "placed": "Your order has been placed and is being confirmed.",
            "confirmed": "Your order is confirmed and will be prepared shortly.",
            "preparing": "Your order is being prepared at the restaurant.",
            "ready": "Your order is ready and waiting for driver pickup.",
            "picked_up": "Driver has picked up your order and is on the way to you.",
            "in_transit": "Your order is on the way! Expected delivery soon."
        }
        
        response = f"Your order {order_id} status: {status_messages.get(status, status)}. "
        
        # Add items info
        items = ", ".join([item['name'] for item in order['items']])
        response += f"Items: {items}. Total: ₹{order['total']}."
        
        return response
    
    def process_refund(self, order_id: str, reason: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Process refund request
        
        Args:
            order_id: Order identifier
            reason: Refund reason
            amount: Refund amount (None for full refund)
        
        Returns:
            Refund result
        """
        order = self.order_service.get_order(order_id)
        
        if not order:
            return {"success": False, "error": "Order not found"}
        
        # Determine refund amount
        refund_amount = amount if amount else order["total"]
        
        # Create refund record
        refund_id = f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        refund = {
            "refund_id": refund_id,
            "order_id": order_id,
            "amount": refund_amount,
            "reason": reason,
            "status": "processed",
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"💰 Refund processed: {refund_id} - ₹{refund_amount} for order {order_id}")
        logger.info(f"   Reason: {reason}")
        
        return {
            "success": True,
            "refund_id": refund_id,
            "amount": refund_amount,
            "message": f"Refund of ₹{refund_amount} will be credited to your account within 5-7 business days."
        }
    
    def create_complaint(self, customer_phone: str, order_id: str, complaint: str) -> Dict[str, Any]:
        """
        Create support ticket for complaint
        
        Args:
            customer_phone: Customer phone
            order_id: Related order ID
            complaint: Complaint description
        
        Returns:
            Ticket information
        """
        ticket_id = f"TKT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        ticket = {
            "ticket_id": ticket_id,
            "customer_phone": customer_phone,
            "order_id": order_id,
            "complaint": complaint,
            "status": "open",
            "priority": "high",
            "created_at": datetime.now().isoformat()
        }
        
        self.support_tickets[ticket_id] = ticket
        
        logger.info(f"🎫 Support ticket created: {ticket_id}")
        logger.info(f"   Order: {order_id}, Complaint: {complaint}")
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": f"Your complaint has been registered with ticket ID {ticket_id}. Our team will contact you within 1 hour."
        }
    
    def cancel_order_request(self, order_id: str, reason: str) -> Dict[str, Any]:
        """
        Handle order cancellation request
        
        Args:
            order_id: Order identifier
            reason: Cancellation reason
        
        Returns:
            Cancellation result
        """
        success = self.order_service.cancel_order(order_id, reason)
        
        if success:
            order = self.order_service.get_order(order_id)
            return {
                "success": True,
                "message": f"Order {order_id} has been cancelled. Refund of ₹{order['total']} will be processed."
            }
        else:
            return {
                "success": False,
                "message": "Order cannot be cancelled at this stage. Please contact support for assistance."
            }
