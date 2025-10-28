"""RAG Module - Retrieval Augmented Generation using FAISS and SentenceTransformers"""

import os
import numpy as np
from typing import List, Tuple, Optional
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import json
from pathlib import Path


class DocumentStore:
    """Document storage and retrieval using FAISS"""
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        index_path: Optional[str] = None
    ):
        """Initialize document store
        
        Args:
            embedding_model: SentenceTransformer model name
            index_path: Path to save/load FAISS index
        """
        self.encoder = SentenceTransformer(embedding_model)
        self.dimension = self.encoder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.metadata = []
        self.index_path = index_path
        
        if index_path and os.path.exists(index_path):
            self.load_index(index_path)
    
    def add_documents(
        self,
        texts: List[str],
        metadata: Optional[List[dict]] = None
    ):
        """Add documents to the store
        
        Args:
            texts: List of document texts
            metadata: Optional metadata for each document
        """
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        self.index.add(embeddings)
        self.documents.extend(texts)
        
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{} for _ in texts])
    
    def search(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[str, float, dict]]:
        """Search for relevant documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (document, score, metadata) tuples
        """
        query_embedding = self.encoder.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((
                    self.documents[idx],
                    float(distance),
                    self.metadata[idx]
                ))
        
        return results
    
    def save_index(self, path: str):
        """Save FAISS index and documents
        
        Args:
            path: Directory path to save index
        """
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        
        # Save documents and metadata
        with open(os.path.join(path, "documents.pkl"), "wb") as f:
            pickle.dump(self.documents, f)
        
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(self.metadata, f)
    
    def load_index(self, path: str):
        """Load FAISS index and documents
        
        Args:
            path: Directory path to load index from
        """
        # Load FAISS index
        index_file = os.path.join(path, "index.faiss")
        if os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
        
        # Load documents
        docs_file = os.path.join(path, "documents.pkl")
        if os.path.exists(docs_file):
            with open(docs_file, "rb") as f:
                self.documents = pickle.load(f)
        
        # Load metadata
        meta_file = os.path.join(path, "metadata.json")
        if os.path.exists(meta_file):
            with open(meta_file, "r") as f:
                self.metadata = json.load(f)


class RAGRetriever:
    """RAG system for context retrieval"""
    
    def __init__(
        self,
        data_dirs: List[str],
        index_dir: str = "data/index"
    ):
        """Initialize RAG retriever
        
        Args:
            data_dirs: List of directories containing documents
            index_dir: Directory to store FAISS index
        """
        self.document_store = DocumentStore(index_path=index_dir)
        self.data_dirs = data_dirs
        self.index_dir = index_dir
        
    def index_documents(self):
        """Index all documents from data directories"""
        all_texts = []
        all_metadata = []
        
        for data_dir in self.data_dirs:
            if not os.path.exists(data_dir):
                continue
                
            for file_path in Path(data_dir).rglob("*.txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Split into chunks for better retrieval
                    chunks = self._split_text(content)
                    all_texts.extend(chunks)
                    all_metadata.extend([{
                        "source": str(file_path),
                        "subject": os.path.basename(data_dir)
                    } for _ in chunks])
        
        if all_texts:
            self.document_store.add_documents(all_texts, all_metadata)
            self.document_store.save_index(self.index_dir)
    
    def retrieve_context(
        self,
        query: str,
        k: int = 3
    ) -> str:
        """Retrieve relevant context for a query
        
        Args:
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            Concatenated context string
        """
        results = self.document_store.search(query, k=k)
        context = "\n\n".join([doc for doc, _, _ in results])
        return context
    
    def _split_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """Split text into overlapping chunks
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += chunk_size - overlap
        
        return chunks
