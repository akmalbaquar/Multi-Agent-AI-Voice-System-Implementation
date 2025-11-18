"""
State Manager
Redis-based session and state management
Handles conversation context, order state, and agent transitions
"""
import logging
import json
from typing import Dict, List, Any, Optional
from redis import asyncio as aioredis
from datetime import datetime, timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages session state and conversation context using Redis
    """
    
    def __init__(self):
        self.redis_client = None
        self._initialized = False
    
    async def _ensure_connection(self):
        """Ensure Redis connection is established"""
        if not self._initialized:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            self._initialized = True
    
    async def create_session(
        self,
        session_id: str,
        call_sid: str,
        customer_id: Optional[str] = None,
        agent_type: str = "customer_order"
    ) -> Dict[str, Any]:
        """
        Create a new session
        
        Args:
            session_id: Unique session identifier
            call_sid: Twilio call SID
            customer_id: Customer UUID
            agent_type: Initial agent type
        
        Returns:
            Session data dict
        """
        await self._ensure_connection()
        
        session_data = {
            "session_id": session_id,
            "call_sid": call_sid,
            "customer_id": customer_id,
            "current_agent": agent_type,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [],
            "order_state": {},
            "context": {},
            "agent_history": [{"agent": agent_type, "timestamp": datetime.utcnow().isoformat()}]
        }
        
        # Store in Redis with TTL
        await self.redis_client.setex(
            f"session:{session_id}",
            settings.REDIS_SESSION_TTL,
            json.dumps(session_data)
        )
        
        logger.info(f"Created session: {session_id}")
        return session_data
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session data or None if not found
        """
        await self._ensure_connection()
        
        data = await self.redis_client.get(f"session:{session_id}")
        
        if data:
            return json.loads(data)
        return None
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]):
        """
        Update session data
        
        Args:
            session_id: Session identifier
            updates: Dict of fields to update
        """
        await self._ensure_connection()
        
        session_data = await self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        # Update fields
        session_data.update(updates)
        
        # Save back to Redis
        await self.redis_client.setex(
            f"session:{session_id}",
            settings.REDIS_SESSION_TTL,
            json.dumps(session_data)
        )
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add message to conversation history
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant)
            content: Message content
            metadata: Optional metadata
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        session_data["messages"].append(message)
        
        await self.update_session(session_id, {"messages": session_data["messages"]})
        logger.debug(f"Added message to session {session_id}: {role}")
    
    async def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history
        
        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages
        
        Returns:
            List of messages
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return []
        
        messages = session_data.get("messages", [])
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    async def update_order_state(self, session_id: str, order_data: Dict[str, Any]):
        """
        Update order state
        
        Args:
            session_id: Session identifier
            order_data: Order data to merge
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        order_state = session_data.get("order_state", {})
        order_state.update(order_data)
        
        await self.update_session(session_id, {"order_state": order_state})
        logger.info(f"Updated order state for session {session_id}")
    
    async def get_order_state(self, session_id: str) -> Dict[str, Any]:
        """Get current order state"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return {}
        
        return session_data.get("order_state", {})
    
    async def set_context(self, session_id: str, key: str, value: Any):
        """
        Set context variable
        
        Args:
            session_id: Session identifier
            key: Context key
            value: Context value
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        context = session_data.get("context", {})
        context[key] = value
        
        await self.update_session(session_id, {"context": context})
    
    async def get_context(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get context variable"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return default
        
        return session_data.get("context", {}).get(key, default)
    
    async def switch_agent(
        self,
        session_id: str,
        new_agent: str,
        reason: Optional[str] = None
    ):
        """
        Switch to a new agent
        
        Args:
            session_id: Session identifier
            new_agent: New agent type
            reason: Reason for switching
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        old_agent = session_data.get("current_agent")
        
        # Add to agent history
        agent_history = session_data.get("agent_history", [])
        agent_history.append({
            "from_agent": old_agent,
            "to_agent": new_agent,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update current agent
        await self.update_session(session_id, {
            "current_agent": new_agent,
            "agent_history": agent_history
        })
        
        logger.info(f"Switched agent: {old_agent} -> {new_agent}")
    
    async def get_current_agent(self, session_id: str) -> str:
        """Get current agent type"""
        session_data = await self.get_session(session_id)
        if not session_data:
            return "customer_order"  # Default
        
        return session_data.get("current_agent", "customer_order")
    
    async def save_metrics(self, session_id: str, metrics: Dict[str, Any]):
        """Save performance metrics"""
        await self._ensure_connection()
        
        metrics_key = f"metrics:{session_id}"
        await self.redis_client.setex(
            metrics_key,
            settings.REDIS_SESSION_TTL,
            json.dumps(metrics)
        )
        
        logger.info(f"Saved metrics for session {session_id}")
    
    async def get_metrics(self, session_id: str) -> Dict[str, Any]:
        """Retrieve metrics"""
        await self._ensure_connection()
        
        data = await self.redis_client.get(f"metrics:{session_id}")
        if data:
            return json.loads(data)
        return {}
    
    async def cache_set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        Set cache value
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        await self._ensure_connection()
        
        ttl = ttl or settings.REDIS_CACHE_TTL
        
        await self.redis_client.setex(
            f"cache:{key}",
            ttl,
            json.dumps(value)
        )
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        await self._ensure_connection()
        
        data = await self.redis_client.get(f"cache:{key}")
        if data:
            return json.loads(data)
        return None
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        await self._ensure_connection()
        
        await self.redis_client.delete(f"session:{session_id}")
        await self.redis_client.delete(f"metrics:{session_id}")
        
        logger.info(f"Deleted session: {session_id}")
    
    async def cleanup_expired_sessions(self):
        """Cleanup expired sessions (handled by Redis TTL)"""
        # Redis automatically handles TTL expiration
        # This method is for manual cleanup if needed
        pass
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self._initialized = False
