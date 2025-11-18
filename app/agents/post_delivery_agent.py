"""
Post-Delivery Agent
Handles feedback collection and post-delivery follow-up
"""
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PostDeliveryAgent:
    """Handles post-delivery interactions"""
    
    def __init__(self):
        self.feedback_db = {}
    
    def collect_feedback(self, order_id: str, rating: int, comments: str = "") -> Dict[str, Any]:
        """
        Collect delivery feedback
        
        Args:
            order_id: Order identifier
            rating: Rating (1-5)
            comments: Optional feedback comments
        
        Returns:
            Feedback confirmation
        """
        if not 1 <= rating <= 5:
            return {"success": False, "error": "Rating must be between 1 and 5"}
        
        feedback = {
            "feedback_id": f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "order_id": order_id,
            "rating": rating,
            "comments": comments,
            "collected_at": datetime.now().isoformat()
        }
        
        self.feedback_db[order_id] = feedback
        
        logger.info(f"⭐ Feedback collected for order {order_id}: {rating}/5")
        if comments:
            logger.info(f"   Comments: {comments}")
        
        # Determine response based on rating
        if rating >= 4:
            message = "Thank you for your positive feedback! We're glad you enjoyed your meal."
        elif rating == 3:
            message = "Thank you for your feedback. We'll work on improving your experience."
        else:
            message = "We're sorry you weren't satisfied. Our support team will contact you shortly."
        
        return {
            "success": True,
            "message": message,
            "feedback_id": feedback["feedback_id"]
        }
    
    def offer_promotion(self, customer_phone: str, order_history: list) -> Dict[str, Any]:
        """
        Offer promotional discount based on order history
        
        Args:
            customer_phone: Customer phone number
            order_history: List of previous orders
        
        Returns:
            Promotion details
        """
        # Determine promotion based on order count
        order_count = len(order_history)
        
        if order_count >= 5:
            discount = 20
            message = "Congratulations! As a valued customer, you get 20% off on your next order!"
        elif order_count >= 3:
            discount = 15
            message = "Great news! You've earned 15% off on your next order!"
        else:
            discount = 10
            message = "Thank you for ordering! Here's 10% off on your next order!"
        
        promo_code = f"SAVE{discount}{datetime.now().strftime('%m%d')}"
        
        logger.info(f"🎁 Promotion offered to {customer_phone}: {discount}% off")
        logger.info(f"   Promo code: {promo_code}")
        
        return {
            "success": True,
            "discount_percent": discount,
            "promo_code": promo_code,
            "valid_until": "30 days",
            "message": message
        }
    
    def handle_issue_resolution(self, order_id: str, issue: str) -> Dict[str, Any]:
        """
        Handle post-delivery issues (missing items, quality issues)
        
        Args:
            order_id: Order identifier
            issue: Issue description
        
        Returns:
            Resolution details
        """
        logger.info(f"🔧 Post-delivery issue reported for order {order_id}")
        logger.info(f"   Issue: {issue}")
        
        # Classify issue and provide resolution
        issue_lower = issue.lower()
        
        if "missing" in issue_lower or "forgot" in issue_lower:
            resolution = "We'll immediately send the missing items at no extra cost."
            compensation = "Free delivery on missing items"
        elif "cold" in issue_lower or "quality" in issue_lower:
            resolution = "We apologize for the quality issue. We'll issue a 50% refund."
            compensation = "50% refund"
        elif "wrong" in issue_lower or "incorrect" in issue_lower:
            resolution = "We'll send the correct order immediately and you can keep the incorrect one."
            compensation = "Free correct order"
        else:
            resolution = "Our support team will contact you within 15 minutes to resolve this."
            compensation = "Priority support callback"
        
        return {
            "success": True,
            "resolution": resolution,
            "compensation": compensation,
            "estimated_resolution_time": "15-30 minutes"
        }
