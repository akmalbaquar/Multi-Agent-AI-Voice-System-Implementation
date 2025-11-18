"""
AI Order Handler
Integrates with Orchestrator Agent for intelligent multi-agent routing
"""
import os
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI
from app.data.menu import MENU, search_menu, get_menu_text
from app.services.order_service import OrderService
from app.services.restaurant_service import RestaurantService
from app.services.driver_service import DriverService
from app.agents.orchestrator_agent import orchestrator

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OpenAI API key not found!")
    client = None
else:
    client = OpenAI(api_key=api_key)

# Services for backend integration
order_service = OrderService()
restaurant_service = RestaurantService()
driver_service = DriverService()

# Conversation history storage (in-memory for now)
conversations = {}

# Order workflow states
class OrderState:
    MENU = "menu"
    ORDERING = "ordering"
    ADDRESS = "address"
    PAYMENT = "payment"
    CONFIRMED = "confirmed"
    TRACKING = "tracking"
    SUPPORT = "support"
    FEEDBACK = "feedback"


def process_order_with_ai(call_sid: str, user_speech: str):
    """Process user speech with AI and return response"""
    
    logger.info(f"=== STARTING AI PROCESSING for {call_sid} ===")
    logger.info(f"User said: {user_speech}")
    
    try:
        # Initialize conversation history
        if call_sid not in conversations:
            conversations[call_sid] = {
                "messages": [],
                "order": [],
                "state": OrderState.MENU,
                "address": None,
                "payment_method": None,
                "order_id": None
            }
            logger.info("Created new conversation")
        
        conv = conversations[call_sid]
        
        # ========== ORCHESTRATOR ROUTING DECISION ==========
        logger.info("="*70)
        logger.info("🎯 ORCHESTRATOR AGENT - ANALYZING USER INTENT")
        logger.info("="*70)
        
        routing = orchestrator.route_to_agent(user_speech, conv)
        
        logger.info(f"📊 ROUTING DECISION:")
        logger.info(f"   ├─ Target Agent: {routing['agent'].upper()}")
        logger.info(f"   ├─ Intent: {routing['intent']}")
        logger.info(f"   ├─ Confidence: {routing['confidence']}")
        logger.info(f"   └─ Reason: {routing['reason']}")
        logger.info("="*70)
        
        # Route to appropriate agent handler
        if routing['agent'] == 'tracking':
            logger.info("📍 Routing to TRACKING AGENT...")
            return _handle_tracking_agent(conv, user_speech)
        elif routing['agent'] == 'support':
            logger.info("🆘 Routing to SUPPORT AGENT...")
            return _handle_support_agent(conv, user_speech)
        elif routing['agent'] == 'feedback':
            logger.info("⭐ Routing to FEEDBACK AGENT...")
            return _handle_feedback_agent(conv, user_speech)
        else:  # Default to order agent
            logger.info("📦 Routing to ORDER AGENT...")
            return _handle_order_agent(conv, user_speech)
        
    except Exception as e:
        logger.error(f"Error in AI handler: {e}", exc_info=True)
        return "I'm having trouble processing that. Could you repeat your order?"


def _handle_order_agent(conv: dict, user_speech: str) -> str:
    """Handle order-related requests"""
    user_lower = user_speech.lower().strip()
    
    logger.info(f"📦 ORDER AGENT handling: state={conv['state']}")
    
    # Check for "yes" response first (menu request)
    if user_lower in ["yes", "yeah", "yep", "sure", "okay", "ok"]:
        return "Here's our menu: Margherita Pizza for 299 rupees, Chicken Burger for 199 rupees, French Fries for 99 rupees, Pasta Alfredo for 279 rupees, and Club Sandwich for 179 rupees. What would you like?"
    
    # Check for "no" response - end conversation gracefully
    if user_lower in ["no", "nope", "no thanks", "nah", "no."]:
        if conv["state"] in [OrderState.MENU, OrderState.ORDERING]:
            return "Would you like me to list our menu? Say yes to hear the items."
        else:
            # After order confirmed, "no" means end call
            return "Thank you for ordering with us! Goodbye!"
    
    # Check for menu request
    if any(word in user_lower for word in ["menu", "list", "what do you have", "show me", "tell me items"]):
        return "Here's our menu: Margherita Pizza for 299 rupees, Chicken Burger for 199 rupees, French Fries for 99 rupees, Pasta Alfredo for 279 rupees, and Club Sandwich for 179 rupees. What would you like to order?"
    
    # Check for order completion - move to address collection
    if any(word in user_lower for word in ["that's all", "thats all", "done", "finish", "complete"]):
        if conv["order"]:
            conv["state"] = OrderState.ADDRESS
            total = sum(item['price'] for item in conv["order"])
            item_count = len(conv["order"])
            return f"Perfect! {item_count} items, total {total} rupees. Please tell me your delivery address."
        else:
            return "You haven't ordered anything yet. Would you like me to list the menu?"
    
    # Handle address collection
    if conv["state"] == OrderState.ADDRESS:
        if len(user_speech.split()) >= 3:  # Basic validation
            conv["address"] = user_speech
            conv["state"] = OrderState.PAYMENT
            return "Perfect! I've noted your address. For payment, say 'cash on delivery' or 'online payment'."
        else:
            return "Please provide a complete address with street, area, and city."
    
    # Handle payment selection - CREATE ORDER WITH BACKEND SERVICES
    if conv["state"] == OrderState.PAYMENT:
        if "cash" in user_lower or "cod" in user_lower:
            conv["payment_method"] = "Cash on Delivery"
            conv["state"] = OrderState.CONFIRMED
            
            # ========== BACKEND INTEGRATION: CREATE ORDER ==========
            try:
                # Create order via Order Service
                order = order_service.create_order(
                    customer_phone="+919490362478",  # From call
                    items=conv["order"],
                    address=conv["address"],
                    payment_method="Cash on Delivery"
                )
                order_id = order["order_id"]
                conv["order_id"] = order_id
                
                # Notify Restaurant Agent
                restaurant_result = restaurant_service.notify_restaurant(order_id, order)
                prep_time = restaurant_result.get("prep_time_minutes", 20)
                
                # Assign Driver Agent
                driver_result = driver_service.assign_driver(
                    order_id=order_id,
                    driver_id="drv_001",
                    restaurant_location={"lat": 28.7041, "lng": 77.1025},
                    customer_location={"address": conv["address"]}
                )
                delivery_eta = driver_result.get("delivery_eta_minutes", 35)
                
                logger.info(f"✅ Order {order_id} created → Restaurant notified → Driver assigned")
                
                total = sum(item['price'] for item in conv["order"])
                
                # Offer tracking/support option
                conv["state"] = OrderState.TRACKING
                return f"Perfect! Order {order_id} confirmed for {total} rupees. Delivery in {delivery_eta} minutes. Say 'track order' for updates or 'support' for help. Thank you!"
                
            except Exception as e:
                logger.error(f"Error creating order: {e}")
                total = sum(item['price'] for item in conv["order"])
                return f"Perfect! Order confirmed for {total} rupees. Delivery in 30-45 minutes. Thank you!"
            
        elif "online" in user_lower or "card" in user_lower or "upi" in user_lower:
            conv["payment_method"] = "Online Payment"
            conv["state"] = OrderState.CONFIRMED
            total = sum(item['price'] for item in conv["order"])
            return f"Perfect! Order confirmed for {total} rupees. Payment link sent. Expected delivery in 30 to 45 minutes. Thank you!"
        else:
            return "Please say cash on delivery or online payment."
    
    # Add items to order (only in MENU or ORDERING state)
    if conv["state"] in [OrderState.MENU, OrderState.ORDERING]:
        conv["state"] = OrderState.ORDERING
        
        # Detect multiple items in one sentence
        items_added = []
        
        if "pizza" in user_lower:
            conv["order"].append({"name": "Margherita Pizza", "price": 299})
            items_added.append("Pizza (299 rupees)")
        
        if "burger" in user_lower:
            conv["order"].append({"name": "Chicken Burger", "price": 199})
            items_added.append("Burger (199 rupees)")
        
        if "fries" in user_lower or "french fries" in user_lower:
            conv["order"].append({"name": "French Fries", "price": 99})
            items_added.append("Fries (99 rupees)")
        
        if "pasta" in user_lower:
            conv["order"].append({"name": "Pasta Alfredo", "price": 279})
            items_added.append("Pasta (279 rupees)")
        
        if "sandwich" in user_lower or "sandwiches" in user_lower:
            conv["order"].append({"name": "Club Sandwich", "price": 179})
            items_added.append("Sandwich (179 rupees)")
        
        if items_added:
            items_str = ", ".join(items_added)
            return f"Added {items_str}. Anything else? Say 'done' when finished."
        else:
            return "I can help you order Pizza, Burger, French Fries, Pasta, or Sandwich. Would you like me to list the full menu with prices?"
    
    return "I didn't quite catch that. Could you please repeat?"


def _handle_tracking_agent(conv: dict, user_speech: str) -> str:
    """Handle tracking-related requests"""
    user_lower = user_speech.lower().strip()
    
    logger.info(f"📍 TRACKING AGENT handling request")
    
    # Check for "no" - customer doesn't want tracking/help
    if user_lower in ["no", "nope", "no thanks", "nah", "no."]:
        return "Thank you for ordering with us! Goodbye!"
    
    conv["state"] = OrderState.TRACKING
    order_id = conv.get("order_id", "your order")
    
    if not order_id or order_id == "your order":
        return "I don't see an active order. Would you like to place a new order?"
    
    return f"Your order {order_id} is on the way! Driver will arrive in approximately 30 minutes. Say 'support' if you need help or 'rate' to give feedback."


def _handle_support_agent(conv: dict, user_speech: str) -> str:
    """Handle support/complaint requests"""
    user_lower = user_speech.lower().strip()
    
    logger.info(f"🆘 SUPPORT AGENT handling complaint/issue")
    
    conv["state"] = OrderState.SUPPORT
    
    # Detect specific issues
    if any(word in user_lower for word in ["cold", "late", "wrong", "missing"]):
        conv["state"] = OrderState.FEEDBACK  # Move to feedback after resolving
        return "I apologize for that. I'm processing a 50% refund immediately. Would you like to rate your experience?"
    
    if "refund" in user_lower or "cancel" in user_lower:
        conv["state"] = OrderState.FEEDBACK
        return "Your refund is being processed. You'll receive it in 5-7 days. Would you like to provide feedback?"
    
    # First time entering support
    return "I'm connecting you to customer support. What can I help you with? You can report issues, request refunds, or cancel your order."


def _handle_feedback_agent(conv: dict, user_speech: str) -> str:
    """Handle feedback/rating requests"""
    user_lower = user_speech.lower().strip()
    
    logger.info(f"⭐ FEEDBACK AGENT collecting rating")
    
    conv["state"] = OrderState.FEEDBACK
    
    # Check for rating (numbers or words)
    rating = None
    rating_words = ["one", "two", "three", "four", "five"]
    
    for i in range(1, 6):
        if str(i) in user_lower or rating_words[i-1] in user_lower:
            rating = i
            break
    
    if rating:
        if rating >= 4:
            return f"Thank you for the {rating}-star rating! Here's 10% off your next order with code SAVE10. Goodbye!"
        elif rating == 3:
            return f"Thanks for your feedback. Here's 15% off next time. Code: SAVE15. Goodbye!"
        else:
            return f"We're sorry about your experience. Here's 20% off. Code: SAVE20. Support will call you. Goodbye!"
    
    return "Please rate us from 1 to 5 stars."


def get_order_summary(call_sid: str):
    """Get order summary for confirmation"""
    if call_sid not in conversations or not conversations[call_sid]["order"]:
        return "No items in order yet."
    
    order = conversations[call_sid]["order"]
    total = sum(item['price'] * item['quantity'] for item in order)
    
    summary = "Your order: "
    for item in order:
        summary += f"{item['quantity']} {item['name']}, "
    summary += f"Total: ₹{total}"
    
    return summary
