"""Vector database types and interfaces."""

from enum import Enum


class VectorDBType(str, Enum):
    """Supported vector database types."""

    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    CHROMADB = "chromadb"
    PGVECTOR = "pgvector"
    FAISS = "faiss"  # Facebook AI Similarity Search
    MEMORY = "memory"  # In-memory for testing

    def __str__(self) -> str:
        return self.value

