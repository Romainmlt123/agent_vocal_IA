"""
ASR Module - Automatic Speech Recognition for Agent Vocal IA.

This module handles speech recognition using Faster-Whisper with Silero VAD
for voice activity detection.
"""

import argparse
import logging
import time
from pathlib import Path
from typing import Generator, Optional, Union

import numpy as np
import soundfile as sf
import torch
from faster_whisper import WhisperModel

from .utils import Config, get_config, get_device, setup_logging


class ASR:
    """Automatic Speech Recognition using Faster-Whisper and Silero VAD."""
    
    def __init__(self, config: Config):
        """
        Initialize ASR system.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get ASR parameters from config
        self.model_name = config.get('asr.model_name', 'small')
        self.language = config.get('asr.language', 'fr')
        self.device = config.get('asr.device', 'cuda')
        self.compute_type = config.get('asr.compute_type', 'float16')
        self.vad_enabled = config.get('asr.vad_enabled', True)
        self.sample_rate = config.get('asr.sample_rate', 16000)
        
        # Fallback to CPU if CUDA not available
        if self.device == 'cuda' and not torch.cuda.is_available():
            self.logger.warning("CUDA not available, falling back to CPU")
            self.device = 'cpu'
            self.compute_type = 'int8'
        
        # Initialize Whisper model
        self.logger.info(f"Loading Whisper model: {self.model_name}")
        self.logger.info(f"Device: {self.device}, Compute type: {self.compute_type}")
        
        try:
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
                download_root="models/whisper"
            )
            self.logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {e}")
            raise
        
        # Initialize VAD if enabled
        self.vad_model = None
        if self.vad_enabled:
            self._init_vad()
    
    def _init_vad(self) -> None:
        """Initialize Silero VAD model."""
        try:
            self.logger.info("Loading Silero VAD model...")
            self.vad_model, vad_utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.vad_model.eval()
            
            # Get VAD utilities
            (self.get_speech_timestamps,
             self.save_audio,
             self.read_audio,
             self.VADIterator,
             self.collect_chunks) = vad_utils
            
            self.logger.info("✅ VAD model loaded successfully")
        except Exception as e:
            self.logger.warning(f"Could not load VAD model: {e}")
            self.vad_enabled = False
            self.vad_model = None
    
    def detect_speech(self, audio: np.ndarray, sample_rate: int = 16000) -> bool:
        """
        Detect if audio contains speech using VAD.
        
        Args:
            audio: Audio array
            sample_rate: Sample rate of audio
            
        Returns:
            True if speech detected
        """
        if not self.vad_enabled or self.vad_model is None:
            return True  # Assume speech if VAD not available
        
        try:
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio).float()
            
            # Get speech timestamps
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.vad_model,
                sampling_rate=sample_rate,
                threshold=self.config.get('asr.vad_threshold', 0.5),
                min_silence_duration_ms=self.config.get('asr.min_silence_duration_ms', 300),
                speech_pad_ms=self.config.get('asr.speech_pad_ms', 30)
            )
            
            return len(speech_timestamps) > 0
        except Exception as e:
            self.logger.error(f"Error in VAD: {e}")
            return True  # Assume speech on error
    
    def transcribe_file(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> str:
        """
        Transcribe audio from file.
        
        Args:
            audio_path: Path to audio file
            language: Optional language override
            task: Task type ('transcribe' or 'translate')
            
        Returns:
            Transcribed text
        """
        self.logger.info(f"Transcribing file: {audio_path}")
        start_time = time.time()
        
        # Read audio file
        try:
            audio, sr = sf.read(audio_path)
            
            # Convert stereo to mono if needed
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)
            
            # Resample if needed (Whisper expects 16kHz)
            if sr != self.sample_rate:
                self.logger.info(f"Resampling from {sr}Hz to {self.sample_rate}Hz")
                from scipy import signal
                num_samples = int(len(audio) * self.sample_rate / sr)
                audio = signal.resample(audio, num_samples)
        except Exception as e:
            self.logger.error(f"Error reading audio file: {e}")
            raise
        
        # Check for speech using VAD
        if self.vad_enabled and not self.detect_speech(audio, self.sample_rate):
            self.logger.warning("No speech detected in audio")
            return ""
        
        # Transcribe
        lang = language or self.language
        segments, info = self.model.transcribe(
            audio,
            language=lang,
            task=task,
            vad_filter=self.vad_enabled,
            vad_parameters={
                'threshold': self.config.get('asr.vad_threshold', 0.5),
                'min_silence_duration_ms': self.config.get('asr.min_silence_duration_ms', 300),
            } if self.vad_enabled else None
        )
        
        # Combine segments
        text = " ".join([segment.text for segment in segments]).strip()
        
        elapsed = time.time() - start_time
        self.logger.info(f"Transcription completed in {elapsed:.2f}s")
        self.logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
        
        return text
    
    def transcribe_array(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio from numpy array.
        
        Args:
            audio: Audio array
            sample_rate: Sample rate of audio
            language: Optional language override
            
        Returns:
            Transcribed text
        """
        self.logger.debug(f"Transcribing audio array: shape {audio.shape}, sr {sample_rate}")
        
        # Resample if needed
        if sample_rate != self.sample_rate:
            from scipy import signal
            num_samples = int(len(audio) * self.sample_rate / sample_rate)
            audio = signal.resample(audio, num_samples)
            sample_rate = self.sample_rate
        
        # Check for speech
        if self.vad_enabled and not self.detect_speech(audio, sample_rate):
            self.logger.debug("No speech detected")
            return ""
        
        # Transcribe
        lang = language or self.language
        segments, info = self.model.transcribe(
            audio,
            language=lang,
            vad_filter=self.vad_enabled
        )
        
        text = " ".join([segment.text for segment in segments]).strip()
        return text
    
    def transcribe_streaming(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Transcribe audio with streaming output (segment by segment).
        
        Args:
            audio_path: Path to audio file
            language: Optional language override
            
        Yields:
            Text segments as they are transcribed
        """
        self.logger.info(f"Streaming transcription: {audio_path}")
        
        # Read audio
        audio, sr = sf.read(audio_path)
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        
        # Transcribe with segments
        lang = language or self.language
        segments, info = self.model.transcribe(
            audio,
            language=lang,
            vad_filter=self.vad_enabled
        )
        
        # Yield segments
        for segment in segments:
            text = segment.text.strip()
            if text:
                self.logger.debug(f"Segment [{segment.start:.2f}s - {segment.end:.2f}s]: {text}")
                yield text
    
    def get_model_info(self) -> dict:
        """
        Get information about loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': self.model_name,
            'language': self.language,
            'device': self.device,
            'compute_type': self.compute_type,
            'vad_enabled': self.vad_enabled,
            'sample_rate': self.sample_rate
        }


def record_audio(duration: float = 5.0, sample_rate: int = 16000) -> np.ndarray:
    """
    Record audio from microphone.
    
    Args:
        duration: Recording duration in seconds
        sample_rate: Sample rate
        
    Returns:
        Recorded audio as numpy array
    """
    import sounddevice as sd
    
    logging.info(f"Recording for {duration} seconds...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    logging.info("Recording finished")
    
    return audio.flatten()


def main():
    """CLI interface for ASR testing."""
    parser = argparse.ArgumentParser(description="Test ASR module")
    parser.add_argument('--demo', action='store_true', help="Run demo mode")
    parser.add_argument('--audio', type=str, help="Path to audio file")
    parser.add_argument('--record', type=float, help="Record audio for N seconds")
    parser.add_argument('--output', type=str, help="Save recording to file")
    parser.add_argument('--language', type=str, default='fr', help="Language code")
    parser.add_argument('--stream', action='store_true', help="Use streaming mode")
    parser.add_argument('--config', type=str, default='config.yaml', help="Config file")
    
    args = parser.parse_args()
    
    setup_logging(level='INFO')
    logger = logging.getLogger(__name__)
    
    # Load config and initialize ASR
    config = get_config(args.config)
    asr = ASR(config)
    
    # Display model info
    info = asr.get_model_info()
    logger.info("ASR Configuration:")
    for key, value in info.items():
        logger.info(f"  {key}: {value}")
    
    # Demo mode
    if args.demo:
        logger.info("\n🎤 Demo Mode: Record 5 seconds of audio")
        audio = record_audio(duration=5.0, sample_rate=16000)
        
        if args.output:
            sf.write(args.output, audio, 16000)
            logger.info(f"Audio saved to: {args.output}")
        
        logger.info("Transcribing...")
        text = asr.transcribe_array(audio, sample_rate=16000, language=args.language)
        
        print("\n" + "=" * 60)
        print("🎯 TRANSCRIPTION RESULT")
        print("=" * 60)
        print(text)
        print("=" * 60)
    
    # Record mode
    elif args.record:
        logger.info(f"\n🎤 Recording for {args.record} seconds...")
        audio = record_audio(duration=args.record, sample_rate=16000)
        
        if args.output:
            sf.write(args.output, audio, 16000)
            logger.info(f"Audio saved to: {args.output}")
        
        text = asr.transcribe_array(audio, sample_rate=16000, language=args.language)
        
        print("\n" + "=" * 60)
        print("🎯 TRANSCRIPTION")
        print("=" * 60)
        print(text)
        print("=" * 60)
    
    # File mode
    elif args.audio:
        if args.stream:
            logger.info("\n🎤 Streaming transcription...")
            print("\n" + "=" * 60)
            print("🎯 TRANSCRIPTION (STREAMING)")
            print("=" * 60)
            for segment in asr.transcribe_streaming(args.audio, language=args.language):
                print(segment, end=' ', flush=True)
            print("\n" + "=" * 60)
        else:
            text = asr.transcribe_file(args.audio, language=args.language)
            print("\n" + "=" * 60)
            print("🎯 TRANSCRIPTION")
            print("=" * 60)
            print(text)
            print("=" * 60)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
