"""
RAG Module - Document retrieval for Agent Vocal IA.

This module handles searching through FAISS indices to retrieve
relevant document chunks for answering questions.
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .utils import Config, get_config


class RAGRetriever:
    """RAG retrieval system for finding relevant document chunks."""
    
    def __init__(self, config: Config, subject: Optional[str] = None):
        """
        Initialize RAG retriever.
        
        Args:
            config: Configuration instance
            subject: Optional subject to load index for
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load embedding model
        model_name = config.get('rag.embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        self.logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        self.index_dir = Path(config.get('rag.index_dir', 'data/indices'))
        self.top_k = config.get('rag.top_k', 3)
        self.similarity_threshold = config.get('rag.similarity_threshold', 0.3)
        
        # Cache for loaded indices
        self._indices: Dict[str, faiss.Index] = {}
        self._chunks: Dict[str, List[Dict]] = {}
        
        # Load subject index if specified
        if subject:
            self.load_index(subject)
    
    def load_index(self, subject: str) -> None:
        """
        Load FAISS index and chunks for a subject.
        
        Args:
            subject: Subject name (maths, physique, anglais)
        """
        if subject in self._indices:
            self.logger.debug(f"Index for {subject} already loaded")
            return
        
        index_path = self.index_dir / f"{subject}.index"
        chunks_path = self.index_dir / f"{subject}_chunks.pkl"
        
        if not index_path.exists():
            raise FileNotFoundError(
                f"Index not found for subject '{subject}'. "
                f"Please build it first using: python -m src.rag_build --subject {subject}"
            )
        
        # Load FAISS index
        self.logger.info(f"Loading FAISS index: {index_path}")
        index = faiss.read_index(str(index_path))
        self._indices[subject] = index
        
        # Load chunks metadata
        self.logger.info(f"Loading chunks metadata: {chunks_path}")
        with open(chunks_path, 'rb') as f:
            chunks = pickle.load(f)
        self._chunks[subject] = chunks
        
        self.logger.info(f"Loaded index for {subject}: {index.ntotal} vectors")
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query.
        
        Args:
            query: Query text
            
        Returns:
            Query embedding vector
        """
        embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding
    
    def search(
        self,
        query: str,
        subject: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> List[Dict]:
        """
        Search for relevant chunks.
        
        Args:
            query: Search query
            subject: Subject to search in
            top_k: Optional override for number of results
            min_score: Optional minimum similarity score
            
        Returns:
            List of relevant chunks with scores
        """
        # Load index if not already loaded
        if subject not in self._indices:
            self.load_index(subject)
        
        index = self._indices[subject]
        chunks = self._chunks[subject]
        
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search
        k = top_k or self.top_k
        scores, indices = index.search(query_embedding, k)
        
        # Filter by threshold and prepare results
        min_score = min_score or self.similarity_threshold
        results = []
        
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(chunks) and score >= min_score:
                chunk = chunks[idx].copy()
                chunk['score'] = float(score)
                chunk['rank'] = len(results) + 1
                results.append(chunk)
        
        self.logger.info(f"Found {len(results)} relevant chunks for query in {subject}")
        return results
    
    def format_context(self, results: List[Dict], max_length: Optional[int] = None) -> str:
        """
        Format search results into context string.
        
        Args:
            results: Search results from search()
            max_length: Optional maximum context length
            
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        context_parts = []
        total_length = 0
        
        for result in results:
            source = result['metadata'].get('filename', 'Unknown')
            text = result['text']
            score = result['score']
            
            part = f"[Source: {source}, Score: {score:.3f}]\n{text}\n"
            part_length = len(part)
            
            if max_length and total_length + part_length > max_length:
                # Try to fit at least one result
                if not context_parts:
                    remaining = max_length - total_length
                    if remaining > 100:
                        context_parts.append(part[:remaining] + "...")
                break
            
            context_parts.append(part)
            total_length += part_length
        
        return "\n".join(context_parts)
    
    def get_sources(self, results: List[Dict]) -> List[Dict]:
        """
        Extract source information from results.
        
        Args:
            results: Search results
            
        Returns:
            List of source dictionaries
        """
        sources = []
        seen = set()
        
        for result in results:
            metadata = result['metadata']
            source_key = (metadata.get('filename'), metadata.get('subject'))
            
            if source_key not in seen:
                sources.append({
                    'filename': metadata.get('filename', 'Unknown'),
                    'subject': metadata.get('subject', 'Unknown'),
                    'score': result['score']
                })
                seen.add(source_key)
        
        return sources
    
    def retrieve_with_context(
        self,
        query: str,
        subject: str,
        top_k: Optional[int] = None,
        max_context_length: Optional[int] = None
    ) -> Tuple[str, List[Dict]]:
        """
        Retrieve relevant chunks and format as context.
        
        Args:
            query: Search query
            subject: Subject to search in
            top_k: Optional number of results
            max_context_length: Optional maximum context length
            
        Returns:
            Tuple of (formatted context, list of sources)
        """
        results = self.search(query, subject, top_k=top_k)
        context = self.format_context(results, max_length=max_context_length)
        sources = self.get_sources(results)
        
        return context, sources
    
    def list_available_subjects(self) -> List[str]:
        """
        List available subjects with indices.
        
        Returns:
            List of subject names
        """
        subjects = []
        for subject in ['maths', 'physique', 'anglais']:
            index_path = self.index_dir / f"{subject}.index"
            if index_path.exists():
                subjects.append(subject)
        return subjects
    
    def get_index_info(self, subject: str) -> Dict:
        """
        Get information about an index.
        
        Args:
            subject: Subject name
            
        Returns:
            Dictionary with index information
        """
        if subject not in self._indices:
            self.load_index(subject)
        
        index = self._indices[subject]
        chunks = self._chunks[subject]
        
        # Get unique sources
        sources = set()
        for chunk in chunks:
            sources.add(chunk['metadata'].get('filename', 'Unknown'))
        
        return {
            'subject': subject,
            'num_vectors': index.ntotal,
            'num_chunks': len(chunks),
            'num_sources': len(sources),
            'sources': sorted(sources)
        }


def main():
    """CLI interface for testing RAG retrieval."""
    import argparse
    from .utils import setup_logging
    
    parser = argparse.ArgumentParser(description="Test RAG retrieval")
    parser.add_argument('--query', type=str, required=True, help="Search query")
    parser.add_argument('--subject', type=str, required=True, 
                       choices=['maths', 'physique', 'anglais'], help="Subject")
    parser.add_argument('--top-k', type=int, default=3, help="Number of results")
    parser.add_argument('--config', type=str, default='config.yaml', help="Config file")
    
    args = parser.parse_args()
    
    setup_logging(level='INFO')
    logger = logging.getLogger(__name__)
    
    # Initialize retriever
    config = get_config(args.config)
    retriever = RAGRetriever(config, subject=args.subject)
    
    # Search
    logger.info(f"Searching for: '{args.query}' in {args.subject}")
    context, sources = retriever.retrieve_with_context(args.query, args.subject, top_k=args.top_k)
    
    # Display results
    print("\n" + "=" * 60)
    print("🔍 SEARCH RESULTS")
    print("=" * 60)
    print(f"\nQuery: {args.query}")
    print(f"Subject: {args.subject}")
    print(f"\n📚 Sources ({len(sources)}):")
    for src in sources:
        print(f"  - {src['filename']} (score: {src['score']:.3f})")
    
    print(f"\n📄 Context:\n")
    print(context)
    print("=" * 60)


if __name__ == "__main__":
    main()
