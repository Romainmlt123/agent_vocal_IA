"""Pipeline Module - Main orchestration for Agent Vocal IA"""

from typing import Optional, Dict, Any
import os
from .asr import SpeechRecognizer
from .rag import RAGRetriever
from .llm import TutorLLM
from .tts import MultilingualTTS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceTutorPipeline:
    """Complete voice tutor pipeline"""
    
    def __init__(
        self,
        llm_model_path: str,
        data_dirs: list,
        whisper_model_size: str = "base",
        device: str = "cuda",
        voices_dir: str = "models/voices"
    ):
        """Initialize the complete pipeline
        
        Args:
            llm_model_path: Path to LLM GGUF model
            data_dirs: List of data directories for RAG
            whisper_model_size: Whisper model size
            device: Device for computation (cuda/cpu)
            voices_dir: Directory containing TTS voices
        """
        logger.info("Initializing Voice Tutor Pipeline...")
        
        # Initialize ASR
        logger.info("Loading ASR model...")
        self.asr = SpeechRecognizer(
            model_size=whisper_model_size,
            device=device
        )
        
        # Initialize RAG
        logger.info("Loading RAG system...")
        self.rag = RAGRetriever(data_dirs=data_dirs)
        
        # Initialize LLM
        logger.info("Loading LLM model...")
        self.llm = TutorLLM(model_path=llm_model_path)
        
        # Initialize TTS
        logger.info("Loading TTS engine...")
        self.tts = MultilingualTTS(voices_dir=voices_dir)
        
        logger.info("Pipeline initialized successfully!")
    
    def process_voice_query(
        self,
        audio_path: Optional[str] = None,
        audio_array: Optional[Any] = None,
        language: str = "fr",
        use_rag: bool = True,
        speak_response: bool = True
    ) -> Dict[str, Any]:
        """Process a complete voice query
        
        Args:
            audio_path: Path to audio file
            audio_array: Audio array (alternative to path)
            language: Language code
            use_rag: Whether to use RAG for context
            speak_response: Whether to synthesize speech response
            
        Returns:
            Dict with transcription, response, and audio
        """
        # Step 1: Transcribe audio (ASR)
        logger.info("Transcribing audio...")
        transcription = self.asr.transcribe(
            audio_path=audio_path,
            audio_array=audio_array,
            language=language
        )
        logger.info(f"Transcription: {transcription}")
        
        # Step 2: Retrieve context (RAG)
        context = None
        if use_rag:
            logger.info("Retrieving relevant context...")
            context = self.rag.retrieve_context(transcription)
            logger.info(f"Retrieved context ({len(context)} chars)")
        
        # Step 3: Generate response (LLM)
        logger.info("Generating response...")
        response = self.llm.answer_question(
            question=transcription,
            context=context
        )
        logger.info(f"Response: {response}")
        
        # Step 4: Synthesize speech (TTS)
        response_audio = None
        if speak_response:
            logger.info("Synthesizing speech...")
            response_audio = self.tts.synthesize(
                text=response,
                language=language
            )
        
        return {
            "transcription": transcription,
            "response": response,
            "context": context,
            "response_audio": response_audio
        }
    
    def process_text_query(
        self,
        question: str,
        use_rag: bool = True,
        speak_response: bool = True,
        language: str = "fr"
    ) -> Dict[str, Any]:
        """Process a text-based query
        
        Args:
            question: User question
            use_rag: Whether to use RAG for context
            speak_response: Whether to synthesize speech response
            language: Language for TTS
            
        Returns:
            Dict with response and audio
        """
        # Retrieve context (RAG)
        context = None
        if use_rag:
            logger.info("Retrieving relevant context...")
            context = self.rag.retrieve_context(question)
        
        # Generate response (LLM)
        logger.info("Generating response...")
        response = self.llm.answer_question(
            question=question,
            context=context
        )
        
        # Synthesize speech (TTS)
        response_audio = None
        if speak_response:
            logger.info("Synthesizing speech...")
            response_audio = self.tts.synthesize(
                text=response,
                language=language
            )
        
        return {
            "response": response,
            "context": context,
            "response_audio": response_audio
        }
    
    def index_documents(self):
        """Index all documents in data directories"""
        logger.info("Indexing documents...")
        self.rag.index_documents()
        logger.info("Indexing complete!")
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.llm.reset_conversation()
        logger.info("Conversation reset")


def create_pipeline(
    config: Optional[Dict[str, Any]] = None
) -> VoiceTutorPipeline:
    """Factory function to create pipeline with config
    
    Args:
        config: Configuration dict
        
    Returns:
        Initialized pipeline
    """
    if config is None:
        config = {}
    
    # Default configuration
    default_config = {
        "llm_model_path": "models/llm/model.gguf",
        "data_dirs": [
            "data/maths",
            "data/physique",
            "data/anglais"
        ],
        "whisper_model_size": "base",
        "device": "cuda",
        "voices_dir": "models/voices"
    }
    
    # Merge with provided config
    default_config.update(config)
    
    return VoiceTutorPipeline(**default_config)
