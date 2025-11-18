"""
Orchestrator Decision Log Viewer
Shows real-time routing decisions during voice calls
"""
import logging
from app.services.ai_handler import conversations
from app.agents.orchestrator_agent import orchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demo_orchestrator_decisions():
    """
    Demonstrate how Orchestrator makes routing decisions
    """
    print("\n" + "="*70)
    print("  🎯 ORCHESTRATOR AGENT DECISION DEMO")
    print("="*70)
    
    # Simulate different scenarios
    scenarios = [
        {
            "user_speech": "I want pizza and burger",
            "state": {"state": "menu", "order_id": None, "order": []},
            "description": "New customer wants to order"
        },
        {
            "user_speech": "Where is my order?",
            "state": {"state": "tracking", "order_id": "ORD123", "order": [{"name": "Pizza"}]},
            "description": "Customer tracking existing order"
        },
        {
            "user_speech": "Food was cold",
            "state": {"state": "tracking", "order_id": "ORD123", "order": [{"name": "Pizza"}]},
            "description": "Customer complaint"
        },
        {
            "user_speech": "3 stars",
            "state": {"state": "feedback", "order_id": "ORD123", "order": [{"name": "Pizza"}]},
            "description": "Customer providing feedback"
        },
        {
            "user_speech": "123 MG Road Bangalore",
            "state": {"state": "address", "order_id": None, "order": [{"name": "Pizza"}]},
            "description": "Customer providing address during order"
        },
        {
            "user_speech": "I need help",
            "state": {"state": "tracking", "order_id": "ORD123", "order": [{"name": "Pizza"}]},
            "description": "Customer requesting support"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─'*70}")
        print(f"SCENARIO {i}: {scenario['description']}")
        print(f"{'─'*70}")
        print(f"User Said: \"{scenario['user_speech']}\"")
        print(f"Current State: {scenario['state']['state']}")
        print(f"Order ID: {scenario['state'].get('order_id', 'None')}")
        
        # Get orchestrator decision
        routing = orchestrator.route_to_agent(
            scenario['user_speech'],
            scenario['state']
        )
        
        print(f"\n🤖 ORCHESTRATOR DECISION:")
        print(f"   ┌─ Route To: {routing['agent'].upper()} AGENT")
        print(f"   ├─ Intent: {routing['intent']}")
        print(f"   ├─ Confidence: {routing['confidence'].upper()}")
        print(f"   └─ Reason: {routing['reason']}")
    
    print("\n" + "="*70)
    print("  ✅ ALL SCENARIOS ANALYZED")
    print("="*70)
    
    print("\n🎯 Key Takeaways:")
    print("   1. Orchestrator decides BEFORE any agent is called")
    print("   2. Routing based on: state > keywords > context")
    print("   3. Single entry point for all voice interactions")
    print("   4. Ensures correct agent handles each request")
    print("\n")

if __name__ == "__main__":
    demo_orchestrator_decisions()
