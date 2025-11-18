"""
Base Agent Class
Foundation for all specialized agents
"""
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from app.llm.llm_service import LLMService
from app.services.state_manager import StateManager
from app.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI agents
    Provides common functionality for conversation management,
    tool execution, and state handling
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.llm_service = LLMService()
        self.state_manager = StateManager()
        self.tool_registry = ToolRegistry()
        
        # Agent metadata
        self.agent_type = self.get_agent_type()
        self.agent_name = self.get_agent_name()
        
        # Conversation state
        self.max_context_messages = 20
    
    @abstractmethod
    def get_agent_type(self) -> str:
        """Return agent type identifier"""
        pass
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """Return human-readable agent name"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this agent"""
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[Dict]:
        """Return list of available tools for this agent"""
        pass
    
    def should_transfer(self, conversation_context: Dict) -> Optional[Dict]:
        """
        Determine if conversation should be transferred to another agent
        
        Returns:
            Dict with transfer_to agent type and reason, or None
        """
        return None
    
    async def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and generate response
        
        Args:
            user_input: User's spoken input (from STT)
        
        Returns:
            Dict containing response message and any actions
        """
        try:
            # Get conversation history
            messages = await self._get_conversation_history()
            
            # Add user message
            messages.append({"role": "user", "content": user_input})
            
            # Get system prompt and tools
            system_prompt = self.get_system_prompt()
            tools = self.get_available_tools()
            
            # Generate LLM response
            llm_response = await self.llm_service.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                tools=tools,
                temperature=0.7
            )
            
            # Execute tool calls if any
            tool_results = []
            if llm_response.get("tool_calls"):
                context = await self._get_session_context()
                tool_results = await self.llm_service.execute_tool_calls(
                    llm_response["tool_calls"],
                    context
                )
                
                # If tools were called, get final response
                if tool_results:
                    messages.append({
                        "role": "assistant",
                        "content": llm_response["message"],
                        "tool_calls": llm_response["tool_calls"]
                    })
                    
                    # Add tool results
                    for result in tool_results:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": result["tool_call_id"],
                            "name": result["name"],
                            "content": result["content"]
                        })
                    
                    # Get final response after tool execution
                    llm_response = await self.llm_service.generate_response(
                        messages=messages,
                        system_prompt=system_prompt,
                        tools=tools,
                        temperature=0.7
                    )
            
            # Check for transfer
            transfer_decision = self.should_transfer(
                {"messages": messages, "last_response": llm_response}
            )
            
            # Build response
            response = {
                "message": llm_response["message"],
                "agent": self.agent_type,
                "tool_calls": llm_response.get("tool_calls", []),
                "tool_results": tool_results,
                "transfer_to": transfer_decision.get("transfer_to") if transfer_decision else None,
                "transfer_reason": transfer_decision.get("reason") if transfer_decision else None,
                "cost": llm_response.get("cost", 0.0),
                "latency": llm_response.get("latency", 0.0)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing input in {self.agent_type}: {e}", exc_info=True)
            return {
                "message": "I apologize, but I'm having trouble processing that. Could you please repeat?",
                "agent": self.agent_type,
                "error": str(e)
            }
    
    async def get_greeting(self) -> str:
        """
        Get initial greeting message
        Override in subclasses for custom greetings
        """
        return f"Hello! I'm your {self.agent_name}. How can I help you today?"
    
    async def _get_conversation_history(self) -> List[Dict[str, str]]:
        """Get formatted conversation history for LLM"""
        messages = await self.state_manager.get_messages(
            self.session_id,
            limit=self.max_context_messages
        )
        
        # Format for LLM
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted
    
    async def _get_session_context(self) -> Dict[str, Any]:
        """Get current session context"""
        session = await self.state_manager.get_session(self.session_id)
        if not session:
            return {}
        
        return {
            "session_id": self.session_id,
            "customer_id": session.get("customer_id"),
            "order_state": session.get("order_state", {}),
            "context": session.get("context", {}),
            "current_agent": session.get("current_agent")
        }
    
    def _format_tool_for_llm(self, tool_name: str, tool_func: callable) -> Dict:
        """
        Format tool definition for LLM function calling
        Override if using different LLM format
        """
        # This is Claude's format
        # TODO: Extract from tool function's docstring and type hints
        return {
            "name": tool_name,
            "description": tool_func.__doc__ or f"Execute {tool_name}",
            "input_schema": {
                "type": "object",
                "properties": {},  # TODO: Extract from function signature
                "required": []
            }
        }


# TODO: Implement specialized agents:
# - CustomerOrderAgent
# - RestaurantCoordinationAgent
# - DriverAssignmentAgent
# - DeliveryTrackingAgent
# - CustomerSupportAgent
# - PostDeliveryAgent
