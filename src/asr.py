"""ASR Module - Automatic Speech Recognition using faster-whisper and silero-vad"""

import torch
import numpy as np
from typing import Optional, List, Tuple
from faster_whisper import WhisperModel
import soundfile as sf


class VoiceActivityDetector:
    """Voice Activity Detection using Silero VAD"""
    
    def __init__(self, sample_rate: int = 16000):
        """Initialize VAD model
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )
        (self.get_speech_timestamps,
         self.save_audio,
         self.read_audio,
         self.VADIterator,
         self.collect_chunks) = utils
        
    def detect_speech(self, audio: np.ndarray) -> List[dict]:
        """Detect speech segments in audio
        
        Args:
            audio: Audio array
            
        Returns:
            List of speech timestamps
        """
        audio_tensor = torch.from_numpy(audio).float()
        speech_timestamps = self.get_speech_timestamps(
            audio_tensor, 
            self.model,
            sampling_rate=self.sample_rate
        )
        return speech_timestamps


class SpeechRecognizer:
    """Speech Recognition using faster-whisper"""
    
    def __init__(
        self, 
        model_size: str = "base",
        device: str = "cuda",
        compute_type: str = "float16"
    ):
        """Initialize speech recognizer
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cuda or cpu)
            compute_type: Computation precision (float16, int8, etc.)
        """
        self.model = WhisperModel(
            model_size, 
            device=device, 
            compute_type=compute_type
        )
        self.vad = VoiceActivityDetector()
        
    def transcribe(
        self, 
        audio_path: Optional[str] = None,
        audio_array: Optional[np.ndarray] = None,
        language: str = "fr"
    ) -> str:
        """Transcribe audio to text
        
        Args:
            audio_path: Path to audio file
            audio_array: Audio array (if path not provided)
            language: Language code (fr, en, etc.)
            
        Returns:
            Transcribed text
        """
        if audio_path:
            segments, info = self.model.transcribe(
                audio_path, 
                language=language,
                vad_filter=True
            )
        elif audio_array is not None:
            # Save array to temp file for processing
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                sf.write(tmp.name, audio_array, 16000)
                segments, info = self.model.transcribe(
                    tmp.name,
                    language=language,
                    vad_filter=True
                )
        else:
            raise ValueError("Either audio_path or audio_array must be provided")
        
        # Combine all segments
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    
    def transcribe_with_timestamps(
        self,
        audio_path: str,
        language: str = "fr"
    ) -> List[Tuple[float, float, str]]:
        """Transcribe with timestamps
        
        Args:
            audio_path: Path to audio file
            language: Language code
            
        Returns:
            List of (start, end, text) tuples
        """
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            vad_filter=True
        )
        
        results = []
        for segment in segments:
            results.append((segment.start, segment.end, segment.text))
        
        return results
