"""LLM Module - Local Language Model using llama-cpp-python"""

from typing import Optional, List, Dict
from llama_cpp import Llama
import os


class LocalLLM:
    """Local Language Model interface using llama.cpp"""
    
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_gpu_layers: int = -1,  # -1 means use all GPU layers
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """Initialize local LLM
        
        Args:
            model_path: Path to GGUF model file
            n_ctx: Context window size
            n_gpu_layers: Number of layers to offload to GPU (-1 for all)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        self.model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False
        )
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None
    ) -> str:
        """Generate text from prompt
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (overrides default)
            max_tokens: Max tokens to generate (overrides default)
            stop: Stop sequences
            
        Returns:
            Generated text
        """
        output = self.model(
            prompt,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stop=stop or [],
            echo=False
        )
        
        return output['choices'][0]['text'].strip()
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate response in chat format
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            Generated response
        """
        # Format messages into a prompt
        prompt = self._format_chat_prompt(messages)
        return self.generate(prompt, temperature, max_tokens)
    
    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into a prompt string
        
        Args:
            messages: List of message dicts
            
        Returns:
            Formatted prompt
        """
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)


class TutorLLM:
    """Tutor-specific LLM wrapper with RAG integration"""
    
    def __init__(
        self,
        model_path: str,
        system_prompt: Optional[str] = None
    ):
        """Initialize tutor LLM
        
        Args:
            model_path: Path to GGUF model file
            system_prompt: System prompt for tutor behavior
        """
        self.llm = LocalLLM(model_path)
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.conversation_history = []
    
    def _default_system_prompt(self) -> str:
        """Get default system prompt for tutor"""
        return """Tu es un tuteur vocal intelligent et bienveillant. 
Tu aides les élèves à comprendre les mathématiques, la physique et l'anglais.
Tu fournis des explications claires, des exemples concrets et tu encourages l'apprentissage.
Réponds de manière concise et pédagogique."""
    
    def answer_question(
        self,
        question: str,
        context: Optional[str] = None,
        subject: Optional[str] = None
    ) -> str:
        """Answer a student question with optional context
        
        Args:
            question: Student's question
            context: Retrieved context from RAG
            subject: Subject area (maths, physique, anglais)
            
        Returns:
            Tutor's response
        """
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add subject-specific context if provided
        if subject:
            messages.append({
                "role": "system",
                "content": f"Le sujet de cette question concerne: {subject}"
            })
        
        # Add retrieved context if available
        if context:
            messages.append({
                "role": "system",
                "content": f"Contexte pertinent:\n{context}"
            })
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        # Generate response
        response = self.llm.chat(messages)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": question})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep only last 6 messages (3 exchanges) to manage context
        if len(self.conversation_history) > 6:
            self.conversation_history = self.conversation_history[-6:]
        
        return response
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
