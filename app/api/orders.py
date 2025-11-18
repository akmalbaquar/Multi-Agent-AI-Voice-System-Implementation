"""
Complete Order Fulfillment API
Orchestrates restaurant, driver, and order services
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from app.services.order_service import OrderService, OrderStatus
from app.services.restaurant_service import RestaurantService
from app.services.driver_service import DriverService
from app.agents.tracking_agent import TrackingAgent
from app.agents.support_agent import SupportAgent
from app.agents.post_delivery_agent import PostDeliveryAgent

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
order_service = OrderService()
restaurant_service = RestaurantService()
driver_service = DriverService()
tracking_agent = TrackingAgent()
support_agent = SupportAgent()
post_delivery_agent = PostDeliveryAgent()


class OrderRequest(BaseModel):
    customer_phone: str
    items: List[Dict[str, Any]]
    address: str
    payment_method: str


class FeedbackRequest(BaseModel):
    order_id: str
    rating: int
    comments: str = ""


@router.post("/order/create")
async def create_order(request: OrderRequest):
    """Create and process complete order with restaurant and driver"""
    try:
        # 1. Create order
        order = order_service.create_order(
            customer_phone=request.customer_phone,
            items=request.items,
            address=request.address,
            payment_method=request.payment_method
        )
        
        order_id = order["order_id"]
        
        # 2. Notify restaurant
        restaurant_result = restaurant_service.notify_restaurant(order_id, order)
        
        if restaurant_result["success"]:
            order_service.update_status(order_id, OrderStatus.PREPARING)
        
        # 3. Assign driver
        driver_result = driver_service.assign_driver(
            order_id=order_id,
            driver_id="drv_001",  # Auto-assign first available
            restaurant_location={"lat": 28.7041, "lng": 77.1025},
            customer_location={"address": request.address}
        )
        
        if driver_result["success"]:
            order_service.update_status(order_id, OrderStatus.CONFIRMED)
        
        # 4. Return complete order info
        return {
            "success": True,
            "order": order,
            "restaurant": restaurant_result,
            "driver": driver_result,
            "message": f"Order {order_id} confirmed! Expected delivery in {driver_result['delivery_eta_minutes']} minutes."
        }
        
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/order/{order_id}/track")
async def track_order(order_id: str):
    """Get real-time order tracking"""
    tracking = tracking_agent.get_order_tracking(order_id)
    
    if "error" in tracking:
        raise HTTPException(status_code=404, detail=tracking["error"])
    
    return tracking


@router.get("/order/{order_id}/status")
async def get_order_status(order_id: str):
    """Get order status"""
    order = order_service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order


@router.post("/order/{order_id}/cancel")
async def cancel_order(order_id: str, reason: str):
    """Cancel order"""
    result = support_agent.cancel_order_request(order_id, reason)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/support/inquiry")
async def handle_inquiry(customer_phone: str, query: str):
    """Handle customer support inquiry"""
    response = support_agent.handle_order_inquiry(customer_phone, query)
    return {"response": response}


@router.post("/support/complaint")
async def create_complaint(customer_phone: str, order_id: str, complaint: str):
    """Create support complaint"""
    result = support_agent.create_complaint(customer_phone, order_id, complaint)
    return result


@router.post("/support/refund")
async def process_refund(order_id: str, reason: str):
    """Process refund"""
    result = support_agent.process_refund(order_id, reason)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit post-delivery feedback"""
    result = post_delivery_agent.collect_feedback(
        order_id=request.order_id,
        rating=request.rating,
        comments=request.comments
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/customer/{phone}/orders")
async def get_customer_orders(phone: str):
    """Get all orders for customer"""
    orders = order_service.get_customer_orders(phone)
    return {"orders": orders, "count": len(orders)}


@router.post("/driver/{driver_id}/location")
async def update_driver_location(driver_id: str, lat: float, lng: float):
    """Update driver location"""
    success = driver_service.update_driver_location(driver_id, {"lat": lat, "lng": lng})
    
    if not success:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return {"success": True}


@router.post("/order/{order_id}/picked-up")
async def mark_picked_up(order_id: str):
    """Mark order as picked up"""
    success = driver_service.mark_picked_up(order_id)
    
    if success:
        order_service.update_status(order_id, OrderStatus.PICKED_UP)
        return {"success": True, "message": "Order marked as picked up"}
    
    raise HTTPException(status_code=404, detail="Order not found")


@router.post("/order/{order_id}/delivered")
async def mark_delivered(order_id: str):
    """Mark order as delivered"""
    success = tracking_agent.confirm_delivery(order_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"success": True, "message": "Order delivered successfully"}
