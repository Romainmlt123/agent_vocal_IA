"""
Agent Vocal IA - Tuteur éducatif 100% local.

Modules principaux:
    - asr: Reconnaissance vocale (Faster-Whisper + Silero VAD)
    - rag: Système RAG (FAISS + SentenceTransformers)
    - llm: Génération de texte (llama-cpp-python)
    - tts: Synthèse vocale (Piper-TTS)
    - orchestrator: Orchestration du pipeline complet
    - utils: Utilitaires et helpers
"""

__version__ = "1.0.0"
__author__ = "Romain Mallet - Intelligence Lab"

from . import utils

__all__ = ["utils", "__version__", "__author__"]
