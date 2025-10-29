"""
Conversation Manager - Handles continuous vocal conversation with automatic VAD.

This module manages a continuous conversation loop where the user speaks,
the system automatically detects speech end via VAD, processes the question,
and responds vocally. The conversation continues until the user stops it.
"""

import logging
import queue
import threading
import time
from collections import deque
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
import soundfile as sf
import torch

from .utils import Config


class ConversationManager:
    """Manages continuous vocal conversation with automatic VAD."""
    
    def __init__(self, config: Config, orchestrator):
        """
        Initialize conversation manager.
        
        Args:
            config: Configuration instance
            orchestrator: VocalTutorOrchestrator instance
        """
        self.config = config
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)
        
        # Audio parameters
        self.sample_rate = config.get('asr.sample_rate', 16000)
        self.chunk_duration = 0.5  # 500ms chunks
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # VAD parameters
        self.vad_threshold = config.get('conversation.vad_threshold', 0.5)
        self.speech_pad_ms = config.get('conversation.speech_pad_ms', 300)
        self.min_speech_duration_ms = config.get('conversation.min_speech_duration_ms', 500)
        self.min_silence_duration_ms = config.get('conversation.min_silence_duration_ms', 800)
        
        # Conversation state
        self.is_running = False
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.speech_buffer = deque(maxlen=100)  # Keep last 50 seconds
        
        # Results queue for UI updates
        self.results_queue = queue.Queue()
        self.latest_transcript = ""
        self.latest_response = ""
        self.latest_audio_path = ""
        self.status_message = ""
        
        # Callbacks
        self.on_transcript: Optional[Callable[[str], None]] = None
        self.on_response: Optional[Callable[[str, str], None]] = None  # (text, audio_path)
        self.on_status: Optional[Callable[[str], None]] = None
        
        # Initialize VAD
        self._init_vad()
        
        self.logger.info("ConversationManager initialized")
    
    def _init_vad(self) -> None:
        """Initialize Silero VAD model."""
        try:
            self.logger.info("Loading Silero VAD for conversation...")
            
            # Load Silero VAD
            model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            
            self.vad_model = model
            self.vad_model.eval()
            
            # Get VAD utilities
            (self.get_speech_timestamps,
             _,  # save_audio
             _,  # read_audio
             _,  # VADIterator
             self.collect_chunks) = utils
            
            self.logger.info("✅ VAD loaded for conversation")
            
        except Exception as e:
            self.logger.error(f"Error loading VAD: {e}")
            self.vad_model = None
    
    def _detect_speech_in_chunk(self, audio_chunk: np.ndarray) -> float:
        """
        Detect speech probability in audio chunk.
        
        Args:
            audio_chunk: Audio data (16kHz, mono)
            
        Returns:
            Speech probability (0-1)
        """
        if self.vad_model is None:
            return 0.5  # Fallback if VAD not available
        
        try:
            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio_chunk).float()
            
            # Get speech probability
            with torch.no_grad():
                speech_prob = self.vad_model(audio_tensor, self.sample_rate).item()
            
            return speech_prob
            
        except Exception as e:
            self.logger.warning(f"VAD detection error: {e}")
            return 0.5
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream."""
        if status:
            self.logger.warning(f"Audio stream status: {status}")
        
        # Put audio chunk in queue
        self.audio_queue.put(indata.copy())
    
    def _process_audio_loop(self):
        """Main loop for processing audio chunks with VAD."""
        self.logger.info("Starting audio processing loop...")
        
        speech_chunks = []
        is_speaking = False
        silence_duration = 0
        speech_duration = 0
        
        while self.is_running:
            try:
                # Get audio chunk from queue (timeout to check is_running)
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Convert to mono if stereo
                if len(audio_chunk.shape) > 1:
                    audio_chunk = audio_chunk.mean(axis=1)
                
                # Detect speech
                speech_prob = self._detect_speech_in_chunk(audio_chunk)
                
                # State machine for speech detection
                if speech_prob > self.vad_threshold:
                    # Speech detected
                    if not is_speaking:
                        self.logger.debug("🗣️ Speech started")
                        if self.on_status:
                            self.on_status("🗣️ Parole détectée...")
                        is_speaking = True
                        speech_duration = 0
                        silence_duration = 0
                    
                    speech_chunks.append(audio_chunk)
                    speech_duration += self.chunk_duration * 1000  # ms
                    silence_duration = 0
                    
                else:
                    # Silence detected
                    if is_speaking:
                        silence_duration += self.chunk_duration * 1000  # ms
                        speech_chunks.append(audio_chunk)  # Keep some silence
                        
                        # Check if enough silence to consider speech ended
                        if (silence_duration >= self.min_silence_duration_ms and
                            speech_duration >= self.min_speech_duration_ms):
                            
                            self.logger.info(f"🛑 Speech ended (duration: {speech_duration:.0f}ms)")
                            if self.on_status:
                                self.on_status("⏳ Traitement en cours...")
                            
                            # Process the speech
                            self._process_speech(speech_chunks)
                            
                            # Reset
                            speech_chunks = []
                            is_speaking = False
                            silence_duration = 0
                            speech_duration = 0
                
            except Exception as e:
                self.logger.error(f"Error in audio processing loop: {e}", exc_info=True)
        
        self.logger.info("Audio processing loop stopped")
    
    def _process_speech(self, speech_chunks: list):
        """
        Process detected speech.
        
        Args:
            speech_chunks: List of audio chunks
        """
        try:
            # Concatenate chunks
            audio_data = np.concatenate(speech_chunks)
            
            # Save to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
                sf.write(tmp_path, audio_data, self.sample_rate)
            
            self.logger.info(f"Processing speech from {tmp_path}")
            
            # Process through orchestrator
            results = self.orchestrator.process_audio_file(tmp_path)
            
            # Clean up temp file
            import os
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            
            # Handle results
            if results.get('success'):
                transcript = results.get('transcript', '')
                response = results.get('response', '')
                audio_output = results.get('audio_output')
                
                self.logger.info(f"✅ Transcript: {transcript[:50]}...")
                
                # Callbacks
                if self.on_transcript:
                    self.on_transcript(transcript)
                
                if self.on_response:
                    self.on_response(response, audio_output)
                
                # Store latest results
                self.latest_transcript = transcript
                self.latest_response = response
                self.latest_audio_path = audio_output or ""
                
                # Put results in queue
                self.results_queue.put({
                    'type': 'result',
                    'transcript': transcript,
                    'response': response,
                    'audio_path': audio_output
                })
                
                # Play audio response
                if audio_output and Path(audio_output).exists():
                    self._play_audio_file(audio_output)
                
                if self.on_status:
                    self.on_status("✅ Réponse générée. Vous pouvez continuer...")
                
            else:
                error = results.get('error', 'Erreur inconnue')
                self.logger.error(f"Processing error: {error}")
                if self.on_status:
                    self.on_status(f"❌ Erreur: {error}")
        
        except Exception as e:
            self.logger.error(f"Error processing speech: {e}", exc_info=True)
            if self.on_status:
                self.on_status(f"❌ Erreur: {str(e)}")
    
    def _play_audio_file(self, audio_path: str):
        """
        Play audio file.
        
        Args:
            audio_path: Path to audio file
        """
        try:
            self.logger.info(f"Playing audio: {audio_path}")
            
            # Load audio
            audio_data, sample_rate = sf.read(audio_path)
            
            # Play
            sd.play(audio_data, sample_rate)
            sd.wait()  # Wait until audio is finished
            
            self.logger.info("Audio playback finished")
            
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
    
    def start_conversation(self):
        """Start continuous conversation mode."""
        if self.is_running:
            self.logger.warning("Conversation already running")
            return
        
        self.logger.info("🎤 Starting conversation mode...")
        
        self.is_running = True
        
        # Start audio stream
        try:
            self.audio_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self._audio_callback,
                blocksize=self.chunk_size
            )
            self.audio_stream.start()
            self.logger.info("✅ Audio stream started")
            
        except Exception as e:
            self.logger.error(f"Error starting audio stream: {e}")
            self.is_running = False
            raise
        
        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_audio_loop,
            daemon=True
        )
        self.processing_thread.start()
        
        if self.on_status:
            self.on_status("🎤 Conversation démarrée. Parlez naturellement!")
        
        self.logger.info("✅ Conversation mode active")
    
    def stop_conversation(self):
        """Stop continuous conversation mode."""
        if not self.is_running:
            self.logger.warning("Conversation not running")
            return
        
        self.logger.info("🛑 Stopping conversation mode...")
        
        self.is_running = False
        
        # Stop audio stream
        if hasattr(self, 'audio_stream'):
            self.audio_stream.stop()
            self.audio_stream.close()
            self.logger.info("Audio stream stopped")
        
        # Wait for processing thread
        if hasattr(self, 'processing_thread') and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        if self.on_status:
            self.on_status("✅ Conversation terminée")
        
        self.logger.info("✅ Conversation mode stopped")
    
    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self.is_running
    
    def get_latest_results(self) -> dict:
        """
        Get latest conversation results (for UI polling).
        
        Returns:
            Dictionary with latest transcript, response, and audio path
        """
        return {
            'transcript': self.latest_transcript,
            'response': self.latest_response,
            'audio_path': self.latest_audio_path,
            'status': self.status_message,
            'is_active': self.is_running
        }
    
    def poll_results(self) -> Optional[dict]:
        """
        Poll for new results (non-blocking).
        
        Returns:
            Latest result from queue or None
        """
        try:
            return self.results_queue.get_nowait()
        except queue.Empty:
            return None
