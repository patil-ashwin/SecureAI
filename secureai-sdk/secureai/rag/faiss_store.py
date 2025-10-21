"""
FAISS Vector Store for RAG.

Provides in-memory vector similarity search using Facebook's FAISS library.
"""

import numpy as np
from typing import List, Dict, Any, Optional
import logging

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """
    FAISS-based vector store for efficient similarity search.
    
    Uses sentence transformers for embeddings and FAISS for fast nearest neighbor search.
    """

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", embedder: Optional[Any] = None):
        """
        Initialize FAISS vector store.
        
        Args:
            embedding_model: SentenceTransformer model name
        """
        if not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS is not installed. Install with: pip install faiss-cpu"
            )
        
        # Use provided embedder if available; else fallback to SentenceTransformer
        if embedder is not None:
            self.model = embedder
            # Try different ways to get embedding dimension
            if hasattr(embedder, 'get_sentence_embedding_dimension'):
                self.embedding_dim = embedder.get_sentence_embedding_dimension()
            elif hasattr(embedder, 'embedding_dim'):
                self.embedding_dim = embedder.embedding_dim
            else:
                raise ValueError("Embedder must have either get_sentence_embedding_dimension() or embedding_dim attribute")
            self._embedding_model_name = getattr(embedder, "model", None) or "custom"
        else:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(embedding_model)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                self._embedding_model_name = embedding_model
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
        
        # Initialize FAISS index (using L2 distance)
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Store document metadata
        self.documents: List[Dict[str, Any]] = []
        self.doc_ids: List[str] = []
        
        logger.info(f"Initialized FAISS store with {embedding_model}")

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents with 'text', 'doc_id', and optional 'metadata'
        """
        if not documents:
            return
        
        # Extract texts
        texts = [doc.get("text", "") for doc in documents]
        
        # Generate embeddings
        # Check if model is SentenceTransformer (has convert_to_numpy) or custom embedder
        if hasattr(self.model, '__class__') and 'SentenceTransformer' in str(self.model.__class__):
            embeddings = self.model.encode(texts, convert_to_numpy=True)
        else:
            # Custom embedder (Azure, AWS, etc.) - already returns numpy
            embeddings = self.model.encode(texts)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        for doc in documents:
            self.documents.append(doc)
            self.doc_ids.append(doc.get("doc_id", str(len(self.doc_ids))))
        
        logger.info(f"Added {len(documents)} documents to FAISS index")

    def search(
        self, 
        query: str, 
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum similarity score (optional)
        
        Returns:
            List of documents with scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        if hasattr(self.model, '__class__') and 'SentenceTransformer' in str(self.model.__class__):
            query_embedding = self.model.encode([query], convert_to_numpy=True)
        else:
            # Custom embedder
            query_embedding = self.model.encode([query])
        
        # Search FAISS index
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            min(top_k, self.index.ntotal)
        )
        
        # Convert to results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for invalid indices
                continue
            
            # Convert L2 distance to similarity score (inverse)
            # Lower distance = higher similarity
            similarity_score = 1.0 / (1.0 + distance)
            
            # Apply threshold if specified
            if score_threshold and similarity_score < score_threshold:
                continue
            
            doc = self.documents[idx].copy()
            doc['score'] = float(similarity_score)
            doc['distance'] = float(distance)
            doc['rank'] = i + 1
            
            results.append(doc)
        
        return results

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID.
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document or None if not found
        """
        try:
            idx = self.doc_ids.index(doc_id)
            return self.documents[idx]
        except ValueError:
            return None

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document by ID.
        
        Note: FAISS doesn't support deletion efficiently.
        This rebuilds the entire index.
        
        Args:
            doc_id: Document ID
        
        Returns:
            True if deleted, False if not found
        """
        try:
            idx = self.doc_ids.index(doc_id)
        except ValueError:
            return False
        
        # Remove from metadata
        del self.documents[idx]
        del self.doc_ids[idx]
        
        # Rebuild index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        if self.documents:
            texts = [doc.get("text", "") for doc in self.documents]
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            self.index.add(embeddings.astype('float32'))
        
        logger.info(f"Deleted document {doc_id} and rebuilt index")
        return True

    def clear(self) -> None:
        """Clear all documents from the store."""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        self.doc_ids = []
        logger.info("Cleared FAISS index")

    def count(self) -> int:
        """Get number of documents in the store."""
        return self.index.ntotal

    def save(self, path: str) -> None:
        """
        Save index to disk.
        
        Args:
            path: Path to save index
        """
        import pickle
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}.faiss")
        
        # Save metadata
        with open(f"{path}.meta", 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'doc_ids': self.doc_ids,
                'embedding_model': getattr(getattr(self.model, "_model_card_data", None), "model_id", None) or getattr(self, "_embedding_model_name", "unknown"),
                'embedding_dim': self.embedding_dim,
            }, f)
        
        logger.info(f"Saved FAISS index to {path}")

    def load(self, path: str) -> None:
        """
        Load index from disk.
        
        Args:
            path: Path to load index from
        """
        import pickle
        
        # Load FAISS index
        self.index = faiss.read_index(f"{path}.faiss")
        
        # Load metadata
        with open(f"{path}.meta", 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.doc_ids = data['doc_ids']
            self.embedding_dim = data['embedding_dim']
        
        logger.info(f"Loaded FAISS index from {path}")

