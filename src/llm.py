"""
LLM Module - Local Language Model inference for Agent Vocal IA.

This module handles local LLM inference using llama-cpp-python with a
specialized tutoring system that provides progressive hints.
"""

import argparse
import logging
import os
from pathlib import Path
from typing import Dict, Generator, List, Optional

from llama_cpp import Llama

from .utils import Config, get_config, setup_logging


class TutorLLM:
    """Local LLM for educational tutoring with progressive hints."""
    
    # Tutor system prompt
    SYSTEM_PROMPT = """Tu es un tuteur pédagogique bienveillant et patient. Ton rôle est d'aider les élèves à comprendre par eux-mêmes sans donner directement la réponse complète.

Principes importants :
- Ne donne JAMAIS la solution complète directement
- Fournis des indices progressifs en 3 niveaux de difficulté
- Encourage l'élève à réfléchir
- Utilise des exemples concrets et des analogies
- Reste positif et motivant

Structure de réponse pour une question :
1. **Indice Niveau 1 (Léger)** : Question guidante ou rappel de concept
2. **Indice Niveau 2 (Moyen)** : Méthode ou approche à utiliser
3. **Indice Niveau 3 (Fort)** : Début de résolution mais sans la réponse finale

N'oublie pas : l'objectif est que l'élève trouve lui-même la solution !"""
    
    def __init__(self, config: Config):
        """
        Initialize LLM.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get LLM parameters
        self.model_path = config.get('llm.model_path', 'models/llm/phi-3-mini-4k-instruct.Q4_K_M.gguf')
        self.n_ctx = config.get('llm.n_ctx', 4096)
        self.n_threads = config.get('llm.n_threads', 4)
        self.n_gpu_layers = config.get('llm.n_gpu_layers', 35)
        self.temperature = config.get('llm.temperature', 0.7)
        self.top_p = config.get('llm.top_p', 0.9)
        self.top_k = config.get('llm.top_k', 40)
        self.max_tokens = config.get('llm.max_tokens', 512)
        self.repeat_penalty = config.get('llm.repeat_penalty', 1.1)
        self.stream = config.get('llm.stream', True)
        
        # Tutor settings
        self.progressive_hints = config.get('llm.progressive_hints', True)
        self.hint_levels = config.get('llm.hint_levels', 3)
        
        # Check if model exists
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"LLM model not found at {self.model_path}. "
                f"Please download it first."
            )
        
        # Initialize model
        self.logger.info(f"Loading LLM model: {self.model_path}")
        self.logger.info(f"Context window: {self.n_ctx}, GPU layers: {self.n_gpu_layers}")
        
        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )
            self.logger.info("✅ LLM model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading LLM model: {e}")
            raise
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
    
    def build_prompt(
        self,
        question: str,
        context: Optional[str] = None,
        subject: Optional[str] = None
    ) -> str:
        """
        Build prompt for tutor LLM.
        
        Args:
            question: Student's question
            context: Optional RAG context
            subject: Optional subject (maths, physique, anglais)
            
        Returns:
            Formatted prompt
        """
        prompt_parts = [self.SYSTEM_PROMPT]
        
        # Add subject if provided
        if subject:
            subject_names = {
                'maths': 'Mathématiques',
                'physique': 'Physique',
                'anglais': 'Anglais'
            }
            prompt_parts.append(f"\nMatière : {subject_names.get(subject, subject)}")
        
        # Add RAG context if available
        if context:
            prompt_parts.append(f"\nDocuments de référence :\n{context}")
        
        # Add question
        prompt_parts.append(f"\nQuestion de l'élève : {question}")
        
        # Add instruction for progressive hints
        if self.progressive_hints:
            prompt_parts.append(
                f"\nFournis {self.hint_levels} indices progressifs pour aider l'élève "
                "à trouver la réponse par lui-même. N'oublie pas : ne donne JAMAIS "
                "la solution complète."
            )
        
        return "\n".join(prompt_parts)
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: Optional[bool] = None
    ) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Optional override for max tokens
            temperature: Optional override for temperature
            stream: Optional override for streaming
            
        Returns:
            Generated text
        """
        max_tok = max_tokens or self.max_tokens
        temp = temperature or self.temperature
        do_stream = stream if stream is not None else self.stream
        
        self.logger.debug(f"Generating response (max_tokens={max_tok}, temp={temp})")
        
        try:
            output = self.model(
                prompt,
                max_tokens=max_tok,
                temperature=temp,
                top_p=self.top_p,
                top_k=self.top_k,
                repeat_penalty=self.repeat_penalty,
                stop=["Question de l'élève:", "\n\n\n"],
                stream=do_stream
            )
            
            if do_stream:
                # Collect streamed output
                text = ""
                for chunk in output:
                    text += chunk['choices'][0]['text']
                return text
            else:
                return output['choices'][0]['text']
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    def generate_streaming(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Generator[str, None, None]:
        """
        Generate response with streaming output.
        
        Args:
            prompt: Input prompt
            max_tokens: Optional override for max tokens
            temperature: Optional override for temperature
            
        Yields:
            Text chunks as they are generated
        """
        max_tok = max_tokens or self.max_tokens
        temp = temperature or self.temperature
        
        try:
            output = self.model(
                prompt,
                max_tokens=max_tok,
                temperature=temp,
                top_p=self.top_p,
                top_k=self.top_k,
                repeat_penalty=self.repeat_penalty,
                stop=["Question de l'élève:", "\n\n\n"],
                stream=True
            )
            
            for chunk in output:
                text = chunk['choices'][0]['text']
                if text:
                    yield text
        except Exception as e:
            self.logger.error(f"Error in streaming generation: {e}")
            raise
    
    def answer_question(
        self,
        question: str,
        context: Optional[str] = None,
        subject: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Answer a student's question with progressive hints.
        
        Args:
            question: Student's question
            context: Optional RAG context
            subject: Optional subject
            stream: Whether to stream output
            
        Returns:
            Generated answer with hints
        """
        self.logger.info(f"Answering question: '{question[:50]}...'")
        
        # Build prompt
        prompt = self.build_prompt(question, context, subject)
        
        # Generate response
        if stream:
            # Return streaming generator
            return self.generate_streaming(prompt)
        else:
            response = self.generate(prompt, stream=False)
            return response
    
    def parse_hints(self, response: str) -> Dict[str, str]:
        """
        Parse response to extract progressive hints.
        
        Args:
            response: LLM response text
            
        Returns:
            Dictionary with hint levels
        """
        hints = {
            'niveau_1': '',
            'niveau_2': '',
            'niveau_3': ''
        }
        
        # Simple parsing based on keywords
        lines = response.split('\n')
        current_level = None
        
        for line in lines:
            line_lower = line.lower()
            
            if 'niveau 1' in line_lower or 'indice 1' in line_lower or 'hint 1' in line_lower:
                current_level = 'niveau_1'
            elif 'niveau 2' in line_lower or 'indice 2' in line_lower or 'hint 2' in line_lower:
                current_level = 'niveau_2'
            elif 'niveau 3' in line_lower or 'indice 3' in line_lower or 'hint 3' in line_lower:
                current_level = 'niveau_3'
            elif current_level and line.strip():
                hints[current_level] += line + '\n'
        
        # Clean up hints
        for key in hints:
            hints[key] = hints[key].strip()
        
        return hints
    
    def add_to_history(self, role: str, content: str) -> None:
        """
        Add message to conversation history.
        
        Args:
            role: Role (user/assistant)
            content: Message content
        """
        self.conversation_history.append({
            'role': role,
            'content': content
        })
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        self.logger.debug("Conversation history cleared")
    
    def get_model_info(self) -> Dict:
        """
        Get information about loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_path': self.model_path,
            'n_ctx': self.n_ctx,
            'n_gpu_layers': self.n_gpu_layers,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'progressive_hints': self.progressive_hints,
            'hint_levels': self.hint_levels
        }


def main():
    """CLI interface for LLM testing."""
    parser = argparse.ArgumentParser(description="Test LLM module")
    parser.add_argument('--question', type=str, required=True, help="Question to ask")
    parser.add_argument('--context', type=str, help="Optional context from RAG")
    parser.add_argument('--subject', type=str, choices=['maths', 'physique', 'anglais'], 
                       help="Subject")
    parser.add_argument('--stream', action='store_true', help="Use streaming output")
    parser.add_argument('--config', type=str, default='config.yaml', help="Config file")
    
    args = parser.parse_args()
    
    setup_logging(level='INFO')
    logger = logging.getLogger(__name__)
    
    # Initialize LLM
    config = get_config(args.config)
    llm = TutorLLM(config)
    
    # Display model info
    info = llm.get_model_info()
    logger.info("LLM Configuration:")
    for key, value in info.items():
        logger.info(f"  {key}: {value}")
    
    # Generate answer
    print("\n" + "=" * 60)
    print("🧠 TUTOR LLM RESPONSE")
    print("=" * 60)
    print(f"\nQuestion: {args.question}")
    if args.subject:
        print(f"Matière: {args.subject}")
    print("\n" + "-" * 60)
    print("Réponse:\n")
    
    if args.stream:
        for chunk in llm.answer_question(
            args.question,
            context=args.context,
            subject=args.subject,
            stream=True
        ):
            print(chunk, end='', flush=True)
        print()
    else:
        response = llm.answer_question(
            args.question,
            context=args.context,
            subject=args.subject,
            stream=False
        )
        print(response)
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
