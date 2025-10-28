"""
Integration tests for Agent Vocal IA.

These tests verify the complete pipeline works end-to-end.
"""

import os
import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.orchestrator import VocalTutorOrchestrator
from src.utils import Config, get_config


@pytest.fixture
def test_config():
    """Create a test configuration."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
asr:
  model_name: "tiny"
  language: "fr"
  device: "cpu"
  compute_type: "int8"
  vad_enabled: false
  sample_rate: 16000

rag:
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  chunk_size: 100
  chunk_overlap: 20
  top_k: 2
  index_dir: "data/indices"

llm:
  model_path: "models/llm/test-model.gguf"
  n_ctx: 512
  n_threads: 2
  n_gpu_layers: 0
  temperature: 0.7
  max_tokens: 100

tts:
  model_path: "models/voices/test-voice.onnx"
  sample_rate: 16000

orchestrator:
  auto_detect_subject: true
  default_subject: "maths"
  audio_output_dir: "outputs/audio"
""")
        config_path = f.name
    
    config = Config(config_path)
    yield config
    os.remove(config_path)


def test_subject_detection():
    """Test automatic subject detection."""
    # Use actual config for this test
    try:
        config = get_config('config.yaml')
        orchestrator = VocalTutorOrchestrator(config)
        
        # Test math detection
        math_text = "Comment résoudre une équation du second degré en mathématiques ?"
        detected = orchestrator.detect_subject(math_text)
        assert detected == 'maths'
        
        # Test physics detection
        physics_text = "Quelle est la force exercée par cette masse ?"
        detected = orchestrator.detect_subject(physics_text)
        assert detected == 'physique'
        
        # Test English detection
        english_text = "How do you conjugate irregular verbs in English?"
        detected = orchestrator.detect_subject(english_text)
        assert detected == 'anglais'
        
    except FileNotFoundError:
        pytest.skip("Config file not found")


def test_conversation_history():
    """Test conversation history management."""
    try:
        config = get_config('config.yaml')
        orchestrator = VocalTutorOrchestrator(config)
        
        # Add some history
        orchestrator.add_to_history("Question 1", "Response 1", "maths")
        orchestrator.add_to_history("Question 2", "Response 2", "physique")
        
        history = orchestrator.get_conversation_history()
        assert len(history) == 2
        assert history[0]['question'] == "Question 1"
        assert history[1]['subject'] == "physique"
        
        # Clear history
        orchestrator.clear_history()
        assert len(orchestrator.get_conversation_history()) == 0
        
    except FileNotFoundError:
        pytest.skip("Config file not found")


def test_orchestrator_status():
    """Test orchestrator status reporting."""
    try:
        config = get_config('config.yaml')
        orchestrator = VocalTutorOrchestrator(config)
        
        status = orchestrator.get_status()
        assert 'current_subject' in status
        assert 'available_subjects' in status
        assert 'conversation_length' in status
        assert 'modules_loaded' in status
        
        # Initially no modules should be loaded
        assert not any(status['modules_loaded'].values())
        
    except FileNotFoundError:
        pytest.skip("Config file not found")


def test_text_processing_mock():
    """Test text processing with mocked components (no real models)."""
    # This test verifies the pipeline structure without loading heavy models
    try:
        config = get_config('config.yaml')
        orchestrator = VocalTutorOrchestrator(config)
        
        # Test that we can create the orchestrator and access its methods
        assert orchestrator.auto_detect_subject == True
        assert orchestrator.default_subject in ['maths', 'physique', 'anglais']
        
        # Test subject setting
        orchestrator.set_subject('maths')
        assert orchestrator.current_subject == 'maths'
        
        # Test invalid subject
        with pytest.raises(ValueError):
            orchestrator.set_subject('invalid_subject')
            
    except FileNotFoundError:
        pytest.skip("Config file not found")


def test_pipeline_error_handling():
    """Test that pipeline handles errors gracefully."""
    try:
        config = get_config('config.yaml')
        orchestrator = VocalTutorOrchestrator(config)
        
        # Test with non-existent audio file
        results = orchestrator.process_audio_file("nonexistent.wav")
        assert results['success'] == False
        assert 'error' in results
        
    except FileNotFoundError:
        pytest.skip("Config file not found")


def test_available_subjects():
    """Test getting available subjects."""
    try:
        config = get_config('config.yaml')
        orchestrator = VocalTutorOrchestrator(config)
        
        subjects = orchestrator.get_available_subjects()
        assert isinstance(subjects, list)
        # Subjects might be empty if indices not built yet
        
    except FileNotFoundError:
        pytest.skip("Config file not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
