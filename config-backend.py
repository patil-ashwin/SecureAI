#!/usr/bin/env python3
"""
SecureAI Configuration Management Backend
Provides centralized configuration storage and sync for all SecureAI applications
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime

app = FastAPI(title="SecureAI Configuration API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory configuration storage (can be replaced with database)
CONFIGURATION_STORE = {}
CONFIG_FILE = "/home/patil/Data/Projects/Python/SecureAI/config.json"

# Configuration Models
class MaskingPattern(BaseModel):
    type: str  # 'show_first', 'show_last', 'show_first_last', 'full_mask', 'custom'
    showFirst: Optional[int] = 0
    showLast: Optional[int] = 0
    maskChar: str = "*"
    separator: Optional[str] = None
    preserveFormat: Optional[bool] = True

class MaskingStrategy(BaseModel):
    enabled: bool
    pattern: MaskingPattern
    context: List[str]
    description: Optional[str] = None

class PHIDetection(BaseModel):
    enabled: bool
    confidence: float
    entities: List[str]
    realTimeDetection: bool

class AuditSettings(BaseModel):
    enabled: bool
    logLevel: str
    retentionDays: int
    realTimeAlerts: bool

class RolePermissions(BaseModel):
    phiAccess: str
    canDecrypt: bool
    canGeneratePDF: bool
    allowedEntities: List[str]

class SystemSettings(BaseModel):
    apiEndpoint: str
    encryptionKey: str
    syncInterval: int
    offlineMode: bool

class Configuration(BaseModel):
    phiDetection: PHIDetection
    maskingStrategies: Dict[str, MaskingStrategy]
    auditSettings: AuditSettings
    roleBasedAccess: Dict[str, RolePermissions]
    systemSettings: SystemSettings

# Default configuration
DEFAULT_CONFIG = {
    "phiDetection": {
        "enabled": True,
        "confidence": 0.6,
        "entities": ["PERSON", "EMAIL", "PHONE", "SSN", "CREDIT_CARD", "DATE_OF_BIRTH", "ADDRESS"],
        "realTimeDetection": True
    },
    "maskingStrategies": {
        "PERSON": {
            "enabled": True,
            "pattern": {
                "type": "show_first",
                "showFirst": 1,
                "showLast": 0,
                "maskChar": "*",
                "preserveFormat": False
            },
            "context": ["API", "LLM", "LOGS"],
            "description": "Show first initial, mask rest (e.g., J*** S***)"
        },
        "EMAIL": {
            "enabled": True,
            "pattern": {
                "type": "custom",
                "showFirst": 1,
                "showLast": 0,
                "maskChar": "*",
                "separator": "@",
                "preserveFormat": True
            },
            "context": ["LOGS", "API"],
            "description": "Show first char and domain (e.g., j***@company.com)"
        },
        "PHONE": {
            "enabled": True,
            "pattern": {
                "type": "show_last",
                "showFirst": 0,
                "showLast": 4,
                "maskChar": "*",
                "preserveFormat": True
            },
            "context": ["API", "LLM", "LOGS"],
            "description": "Show last 4 digits (e.g., ***-***-1234)"
        },
        "SSN": {
            "enabled": True,
            "pattern": {
                "type": "show_last",
                "showFirst": 0,
                "showLast": 4,
                "maskChar": "*",
                "preserveFormat": True
            },
            "context": ["API", "LLM"],
            "description": "Show last 4 digits (e.g., ***-**-1234)"
        },
        "CREDIT_CARD": {
            "enabled": True,
            "pattern": {
                "type": "show_first_last",
                "showFirst": 4,
                "showLast": 4,
                "maskChar": "*",
                "preserveFormat": True
            },
            "context": ["DATABASE", "API", "LOGS"],
            "description": "Show first 4 and last 4 (e.g., 1234-****-****-5678)"
        },
        "DATE_OF_BIRTH": {
            "enabled": True,
            "pattern": {
                "type": "show_last",
                "showFirst": 0,
                "showLast": 4,
                "maskChar": "*",
                "preserveFormat": True
            },
            "context": ["LOGS"],
            "description": "Show only year (e.g., **/**/1985)"
        },
        "ADDRESS": {
            "enabled": True,
            "pattern": {
                "type": "show_last",
                "showFirst": 0,
                "showLast": 15,
                "maskChar": "*",
                "preserveFormat": False
            },
            "context": ["LOGS"],
            "description": "Show city/state only"
        }
    },
    "auditSettings": {
        "enabled": True,
        "logLevel": "INFO",
        "retentionDays": 90,
        "realTimeAlerts": True
    },
    "roleBasedAccess": {
        "doctor": {
            "phiAccess": "full",
            "canDecrypt": True,
            "canGeneratePDF": True,
            "allowedEntities": ["PERSON", "EMAIL", "PHONE", "SSN", "DATE_OF_BIRTH"]
        },
        "nurse": {
            "phiAccess": "masked",
            "canDecrypt": False,
            "canGeneratePDF": False,
            "allowedEntities": ["PERSON", "EMAIL"]
        },
        "supervisor": {
            "phiAccess": "full",
            "canDecrypt": True,
            "canGeneratePDF": True,
            "allowedEntities": ["PERSON", "EMAIL", "PHONE", "SSN", "CREDIT_CARD", "DATE_OF_BIRTH"]
        },
        "admin": {
            "phiAccess": "full",
            "canDecrypt": True,
            "canGeneratePDF": True,
            "allowedEntities": ["PERSON", "EMAIL", "PHONE", "SSN", "CREDIT_CARD", "DATE_OF_BIRTH"]
        }
    },
    "systemSettings": {
        "apiEndpoint": "http://localhost:8002",
        "encryptionKey": "healthcare-phi-key",
        "syncInterval": 5,
        "offlineMode": True
    }
}

# Load configuration from file on startup
def load_config():
    global CONFIGURATION_STORE
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                CONFIGURATION_STORE = json.load(f)
            print(f"✅ Configuration loaded from {CONFIG_FILE}")
        except Exception as e:
            print(f"⚠️ Error loading config file: {e}")
            CONFIGURATION_STORE = DEFAULT_CONFIG
    else:
        CONFIGURATION_STORE = DEFAULT_CONFIG
        save_config()

# Save configuration to file
def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIGURATION_STORE, f, indent=2)
        print(f"✅ Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"⚠️ Error saving config file: {e}")

# API Endpoints
@app.get("/")
async def root():
    return {
        "service": "SecureAI Configuration API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/config",
            "/api/config/masking",
            "/api/config/roles",
            "/api/health"
        ]
    }

@app.get("/api/config")
async def get_configuration():
    """Get current configuration"""
    return CONFIGURATION_STORE

@app.post("/api/config")
async def update_configuration(config: Configuration):
    """Update entire configuration"""
    global CONFIGURATION_STORE
    CONFIGURATION_STORE = config.dict()
    save_config()
    return {
        "status": "success",
        "message": "Configuration updated successfully",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/config/masking")
async def get_masking_config():
    """Get only masking configuration"""
    return {
        "maskingStrategies": CONFIGURATION_STORE.get("maskingStrategies", {}),
        "phiDetection": CONFIGURATION_STORE.get("phiDetection", {})
    }

@app.get("/api/config/masking/{entity}")
async def get_entity_masking(entity: str):
    """Get masking configuration for specific entity"""
    strategies = CONFIGURATION_STORE.get("maskingStrategies", {})
    if entity.upper() not in strategies:
        raise HTTPException(status_code=404, detail=f"Entity {entity} not found")
    return strategies[entity.upper()]

@app.get("/api/config/roles")
async def get_role_config():
    """Get role-based access configuration"""
    return {
        "roleBasedAccess": CONFIGURATION_STORE.get("roleBasedAccess", {})
    }

@app.get("/api/config/roles/{role}")
async def get_role_permissions(role: str):
    """Get permissions for specific role"""
    roles = CONFIGURATION_STORE.get("roleBasedAccess", {})
    if role not in roles:
        raise HTTPException(status_code=404, detail=f"Role {role} not found")
    return roles[role]

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SecureAI Configuration API",
        "timestamp": datetime.now().isoformat(),
        "config_loaded": bool(CONFIGURATION_STORE),
        "entities_configured": len(CONFIGURATION_STORE.get("maskingStrategies", {})),
        "roles_configured": len(CONFIGURATION_STORE.get("roleBasedAccess", {}))
    }

@app.post("/api/config/reset")
async def reset_configuration():
    """Reset configuration to defaults"""
    global CONFIGURATION_STORE
    CONFIGURATION_STORE = DEFAULT_CONFIG.copy()
    save_config()
    return {
        "status": "success",
        "message": "Configuration reset to defaults",
        "timestamp": datetime.now().isoformat()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    load_config()
    print("🚀 SecureAI Configuration API started")
    print(f"📍 Configuration file: {CONFIG_FILE}")
    print(f"🔧 Entities configured: {len(CONFIGURATION_STORE.get('maskingStrategies', {}))}")
    print(f"👥 Roles configured: {len(CONFIGURATION_STORE.get('roleBasedAccess', {}))}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
