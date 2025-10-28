"""
RAG Build Module - Document indexing for Agent Vocal IA.

This module handles document processing, chunking, embedding generation,
and FAISS index creation for the RAG (Retrieval Augmented Generation) system.
"""

import argparse
import logging
import os
import pickle
from pathlib import Path
from typing import Dict, List, Tuple

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from .utils import Config, ensure_dir, get_config, setup_logging


class DocumentProcessor:
    """Process and chunk documents for RAG indexing."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Maximum size of text chunks
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logging.getLogger(__name__)
    
    def load_pdf(self, file_path: str) -> str:
        """
        Load text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            self.logger.info(f"Loaded PDF: {file_path} ({len(reader.pages)} pages)")
            return text
        except Exception as e:
            self.logger.error(f"Error loading PDF {file_path}: {e}")
            raise
    
    def load_txt(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Load text from TXT file.
        
        Args:
            file_path: Path to TXT file
            encoding: File encoding
            
        Returns:
            File contents
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()
            self.logger.info(f"Loaded TXT: {file_path}")
            return text
        except Exception as e:
            self.logger.error(f"Error loading TXT {file_path}: {e}")
            raise
    
    def load_document(self, file_path: str) -> str:
        """
        Load document based on file extension.
        
        Args:
            file_path: Path to document
            
        Returns:
            Document text
        """
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            return self.load_pdf(file_path)
        elif ext in ['.txt', '.md']:
            return self.load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if metadata is None:
            metadata = {}
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings
                for punct in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                    last_punct = chunk_text.rfind(punct)
                    if last_punct > self.chunk_size * 0.5:  # At least 50% into chunk
                        chunk_text = chunk_text[:last_punct + 1]
                        end = start + last_punct + 1
                        break
            
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text.strip(),
                    'metadata': metadata.copy(),
                    'char_start': start,
                    'char_end': end
                })
            
            start = end - self.chunk_overlap
        
        self.logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def process_directory(self, directory: str, subject: str) -> List[Dict]:
        """
        Process all documents in a directory.
        
        Args:
            directory: Path to directory containing documents
            subject: Subject name (maths, physique, anglais)
            
        Returns:
            List of all chunks with metadata
        """
        all_chunks = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            self.logger.warning(f"Directory not found: {directory}")
            return all_chunks
        
        # Find all supported files
        files = list(directory_path.glob('*.pdf')) + \
                list(directory_path.glob('*.txt')) + \
                list(directory_path.glob('*.md'))
        
        self.logger.info(f"Found {len(files)} documents in {directory}")
        
        for file_path in files:
            try:
                text = self.load_document(str(file_path))
                metadata = {
                    'source': str(file_path),
                    'filename': file_path.name,
                    'subject': subject
                }
                chunks = self.chunk_text(text, metadata)
                all_chunks.extend(chunks)
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
        
        self.logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks


class RAGIndexBuilder:
    """Build FAISS index for RAG retrieval."""
    
    def __init__(self, config: Config):
        """
        Initialize RAG index builder.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load embedding model
        model_name = config.get('rag.embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        self.logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        self.processor = DocumentProcessor(
            chunk_size=config.get('rag.chunk_size', 512),
            chunk_overlap=config.get('rag.chunk_overlap', 50)
        )
    
    def generate_embeddings(self, chunks: List[Dict]) -> np.ndarray:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        texts = [chunk['text'] for chunk in chunks]
        self.logger.info(f"Generating embeddings for {len(texts)} chunks...")
        
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        self.logger.info(f"Generated embeddings: shape {embeddings.shape}")
        return embeddings
    
    def build_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Build FAISS index from embeddings.
        
        Args:
            embeddings: Numpy array of embeddings
            
        Returns:
            FAISS index
        """
        self.logger.info("Building FAISS index...")
        
        # Use IndexFlatIP for cosine similarity (with normalized embeddings)
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings.astype('float32'))
        
        self.logger.info(f"FAISS index built: {index.ntotal} vectors")
        return index
    
    def save_index(self, index: faiss.Index, chunks: List[Dict], subject: str) -> None:
        """
        Save FAISS index and chunk metadata.
        
        Args:
            index: FAISS index
            chunks: List of chunk dictionaries
            subject: Subject name
        """
        index_dir = Path(self.config.get('rag.index_dir', 'data/indices'))
        ensure_dir(str(index_dir))
        
        # Save FAISS index
        index_path = index_dir / f"{subject}.index"
        faiss.write_index(index, str(index_path))
        self.logger.info(f"FAISS index saved: {index_path}")
        
        # Save chunks metadata
        chunks_path = index_dir / f"{subject}_chunks.pkl"
        with open(chunks_path, 'wb') as f:
            pickle.dump(chunks, f)
        self.logger.info(f"Chunks metadata saved: {chunks_path}")
    
    def build_for_subject(self, subject: str, input_dir: str = None) -> Tuple[faiss.Index, List[Dict]]:
        """
        Build complete RAG index for a subject.
        
        Args:
            subject: Subject name (maths, physique, anglais)
            input_dir: Optional input directory (defaults to data/{subject})
            
        Returns:
            Tuple of (FAISS index, chunks list)
        """
        if input_dir is None:
            input_dir = f"data/{subject}"
        
        self.logger.info(f"Building RAG index for subject: {subject}")
        self.logger.info(f"Input directory: {input_dir}")
        
        # Process documents
        chunks = self.processor.process_directory(input_dir, subject)
        
        if not chunks:
            raise ValueError(f"No documents found in {input_dir}")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)
        
        # Build index
        index = self.build_index(embeddings)
        
        # Save index and metadata
        self.save_index(index, chunks, subject)
        
        self.logger.info(f"✅ RAG index built successfully for {subject}")
        return index, chunks


def main():
    """CLI interface for building RAG indices."""
    parser = argparse.ArgumentParser(description="Build RAG index for Agent Vocal IA")
    parser.add_argument(
        '--subject',
        type=str,
        required=True,
        choices=['maths', 'physique', 'anglais', 'all'],
        help="Subject to build index for"
    )
    parser.add_argument(
        '--input',
        type=str,
        help="Input directory with documents (default: data/{subject})"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help="Path to configuration file"
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = get_config(args.config)
    
    # Build indices
    builder = RAGIndexBuilder(config)
    
    if args.subject == 'all':
        subjects = config.get('rag.subjects', ['maths', 'physique', 'anglais'])
    else:
        subjects = [args.subject]
    
    for subject in subjects:
        try:
            input_dir = args.input or f"data/{subject}"
            builder.build_for_subject(subject, input_dir)
        except Exception as e:
            logger.error(f"Error building index for {subject}: {e}")
    
    logger.info("✅ All indices built successfully!")


if __name__ == "__main__":
    main()
