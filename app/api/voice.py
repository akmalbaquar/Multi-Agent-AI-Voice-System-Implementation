"""
Voice API - Twilio Webhook Handler
"""
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import logging
from app.services.ai_handler import process_order_with_ai, get_order_summary

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/incoming")
async def incoming_call(request: Request):
    """Handle incoming voice call from Twilio"""
    logger.info("📞 Incoming call received!")
    
    # Get form data
    form_data = await request.form()
    caller = form_data.get('From', 'Unknown')
    call_sid = form_data.get('CallSid', 'Unknown')
    
    logger.info(f"Caller: {caller}, CallSid: {call_sid}")
    
    # TwiML Voice Response with menu
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello! Welcome to Food Delivery AI. I can help you order delicious food today!</Say>
    <Say voice="alice">We have Margherita Pizza for 299 rupees, Chicken Burger for 199 rupees, French Fries for 99 rupees, Pasta Alfredo for 279 rupees, and Club Sandwich for 179 rupees.</Say>
    <Gather input="speech" action="/api/voice/process" method="POST" speechTimeout="auto">
        <Say voice="alice">What would you like to order?</Say>
    </Gather>
    <Say voice="alice">Sorry, I didn't hear anything. Goodbye!</Say>
</Response>
"""
    return PlainTextResponse(twiml, media_type="application/xml")


@router.get("/incoming")
async def incoming_test():
    """Test endpoint to verify webhook is reachable"""
    return {"message": "Twilio webhook reachable!", "status": "ok"}


@router.post("/process")
async def process_speech(request: Request):
    """Process speech input from caller"""
    form_data = await request.form()
    
    speech_result = form_data.get('SpeechResult', '')
    call_sid = form_data.get('CallSid', 'Unknown')
    
    logger.info(f"CallSid: {call_sid}, User said: {speech_result}")
    
    # Process with AI
    try:
        ai_response = process_order_with_ai(call_sid, speech_result)
        logger.info(f"AI Response: {ai_response}")
    except Exception as e:
        logger.error(f"Error processing order: {e}", exc_info=True)
        ai_response = "I understood you want to order. Let me process that for you."
    
    # TwiML response with AI
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{ai_response}</Say>
    <Gather input="speech" action="/api/voice/process" method="POST" speechTimeout="auto">
        <Say voice="alice">Anything else?</Say>
    </Gather>
    <Say voice="alice">Great! Your order total is being calculated. Thank you for calling!</Say>
</Response>
"""
    return PlainTextResponse(twiml, media_type="application/xml")


@router.post("/status")
async def call_status(request: Request):
    """Handle call status callbacks"""
    form_data = await request.form()
    
    call_sid = form_data.get('CallSid', 'Unknown')
    call_status = form_data.get('CallStatus', 'Unknown')
    
    logger.info(f"Call status update - CallSid: {call_sid}, Status: {call_status}")
    
    return {"status": "received"}
