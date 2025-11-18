"""
Master Orchestrator Agent
Analyzes user intent and routes to appropriate specialized agent
Single entry point for all voice interactions
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Master agent that decides which specialized agent should handle the request
    Routes based on conversation context and user intent
    """
    
    def __init__(self):
        self.agent_routing = {
            "order": ["order", "food", "menu", "pizza", "burger", "fries", "pasta", "sandwich", 
                     "want", "buy", "purchase", "get", "hungry"],
            "tracking": ["track", "where", "status", "eta", "arriving", "delivery", "driver", 
                        "location", "when", "time"],
            "support": ["support", "help", "problem", "issue", "complaint", "wrong", "missing",
                       "cold", "late", "refund", "cancel", "bad", "upset"],
            "feedback": ["rate", "rating", "review", "feedback", "star", "stars", "experience",
                        "satisfied", "happy", "unhappy"],
            "restaurant": ["restaurant", "kitchen", "preparing", "ready", "cook", "chef"],
            "driver": ["driver", "deliver", "pickup", "vehicle", "bike", "car"]
        }
    
    def route_to_agent(self, user_speech: str, conversation_state: Dict[str, Any]) -> Dict[str, str]:
        """
        Analyze user intent and route to appropriate agent
        
        Args:
            user_speech: What the user said
            conversation_state: Current conversation context
            
        Returns:
            {
                "agent": "order|tracking|support|feedback|restaurant|driver",
                "intent": "specific_intent",
                "confidence": "high|medium|low"
            }
        """
        user_lower = user_speech.lower().strip()
        current_state = conversation_state.get("state", "menu")
        order_exists = bool(conversation_state.get("order_id"))
        
        logger.info(f"🎯 Orchestrator analyzing: '{user_speech}'")
        logger.info(f"   Current state: {current_state}, Order exists: {order_exists}")
        
        # ========== PRIORITY 0: Handle "No" responses (highest priority) ==========
        
        # If customer says "no" after order confirmation → End conversation
        if user_lower in ["no", "nope", "no thanks", "nah", "no."]:
            if current_state in ["confirmed", "tracking"] and order_exists:
                return {
                    "agent": "order",  # Let order agent handle goodbye
                    "intent": "end_conversation",
                    "confidence": "high",
                    "reason": "Customer declined further assistance - ending call"
                }
            elif current_state in ["menu", "ordering"]:
                return {
                    "agent": "order",
                    "intent": "continue_ordering",
                    "confidence": "high",
                    "reason": "Customer said no during ordering - offering menu"
                }
        
        # ========== PRIORITY 1: Current state-based routing ==========
        
        # If actively ordering, address, or payment → Order Agent
        if current_state in ["menu", "ordering", "address", "payment"]:
            return {
                "agent": "order",
                "intent": "continue_ordering",
                "confidence": "high",
                "reason": f"Currently in {current_state} state - continuing order flow"
            }
        
        # ========== PRIORITY 2: Explicit keyword-based routing ==========
        
        # Support keywords (high priority) → Support Agent
        if self._matches_keywords(user_lower, "support"):
            return {
                "agent": "support",
                "intent": "handle_complaint",
                "confidence": "high",
                "reason": "Support/complaint keywords detected"
            }
        
        # Tracking keywords + order exists → Tracking Agent
        if order_exists and self._matches_keywords(user_lower, "tracking"):
            return {
                "agent": "tracking",
                "intent": "check_order_status",
                "confidence": "high",
                "reason": "Order exists + tracking keywords detected"
            }
        
        # Feedback keywords → Feedback Agent
        if self._matches_keywords(user_lower, "feedback"):
            return {
                "agent": "feedback",
                "intent": "collect_rating",
                "confidence": "high",
                "reason": "Feedback/rating keywords detected"
            }
        
        # Rating numbers detected (only if in feedback or support state) → Feedback Agent
        if current_state in ["feedback", "support"] and any(word in user_lower for word in ["1", "2", "3", "4", "5", "one", "two", "three", "four", "five", "star"]):
            return {
                "agent": "feedback",
                "intent": "process_rating",
                "confidence": "high",
                "reason": "Rating number detected in feedback/support context"
            }
        
        # ========== PRIORITY 3: Context-based defaults ==========
        
        # Order confirmed/tracking state but no specific keywords → Tracking Agent
        if current_state in ["confirmed", "tracking"] and order_exists:
            return {
                "agent": "tracking",
                "intent": "provide_update",
                "confidence": "medium",
                "reason": "Post-order state - defaulting to tracking"
            }
        
        # Fallback: Order Agent (start new order or handle food requests)
        return {
            "agent": "order",
            "intent": "start_new_order",
            "confidence": "low",
            "reason": "No clear routing - defaulting to Order Agent"
        }
    
    def _matches_keywords(self, user_speech: str, agent_type: str) -> bool:
        """Check if user speech matches keywords for an agent type"""
        keywords = self.agent_routing.get(agent_type, [])
        return any(keyword in user_speech for keyword in keywords)
    
    def get_routing_explanation(self, user_speech: str, conversation_state: Dict[str, Any]) -> str:
        """
        Get human-readable explanation of routing decision
        Useful for debugging and logging
        """
        routing = self.route_to_agent(user_speech, conversation_state)
        
        explanation = f"""
🎯 ORCHESTRATOR ROUTING DECISION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User Said: "{user_speech}"
Current State: {conversation_state.get('state', 'unknown')}
Order ID: {conversation_state.get('order_id', 'None')}

🤖 ROUTING TO: {routing['agent'].upper()} AGENT
Intent: {routing['intent']}
Confidence: {routing['confidence'].upper()}
Reason: {routing['reason']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return explanation


# Global orchestrator instance
orchestrator = OrchestratorAgent()
