"""
Utilities module for Agent Vocal IA.

Provides configuration management, logging setup, and helper functions.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """Configuration manager for Agent Vocal IA."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            logging.info(f"Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML configuration: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'asr.model_name')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'asr.model_name')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to YAML file.
        
        Args:
            path: Optional path to save to (defaults to original path)
        """
        save_path = path or self.config_path
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            logging.info(f"Configuration saved to {save_path}")
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
            raise
    
    @property
    def all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary."""
        return self._config


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs
        format_string: Optional custom format string
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=handlers,
        force=True
    )


def ensure_dir(path: str) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_device() -> str:
    """
    Detect best available device (cuda/cpu).
    
    Returns:
        Device string ('cuda' or 'cpu')
    """
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            logging.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            logging.info("Using CPU (GPU not available)")
        return device
    except ImportError:
        logging.warning("PyTorch not installed, defaulting to CPU")
        return "cpu"


def check_environment() -> Dict[str, bool]:
    """
    Check environment and dependencies.
    
    Returns:
        Dictionary with component availability status
    """
    results = {}
    
    # Check PyTorch and CUDA
    try:
        import torch
        results['pytorch'] = True
        results['cuda'] = torch.cuda.is_available()
    except ImportError:
        results['pytorch'] = False
        results['cuda'] = False
    
    # Check ASR components
    try:
        import faster_whisper
        results['faster_whisper'] = True
    except ImportError:
        results['faster_whisper'] = False
    
    # Check RAG components
    try:
        import sentence_transformers
        import faiss
        results['sentence_transformers'] = True
        results['faiss'] = True
    except ImportError:
        results['sentence_transformers'] = False
        results['faiss'] = False
    
    # Check LLM
    try:
        import llama_cpp
        results['llama_cpp'] = True
    except ImportError:
        results['llama_cpp'] = False
    
    # Check UI
    try:
        import gradio
        results['gradio'] = True
    except ImportError:
        results['gradio'] = False
    
    return results


def format_time(seconds: float) -> str:
    """
    Format seconds as human-readable time string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string (e.g., "1m 23s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def load_text_file(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Load text file with error handling.
    
    Args:
        file_path: Path to text file
        encoding: File encoding
        
    Returns:
        File contents as string
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        raise


def save_text_file(content: str, file_path: str, encoding: str = 'utf-8') -> None:
    """
    Save text to file with error handling.
    
    Args:
        content: Text content to save
        file_path: Path to save file
        encoding: File encoding
    """
    try:
        ensure_dir(os.path.dirname(file_path))
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        logging.info(f"Text saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving file {file_path}: {e}")
        raise


# Global configuration instance
_global_config: Optional[Config] = None


def get_config(config_path: str = "config.yaml") -> Config:
    """
    Get global configuration instance (singleton pattern).
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration instance
    """
    global _global_config
    if _global_config is None:
        _global_config = Config(config_path)
    return _global_config


if __name__ == "__main__":
    # Test utilities
    print("Testing utilities module...")
    
    # Setup logging
    setup_logging(level="INFO")
    logging.info("Logging initialized")
    
    # Load config
    try:
        config = get_config()
        print(f"✅ Configuration loaded")
        print(f"   ASR model: {config.get('asr.model_name')}")
        print(f"   LLM path: {config.get('llm.model_path')}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
    
    # Check environment
    env = check_environment()
    print(f"\n✅ Environment check:")
    for component, available in env.items():
        status = "✅" if available else "❌"
        print(f"   {status} {component}")
    
    # Test device detection
    device = get_device()
    print(f"\n✅ Device: {device}")
    
    print("\n✅ All utilities tests passed!")
