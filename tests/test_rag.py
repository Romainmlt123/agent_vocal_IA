"""
Unit tests for RAG module.
"""

import os
import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.rag_build import DocumentProcessor, RAGIndexBuilder
from src.utils import Config


def test_document_processor_chunking():
    """Test text chunking."""
    processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
    
    text = "This is sentence one. This is sentence two. This is sentence three. This is sentence four."
    chunks = processor.chunk_text(text, metadata={'source': 'test'})
    
    assert len(chunks) > 0
    assert all('text' in chunk for chunk in chunks)
    assert all('metadata' in chunk for chunk in chunks)
    assert all(chunk['metadata']['source'] == 'test' for chunk in chunks)


def test_document_processor_load_txt():
    """Test loading text files."""
    processor = DocumentProcessor()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Test content for RAG")
        txt_path = f.name
    
    try:
        text = processor.load_txt(txt_path)
        assert text == "Test content for RAG"
    finally:
        os.remove(txt_path)


def test_chunk_overlap():
    """Test chunk overlap functionality."""
    processor = DocumentProcessor(chunk_size=20, chunk_overlap=5)
    
    text = "A" * 100  # Long repetitive text
    chunks = processor.chunk_text(text)
    
    # Check overlap exists
    if len(chunks) > 1:
        # Last chars of first chunk should appear in second chunk
        assert chunks[0]['text'][-3:] in chunks[1]['text'][:10]


def test_empty_text_handling():
    """Test handling of empty text."""
    processor = DocumentProcessor()
    
    chunks = processor.chunk_text("")
    assert len(chunks) == 0
    
    chunks = processor.chunk_text("   \n  \t  ")
    assert len(chunks) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
