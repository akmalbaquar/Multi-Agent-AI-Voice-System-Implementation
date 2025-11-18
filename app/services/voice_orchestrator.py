"""
Unified Voice Orchestrator
Routes single call through multiple agents based on context
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class VoiceOrchestrator:
    """
    Master orchestrator that routes voice conversations through appropriate agents
    Single call can flow through: Order → Restaurant → Driver → Tracking → Support → Feedback
    """
    
    def __init__(self, call_sid: str):
        self.call_sid = call_sid
        self.conversation_state = {
            "phase": "ordering",  # ordering, confirming, tracking, support, feedback
            "order_id": None,
            "order": [],
            "address": None,
            "payment_method": None,
            "issue_reported": False
        }
    
    def route_message(self, user_speech: str) -> Dict[str, Any]:
        """
        Route user speech to appropriate agent based on conversation phase
        
        Returns:
            {
                "response": str,
                "agent": str,
                "next_phase": str,
                "order_id": str (optional)
            }
        """
        user_lower = user_speech.lower().strip()
        current_phase = self.conversation_state["phase"]
        
        logger.info(f"🎯 Orchestrator routing: phase={current_phase}, speech='{user_speech}'")
        
        # ========== PHASE 1: ORDER AGENT ==========
        if current_phase == "ordering":
            return self._handle_ordering(user_lower, user_speech)
        
        # ========== PHASE 2: TRACKING AGENT ==========
        elif current_phase == "tracking":
            return self._handle_tracking(user_lower)
        
        # ========== PHASE 3: SUPPORT AGENT ==========
        elif current_phase == "support":
            return self._handle_support(user_lower)
        
        # ========== PHASE 4: FEEDBACK AGENT ==========
        elif current_phase == "feedback":
            return self._handle_feedback(user_lower)
        
        # Default fallback
        return {
            "response": "I didn't quite catch that. Could you repeat?",
            "agent": "orchestrator",
            "next_phase": current_phase
        }
    
    def _handle_ordering(self, user_lower: str, user_speech: str) -> Dict[str, Any]:
        """Order Agent - Handle food ordering"""
        
        # Check for items
        if "pizza" in user_lower:
            self.conversation_state["order"].append({"name": "Pizza", "price": 299})
            return {
                "response": "Pizza added for 299 rupees. Anything else?",
                "agent": "order_agent",
                "next_phase": "ordering"
            }
        elif "burger" in user_lower:
            self.conversation_state["order"].append({"name": "Burger", "price": 199})
            return {
                "response": "Burger added for 199 rupees. Anything else?",
                "agent": "order_agent",
                "next_phase": "ordering"
            }
        elif "fries" in user_lower:
            self.conversation_state["order"].append({"name": "Fries", "price": 99})
            return {
                "response": "Fries added for 99 rupees. Anything else?",
                "agent": "order_agent",
                "next_phase": "ordering"
            }
        
        # Order completion → Move to address
        elif any(word in user_lower for word in ["done", "that's all", "finish"]):
            if not self.conversation_state["order"]:
                return {
                    "response": "You haven't ordered anything yet. What would you like?",
                    "agent": "order_agent",
                    "next_phase": "ordering"
                }
            
            total = sum(item['price'] for item in self.conversation_state["order"])
            self.conversation_state["phase"] = "address"
            return {
                "response": f"Perfect! {len(self.conversation_state['order'])} items, total {total} rupees. Please tell me your delivery address.",
                "agent": "order_agent",
                "next_phase": "address"
            }
        
        return {
            "response": "I can help you order Pizza, Burger, or Fries. What would you like?",
            "agent": "order_agent",
            "next_phase": "ordering"
        }
    
    def _handle_tracking(self, user_lower: str) -> Dict[str, Any]:
        """Tracking Agent - Handle order tracking inquiries"""
        
        if not self.conversation_state["order_id"]:
            return {
                "response": "Let me check your order status. One moment please.",
                "agent": "tracking_agent",
                "next_phase": "tracking"
            }
        
        # Simulate tracking response
        if any(word in user_lower for word in ["where", "status", "track", "eta"]):
            response = f"Your order {self.conversation_state['order_id']} is on the way! Driver Rahul is 15 minutes away. Would you like to speak with support or provide feedback?"
            
            # Offer next steps
            self.conversation_state["phase"] = "post_order_options"
            return {
                "response": response,
                "agent": "tracking_agent",
                "next_phase": "post_order_options"
            }
        
        return {
            "response": "Your order is being prepared and will be delivered soon.",
            "agent": "tracking_agent",
            "next_phase": "tracking"
        }
    
    def _handle_support(self, user_lower: str) -> Dict[str, Any]:
        """Support Agent - Handle complaints, refunds, issues"""
        
        # Detect issue type
        if any(word in user_lower for word in ["cold", "wrong", "missing", "late", "problem", "issue"]):
            self.conversation_state["issue_reported"] = True
            
            # Automatic compensation logic
            if "cold" in user_lower or "late" in user_lower:
                return {
                    "response": "I apologize for that. I'm processing a 50% refund for you immediately. Is there anything else I can help with?",
                    "agent": "support_agent",
                    "next_phase": "feedback"
                }
            elif "wrong" in user_lower or "missing" in user_lower:
                return {
                    "response": "I'm very sorry. We'll send the correct order right away at no charge. Can I get your feedback on this experience?",
                    "agent": "support_agent",
                    "next_phase": "feedback"
                }
        
        # Refund request
        if "refund" in user_lower or "cancel" in user_lower:
            return {
                "response": "I've processed your refund. You'll receive it in 5-7 business days. Would you like to share feedback?",
                "agent": "support_agent",
                "next_phase": "feedback"
            }
        
        return {
            "response": "I'm here to help. What issue are you experiencing?",
            "agent": "support_agent",
            "next_phase": "support"
        }
    
    def _handle_feedback(self, user_lower: str) -> Dict[str, Any]:
        """Feedback Agent - Collect ratings and feedback"""
        
        # Detect rating
        rating = None
        for i in range(1, 6):
            if str(i) in user_lower or ["one", "two", "three", "four", "five"][i-1] in user_lower:
                rating = i
                break
        
        if rating:
            if rating >= 4:
                response = "Thank you for the great rating! As a token of appreciation, here's 10% off your next order. Code: SAVE10. Goodbye!"
            elif rating == 3:
                response = "Thank you for your feedback. We'll work on improving. Here's 15% off your next order. Code: SAVE15. Goodbye!"
            else:
                response = "We're very sorry about your experience. Our support team will contact you within 1 hour. Here's 20% off your next order. Code: SAVE20. Goodbye!"
            
            return {
                "response": response,
                "agent": "feedback_agent",
                "next_phase": "complete",
                "promo_code": f"SAVE{[20, 20, 15, 10, 10][rating-1]}"
            }
        
        return {
            "response": "How would you rate your experience from 1 to 5 stars?",
            "agent": "feedback_agent",
            "next_phase": "feedback"
        }
    
    def get_current_phase(self) -> str:
        """Get current conversation phase"""
        return self.conversation_state["phase"]
    
    def set_order_id(self, order_id: str):
        """Set order ID after creation"""
        self.conversation_state["order_id"] = order_id


# Global orchestrators for each call
active_orchestrators = {}


def get_orchestrator(call_sid: str) -> VoiceOrchestrator:
    """Get or create orchestrator for call"""
    if call_sid not in active_orchestrators:
        active_orchestrators[call_sid] = VoiceOrchestrator(call_sid)
    return active_orchestrators[call_sid]
