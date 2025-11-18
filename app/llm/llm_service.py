"""
LLM Service
Handles interactions with Claude Sonnet 4.5 and GPT-4o-mini
Implements function calling and cost tracking
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
from anthropic import Anthropic, AsyncAnthropic
from openai import AsyncOpenAI
import json

from app.core.config import settings
from app.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for LLM interactions with Claude and OpenAI
    Supports function calling, streaming, and cost optimization
    """
    
    def __init__(self):
        # Initialize clients
        self.claude_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Tool registry
        self.tool_registry = ToolRegistry()
        
        # Cost tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        
        # Model selection
        self.primary_model = settings.ANTHROPIC_MODEL
        self.fallback_model = settings.OPENAI_MODEL
        self.use_fallback = False
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate LLM response with function calling support
        
        Args:
            messages: Conversation history
            system_prompt: System instructions for the agent
            tools: Available tools/functions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream response
        
        Returns:
            Response dict with message and tool calls
        """
        try:
            # Try Claude first
            if not self.use_fallback:
                return await self._generate_claude(
                    messages, system_prompt, tools, max_tokens, temperature, stream
                )
            else:
                return await self._generate_openai(
                    messages, system_prompt, tools, max_tokens, temperature, stream
                )
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}", exc_info=True)
            
            # Fallback to OpenAI if Claude fails
            if not self.use_fallback:
                logger.warning("Falling back to OpenAI")
                self.use_fallback = True
                return await self._generate_openai(
                    messages, system_prompt, tools, max_tokens, temperature, stream
                )
            
            raise
    
    async def _generate_claude(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict]],
        max_tokens: int,
        temperature: float,
        stream: bool
    ) -> Dict[str, Any]:
        """Generate response using Claude"""
        
        start_time = asyncio.get_event_loop().time()
        
        # Prepare request
        request_params = {
            "model": self.primary_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": messages,
        }
        
        # Add tools if provided
        if tools:
            request_params["tools"] = tools
        
        # Make API call
        if stream:
            response = await self._stream_claude(request_params)
        else:
            response = await self.claude_client.messages.create(**request_params)
        
        # Calculate latency
        latency = asyncio.get_event_loop().time() - start_time
        
        # Extract response
        result = {
            "message": "",
            "tool_calls": [],
            "stop_reason": response.stop_reason,
            "model": self.primary_model,
            "latency": latency,
            "cost": 0.0
        }
        
        # Process content blocks
        for content in response.content:
            if content.type == "text":
                result["message"] += content.text
            elif content.type == "tool_use":
                result["tool_calls"].append({
                    "id": content.id,
                    "name": content.name,
                    "input": content.input
                })
        
        # Calculate cost
        input_cost = (response.usage.input_tokens / 1_000_000) * 3.0  # $3 per 1M tokens
        output_cost = (response.usage.output_tokens / 1_000_000) * 15.0  # $15 per 1M tokens
        total_cost = input_cost + output_cost
        
        result["cost"] = total_cost
        
        # Update tracking
        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens
        self.total_cost += total_cost
        
        logger.info(f"Claude response generated in {latency:.3f}s, cost: ${total_cost:.4f}")
        
        return result
    
    async def _stream_claude(self, request_params: Dict) -> Any:
        """Stream Claude response"""
        # TODO: Implement streaming
        # For now, use non-streaming
        response = await self.claude_client.messages.create(**request_params)
        return response
    
    async def _generate_openai(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict]],
        max_tokens: int,
        temperature: float,
        stream: bool
    ) -> Dict[str, Any]:
        """Generate response using OpenAI (fallback)"""
        
        start_time = asyncio.get_event_loop().time()
        
        # Prepare messages with system prompt
        openai_messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Prepare request
        request_params = {
            "model": self.fallback_model,
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        # Add tools if provided
        if tools:
            request_params["tools"] = self._convert_tools_to_openai_format(tools)
        
        # Make API call
        response = await self.openai_client.chat.completions.create(**request_params)
        
        # Calculate latency
        latency = asyncio.get_event_loop().time() - start_time
        
        # Extract response
        message = response.choices[0].message
        
        result = {
            "message": message.content or "",
            "tool_calls": [],
            "stop_reason": response.choices[0].finish_reason,
            "model": self.fallback_model,
            "latency": latency,
            "cost": 0.0
        }
        
        # Process tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                result["tool_calls"].append({
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "input": json.loads(tool_call.function.arguments)
                })
        
        # Calculate cost
        input_cost = (response.usage.prompt_tokens / 1_000_000) * 0.15
        output_cost = (response.usage.completion_tokens / 1_000_000) * 0.60
        total_cost = input_cost + output_cost
        
        result["cost"] = total_cost
        
        # Update tracking
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        self.total_cost += total_cost
        
        logger.info(f"OpenAI response generated in {latency:.3f}s, cost: ${total_cost:.4f}")
        
        return result
    
    def _convert_tools_to_openai_format(self, tools: List[Dict]) -> List[Dict]:
        """Convert Claude tool format to OpenAI format"""
        openai_tools = []
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
        return openai_tools
    
    async def execute_tool_calls(
        self,
        tool_calls: List[Dict],
        session_context: Dict
    ) -> List[Dict]:
        """
        Execute tool calls and return results
        
        Args:
            tool_calls: List of tool calls from LLM
            session_context: Current session context
        
        Returns:
            List of tool results
        """
        results = []
        
        for tool_call in tool_calls:
            try:
                logger.info(f"Executing tool: {tool_call['name']}")
                
                # Get tool function
                tool_func = self.tool_registry.get_tool(tool_call['name'])
                
                if not tool_func:
                    raise ValueError(f"Tool not found: {tool_call['name']}")
                
                # Execute tool
                result = await tool_func(
                    **tool_call['input'],
                    context=session_context
                )
                
                results.append({
                    "tool_call_id": tool_call['id'],
                    "name": tool_call['name'],
                    "content": json.dumps(result)
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_call['name']}: {e}", exc_info=True)
                results.append({
                    "tool_call_id": tool_call['id'],
                    "name": tool_call['name'],
                    "content": json.dumps({"error": str(e)})
                })
        
        return results
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        try:
            response = await self.openai_client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}", exc_info=True)
            raise
    
    def get_cost_stats(self) -> Dict[str, Any]:
        """Get cost statistics"""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": self.total_cost,
            "primary_model": self.primary_model,
            "fallback_model": self.fallback_model,
            "using_fallback": self.use_fallback
        }
