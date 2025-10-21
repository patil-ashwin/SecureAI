# SecureAI Python SDK

AI Privacy Protection Platform - Protect sensitive data in AI/ML workloads with Format-Preserving Encryption (FPE).

## Features

- 🔒 **Format-Preserving Encryption (FPE)**: Encrypt PII while maintaining data format and AI utility
- 🔍 **Automatic PII Detection**: Regex + NER-based detection of sensitive entities
- 🤖 **LLM Protection**: Secure ChatGPT/Claude integrations with automatic PII encryption
- 📚 **Secure RAG**: Privacy-safe Retrieval-Augmented Generation over sensitive documents
- 📝 **Auto-Log Masking**: Automatically mask PII in all log messages (zero code changes)
- 🎯 **Policy-Based**: Centrally managed policies with automatic SDK sync
- 🔐 **Role-Based Access**: Different users see different data based on permissions
- 📊 **Audit Trail**: Complete logging of all PII access and transformations

## Installation

### Basic Installation

```bash
pip install secureai
```

### With Optional Dependencies

```bash
# For advanced PII detection
pip install secureai[pii-detection]

# For FastAPI integration
pip install secureai[fastapi]

# For LLM integrations (OpenAI, Anthropic)
pip install secureai[openai,anthropic]

# For RAG with vector databases
pip install secureai[pinecone,weaviate]

# For LangChain integration
pip install secureai[langchain]

# Install everything
pip install secureai[all]
```

## Quick Start

### 1. Initialize SDK

```python
from secureai import SecureAI

# Initialize with API key
SecureAI.init(
    api_key="secai_your_api_key",
    app_id="my-app",
    auto_protect_logs=True  # Automatically mask PII in logs
)
```

### 2. Automatic Log Protection (Zero Code Changes!)

```python
import logging

logger = logging.getLogger(__name__)

# Your existing logging code - unchanged!
logger.info("User john@example.com with SSN 123-45-6789 logged in")

# Actual log output: "User j***@example.com with SSN ***-**-6789 logged in"
# ✅ PII automatically masked based on your policy!
```

### 3. Protect Data Before AI Processing

```python
from secureai import protect, detect_pii

# Detect PII in text
text = "Patient John Smith, SSN: 123-45-6789, has diabetes"
entities = detect_pii(text)
# Returns: [{"type": "PERSON", "value": "John Smith", ...}, {"type": "SSN", ...}]

# Protect text (encrypt PII)
protected = protect(text)
# Returns: "Patient Mike Wilson, SSN: 987-65-4321, has diabetes"
# ✅ AI can still process it normally!
```

### 4. Secure LLM Integration

```python
from secureai.llm import SecureLLM

# Create secure LLM client
llm = SecureLLM(provider="openai", api_key="your_openai_key")

# Use normally - PII automatically protected!
response = llm.chat("Summarize John Smith's medical history")

# SecureAI automatically:
# 1. Detects "John Smith" in prompt
# 2. Encrypts to "Mike Wilson" before sending to OpenAI
# 3. Decrypts response back to "John Smith"
# 4. Logs the interaction for audit
```

### 5. Secure RAG Over Sensitive Documents

```python
from secureai.rag import RAGProtector

# Initialize RAG protector
rag = RAGProtector()

# Index documents with automatic PII protection
documents = [
    {"text": "Patient John Smith has diabetes", "id": "doc1"},
    {"text": "John Smith's blood pressure is 140/90", "id": "doc2"}
]

rag.protect_and_index(
    documents=documents,
    vector_db="pinecone",
    index_name="medical-records"
)

# Query with automatic protection/decryption
response = rag.query(
    query="What is John Smith's condition?",
    user_role="doctor",  # Role-based access
    auto_decrypt=True
)

# Returns: "John Smith has diabetes and blood pressure of 140/90"
# ✅ LLM never saw real PII, but authorized doctor gets decrypted result!
```

### 6. FastAPI Middleware (Auto-Protect All Endpoints)

```python
from fastapi import FastAPI
from secureai.middleware import SecureAIMiddleware

app = FastAPI()

# Add middleware - all endpoints automatically protected!
app.add_middleware(
    SecureAIMiddleware,
    api_key="secai_your_key",
    auto_detect_pii=True,
    encrypt_pii=True
)

@app.post("/patients")
async def create_patient(patient: dict):
    # patient.ssn is already encrypted by middleware
    # You just work with it normally
    db.save(patient)
    return patient
```

## Configuration

### Policy-Based Protection

All protection is controlled by policies configured in the SecureAI platform:

```python
# Policies are automatically synced from central platform
# You can also override locally:

from secureai import SecureAI

SecureAI.init(
    api_key="your_key",
    policies={
        "SSN": {
            "strategy": "FPE",  # Format-Preserving Encryption
            "contexts": ["api", "logs", "llm"]
        },
        "EMAIL": {
            "strategy": "PARTIAL_MASK",
            "pattern": "keep_first_and_domain"
        },
        "CREDIT_CARD": {
            "strategy": "TOKENIZE"
        }
    }
)
```

### Protection Strategies

- **FPE** (Format-Preserving Encryption): Reversible, maintains format
- **PARTIAL_MASK**: Show last N characters (e.g., `***-**-6789`)
- **FULL_MASK**: Complete masking (`***********`)
- **TOKENIZE**: Replace with random token (`TOK_abc123`)
- **HASH**: One-way hashing (for matching)
- **REDACT**: Remove completely (`[REDACTED]`)
- **ALLOW**: No protection (for authorized users)

## Advanced Usage

See [documentation](https://docs.secureai.com) for:
- Custom PII detection rules
- Role-based access control
- Differential privacy
- Vector database integrations
- LangChain/LlamaIndex integration
- Audit log analysis

## Development

```bash
# Clone repository
git clone https://github.com/secureai/secureai-python
cd secureai-python

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=secureai --cov-report=html

# Format code
black .
ruff check --fix .

# Type checking
mypy secureai
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- Documentation: https://docs.secureai.com
- GitHub Issues: https://github.com/secureai/secureai-python/issues
- Email: support@secureai.com

