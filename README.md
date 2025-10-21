# SecureAI - AI Privacy Protection Platform

**Character-based PII/PHI masking system with centralized configuration management**

---

## 🚀 Quick Start

### Start All Services (One Command)
```bash
./start-all.sh
```

This starts:
- ✅ Configuration Backend (Port 8003)
- ✅ Healthcare Backend (Port 8002)
- ✅ Healthcare Frontend (Port 3001)
- ✅ Configuration UI (Port 3002)

### Stop All Services
Press `Ctrl+C` in the terminal running `start-all.sh`

### View Structured Logs
```bash
./view-structured-logs.sh           # View all logs
./view-structured-logs.sh tail      # Follow logs in real-time
./view-structured-logs.sh stats     # Show statistics
```

---

## 📍 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Configuration UI** | http://localhost:3002 | Configure masking rules |
| **Healthcare Chat** | http://localhost:3001 | Demo app with PHI protection |
| **Configuration API** | http://localhost:8003 | Configuration service |
| **Healthcare API** | http://localhost:8002 | Backend API |

---

## 🎯 Key Features

### ✅ Real-Time Configuration
- Centralized configuration management
- Live preview of masking patterns
- Changes sync automatically to all apps
- No deployment needed for config changes

### ✅ Character-Based Masking
- Show first N characters
- Show last N characters
- Show first & last N characters
- Full masking
- Custom patterns
- Format preservation (dashes, spaces)

### ✅ Role-Based Access Control
- **Doctor**: Full PHI access
- **Nurse**: Masked PHI only
- **Supervisor**: Full access + PDF generation
- **Admin**: Full system access

### ✅ PHI Protection
- Automatic PII/PHI detection
- Real-time masking
- AWS Bedrock integration (Claude 3.5 Sonnet)
- Langfuse observability

---

## 📊 Masking Examples

### Credit Card
```
Original:           4532-1234-5678-9012
Show First 4, Last 4: 4532-****-****-9012
Show First 6, Last 2: 4532-1****-****-12
Show Last 8:        ****-****-5678-9012
```

### SSN
```
Original:     123-45-6789
Show Last 4:  ***-**-6789
```

### Email
```
Original:     john.doe@company.com
Custom:       j***@company.com
```

---

## 🏗️ Project Structure

```
SecureAI/
├── config-backend.py              # Configuration API service
├── configuration-dashboard/       # React configuration UI
├── healthcare-chat-demo/          # Healthcare demo application
│   ├── backend.py                # FastAPI backend
│   ├── frontend/                 # React frontend
│   ├── start-dev.sh             # Start demo services
│   └── patient_data.json         # Sample data
├── secureai-sdk/                 # SecureAI Python SDK
│   └── secureai/                # Core library
├── logs/                         # Application logs
├── config.json                   # Configuration storage
├── start-all.sh                  # Start all services
├── view-structured-logs.sh       # View structured logs
└── README.md                     # This file
```

---

## 🧪 Test Flow

### 1. Configure Masking Rules
```bash
# Open Configuration UI
http://localhost:3002

# Go to "Masking Strategies" tab
# Select CREDIT_CARD
# Change to "Show First 6, Last 2"
# Watch live preview update
# Click "Save Configuration"
```

### 2. Test in Healthcare App
```bash
# Open Healthcare Chat
http://localhost:3001

# Login as "Nurse Anna Wilson"
# Ask: "Show me patient credit card"
# Verify masked data appears
```

---

---

## 🛠️ Requirements

- Python 3.8+
- Node.js 16+
- npm
- AWS Bedrock access (optional, for AI features)

---

## 📝 Configuration

All configuration is managed through the Configuration UI at http://localhost:3002

Available settings:
- **PHI Detection**: Confidence levels, entity types
- **Masking Strategies**: Pattern-based masking rules
- **Audit Settings**: Logging and retention
- **Role-Based Access**: User permissions
- **System Settings**: API endpoints, sync intervals

---

## 🔧 Development

### Install Dependencies
```bash
# Backend
cd secureai-sdk
pip install -e .

# Frontend
cd configuration-dashboard
npm install

cd healthcare-chat-demo/frontend
npm install
```

### Run Tests
```bash
cd secureai-sdk
pytest
```

---

## 📄 License

MIT License

---

## 🤝 Support

For issues and questions, please refer to:
- This README for complete documentation
- `secureai-sdk/README.md` for SDK-specific details

---

**🎉 Ready to start! Run `./start-all.sh` and open http://localhost:3002**