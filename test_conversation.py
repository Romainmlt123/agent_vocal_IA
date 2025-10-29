"""
Test script for Conversation Manager.

This script tests the continuous conversation functionality.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import get_config, setup_logging
from src.orchestrator import VocalTutorOrchestrator
from src.conversation_manager import ConversationManager


def test_conversation_manager():
    """Test the conversation manager initialization and basic functionality."""
    
    # Setup
    setup_logging(level='INFO')
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Testing Conversation Manager")
    logger.info("=" * 60)
    
    try:
        # Load config
        logger.info("\n1. Loading configuration...")
        config = get_config()
        logger.info("✅ Config loaded")
        
        # Create orchestrator
        logger.info("\n2. Creating orchestrator...")
        orchestrator = VocalTutorOrchestrator(config)
        logger.info("✅ Orchestrator created")
        
        # Create conversation manager
        logger.info("\n3. Creating conversation manager...")
        conv_mgr = ConversationManager(config, orchestrator)
        logger.info("✅ Conversation manager created")
        
        # Test VAD initialization
        if conv_mgr.vad_model is not None:
            logger.info("✅ VAD model loaded successfully")
        else:
            logger.warning("⚠️ VAD model not loaded (will use fallback)")
        
        # Test state
        logger.info("\n4. Testing state management...")
        assert not conv_mgr.is_active(), "Should not be active initially"
        logger.info("✅ Initial state correct")
        
        # Test parameters
        logger.info("\n5. Testing parameters...")
        logger.info(f"   VAD threshold: {conv_mgr.vad_threshold}")
        logger.info(f"   Min speech duration: {conv_mgr.min_speech_duration_ms}ms")
        logger.info(f"   Min silence duration: {conv_mgr.min_silence_duration_ms}ms")
        logger.info(f"   Speech padding: {conv_mgr.speech_pad_ms}ms")
        logger.info("✅ Parameters loaded")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ All tests passed!")
        logger.info("=" * 60)
        
        logger.info("\n📝 Note: Full conversation test requires:")
        logger.info("   - Microphone access")
        logger.info("   - Audio playback capability")
        logger.info("   - Models downloaded")
        logger.info("\n   Use the Gradio UI to test the complete conversation flow.")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
        return False


def main():
    """Main test function."""
    success = test_conversation_manager()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
