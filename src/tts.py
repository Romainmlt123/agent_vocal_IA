"""
TTS Module - Text-to-Speech for Agent Vocal IA.

This module handles text-to-speech synthesis using Piper-TTS for
local, offline voice generation.
"""

import argparse
import logging
import os
import subprocess
import wave
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf

from .utils import Config, ensure_dir, get_config, setup_logging


class TTS:
    """Text-to-Speech using Piper-TTS."""
    
    def __init__(self, config: Config):
        """
        Initialize TTS system.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get TTS parameters
        self.model_path = config.get('tts.model_path', 'models/voices/fr_FR-siwis-medium.onnx')
        self.config_path = config.get('tts.config_path', 'models/voices/fr_FR-siwis-medium.onnx.json')
        self.sample_rate = config.get('tts.sample_rate', 22050)
        self.speed = config.get('tts.speed', 1.0)
        self.speaker_id = config.get('tts.speaker_id', 0)
        
        # Output directory for audio files
        self.output_dir = Path(config.get('orchestrator.audio_output_dir', 'outputs/audio'))
        ensure_dir(str(self.output_dir))
        
        # Check if model exists
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"TTS model not found at {self.model_path}. "
                f"Please download it first."
            )
        
        # Check if piper is installed
        self._check_piper_installation()
        
        self.logger.info(f"TTS initialized with model: {self.model_path}")
    
    def _check_piper_installation(self) -> None:
        """Check if Piper TTS is installed."""
        try:
            # Try to run piper --version or piper --help
            result = subprocess.run(
                ['piper', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.logger.info(f"Piper TTS found: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.logger.warning(
                "Piper TTS binary not found in PATH. "
                "Make sure piper-tts is installed correctly."
            )
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        speed: Optional[float] = None
    ) -> str:
        """
        Synthesize text to audio file using Piper.
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            speed: Optional speech speed override
            
        Returns:
            Path to generated audio file
        """
        if not text or not text.strip():
            self.logger.warning("Empty text provided for synthesis")
            return None
        
        speed = speed or self.speed
        self.logger.info(f"Synthesizing text to: {output_path}")
        self.logger.debug(f"Text: '{text[:50]}...'")
        
        try:
            # Ensure output directory exists
            ensure_dir(os.path.dirname(output_path))
            
            # Build piper command
            cmd = [
                'piper',
                '--model', self.model_path,
                '--config', self.config_path,
                '--output_file', output_path
            ]
            
            # Add speed if different from 1.0
            if speed != 1.0:
                cmd.extend(['--length_scale', str(1.0 / speed)])
            
            # Add speaker if multi-speaker model
            if self.speaker_id > 0:
                cmd.extend(['--speaker', str(self.speaker_id)])
            
            # Run piper with text as stdin
            result = subprocess.run(
                cmd,
                input=text,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"Piper TTS error: {result.stderr}")
                raise RuntimeError(f"TTS synthesis failed: {result.stderr}")
            
            # Verify output file was created
            if not os.path.exists(output_path):
                raise RuntimeError(f"Output file not created: {output_path}")
            
            self.logger.info(f"✅ Audio synthesized successfully: {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            self.logger.error("TTS synthesis timed out")
            raise
        except Exception as e:
            self.logger.error(f"Error in TTS synthesis: {e}")
            raise
    
    def synthesize_to_array(
        self,
        text: str,
        speed: Optional[float] = None
    ) -> tuple:
        """
        Synthesize text to numpy array.
        
        Args:
            text: Text to synthesize
            speed: Optional speech speed override
            
        Returns:
            Tuple of (audio array, sample rate)
        """
        # Generate to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            self.synthesize_to_file(text, tmp_path, speed)
            
            # Load audio
            audio, sr = sf.read(tmp_path)
            return audio, sr
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def synthesize_long_text(
        self,
        text: str,
        output_path: str,
        max_chunk_length: int = 500
    ) -> str:
        """
        Synthesize long text by splitting into chunks.
        
        Args:
            text: Long text to synthesize
            output_path: Path to save final audio
            max_chunk_length: Maximum characters per chunk
            
        Returns:
            Path to generated audio file
        """
        self.logger.info(f"Synthesizing long text ({len(text)} chars)")
        
        # Split text into sentences
        sentences = self._split_text(text, max_chunk_length)
        
        if len(sentences) == 1:
            # Short text, synthesize directly
            return self.synthesize_to_file(text, output_path)
        
        # Synthesize each chunk
        temp_files = []
        for i, sentence in enumerate(sentences):
            temp_path = str(self.output_dir / f"temp_chunk_{i}.wav")
            self.synthesize_to_file(sentence, temp_path)
            temp_files.append(temp_path)
        
        # Concatenate audio files
        self._concatenate_audio_files(temp_files, output_path)
        
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        self.logger.info(f"✅ Long text synthesized: {output_path}")
        return output_path
    
    def _split_text(self, text: str, max_length: int) -> list:
        """
        Split text into chunks at sentence boundaries.
        
        Args:
            text: Text to split
            max_length: Maximum chunk length
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]
        
        # Split by common sentence delimiters
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if char in '.!?' and len(current) > 20:
                sentences.append(current.strip())
                current = ""
        
        if current.strip():
            sentences.append(current.strip())
        
        # Combine short sentences
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _concatenate_audio_files(self, input_files: list, output_path: str) -> None:
        """
        Concatenate multiple audio files into one.
        
        Args:
            input_files: List of input audio file paths
            output_path: Output file path
        """
        self.logger.debug(f"Concatenating {len(input_files)} audio files")
        
        # Read all audio files
        audio_arrays = []
        for file_path in input_files:
            audio, sr = sf.read(file_path)
            audio_arrays.append(audio)
        
        # Concatenate
        combined = np.concatenate(audio_arrays)
        
        # Save
        sf.write(output_path, combined, self.sample_rate)
    
    def play_audio(self, audio_path: str) -> None:
        """
        Play audio file.
        
        Args:
            audio_path: Path to audio file
        """
        try:
            import sounddevice as sd
            audio, sr = sf.read(audio_path)
            self.logger.info(f"Playing audio: {audio_path}")
            sd.play(audio, sr)
            sd.wait()
        except Exception as e:
            self.logger.warning(f"Could not play audio: {e}")
    
    def get_model_info(self) -> dict:
        """
        Get information about TTS model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_path': self.model_path,
            'config_path': self.config_path,
            'sample_rate': self.sample_rate,
            'speed': self.speed,
            'speaker_id': self.speaker_id,
            'output_dir': str(self.output_dir)
        }


def main():
    """CLI interface for TTS testing."""
    parser = argparse.ArgumentParser(description="Test TTS module")
    parser.add_argument('--text', type=str, help="Text to synthesize")
    parser.add_argument('--file', type=str, help="Text file to read from")
    parser.add_argument('--output', type=str, default='output.wav', help="Output audio file")
    parser.add_argument('--play', action='store_true', help="Play audio after synthesis")
    parser.add_argument('--speed', type=float, default=1.0, help="Speech speed")
    parser.add_argument('--config', type=str, default='config.yaml', help="Config file")
    
    args = parser.parse_args()
    
    setup_logging(level='INFO')
    logger = logging.getLogger(__name__)
    
    # Get text
    if args.text:
        text = args.text
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = "Bonjour, je suis votre tuteur vocal. Comment puis-je vous aider aujourd'hui ?"
    
    # Initialize TTS
    config = get_config(args.config)
    tts = TTS(config)
    
    # Display model info
    info = tts.get_model_info()
    logger.info("TTS Configuration:")
    for key, value in info.items():
        logger.info(f"  {key}: {value}")
    
    # Synthesize
    print("\n" + "=" * 60)
    print("🔊 TTS SYNTHESIS")
    print("=" * 60)
    print(f"\nText: {text[:100]}...")
    print(f"Output: {args.output}")
    print()
    
    output_path = tts.synthesize_to_file(text, args.output, speed=args.speed)
    
    print(f"\n✅ Audio generated: {output_path}")
    
    # Get file info
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path) / 1024
        print(f"   File size: {file_size:.2f} KB")
        
        audio, sr = sf.read(output_path)
        duration = len(audio) / sr
        print(f"   Duration: {duration:.2f}s")
    
    # Play if requested
    if args.play:
        print("\n▶️  Playing audio...")
        tts.play_audio(output_path)
    
    print("=" * 60)


if __name__ == "__main__":
    main()
