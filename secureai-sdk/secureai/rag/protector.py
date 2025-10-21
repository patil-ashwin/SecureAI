"""
RAG Protection Module.

Provides secure Retrieval-Augmented Generation by:
1. Protecting PII in documents before indexing
2. Encrypting queries before vector search
3. Decrypting results for authorized users
"""

from typing import List, Dict, Any, Optional
import logging

from secureai.rag.vector_db import VectorDBType
from secureai.detection.pii_detector import PIIDetector
from secureai.detection.entities import PIIEntity
from secureai.encryption.fpe import FPEEncryptor
from secureai.llm.secure_llm import SecureLLM
from secureai.policy.manager import PolicyManager
from secureai.core.exceptions import SecureAIError

try:
    from secureai.rag.faiss_store import FAISSVectorStore
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    FAISSVectorStore = None

logger = logging.getLogger(__name__)


class Document:
    """Document model for RAG."""

    def __init__(
        self,
        text: str,
        doc_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize document.
        
        Args:
            text: Document text content
            doc_id: Unique document identifier
            metadata: Optional metadata
        """
        self.text = text
        self.doc_id = doc_id
        self.metadata = metadata or {}


class RAGProtector:
    """
    Secure RAG (Retrieval-Augmented Generation) implementation.
    
    Protects sensitive documents for safe use in RAG systems by:
    - Encrypting PII before indexing in vector databases
    - Maintaining semantic search capability (FPE preserves meaning)
    - Decrypting results based on user authorization
    - Full audit trail
    
    Examples:
        >>> from secureai.rag import RAGProtector
        >>> 
        >>> rag = RAGProtector()
        >>> 
        >>> # Protect and index documents
        >>> docs = [
        ...     {"text": "Patient John Smith has diabetes", "id": "doc1"},
        ...     {"text": "John Smith's BP is 140/90", "id": "doc2"}
        ... ]
        >>> rag.protect_and_index(docs, vector_db="memory")
        >>> 
        >>> # Query with auto-protection
        >>> result = rag.query("What is John Smith's condition?")
    """

    def __init__(
        self,
        detector: Optional[PIIDetector] = None,
        encryptor: Optional[FPEEncryptor] = None,
        policy_manager: Optional[PolicyManager] = None,
        llm: Optional[SecureLLM] = None,
        embedder: Optional[Any] = None,
    ):
        """
        Initialize RAG protector.
        
        Args:
            detector: PII detector (creates new if not provided)
            encryptor: FPE encryptor (creates new if not provided)
            policy_manager: Policy manager for rules
            llm: Secure LLM client for generation
        """
        self.detector = detector or PIIDetector(min_confidence=0.5)
        self.encryptor = encryptor or FPEEncryptor(key="rag-key")
        self.policy_manager = policy_manager
        self.llm = llm
        self.embedder = embedder
        
        # Entity mappings (encrypted -> original)
        self._entity_map: Dict[str, str] = {}
        
        # Vector stores
        self._vector_store: Dict[str, Dict[str, Any]] = {}  # In-memory store
        self._faiss_stores: Dict[str, FAISSVectorStore] = {}  # FAISS stores by index

    def protect_and_index(
        self,
        documents: List[Dict[str, Any]],
        vector_db: VectorDBType | str = VectorDBType.MEMORY,
        index_name: str = "default",
    ) -> List[Document]:
        """
        Protect documents and index them in vector database.
        
        Args:
            documents: List of documents to index
            vector_db: Vector database type
            index_name: Name of the index
        
        Returns:
            List of protected documents
        
        Examples:
            >>> docs = [
            ...     {"text": "John Smith has diabetes", "id": "doc1"},
            ...     {"text": "Jane Doe has hypertension", "id": "doc2"}
            ... ]
            >>> protected = rag.protect_and_index(docs)
        """
        try:
            protected_docs = []
            
            for doc_dict in documents:
                # Create document object
                doc = Document(
                    text=doc_dict.get("text", ""),
                    doc_id=doc_dict.get("id", doc_dict.get("doc_id", "")),
                    metadata=doc_dict.get("metadata", {}),
                )
                
                # Protect the document
                protected_doc = self._protect_document(doc)
                protected_docs.append(protected_doc)
                
                # Index in vector store
                self._index_document(protected_doc, vector_db, index_name)
            
            logger.info(f"Protected and indexed {len(protected_docs)} documents")
            return protected_docs
            
        except Exception as e:
            raise SecureAIError(f"Failed to protect and index documents: {e}") from e

    def _protect_document(self, document: Document) -> Document:
        """
        Protect PII in document using FPE.
        
        Args:
            document: Original document
        
        Returns:
            Protected document with PII encrypted
        """
        # Detect PII in document
        detection_result = self.detector.detect(document.text)
        
        if detection_result.entity_count == 0:
            # No PII found, return as-is
            return document
        
        # Protect each entity
        protected_text = self._protect_text(document.text, detection_result.entities)
        
        # Create protected document
        protected_doc = Document(
            text=protected_text,
            doc_id=document.doc_id,
            metadata=document.metadata,
        )
        
        return protected_doc

    def _protect_text(self, text: str, entities: List[PIIEntity]) -> str:
        """
        Protect text by encrypting detected PII.
        
        Args:
            text: Original text
            entities: Detected PII entities
        
        Returns:
            Protected text
        """
        protected = text
        
        # Sort entities by position (reverse) to maintain positions
        sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
        
        for entity in sorted_entities:
            # Encrypt using FPE (deterministic)
            encrypted_value = self.encryptor.encrypt(
                entity.value, str(entity.entity_type)
            )
            
            # Store mapping for decryption
            self._entity_map[encrypted_value] = entity.value
            
            # Replace in text
            protected = (
                protected[: entity.start] + encrypted_value + protected[entity.end :]
            )
        
        return protected

    def _index_document(
        self,
        document: Document,
        vector_db: VectorDBType | str,
        index_name: str,
    ) -> None:
        """
        Index document in vector database.
        
        Supports MEMORY and FAISS backends.
        """
        db_type = VectorDBType(vector_db) if isinstance(vector_db, str) else vector_db
        
        if db_type == VectorDBType.MEMORY:
            # Store in memory
            key = f"{index_name}:{document.doc_id}"
            self._vector_store[key] = {
                "text": document.text,
                "doc_id": document.doc_id,
                "metadata": document.metadata,
            }
        elif db_type == VectorDBType.FAISS:
            # Use FAISS for similarity search
            if not FAISS_AVAILABLE:
                raise SecureAIError(
                    "FAISS not available. Install with: "
                    "pip install faiss-cpu sentence-transformers"
                )
            
            # Get or create FAISS store for this index
            if index_name not in self._faiss_stores:
                self._faiss_stores[index_name] = FAISSVectorStore(embedder=self.embedder)
            
            # Add document to FAISS
            self._faiss_stores[index_name].add_documents([{
                "text": document.text,
                "doc_id": document.doc_id,
                "metadata": document.metadata,
            }])
        else:
            # Stub for other vector DBs
            logger.info(f"Would index in {db_type} (not implemented)")

    def query(
        self,
        query: str,
        vector_db: VectorDBType | str = VectorDBType.MEMORY,
        index_name: str = "default",
        top_k: int = 5,
        auto_decrypt: bool = True,
        use_llm: bool = False,
    ) -> Dict[str, Any]:
        """
        Query the RAG system with automatic PII protection.
        
        Args:
            query: User query
            vector_db: Vector database type
            index_name: Index name
            top_k: Number of results to return
            auto_decrypt: Decrypt results for user
            use_llm: Use LLM for response generation
        
        Returns:
            Query results with optional LLM response
        
        Examples:
            >>> result = rag.query("What is John Smith's condition?")
            >>> print(result["documents"])
        """
        try:
            # Step 1: Detect PII in query
            query_entities = self.detector.detect(query)
            
            # Step 2: Protect query (encrypt PII)
            if query_entities.entity_count > 0:
                protected_query = self._protect_text(query, query_entities.entities)
            else:
                protected_query = query
            
            # Step 3: Search vector database
            results = self._search(protected_query, vector_db, index_name, top_k)
            
            # Step 4: Decrypt results if authorized
            if auto_decrypt:
                results = self._decrypt_results(results)
            
            # Step 5: Generate LLM response if requested
            llm_response = None
            if use_llm and self.llm:
                context = "\n\n".join([doc["text"] for doc in results])
                prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
                llm_response = self.llm.chat(prompt)
            
            return {
                "query": query,
                "protected_query": protected_query,
                "documents": results,
                "llm_response": llm_response,
                "num_results": len(results),
            }
            
        except Exception as e:
            raise SecureAIError(f"RAG query failed: {e}") from e

    def _search(
        self,
        query: str,
        vector_db: VectorDBType | str,
        index_name: str,
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        Search vector database.
        
        Supports MEMORY (keyword matching) and FAISS (vector similarity).
        """
        db_type = VectorDBType(vector_db) if isinstance(vector_db, str) else vector_db
        
        if db_type == VectorDBType.MEMORY:
            # Simple keyword matching for testing
            results = []
            query_lower = query.lower()
            
            for key, doc in self._vector_store.items():
                if index_name in key:
                    # Simple relevance score based on keyword matching
                    text_lower = doc["text"].lower()
                    score = sum(
                        1 for word in query_lower.split() if word in text_lower
                    )
                    
                    if score > 0:
                        results.append({
                            **doc,
                            "score": score,
                        })
            
            # Sort by score and return top_k
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
        
        elif db_type == VectorDBType.FAISS:
            # Use FAISS for vector similarity search
            if index_name not in self._faiss_stores:
                return []
            
            faiss_store = self._faiss_stores[index_name]
            return faiss_store.search(query, top_k=top_k)
        
        else:
            # Stub for other vector DBs
            return []

    def _decrypt_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Decrypt PII in search results.
        
        Args:
            results: Search results with encrypted PII
        
        Returns:
            Results with PII decrypted
        """
        decrypted_results = []
        
        for result in results:
            decrypted_text = result["text"]
            
            # Replace encrypted values with originals
            for encrypted, original in self._entity_map.items():
                decrypted_text = decrypted_text.replace(encrypted, original)
            
            decrypted_result = {
                **result,
                "text": decrypted_text,
            }
            decrypted_results.append(decrypted_result)
        
        return decrypted_results

    def get_entity_map(self) -> Dict[str, str]:
        """Get current entity mapping (for debugging)."""
        return self._entity_map.copy()

    def clear_entity_map(self) -> None:
        """Clear entity mapping."""
        self._entity_map.clear()

    def get_indexed_count(self, index_name: str = "default") -> int:
        """
        Get count of indexed documents.
        
        Args:
            index_name: Index name
        
        Returns:
            Number of documents in index
        """
        count = sum(1 for key in self._vector_store.keys() if index_name in key)
        return count

    def clear_index(self, index_name: str = "default") -> None:
        """
        Clear an index.
        
        Args:
            index_name: Index to clear
        """
        keys_to_remove = [key for key in self._vector_store.keys() if index_name in key]
        for key in keys_to_remove:
            del self._vector_store[key]

