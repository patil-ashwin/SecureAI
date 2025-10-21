#!/bin/bash

# AI-Assisted Discharge Summary System
# Development startup script

echo "🏥 Starting AI-Assisted Discharge Summary System..."
echo ""

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -e ../secureai-sdk
else
    source .venv/bin/activate
fi

# Load Azure OpenAI credentials
if [ -f "../credentials.sh" ]; then
    source ../credentials.sh
    echo "✓ Azure OpenAI credentials loaded from ../credentials.sh"
elif [ -f "credentials.sh" ]; then
    source credentials.sh
    echo "✓ Azure OpenAI credentials loaded from credentials.sh"
else
    echo "⚠️  credentials.sh not found. Please create it in the root directory."
    echo "   See SETUP.md for details."
    exit 1
fi
echo ""

# Start backend
echo "🚀 Starting backend server on http://localhost:8002..."
uvicorn backend:app --host 0.0.0.0 --port 8002 --reload

