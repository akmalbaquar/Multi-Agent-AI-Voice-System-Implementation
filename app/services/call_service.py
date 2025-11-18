"""
Call Service
Manages call sessions and Twilio integration
"""
import logging
from datetime import datetime
from typing import Optional
from twilio.rest import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import CallSession, Customer, AgentType, CallDirection
from app.core.config import settings

logger = logging.getLogger(__name__)


class CallService:
    """Service for managing voice calls"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.twilio_client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
    
    async def create_call_session(
        self,
        call_sid: str,
        from_number: str,
        to_number: str,
        direction: str,
        initial_agent: AgentType = AgentType.CUSTOMER_ORDER
    ) -> CallSession:
        """Create a new call session"""
        
        # Look up customer by phone number
        customer = await self._get_customer_by_phone(from_number if direction == "inbound" else to_number)
        
        session = CallSession(
            call_sid=call_sid,
            customer_id=customer.id if customer else None,
            direction=CallDirection(direction),
            from_number=from_number,
            to_number=to_number,
            initial_agent=initial_agent,
            started_at=datetime.utcnow()
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        logger.info(f"Created call session: {session.id} for call {call_sid}")
        return session
    
    async def make_outbound_call(
        self,
        to_number: str,
        agent_type: str,
        context: dict
    ):
        """Initiate outbound call"""
        
        # Check DND registry (TRAI compliance)
        if settings.TRAI_DND_CHECK_ENABLED:
            customer = await self._get_customer_by_phone(to_number)
            if customer and customer.dnd_registered:
                logger.warning(f"Cannot call DND registered number: {to_number}")
                raise ValueError("Customer is registered on DND list")
        
        # Check calling hours (TRAI compliance)
        if not self._is_within_calling_hours():
            logger.warning("Attempted call outside allowed hours")
            raise ValueError("Calls only allowed between 9 AM - 9 PM IST")
        
        # Make Twilio call
        call = self.twilio_client.calls.create(
            to=to_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=f"{settings.TWILIO_WEBHOOK_URL}/api/v1/twilio/incoming",
            status_callback=f"{settings.TWILIO_STATUS_CALLBACK_URL}",
            status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
            machine_detection="Enable",
            machine_detection_timeout=5
        )
        
        # Create call session
        await self.create_call_session(
            call_sid=call.sid,
            from_number=settings.TWILIO_PHONE_NUMBER,
            to_number=to_number,
            direction="outbound",
            initial_agent=AgentType(agent_type)
        )
        
        logger.info(f"Initiated outbound call: {call.sid} to {to_number}")
        return call
    
    async def update_call_status(
        self,
        call_sid: str,
        status: str,
        duration: Optional[int] = None
    ):
        """Update call session status"""
        
        result = await self.db.execute(
            select(CallSession).where(CallSession.call_sid == call_sid)
        )
        session = result.scalars().first()
        
        if session:
            if status in ["completed", "failed", "busy", "no-answer"]:
                session.ended_at = datetime.utcnow()
            
            if duration:
                session.duration = duration
                # Calculate Twilio cost
                session.cost_twilio = duration / 60 * (
                    0.0085 if session.direction == CallDirection.INBOUND else 0.0140
                )
            
            await self.db.commit()
            logger.info(f"Updated call status: {call_sid} - {status}")
    
    async def update_recording_url(self, call_sid: str, recording_url: str):
        """Update recording URL for call session"""
        
        result = await self.db.execute(
            select(CallSession).where(CallSession.call_sid == call_sid)
        )
        session = result.scalars().first()
        
        if session:
            session.recording_url = recording_url
            await self.db.commit()
            logger.info(f"Updated recording URL for call: {call_sid}")
    
    async def _get_customer_by_phone(self, phone_number: str) -> Optional[Customer]:
        """Get customer by phone number"""
        result = await self.db.execute(
            select(Customer).where(Customer.phone_number == phone_number)
        )
        return result.scalars().first()
    
    def _is_within_calling_hours(self) -> bool:
        """Check if current time is within allowed calling hours"""
        from datetime import datetime
        import pytz
        
        tz = pytz.timezone(settings.TRAI_TIMEZONE)
        now = datetime.now(tz)
        hour = now.hour
        
        return settings.TRAI_CALLING_START_HOUR <= hour < settings.TRAI_CALLING_END_HOUR
