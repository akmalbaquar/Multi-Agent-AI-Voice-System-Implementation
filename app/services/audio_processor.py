"""
Audio Processor
Handles real-time audio streaming, STT, TTS, and interruption detection
"""
import asyncio
import logging
import base64
import json
from typing import Optional
from deepgram import Deepgram
from elevenlabs import generate, stream, set_api_key
import websockets

from app.core.config import settings
from app.services.state_manager import StateManager
from app.agents.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

set_api_key(settings.ELEVENLABS_API_KEY)


class AudioProcessor:
    """
    Real-time audio processing with STT/TTS
    Handles bidirectional audio streaming over WebSocket
    """
    
    def __init__(self, call_sid: str, session_id: str, websocket):
        self.call_sid = call_sid
        self.session_id = session_id
        self.websocket = websocket
        
        # Initialize services
        self.deepgram = Deepgram(settings.DEEPGRAM_API_KEY)
        self.state_manager = StateManager()
        self.orchestrator = AgentOrchestrator(session_id)
        
        # Audio buffers
        self.inbound_audio_buffer = bytearray()
        self.silence_duration = 0
        
        # State
        self.is_speaking = False
        self.current_tts_task = None
        self.deepgram_connection = None
        
        # Metrics
        self.start_time = None
        self.total_stt_latency = 0
        self.total_tts_latency = 0
        self.stt_requests = 0
        self.tts_requests = 0
    
    async def start(self):
        """Initialize audio processing"""
        self.start_time = asyncio.get_event_loop().time()
        logger.info(f"Starting audio processor for call: {self.call_sid}")
        
        # Initialize Deepgram streaming STT
        await self._init_deepgram()
        
        # Greet customer
        await self._send_greeting()
    
    async def process_inbound_audio(self, audio_payload: str):
        """
        Process incoming audio from caller
        Args:
            audio_payload: Base64 encoded mulaw audio
        """
        try:
            # Decode audio
            audio_data = base64.b64decode(audio_payload)
            
            # Check for interruption
            if self.is_speaking:
                await self._handle_interruption()
            
            # Send to Deepgram for STT
            if self.deepgram_connection:
                await self.deepgram_connection.send(audio_data)
            
            # Buffer for silence detection
            self.inbound_audio_buffer.extend(audio_data)
            
        except Exception as e:
            logger.error(f"Error processing inbound audio: {e}", exc_info=True)
    
    async def _init_deepgram(self):
        """Initialize Deepgram streaming connection"""
        try:
            self.deepgram_connection = await self.deepgram.transcription.live({
                'model': settings.DEEPGRAM_MODEL,
                'language': settings.DEEPGRAM_LANGUAGE,
                'punctuate': True,
                'interim_results': settings.DEEPGRAM_INTERIM_RESULTS,
                'vad_events': True,
                'smart_format': True,
            })
            
            # Handle transcription results
            self.deepgram_connection.registerHandler(
                self.deepgram_connection.event.TRANSCRIPT_RECEIVED,
                self._handle_transcript
            )
            
            logger.info("Deepgram connection established")
            
        except Exception as e:
            logger.error(f"Error initializing Deepgram: {e}", exc_info=True)
    
    async def _handle_transcript(self, transcript_data):
        """
        Handle transcription results from Deepgram
        """
        try:
            transcript = transcript_data.get('channel', {}).get('alternatives', [{}])[0]
            text = transcript.get('transcript', '').strip()
            is_final = transcript_data.get('is_final', False)
            
            if not text:
                return
            
            if is_final:
                logger.info(f"User said: {text}")
                
                # Track STT latency
                self.stt_requests += 1
                
                # Save to state
                await self.state_manager.add_message(
                    self.session_id,
                    role="user",
                    content=text
                )
                
                # Process with agent
                await self._process_user_input(text)
            else:
                # Interim result - for UI feedback
                logger.debug(f"Interim: {text}")
                
        except Exception as e:
            logger.error(f"Error handling transcript: {e}", exc_info=True)
    
    async def _process_user_input(self, text: str):
        """
        Process user input with agent orchestrator
        """
        try:
            # Get agent response
            response = await self.orchestrator.process_input(text)
            
            # Generate and stream TTS
            await self._speak(response['message'])
            
            # Check for agent transfer
            if response.get('transfer_to'):
                await self.orchestrator.transfer_agent(response['transfer_to'])
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}", exc_info=True)
            await self._speak("I'm sorry, I didn't catch that. Could you please repeat?")
    
    async def _speak(self, text: str):
        """
        Generate speech and stream to caller
        Args:
            text: Text to convert to speech
        """
        try:
            self.is_speaking = True
            tts_start = asyncio.get_event_loop().time()
            
            logger.info(f"AI speaking: {text}")
            
            # Save to state
            await self.state_manager.add_message(
                self.session_id,
                role="assistant",
                content=text
            )
            
            # Use cost-optimized TTS for simple confirmations
            if self._is_simple_confirmation(text) and settings.USE_CHEAPER_TTS_FOR_CONFIRMATIONS:
                await self._speak_deepgram(text)
            else:
                await self._speak_elevenlabs(text)
            
            # Track TTS latency
            tts_latency = asyncio.get_event_loop().time() - tts_start
            self.tts_requests += 1
            self.total_tts_latency += tts_latency
            
            logger.info(f"TTS latency: {tts_latency:.3f}s")
            
            self.is_speaking = False
            
        except Exception as e:
            logger.error(f"Error in TTS: {e}", exc_info=True)
            self.is_speaking = False
    
    async def _speak_elevenlabs(self, text: str):
        """Stream audio using ElevenLabs"""
        try:
            # Generate streaming audio
            audio_stream = generate(
                text=text,
                voice=settings.ELEVENLABS_VOICE_ID,
                model=settings.ELEVENLABS_MODEL,
                stream=True
            )
            
            # Stream to Twilio
            for chunk in audio_stream:
                if not self.is_speaking:  # Interrupted
                    break
                
                # Encode for Twilio (mulaw)
                encoded_chunk = base64.b64encode(chunk).decode('utf-8')
                
                # Send via WebSocket
                await self.websocket.send_text(json.dumps({
                    "event": "media",
                    "media": {
                        "payload": encoded_chunk
                    }
                }))
                
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}", exc_info=True)
    
    async def _speak_deepgram(self, text: str):
        """Stream audio using Deepgram Aura (cheaper alternative)"""
        try:
            # Deepgram TTS implementation
            # TODO: Implement Deepgram Aura TTS
            # For now, fallback to ElevenLabs
            await self._speak_elevenlabs(text)
            
        except Exception as e:
            logger.error(f"Deepgram TTS error: {e}", exc_info=True)
    
    async def _handle_interruption(self):
        """
        Handle user interrupting AI speech
        Implements barge-in functionality
        """
        logger.info("User interruption detected - stopping speech")
        
        self.is_speaking = False
        
        # Cancel current TTS task
        if self.current_tts_task:
            self.current_tts_task.cancel()
        
        # Send mark clear to Twilio to stop audio
        await self.websocket.send_text(json.dumps({
            "event": "clear",
            "streamSid": self.call_sid
        }))
    
    async def _send_greeting(self):
        """Send initial greeting"""
        # Get appropriate greeting from agent
        greeting = await self.orchestrator.get_greeting()
        await self._speak(greeting)
    
    def _is_simple_confirmation(self, text: str) -> bool:
        """Check if text is a simple confirmation"""
        simple_phrases = [
            "okay", "got it", "understood", "yes", "no",
            "sure", "alright", "thank you"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in simple_phrases) and len(text) < 20
    
    async def stop(self):
        """Stop audio processing"""
        logger.info(f"Stopping audio processor for call: {self.call_sid}")
        
        # Close Deepgram connection
        if self.deepgram_connection:
            await self.deepgram_connection.finish()
        
        # Save metrics
        await self._save_metrics()
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.stop()
        
        # Clear buffers
        self.inbound_audio_buffer.clear()
    
    async def _save_metrics(self):
        """Save performance metrics"""
        metrics = {
            'stt_requests': self.stt_requests,
            'tts_requests': self.tts_requests,
            'avg_stt_latency': self.total_stt_latency / self.stt_requests if self.stt_requests > 0 else 0,
            'avg_tts_latency': self.total_tts_latency / self.tts_requests if self.tts_requests > 0 else 0,
            'total_duration': asyncio.get_event_loop().time() - self.start_time
        }
        
        await self.state_manager.save_metrics(self.session_id, metrics)
        logger.info(f"Audio metrics saved: {metrics}")
