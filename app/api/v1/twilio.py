"""
Twilio Voice Integration API
Handles inbound/outbound calls and WebSocket media streaming
"""
import json
import logging
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.call_service import CallService
from app.services.audio_processor import AudioProcessor
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/incoming")
async def handle_incoming_call(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle incoming Twilio voice call
    Creates TwiML response with WebSocket connection
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    to_number = form_data.get("To")
    
    logger.info(f"Incoming call: {call_sid} from {from_number}")
    
    try:
        # Create call session
        call_service = CallService(db)
        session = await call_service.create_call_session(
            call_sid=call_sid,
            from_number=from_number,
            to_number=to_number,
            direction="inbound"
        )
        
        # Generate TwiML response
        response = VoiceResponse()
        
        # Recording consent (TRAI compliance)
        if settings.RECORDING_CONSENT_REQUIRED:
            response.say(
                "This call may be recorded for quality and training purposes.",
                voice="alice",
                language="en-US"
            )
        
        # Connect to WebSocket for media streaming
        connect = Connect()
        stream = Stream(url=f"wss://{settings.TWILIO_WEBHOOK_URL}/api/v1/twilio/media-stream")
        stream.parameter(name="call_sid", value=call_sid)
        stream.parameter(name="session_id", value=str(session.id))
        connect.append(stream)
        response.append(connect)
        
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}", exc_info=True)
        response = VoiceResponse()
        response.say("We're sorry, but we're experiencing technical difficulties. Please try again later.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")


@router.post("/outgoing")
async def initiate_outbound_call(
    to_number: str,
    agent_type: str,
    context: dict = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate outbound call to customer/restaurant/driver
    """
    try:
        call_service = CallService(db)
        call = await call_service.make_outbound_call(
            to_number=to_number,
            agent_type=agent_type,
            context=context or {}
        )
        
        return {
            "status": "success",
            "call_sid": call.sid,
            "message": f"Call initiated to {to_number}"
        }
        
    except Exception as e:
        logger.error(f"Error initiating outbound call: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }


@router.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """
    Handle Twilio media stream WebSocket connection
    Bidirectional audio streaming with real-time processing
    """
    await websocket.accept()
    
    call_sid = None
    session_id = None
    audio_processor = None
    
    try:
        logger.info("WebSocket connection established")
        
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get("event")
            
            if event == "start":
                # Stream started
                call_sid = data["start"]["callSid"]
                custom_params = data["start"].get("customParameters", {})
                session_id = custom_params.get("session_id")
                
                logger.info(f"Media stream started: {call_sid}")
                
                # Initialize audio processor
                audio_processor = AudioProcessor(
                    call_sid=call_sid,
                    session_id=session_id,
                    websocket=websocket
                )
                await audio_processor.start()
                
            elif event == "media":
                # Audio data received from caller
                if audio_processor:
                    payload = data["media"]["payload"]
                    await audio_processor.process_inbound_audio(payload)
                    
            elif event == "stop":
                # Stream stopped
                logger.info(f"Media stream stopped: {call_sid}")
                if audio_processor:
                    await audio_processor.stop()
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {call_sid}")
    except Exception as e:
        logger.error(f"Error in media stream: {e}", exc_info=True)
    finally:
        if audio_processor:
            await audio_processor.cleanup()


@router.post("/status")
async def handle_call_status(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle Twilio call status callback
    Updates call session with final status and metrics
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    call_duration = form_data.get("CallDuration")
    
    logger.info(f"Call status update: {call_sid} - {call_status}")
    
    try:
        call_service = CallService(db)
        await call_service.update_call_status(
            call_sid=call_sid,
            status=call_status,
            duration=int(call_duration) if call_duration else None
        )
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error updating call status: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.post("/recording")
async def handle_recording_status(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle Twilio recording status callback
    Stores recording URL in call session
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    recording_url = form_data.get("RecordingUrl")
    
    logger.info(f"Recording available for call: {call_sid}")
    
    try:
        call_service = CallService(db)
        await call_service.update_recording_url(
            call_sid=call_sid,
            recording_url=recording_url
        )
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error updating recording URL: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
