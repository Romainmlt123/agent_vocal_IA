"""
Unit tests for utilities module.
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.utils import (
    Config,
    ensure_dir,
    format_time,
    get_device,
    load_text_file,
    save_text_file,
    truncate_text,
)


def test_config_loading():
    """Test configuration loading."""
    # Create temp config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
test:
  key1: value1
  nested:
    key2: value2
""")
        config_path = f.name
    
    try:
        config = Config(config_path)
        assert config.get('test.key1') == 'value1'
        assert config.get('test.nested.key2') == 'value2'
        assert config.get('nonexistent', 'default') == 'default'
    finally:
        os.remove(config_path)


def test_config_set_and_save():
    """Test configuration modification and saving."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("test: {}")
        config_path = f.name
    
    try:
        config = Config(config_path)
        config.set('test.newkey', 'newvalue')
        assert config.get('test.newkey') == 'newvalue'
        
        # Save and reload
        config.save()
        config2 = Config(config_path)
        assert config2.get('test.newkey') == 'newvalue'
    finally:
        os.remove(config_path)


def test_ensure_dir():
    """Test directory creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = os.path.join(tmpdir, 'subdir1', 'subdir2')
        result = ensure_dir(test_path)
        assert result.exists()
        assert result.is_dir()


def test_format_time():
    """Test time formatting."""
    assert format_time(30) == "30.0s"
    assert format_time(90) == "1m 30s"
    assert format_time(3661) == "1h 1m"


def test_truncate_text():
    """Test text truncation."""
    text = "This is a long text that needs truncation"
    truncated = truncate_text(text, max_length=20)
    assert len(truncated) <= 20
    assert truncated.endswith("...")
    
    short_text = "Short"
    assert truncate_text(short_text, max_length=20) == short_text


def test_text_file_operations():
    """Test text file loading and saving."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, 'test.txt')
        content = "Test content\nLine 2"
        
        # Save
        save_text_file(content, file_path)
        assert os.path.exists(file_path)
        
        # Load
        loaded = load_text_file(file_path)
        assert loaded == content


def test_get_device():
    """Test device detection."""
    device = get_device()
    assert device in ['cuda', 'cpu']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
