"""TTS Module - Text-to-Speech using piper-tts"""

import os
import subprocess
from typing import Optional
import numpy as np
import soundfile as sf


class TextToSpeech:
    """Text-to-Speech using Piper TTS"""
    
    def __init__(
        self,
        model_path: str,
        config_path: Optional[str] = None,
        sample_rate: int = 22050
    ):
        """Initialize TTS
        
        Args:
            model_path: Path to Piper ONNX model
            config_path: Path to model config JSON (optional)
            sample_rate: Audio sample rate
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        self.model_path = model_path
        self.config_path = config_path
        self.sample_rate = sample_rate
    
    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """Synthesize speech from text
        
        Args:
            text: Text to synthesize
            output_path: Optional path to save audio file
            
        Returns:
            Audio array
        """
        # Use piper command line tool
        import tempfile
        
        if output_path is None:
            # Create temporary output file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_path = temp_file.name
            temp_file.close()
        
        # Prepare piper command
        cmd = ['piper', '--model', self.model_path, '--output_file', output_path]
        
        if self.config_path:
            cmd.extend(['--config', self.config_path])
        
        # Run piper with text input
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                raise RuntimeError(f"Piper TTS failed: {stderr}")
            
            # Load the generated audio
            audio, sr = sf.read(output_path)
            
            return audio
            
        except FileNotFoundError:
            raise RuntimeError(
                "Piper TTS not found. Please install piper-tts and ensure it's in PATH."
            )
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: str
    ):
        """Synthesize speech and save to file
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
        """
        self.synthesize(text, output_path)
    
    def speak(
        self,
        text: str,
        play_audio: bool = True
    ) -> np.ndarray:
        """Synthesize and optionally play audio
        
        Args:
            text: Text to speak
            play_audio: Whether to play audio immediately
            
        Returns:
            Audio array
        """
        audio = self.synthesize(text)
        
        if play_audio:
            self._play_audio(audio)
        
        return audio
    
    def _play_audio(self, audio: np.ndarray):
        """Play audio array
        
        Args:
            audio: Audio array to play
        """
        try:
            import pyaudio
            
            # Convert to int16
            audio_int16 = (audio * 32767).astype(np.int16)
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True
            )
            
            stream.write(audio_int16.tobytes())
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except ImportError:
            print("PyAudio not available. Audio will not be played.")
        except Exception as e:
            print(f"Error playing audio: {e}")


class MultilingualTTS:
    """Multilingual TTS manager"""
    
    def __init__(self, voices_dir: str = "models/voices"):
        """Initialize multilingual TTS
        
        Args:
            voices_dir: Directory containing voice models
        """
        self.voices_dir = voices_dir
        self.tts_engines = {}
        self.default_voice = None
    
    def add_voice(
        self,
        language: str,
        model_path: str,
        config_path: Optional[str] = None
    ):
        """Add a voice for a language
        
        Args:
            language: Language code (fr, en, etc.)
            model_path: Path to voice model
            config_path: Path to model config
        """
        full_model_path = os.path.join(self.voices_dir, model_path)
        full_config_path = None
        
        if config_path:
            full_config_path = os.path.join(self.voices_dir, config_path)
        
        self.tts_engines[language] = TextToSpeech(
            full_model_path,
            full_config_path
        )
        
        if self.default_voice is None:
            self.default_voice = language
    
    def synthesize(
        self,
        text: str,
        language: Optional[str] = None
    ) -> np.ndarray:
        """Synthesize speech in specified language
        
        Args:
            text: Text to synthesize
            language: Language code (uses default if None)
            
        Returns:
            Audio array
        """
        lang = language or self.default_voice
        
        if lang not in self.tts_engines:
            raise ValueError(f"No TTS engine for language: {lang}")
        
        return self.tts_engines[lang].synthesize(text)
