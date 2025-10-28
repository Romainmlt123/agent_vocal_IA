"""
Orchestrator Module - Pipeline coordination for Agent Vocal IA.

This module orchestrates the complete pipeline: ASR → RAG → LLM → TTS,
with automatic subject detection and error handling.
"""

import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from .asr import ASR
from .llm import TutorLLM
from .rag import RAGRetriever
from .tts import TTS
from .utils import Config, ensure_dir, format_time, get_config


class VocalTutorOrchestrator:
    """Orchestrates the complete vocal tutoring pipeline."""
    
    def __init__(self, config: Config):
        """
        Initialize orchestrator.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get orchestrator settings
        self.auto_detect_subject = config.get('orchestrator.auto_detect_subject', True)
        self.subject_keywords = config.get('orchestrator.subject_keywords', {})
        self.default_subject = config.get('orchestrator.default_subject', 'maths')
        
        # Initialize components (lazy loading)
        self._asr: Optional[ASR] = None
        self._rag: Optional[RAGRetriever] = None
        self._llm: Optional[TutorLLM] = None
        self._tts: Optional[TTS] = None
        
        # Conversation state
        self.current_subject: Optional[str] = None
        self.conversation_history: List[Dict] = []
        
        self.logger.info("Vocal Tutor Orchestrator initialized")
    
    @property
    def asr(self) -> ASR:
        """Lazy load ASR module."""
        if self._asr is None:
            self.logger.info("Loading ASR module...")
            self._asr = ASR(self.config)
        return self._asr
    
    @property
    def rag(self) -> RAGRetriever:
        """Lazy load RAG module."""
        if self._rag is None:
            self.logger.info("Loading RAG module...")
            self._rag = RAGRetriever(self.config)
        return self._rag
    
    @property
    def llm(self) -> TutorLLM:
        """Lazy load LLM module."""
        if self._llm is None:
            self.logger.info("Loading LLM module...")
            self._llm = TutorLLM(self.config)
        return self._llm
    
    @property
    def tts(self) -> TTS:
        """Lazy load TTS module."""
        if self._tts is None:
            self.logger.info("Loading TTS module...")
            self._tts = TTS(self.config)
        return self._tts
    
    def detect_subject(self, text: str) -> str:
        """
        Detect subject from text using keywords.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected subject or default
        """
        text_lower = text.lower()
        
        # Count keyword matches for each subject
        matches = {}
        for subject, keywords in self.subject_keywords.items():
            count = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if count > 0:
                matches[subject] = count
        
        if matches:
            # Return subject with most matches
            detected = max(matches, key=matches.get)
            self.logger.info(f"Subject detected: {detected} (matches: {matches[detected]})")
            return detected
        
        self.logger.info(f"No subject detected, using default: {self.default_subject}")
        return self.default_subject
    
    def process_audio_file(
        self,
        audio_path: str,
        subject: Optional[str] = None
    ) -> Dict:
        """
        Process audio file through complete pipeline.
        
        Args:
            audio_path: Path to audio file
            subject: Optional subject override
            
        Returns:
            Dictionary with results from each stage
        """
        self.logger.info(f"Processing audio file: {audio_path}")
        start_time = time.time()
        
        results = {
            'audio_path': audio_path,
            'timestamp': datetime.now().isoformat(),
            'success': False
        }
        
        try:
            # Stage 1: ASR - Transcribe audio
            self.logger.info("Stage 1/4: Transcribing audio...")
            transcript = self.asr.transcribe_file(audio_path)
            results['transcript'] = transcript
            
            if not transcript or not transcript.strip():
                results['error'] = "No speech detected or transcription empty"
                return results
            
            self.logger.info(f"Transcript: {transcript}")
            
            # Stage 2: Detect or use provided subject
            if subject is None and self.auto_detect_subject:
                subject = self.detect_subject(transcript)
            elif subject is None:
                subject = self.current_subject or self.default_subject
            
            results['subject'] = subject
            self.current_subject = subject
            
            # Stage 3: RAG - Retrieve relevant context
            self.logger.info(f"Stage 2/4: Retrieving context for subject '{subject}'...")
            try:
                context, sources = self.rag.retrieve_with_context(
                    transcript,
                    subject,
                    top_k=self.config.get('rag.top_k', 3)
                )
                results['context'] = context
                results['sources'] = sources
                self.logger.info(f"Retrieved {len(sources)} sources")
            except FileNotFoundError:
                self.logger.warning(f"RAG index not found for {subject}, proceeding without context")
                context = None
                results['context'] = None
                results['sources'] = []
            
            # Stage 4: LLM - Generate response
            self.logger.info("Stage 3/4: Generating response...")
            response = self.llm.answer_question(
                transcript,
                context=context,
                subject=subject,
                stream=False
            )
            results['response'] = response
            
            # Parse hints if available
            hints = self.llm.parse_hints(response)
            results['hints'] = hints
            
            # Stage 5: TTS - Synthesize speech
            self.logger.info("Stage 4/4: Synthesizing speech...")
            output_filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            output_path = str(Path(self.config.get('orchestrator.audio_output_dir', 'outputs/audio')) / output_filename)
            
            audio_path = self.tts.synthesize_to_file(response, output_path)
            results['audio_output'] = audio_path
            
            # Success
            results['success'] = True
            elapsed = time.time() - start_time
            results['processing_time'] = elapsed
            
            self.logger.info(f"✅ Pipeline completed successfully in {format_time(elapsed)}")
            
            # Add to conversation history
            self.add_to_history(transcript, response, subject)
            
        except Exception as e:
            self.logger.error(f"Error in pipeline: {e}", exc_info=True)
            results['error'] = str(e)
        
        return results
    
    def process_text_question(
        self,
        question: str,
        subject: Optional[str] = None,
        generate_audio: bool = True
    ) -> Dict:
        """
        Process text question (skip ASR).
        
        Args:
            question: Text question
            subject: Optional subject override
            generate_audio: Whether to generate TTS audio
            
        Returns:
            Dictionary with results
        """
        self.logger.info(f"Processing text question: '{question[:50]}...'")
        start_time = time.time()
        
        results = {
            'question': question,
            'timestamp': datetime.now().isoformat(),
            'success': False
        }
        
        try:
            # Detect or use subject
            if subject is None and self.auto_detect_subject:
                subject = self.detect_subject(question)
            elif subject is None:
                subject = self.current_subject or self.default_subject
            
            results['subject'] = subject
            self.current_subject = subject
            
            # RAG retrieval
            self.logger.info(f"Retrieving context for subject '{subject}'...")
            try:
                context, sources = self.rag.retrieve_with_context(
                    question,
                    subject,
                    top_k=self.config.get('rag.top_k', 3)
                )
                results['context'] = context
                results['sources'] = sources
            except FileNotFoundError:
                self.logger.warning(f"RAG index not found for {subject}")
                context = None
                results['context'] = None
                results['sources'] = []
            
            # LLM generation
            self.logger.info("Generating response...")
            response = self.llm.answer_question(
                question,
                context=context,
                subject=subject,
                stream=False
            )
            results['response'] = response
            
            # Parse hints
            hints = self.llm.parse_hints(response)
            results['hints'] = hints
            
            # TTS (optional)
            if generate_audio:
                self.logger.info("Synthesizing speech...")
                output_filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                output_path = str(Path(self.config.get('orchestrator.audio_output_dir', 'outputs/audio')) / output_filename)
                
                audio_path = self.tts.synthesize_to_file(response, output_path)
                results['audio_output'] = audio_path
            
            # Success
            results['success'] = True
            elapsed = time.time() - start_time
            results['processing_time'] = elapsed
            
            self.logger.info(f"✅ Processing completed in {format_time(elapsed)}")
            
            # Add to history
            self.add_to_history(question, response, subject)
            
        except Exception as e:
            self.logger.error(f"Error processing question: {e}", exc_info=True)
            results['error'] = str(e)
        
        return results
    
    def add_to_history(
        self,
        question: str,
        response: str,
        subject: str
    ) -> None:
        """
        Add interaction to conversation history.
        
        Args:
            question: User's question
            response: Assistant's response
            subject: Subject of conversation
        """
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'subject': subject,
            'question': question,
            'response': response
        })
        
        # Keep only recent history
        max_history = self.config.get('orchestrator.conversation_history_length', 5)
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        if self._llm:
            self._llm.clear_history()
        self.logger.info("Conversation history cleared")
    
    def set_subject(self, subject: str) -> None:
        """
        Manually set current subject.
        
        Args:
            subject: Subject name
        """
        if subject not in ['maths', 'physique', 'anglais']:
            raise ValueError(f"Invalid subject: {subject}")
        
        self.current_subject = subject
        self.logger.info(f"Subject set to: {subject}")
    
    def get_available_subjects(self) -> List[str]:
        """Get list of available subjects with RAG indices."""
        return self.rag.list_available_subjects()
    
    def get_status(self) -> Dict:
        """
        Get orchestrator status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'current_subject': self.current_subject,
            'auto_detect_subject': self.auto_detect_subject,
            'available_subjects': self.get_available_subjects(),
            'conversation_length': len(self.conversation_history),
            'modules_loaded': {
                'asr': self._asr is not None,
                'rag': self._rag is not None,
                'llm': self._llm is not None,
                'tts': self._tts is not None
            }
        }


def main():
    """CLI interface for orchestrator testing."""
    import argparse
    from .utils import setup_logging
    
    parser = argparse.ArgumentParser(description="Test Orchestrator")
    parser.add_argument('--audio', type=str, help="Audio file to process")
    parser.add_argument('--text', type=str, help="Text question to process")
    parser.add_argument('--subject', type=str, choices=['maths', 'physique', 'anglais'],
                       help="Subject override")
    parser.add_argument('--no-audio', action='store_true', help="Skip TTS generation")
    parser.add_argument('--config', type=str, default='config.yaml', help="Config file")
    
    args = parser.parse_args()
    
    setup_logging(level='INFO')
    logger = logging.getLogger(__name__)
    
    # Initialize orchestrator
    config = get_config(args.config)
    orchestrator = VocalTutorOrchestrator(config)
    
    # Display status
    status = orchestrator.get_status()
    logger.info("Orchestrator Status:")
    logger.info(f"  Available subjects: {status['available_subjects']}")
    logger.info(f"  Auto-detect: {status['auto_detect_subject']}")
    
    # Process input
    if args.audio:
        logger.info(f"\n🎤 Processing audio file: {args.audio}")
        results = orchestrator.process_audio_file(args.audio, subject=args.subject)
    elif args.text:
        logger.info(f"\n💬 Processing text question: {args.text}")
        results = orchestrator.process_text_question(
            args.text,
            subject=args.subject,
            generate_audio=not args.no_audio
        )
    else:
        parser.print_help()
        return
    
    # Display results
    print("\n" + "=" * 60)
    print("🎯 ORCHESTRATOR RESULTS")
    print("=" * 60)
    
    if results.get('success'):
        print(f"\n✅ Success!")
        print(f"Subject: {results.get('subject')}")
        
        if 'transcript' in results:
            print(f"\n📝 Transcript:\n{results['transcript']}")
        elif 'question' in results:
            print(f"\n📝 Question:\n{results['question']}")
        
        if results.get('sources'):
            print(f"\n📚 Sources ({len(results['sources'])}):")
            for src in results['sources']:
                print(f"  - {src['filename']} (score: {src['score']:.3f})")
        
        print(f"\n💡 Response:\n{results['response']}")
        
        if results.get('hints'):
            hints = results['hints']
            if any(hints.values()):
                print(f"\n🎓 Indices:")
                for level, hint in hints.items():
                    if hint:
                        print(f"\n{level.replace('_', ' ').title()}:")
                        print(hint)
        
        if results.get('audio_output'):
            print(f"\n🔊 Audio saved: {results['audio_output']}")
        
        print(f"\n⏱️  Processing time: {format_time(results.get('processing_time', 0))}")
    else:
        print(f"\n❌ Error: {results.get('error', 'Unknown error')}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
