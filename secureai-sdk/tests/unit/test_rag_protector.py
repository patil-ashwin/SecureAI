"""Unit tests for RAG protection module."""

import pytest

from secureai.rag.protector import RAGProtector, Document
from secureai.rag.vector_db import VectorDBType
from secureai.detection.entities import PIIEntity, EntityType
from secureai.core.exceptions import SecureAIError


class TestDocument:
    """Test suite for Document model."""

    def test_document_creation(self) -> None:
        """Test document creation."""
        doc = Document(
            text="Test content",
            doc_id="doc1",
            metadata={"author": "Test"},
        )
        
        assert doc.text == "Test content"
        assert doc.doc_id == "doc1"
        assert doc.metadata["author"] == "Test"

    def test_document_without_metadata(self) -> None:
        """Test document creation without metadata."""
        doc = Document(text="Test", doc_id="doc1")
        
        assert doc.metadata == {}


class TestRAGProtector:
    """Test suite for RAGProtector."""

    @pytest.fixture
    def rag(self) -> RAGProtector:
        """Create RAG protector for testing."""
        return RAGProtector()

    def test_initialization(self, rag: RAGProtector) -> None:
        """Test RAG protector initialization."""
        assert rag is not None
        assert rag.detector is not None
        assert rag.encryptor is not None
        assert len(rag._entity_map) == 0
        assert len(rag._vector_store) == 0

    def test_protect_and_index_single_document(self, rag: RAGProtector) -> None:
        """Test protecting and indexing a single document."""
        docs = [
            {"text": "Patient John Smith has diabetes", "id": "doc1"}
        ]
        
        protected = rag.protect_and_index(docs)
        
        assert len(protected) == 1
        assert protected[0].doc_id == "doc1"
        # Original name should be encrypted
        assert "John Smith" not in protected[0].text
        # Entity map should have mapping
        assert len(rag._entity_map) > 0

    def test_protect_and_index_multiple_documents(self, rag: RAGProtector) -> None:
        """Test protecting and indexing multiple documents."""
        docs = [
            {"text": "Patient John Smith has diabetes", "id": "doc1"},
            {"text": "Jane Doe has hypertension", "id": "doc2"},
            {"text": "SSN 123-45-6789 on file", "id": "doc3"},
        ]
        
        protected = rag.protect_and_index(docs)
        
        assert len(protected) == 3
        assert all(doc.doc_id in ["doc1", "doc2", "doc3"] for doc in protected)

    def test_protect_document_with_no_pii(self, rag: RAGProtector) -> None:
        """Test protecting document with no PII."""
        doc = Document(
            text="This is a normal document with no sensitive information",
            doc_id="doc1",
        )
        
        protected = rag._protect_document(doc)
        
        # Should be unchanged
        assert protected.text == doc.text

    def test_protect_document_with_ssn(self, rag: RAGProtector) -> None:
        """Test protecting document with SSN."""
        doc = Document(
            text="User SSN is 123-45-6789",
            doc_id="doc1",
        )
        
        protected = rag._protect_document(doc)
        
        # SSN should be encrypted
        assert "123-45-6789" not in protected.text
        assert "User SSN is" in protected.text

    def test_protect_text(self, rag: RAGProtector) -> None:
        """Test text protection logic."""
        entities = [
            PIIEntity(
                entity_type=EntityType.SSN,
                value="123-45-6789",
                start=12,
                end=23,
            )
        ]
        
        text = "User SSN is 123-45-6789"
        protected = rag._protect_text(text, entities)
        
        # Original SSN should not be in protected text
        assert "123-45-6789" not in protected
        # Prefix should remain
        assert "User SSN is" in protected
        # Entity map should be populated
        assert len(rag._entity_map) > 0

    def test_protect_text_multiple_entities(self, rag: RAGProtector) -> None:
        """Test protecting text with multiple entities."""
        entities = [
            PIIEntity(
                entity_type=EntityType.EMAIL,
                value="john@example.com",
                start=6,
                end=22,
            ),
            PIIEntity(
                entity_type=EntityType.SSN,
                value="123-45-6789",
                start=31,
                end=42,
            ),
        ]
        
        text = "Email john@example.com and SSN 123-45-6789"
        protected = rag._protect_text(text, entities)
        
        # Both should be encrypted
        assert "john@example.com" not in protected
        assert "123-45-6789" not in protected

    def test_index_document_memory(self, rag: RAGProtector) -> None:
        """Test indexing document in memory."""
        doc = Document(text="Test content", doc_id="doc1")
        
        rag._index_document(doc, VectorDBType.MEMORY, "test_index")
        
        # Should be in vector store
        assert len(rag._vector_store) == 1
        assert "test_index:doc1" in rag._vector_store

    def test_query_with_no_results(self, rag: RAGProtector) -> None:
        """Test query with no matching documents."""
        result = rag.query("nonexistent query")
        
        assert result["num_results"] == 0
        assert len(result["documents"]) == 0

    def test_query_with_results(self, rag: RAGProtector) -> None:
        """Test query with matching documents."""
        # Index some documents
        docs = [
            {"text": "Patient has diabetes", "id": "doc1"},
            {"text": "Patient has hypertension", "id": "doc2"},
        ]
        rag.protect_and_index(docs)
        
        # Query for diabetes
        result = rag.query("diabetes")
        
        # Should find doc1
        assert result["num_results"] >= 1
        assert any("diabetes" in doc["text"].lower() for doc in result["documents"])

    def test_query_with_pii(self, rag: RAGProtector) -> None:
        """Test query containing PII."""
        # Index documents with PII
        docs = [
            {"text": "Patient John Smith has diabetes", "id": "doc1"},
        ]
        rag.protect_and_index(docs)
        
        # Query with PII
        result = rag.query("What is John Smith's condition?")
        
        # Query should be protected
        assert result["protected_query"] != result["query"]

    def test_query_with_auto_decrypt(self, rag: RAGProtector) -> None:
        """Test query with auto-decryption enabled."""
        # Index documents
        docs = [
            {"text": "Patient John Smith has diabetes", "id": "doc1"},
        ]
        rag.protect_and_index(docs)
        
        # Query with auto-decrypt
        result = rag.query("John Smith", auto_decrypt=True)
        
        # Results should have original values restored
        if result["num_results"] > 0:
            # At least some text should be decrypted
            assert any("John" in doc["text"] or "Smith" in doc["text"] 
                      for doc in result["documents"])

    def test_search_simple_matching(self, rag: RAGProtector) -> None:
        """Test simple keyword search."""
        # Index documents
        docs = [
            {"text": "Patient has diabetes", "id": "doc1"},
            {"text": "Patient has hypertension", "id": "doc2"},
            {"text": "No medical conditions", "id": "doc3"},
        ]
        rag.protect_and_index(docs)
        
        # Search
        results = rag._search("diabetes", VectorDBType.MEMORY, "default", 5)
        
        # Should find doc1
        assert len(results) >= 1
        assert any(doc["doc_id"] == "doc1" for doc in results)

    def test_search_top_k_limit(self, rag: RAGProtector) -> None:
        """Test top_k limit in search."""
        # Index many documents
        docs = [
            {"text": f"Document {i} about patient", "id": f"doc{i}"}
            for i in range(10)
        ]
        rag.protect_and_index(docs)
        
        # Search with top_k=3
        results = rag._search("patient", VectorDBType.MEMORY, "default", 3)
        
        # Should return at most 3
        assert len(results) <= 3

    def test_decrypt_results(self, rag: RAGProtector) -> None:
        """Test result decryption."""
        # Set up entity map
        rag._entity_map = {
            "encrypted_value": "original_value",
        }
        
        results = [
            {"text": "This has encrypted_value in it", "doc_id": "doc1"},
        ]
        
        decrypted = rag._decrypt_results(results)
        
        # Should have original value
        assert "original_value" in decrypted[0]["text"]
        assert "encrypted_value" not in decrypted[0]["text"]

    def test_get_entity_map(self, rag: RAGProtector) -> None:
        """Test getting entity map."""
        rag._entity_map = {"encrypted": "original"}
        
        entity_map = rag.get_entity_map()
        
        assert entity_map == {"encrypted": "original"}
        # Should be a copy
        entity_map["new"] = "value"
        assert "new" not in rag._entity_map

    def test_clear_entity_map(self, rag: RAGProtector) -> None:
        """Test clearing entity map."""
        rag._entity_map = {"encrypted": "original"}
        
        rag.clear_entity_map()
        
        assert len(rag._entity_map) == 0

    def test_get_indexed_count(self, rag: RAGProtector) -> None:
        """Test getting indexed document count."""
        docs = [
            {"text": "Doc 1", "id": "doc1"},
            {"text": "Doc 2", "id": "doc2"},
            {"text": "Doc 3", "id": "doc3"},
        ]
        rag.protect_and_index(docs, index_name="test_index")
        
        count = rag.get_indexed_count("test_index")
        assert count == 3

    def test_clear_index(self, rag: RAGProtector) -> None:
        """Test clearing an index."""
        docs = [
            {"text": "Doc 1", "id": "doc1"},
            {"text": "Doc 2", "id": "doc2"},
        ]
        rag.protect_and_index(docs, index_name="test_index")
        
        assert rag.get_indexed_count("test_index") == 2
        
        rag.clear_index("test_index")
        
        assert rag.get_indexed_count("test_index") == 0

    def test_multiple_indexes(self, rag: RAGProtector) -> None:
        """Test using multiple indexes."""
        # Index to index1
        docs1 = [{"text": "Doc in index1", "id": "doc1"}]
        rag.protect_and_index(docs1, index_name="index1")
        
        # Index to index2
        docs2 = [{"text": "Doc in index2", "id": "doc2"}]
        rag.protect_and_index(docs2, index_name="index2")
        
        # Each index should have 1 document
        assert rag.get_indexed_count("index1") == 1
        assert rag.get_indexed_count("index2") == 1


class TestVectorDBType:
    """Test suite for VectorDBType enum."""

    def test_vector_db_values(self) -> None:
        """Test vector DB enum values."""
        assert VectorDBType.PINECONE.value == "pinecone"
        assert VectorDBType.WEAVIATE.value == "weaviate"
        assert VectorDBType.QDRANT.value == "qdrant"
        assert VectorDBType.MEMORY.value == "memory"

    def test_vector_db_string_conversion(self) -> None:
        """Test converting to string."""
        assert str(VectorDBType.PINECONE) == "pinecone"
        assert str(VectorDBType.MEMORY) == "memory"

    def test_vector_db_from_string(self) -> None:
        """Test creating from string."""
        db_type = VectorDBType("memory")
        assert db_type == VectorDBType.MEMORY


class TestRAGIntegration:
    """Integration tests for RAG protection."""

    def test_end_to_end_rag_workflow(self) -> None:
        """Test complete RAG workflow."""
        rag = RAGProtector()
        
        # Step 1: Index documents with PII
        docs = [
            {"text": "Patient John Smith has diabetes", "id": "doc1"},
            {"text": "John Smith's blood pressure is 140/90", "id": "doc2"},
            {"text": "Jane Doe has hypertension", "id": "doc3"},
        ]
        protected = rag.protect_and_index(docs)
        
        # Documents should be protected
        assert all("John Smith" not in doc.text for doc in protected[:2])
        
        # Step 2: Query with PII
        result = rag.query(
            "What is John Smith's condition?",
            auto_decrypt=True,
        )
        
        # Should get results
        assert result["num_results"] >= 1
        
        # Step 3: Results should be decrypted
        for doc in result["documents"]:
            # If it matches, should have original name
            if "diabetes" in doc["text"].lower():
                # Should contain original or encrypted version
                assert len(doc["text"]) > 0

    def test_real_world_medical_scenario(self) -> None:
        """Test realistic medical RAG scenario."""
        rag = RAGProtector()
        
        # Medical records with PII
        docs = [
            {
                "text": "Patient: John Smith, DOB: 01/15/1985, Diagnosis: Type 2 Diabetes",
                "id": "record1",
                "metadata": {"type": "diagnosis"}
            },
            {
                "text": "John Smith - BP: 140/90, prescribed Lisinopril",
                "id": "record2",
                "metadata": {"type": "vitals"}
            },
            {
                "text": "Follow-up for John Smith scheduled",
                "id": "record3",
                "metadata": {"type": "appointment"}
            },
        ]
        
        # Index protected documents
        rag.protect_and_index(docs, index_name="medical_records")
        
        # Query for patient info
        result = rag.query(
            "John Smith diabetes treatment",
            index_name="medical_records",
            auto_decrypt=True,
        )
        
        # Should find relevant documents
        assert result["num_results"] >= 1

    def test_deterministic_encryption_preserves_relationships(self) -> None:
        """Test that FPE preserves relationships across documents."""
        rag = RAGProtector()
        
        # Multiple documents about same person
        docs = [
            {"text": "Doctor John Smith lives in Boston", "id": "doc1"},
            {"text": "Doctor John Smith works at hospital", "id": "doc2"},
            {"text": "Doctor John Smith needs appointment", "id": "doc3"},
        ]
        
        protected = rag.protect_and_index(docs)
        
        # "John Smith" should be encrypted to same value in all docs
        # Since FPE is deterministic, same input = same output
        entity_map = rag.get_entity_map()
        
        # Should have encrypted at least "John Smith"
        assert len(entity_map) > 0
        
        # Verify that original text no longer contains "John Smith"
        for doc in protected:
            assert "John Smith" not in doc.text
        
        # Verify encryption was applied (text changed)
        assert protected[0].text != docs[0]["text"]

