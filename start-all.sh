#!/bin/bash

# SecureAI - Start All Services
# This script starts all backend and frontend services

echo "🚀 Starting SecureAI Platform..."
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if a port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -t -i:$port)
    if [ ! -z "$pid" ]; then
        echo "⚠️  Killing existing process on port $port (PID: $pid)"
        kill -9 $pid
        sleep 1
    fi
}

# Check and clear ports if needed
echo "📡 Checking ports..."
kill_port 8003
kill_port 8002
kill_port 3002
kill_port 3001

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Starting Configuration Backend (Port 8003)"
echo "════════════════════════════════════════════════════════"
python3 config-backend.py > logs/config-backend.log 2>&1 &
CONFIG_BACKEND_PID=$!
echo "✓ Configuration Backend started (PID: $CONFIG_BACKEND_PID)"
sleep 2

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Starting Healthcare Backend (Port 8002)"
echo "════════════════════════════════════════════════════════"
cd healthcare-chat-demo
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
if [ -f "credentials.sh" ]; then
    source credentials.sh
    echo "✓ Azure OpenAI credentials loaded from credentials.sh"
else
    echo "⚠️  credentials.sh not found. Please create it with your Azure OpenAI credentials."
    echo "   See SETUP.md for details."
    exit 1
fi

uvicorn backend:app --host 0.0.0.0 --port 8002 --reload > ../logs/healthcare-backend.log 2>&1 &
HEALTHCARE_BACKEND_PID=$!
echo "✓ Healthcare Backend started (PID: $HEALTHCARE_BACKEND_PID)"
cd ..
sleep 2

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Starting Healthcare Frontend (Port 3001)"
echo "════════════════════════════════════════════════════════"
cd healthcare-chat-demo/frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi
PORT=3001 npm start > ../../logs/healthcare-frontend.log 2>&1 &
HEALTHCARE_FRONTEND_PID=$!
echo "✓ Healthcare Frontend started (PID: $HEALTHCARE_FRONTEND_PID)"
cd ../..
sleep 3

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Starting Configuration UI (Port 3002)"
echo "════════════════════════════════════════════════════════"
cd configuration-dashboard
if [ ! -d "node_modules" ]; then
    echo "Installing configuration UI dependencies..."
    npm install
fi
PORT=3002 npm start > ../logs/config-ui.log 2>&1 &
CONFIG_UI_PID=$!
echo "✓ Configuration UI started (PID: $CONFIG_UI_PID)"
cd ..
sleep 3

echo ""
echo "════════════════════════════════════════════════════════"
echo "  🎉 All Services Started Successfully!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📍 Access URLs:"
echo "   • Configuration UI:    http://localhost:3002"
echo "   • Healthcare Chat:     http://localhost:3001"
echo "   • Configuration API:   http://localhost:8003"
echo "   • Healthcare API:      http://localhost:8002"
echo ""
echo "📋 Process IDs:"
echo "   • Config Backend:      $CONFIG_BACKEND_PID"
echo "   • Healthcare Backend:  $HEALTHCARE_BACKEND_PID"
echo "   • Healthcare Frontend: $HEALTHCARE_FRONTEND_PID"
echo "   • Configuration UI:    $CONFIG_UI_PID"
echo ""
echo "📝 Logs are available in the logs/ directory"
echo ""
echo "⚠️  Press Ctrl+C to stop all services"
echo "════════════════════════════════════════════════════════"
echo ""

# Save PIDs to a file for stop script
echo "$CONFIG_BACKEND_PID" > /tmp/secureai-pids.txt
echo "$HEALTHCARE_BACKEND_PID" >> /tmp/secureai-pids.txt
echo "$HEALTHCARE_FRONTEND_PID" >> /tmp/secureai-pids.txt
echo "$CONFIG_UI_PID" >> /tmp/secureai-pids.txt

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping all services...'; kill $CONFIG_BACKEND_PID $HEALTHCARE_BACKEND_PID $HEALTHCARE_FRONTEND_PID $CONFIG_UI_PID 2>/dev/null; rm -f /tmp/secureai-pids.txt; echo '✓ All services stopped'; exit 0" INT

# Keep script running
while true; do
    sleep 1
done

