# SecureAI Setup Guide

## Environment Variables

The application requires Azure OpenAI credentials. These are configured in the startup scripts.

### Required Environment Variables

```bash
# Azure OpenAI Configuration for Embeddings
export AZURE_OPENAI_EMBEDDING_URL="<your-azure-openai-embedding-url>"
export AZURE_OPENAI_EMBEDDING_API_KEY="<your-azure-openai-embedding-api-key>"
export AZURE_OPENAI_EMBEDDING_MODEL="text-embedding-ada-002"
export AZURE_OPENAI_EMBEDDING_DIMENSIONS="1536"

# Azure OpenAI Configuration for LLM
export AZURE_OPENAI_LLM_URL="<your-azure-openai-llm-url>"
export AZURE_OPENAI_LLM_API_KEY="<your-azure-openai-llm-api-key>"
export AZURE_OPENAI_LLM_MODEL="gpt-4.1-mini"
```

### Configuration Note

**Important:** The actual API keys are stored locally in:
1. `.env.template` file (not tracked by git) - contains your actual credentials
2. The shell scripts reference these values directly for convenience

**For Team Members:** 
- Copy `.env.template` to `.env` 
- Update with your own Azure OpenAI credentials
- The startup scripts will load these automatically

## Quick Start

1. Clone the repository
2. Run `./start-all.sh` to start all services
3. Access the applications at:
   - Configuration UI: http://localhost:3002
   - Healthcare Chat: http://localhost:3001
   - Configuration API: http://localhost:8003
   - Healthcare API: http://localhost:8002

## Installation

### Backend Dependencies
```bash
cd secureai-sdk
pip install -e .
```

### Frontend Dependencies
```bash
# Configuration Dashboard
cd configuration-dashboard
npm install

# Healthcare Frontend
cd healthcare-chat-demo/frontend
npm install
```

## Development

See README.md for detailed documentation.

