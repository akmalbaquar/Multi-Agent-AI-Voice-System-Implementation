"""
Complete Multi-Agent System Architecture Diagram
Shows how Orchestrator routes to specialized agents
"""

ARCHITECTURE = """
╔══════════════════════════════════════════════════════════════════════╗
║                    INCOMING VOICE CALL (Twilio)                      ║
╚══════════════════════════════════════════════════════════════════════╝
                                  ↓
                        Speech-to-Text (STT)
                                  ↓
╔══════════════════════════════════════════════════════════════════════╗
║                     🎯 ORCHESTRATOR AGENT                            ║
║                  (Master Decision Maker)                             ║
║                                                                      ║
║  Analyzes:                                                           ║
║  • User speech keywords                                              ║
║  • Current conversation state                                        ║
║  • Order existence                                                   ║
║  • Intent confidence                                                 ║
║                                                                      ║
║  Decision Logic:                                                     ║
║  1. If state=menu/ordering/address/payment → ORDER AGENT            ║
║  2. If keywords="support/problem/issue" → SUPPORT AGENT             ║
║  3. If keywords="track/where/status" + order_exists → TRACKING      ║
║  4. If keywords="rate/feedback/star" → FEEDBACK AGENT               ║
║  5. Else → ORDER AGENT (default)                                    ║
╚══════════════════════════════════════════════════════════════════════╝
                                  ↓
                    ┌─────────────┼─────────────┐
                    ↓             ↓             ↓
        ┌───────────────┐ ┌─────────────┐ ┌──────────────┐
        │  📦 ORDER     │ │ 📍 TRACKING  │ │ 🆘 SUPPORT   │
        │     AGENT     │ │    AGENT     │ │    AGENT     │
        └───────────────┘ └─────────────┘ └──────────────┘
                ↓                 ↓                ↓
        ┌───────────────┐ ┌─────────────┐ ┌──────────────┐
        │ 🍽️ RESTAURANT │ │ 🚗 DRIVER    │ │ ⭐ FEEDBACK  │
        │     AGENT     │ │    AGENT     │ │    AGENT     │
        │  (Auto-notify)│ │ (Auto-assign)│ │              │
        └───────────────┘ └─────────────┘ └──────────────┘
                                  ↓
                        Response (TTS)
                                  ↓
                        Back to Customer

═══════════════════════════════════════════════════════════════════════

EXAMPLE FLOW:

Call 1: New Order
├─ User: "I want pizza"
├─ Orchestrator: state=menu → Route to ORDER AGENT
├─ Order Agent: Add pizza → "Anything else?"
├─ User: "That's all"
├─ Orchestrator: state=ordering → Route to ORDER AGENT
├─ Order Agent: Move to address → "Please tell address"
├─ User: "123 MG Road"
├─ Orchestrator: state=address → Route to ORDER AGENT
├─ Order Agent: Move to payment → "Cash or online?"
├─ User: "Cash on delivery"
├─ Orchestrator: state=payment → Route to ORDER AGENT
├─ Order Agent: Create order → Auto-trigger RESTAURANT + DRIVER
└─ Response: "Order ORD123 confirmed. 30 min delivery"

Call 2: Track Order
├─ User: "Where is my order?"
├─ Orchestrator: keywords="where" + order_exists → Route to TRACKING AGENT
├─ Tracking Agent: Get order status
└─ Response: "Order on the way, driver arriving in 20 mins"

Call 3: Complaint
├─ User: "Food was cold"
├─ Orchestrator: keywords="cold" → Route to SUPPORT AGENT
├─ Support Agent: Process refund → Move to feedback
├─ User: "2 stars"
├─ Orchestrator: state=feedback + number → Route to FEEDBACK AGENT
├─ Feedback Agent: Process rating
└─ Response: "20% off code SAVE20"

═══════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(ARCHITECTURE)
