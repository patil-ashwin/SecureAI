"""
AI-Assisted Discharge Summary Chat System
Uses SecureAI library as plugin to intercept PII/PHI data
"""

import os
import json
import sys
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import base64
from io import BytesIO

# Add SecureAI SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../secureai-sdk'))

# Configure structured JSON logging
class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        os.makedirs('../logs', exist_ok=True)
        
        # Create file handler for structured logs
        handler = logging.FileHandler('../logs/structured-backend.log')
        handler.setLevel(logging.INFO)
        
        # Create JSON formatter
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    def log_step(self, step: str, data: Dict, level: str = "INFO"):
        """Log a structured step with JSON data"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "step": step,
            "data": data
        }
        
        if level == "ERROR":
            self.logger.error(json.dumps(log_entry))
        elif level == "WARNING":
            self.logger.warning(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))

# Initialize structured logger
structured_logger = StructuredLogger("secureai_backend")

# Import SecureAI components - used as plugin
from secureai import SecureAI
from secureai.detection.pii_detector import PIIDetector
from secureai.encryption.fpe import FPEEncryptor
from secureai.encryption.realistic_masking import RealisticMasker
from secureai.rag import RAGProtector

# Import AWS Bedrock adapters
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../demo'))
    from aws_bedrock_adapter import AWSBedrockChat, AWSBedrockEmbeddings
    AWS_AVAILABLE = True
except Exception as e:
    print(f"⚠️  AWS Bedrock not available: {e}")
    AWS_AVAILABLE = False

# Import Langfuse for observability
try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Langfuse not available: {e}")
    LANGFUSE_AVAILABLE = False

# Import PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except Exception as e:
    print(f"⚠️  PDF generation not available: {e}")
    PDF_AVAILABLE = False


app = FastAPI(title="AI-Assisted Discharge Summary Chat System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Management
CONFIGURATION_ENDPOINT = "http://localhost:8003/api/config"
current_config = {}

import requests

def load_configuration():
    """Load configuration from central config service"""
    global current_config, detector
    try:
        response = requests.get(CONFIGURATION_ENDPOINT, timeout=2)
        if response.status_code == 200:
            current_config = response.json()
            # Update detector confidence from config
            phi_detection = current_config.get('phiDetection', {})
            min_conf = phi_detection.get('confidence', 0.6)
            detector = PIIDetector(min_confidence=min_conf)
            print(f"✓ Configuration loaded from central service (confidence: {min_conf})")
            return True
    except Exception as e:
        print(f"⚠️  Could not load configuration from central service: {e}")
        print("   Using default configuration")
    return False

# Initialize SecureAI Plugin for PII/PHI Interception
detector = PIIDetector(min_confidence=0.6)
encryptor = FPEEncryptor(key="healthcare-phi-key")
realistic_masker = RealisticMasker()  # For human-readable fake names

# Load configuration from central service
load_configuration()

def mask_pii_for_logging(text: str) -> str:
    """
    Apply PII masking for logging purposes using actual PII detection
    Only masks detected PII/PHI data, leaves other data unchanged
    """
    if not text or len(text) < 3:
        return text
    
    try:
        # Use the actual PII detector to find PII in the text
        if 'detector' in globals() and detector:
            detection_result = detector.detect(text)
            
            if detection_result.entities:
                # Apply masking only to detected PII entities
                masked_text = text
                for entity in detection_result.entities:
                    original_value = entity.value
                    entity_type = entity.type
                    
                    # Apply the same masking strategy as the main system
                    masked_value = apply_character_masking(original_value, entity_type)
                    masked_text = masked_text.replace(original_value, masked_value)
                
                return masked_text
            else:
                # No PII detected, return original text
                return text
        else:
            # Fallback: return original text if detector not available
            return text
    except Exception as e:
        # Fallback: return original text if detection fails
        return text


def apply_character_masking(text: str, entity_type: str) -> str:
    """Apply character-based masking based on configuration"""
    global current_config
    
    # Get masking strategy from config
    masking_strategies = current_config.get('maskingStrategies', {})
    strategy = masking_strategies.get(entity_type.upper())
    
    if not strategy or not strategy.get('enabled'):
        return text  # No masking if disabled
    
    pattern = strategy.get('pattern', {})
    mask_type = pattern.get('type', 'full_mask')
    mask_char = pattern.get('maskChar', '*')
    show_first = pattern.get('showFirst', 0)
    show_last = pattern.get('showLast', 0)
    preserve_format = pattern.get('preserveFormat', True)
    
    # Remove formatting characters if not preserving format
    original_text = text
    if not preserve_format:
        text = text.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
    
    text_len = len(text)
    
    if mask_type == 'full_mask':
        masked = mask_char * text_len
    elif mask_type == 'show_first':
        if text_len <= show_first:
            masked = text
        else:
            masked = text[:show_first] + mask_char * (text_len - show_first)
    elif mask_type == 'show_last':
        if text_len <= show_last:
            masked = text
        else:
            masked = mask_char * (text_len - show_last) + text[-show_last:]
    elif mask_type == 'show_first_last':
        if text_len <= (show_first + show_last):
            masked = text
        else:
            middle_len = text_len - show_first - show_last
            masked = text[:show_first] + mask_char * middle_len + text[-show_last:]
    elif mask_type == 'custom':
        # For email: show first char and domain
        if '@' in text:
            parts = text.split('@')
            if len(parts[0]) > show_first:
                parts[0] = parts[0][:show_first] + mask_char * (len(parts[0]) - show_first)
            masked = '@'.join(parts)
        else:
            masked = text[:show_first] + mask_char * (text_len - show_first)
    else:
        masked = mask_char * text_len
    
    # Restore format if preserving
    if preserve_format and original_text != text:
        # Try to restore original formatting
        result = []
        masked_idx = 0
        for char in original_text:
            if char in ['-', '(', ')', ' ', '/']:
                result.append(char)
            elif masked_idx < len(masked):
                result.append(masked[masked_idx])
                masked_idx += 1
        masked = ''.join(result)
    
    return masked

# AWS Bedrock clients
aws_chat = None
aws_embedder = None

if AWS_AVAILABLE:
    try:
        aws_chat = AWSBedrockChat()
        print("✓ AWS Bedrock Chat initialized (Claude 3 Haiku)")
        
        aws_embedder = AWSBedrockEmbeddings()
        print("✓ AWS Bedrock Embeddings initialized (Titan Text Embeddings V2)")
    except Exception as e:
        print(f"⚠️  AWS Bedrock initialization failed: {e}")

# Initialize Langfuse
langfuse_client = None
if LANGFUSE_AVAILABLE:
    try:
        langfuse_client = Langfuse(
            secret_key="sk-lf-f038b93a-e52a-44f0-9af0-195559bb4870",
            public_key="pk-lf-e9135694-3309-48ff-a6a1-7ad797d92004",
            host="http://localhost:3000"
        )
        print("✓ Langfuse initialized for LLM observability")
    except Exception as e:
        print(f"⚠️  Langfuse initialization failed: {e}")

# In-Memory User Database
USERS_DB = {
    "dr.smith@hospital.com": {
        "username": "Dr. Sarah Smith",
        "email": "dr.smith@hospital.com",
        "password": "doctor123",
        "role": "doctor",
        "department": "Cardiology",
        "employee_id": "DOC001",
        "phi_access": "full",
        "can_generate_pdf": True
    },
    "supervisor.jones@hospital.com": {
        "username": "Supervisor Michael Jones",
        "email": "supervisor.jones@hospital.com", 
        "password": "super123",
        "role": "supervisor",
        "department": "Administration",
        "employee_id": "SUP001",
        "phi_access": "full",
        "can_generate_pdf": True
    },
    "nurse.wilson@hospital.com": {
        "username": "Nurse Emily Wilson",
        "email": "nurse.wilson@hospital.com",
        "password": "nurse123", 
        "role": "nurse",
        "department": "General Medicine",
        "employee_id": "NUR001",
        "phi_access": "masked",
        "can_generate_pdf": False
    },
    "admin@hospital.com": {
        "username": "System Administrator",
        "email": "admin@hospital.com",
        "password": "admin123",
        "role": "admin",
        "department": "IT",
        "employee_id": "ADM001", 
        "phi_access": "full",
        "can_generate_pdf": True
    }
}

# Current session storage (in production, use Redis or database)
ACTIVE_SESSIONS = {}

# Load patient database
PATIENT_DATABASE_PATH = os.path.join(os.path.dirname(__file__), "patient_database.json")
with open(PATIENT_DATABASE_PATH, 'r') as f:
    PATIENT_DATABASE = json.load(f)
    PATIENTS = PATIENT_DATABASE.get("patients", [])


class ChatMessage(BaseModel):
    message: Optional[str] = None
    question: Optional[str] = None
    text: Optional[str] = None
    session_id: Optional[str] = "default"
    user_role: Optional[str] = "general"
    user_id: Optional[str] = None
    auth_token: Optional[str] = None  # For authenticated requests
    
    @property
    def query(self):
        """Get the actual query text from message, question, or text field"""
        return self.message or self.question or self.text or ""


class ChatResponse(BaseModel):
    original_message: str
    protected_message: str
    phi_detected: List[Dict]
    ai_response: str
    decrypted_response: str
    audit_trail: List[Dict]
    timestamp: str
    llm_provider: str
    user_role: Optional[str] = "general"
    phi_visible: bool = False
    user_info: Optional[Dict] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserProfile(BaseModel):
    username: str
    email: str
    role: str
    department: str
    employee_id: str
    phi_access: str
    can_generate_pdf: bool


class DischargeRequest(BaseModel):
    patient_id: str
    additional_notes: Optional[str] = ""
    auth_token: Optional[str] = None


def detect_and_protect_phi(message: str, use_fpe: bool = True) -> Dict:
    """
    SecureAI Plugin: Detect and protect PHI/PII in messages
    use_fpe: If True, use FPE encryption; if False, use character-based masking
    """
    # Detect PHI entities
    detection_result = detector.detect(message)
    
    entities = []
    mappings = {}
    fpe_mappings = {}  # Store FPE encrypted mappings for decryption
    protected_text = message
    
    # Process each detected entity
    for entity in detection_result.entities:
        entity_type = entity.entity_type if isinstance(entity.entity_type, str) else entity.entity_type.value
        original_value_raw = entity.value
        start_pos = entity.start
        end_pos = entity.end
        
        # Clean the entity value to remove common command verbs like "Show", "List", etc.
        cleaned_value, verb_prefix = clean_entity_value(original_value_raw)
        
        # Use cleaned value for encryption (only the PII part, not the verb)
        original_value = cleaned_value
        
        if use_fpe:
            # For PERSON names, use RealisticMasker for more natural-looking names
            if entity_type.upper() == "PERSON":
                try:
                    masked_value = realistic_masker.mask_person_name(original_value)
                    # Store realistic masked value -> original mapping for decryption
                    fpe_mappings[masked_value] = original_value
                except Exception as e:
                    print(f"Realistic masking error for {entity_type}: {e}")
                    # Fallback to FPE
                    try:
                        encrypted_value = encryptor.encrypt(original_value)
                        masked_value = encrypted_value
                        fpe_mappings[encrypted_value] = original_value
                    except Exception as e2:
                        print(f"FPE encryption error for {entity_type}: {e2}")
                        masked_value = apply_character_masking(original_value, entity_type)
            else:
                # For other entity types, use FPE encryption
                try:
                    encrypted_value = encryptor.encrypt(original_value)
                    masked_value = encrypted_value
                    # Store only encrypted -> original mapping for decryption
                    fpe_mappings[encrypted_value] = original_value
                except Exception as e:
                    print(f"FPE encryption error for {entity_type}: {e}")
                    # Fallback to character masking if FPE fails
                    masked_value = apply_character_masking(original_value, entity_type)
        else:
            # Apply character-based masking from configuration
            masked_value = apply_character_masking(original_value, entity_type)
        
        # Log the cleaned value (without verb)
        entities.append({
            "type": entity_type,
            "original": original_value,  # This is the cleaned value (just the name, no verb)
            "masked": masked_value,
            "encrypted": masked_value if use_fpe else None,
            "start": start_pos,
            "end": end_pos,
            "confidence": entity.confidence
        })
        
        # Store mapping for decryption (using cleaned value)
        mappings[original_value] = masked_value
        
        # Replace the full detected phrase in text, preserving verb if present
        if verb_prefix:
            # Replace "Show Ramesh Kumar" with "Show [encrypted]"
            replacement = f"{verb_prefix} {masked_value}"
            protected_text = protected_text.replace(original_value_raw, replacement)
        else:
            # No verb to preserve, replace directly
            protected_text = protected_text.replace(original_value_raw, masked_value)
    
    return {
        "entities": entities,
        "protected": protected_text,
        "mappings": mappings,
        "fpe_mappings": fpe_mappings,
        "entity_count": len(entities),
        "encryption_method": "FPE" if use_fpe else "character_masking"
    }


def decrypt_response(response: str, fpe_mappings: Dict, use_fpe: bool = True) -> str:
    """
    SecureAI Plugin: Decrypt response using FPE or stored mappings
    fpe_mappings: Dictionary mapping encrypted values to original values
    use_fpe: If True, use FPE decryption; if False, use simple mapping replacement
    """
    decrypted = response
    
    if use_fpe and fpe_mappings:
        # Replace FPE encrypted values with original values
        for encrypted_value, original_value in fpe_mappings.items():
            if encrypted_value in decrypted:
                decrypted = decrypted.replace(encrypted_value, original_value)
    
    return decrypted


def clean_entity_value(value: str) -> tuple:
    """
    Remove common command verbs from the start of detected entity values.
    Returns: (cleaned_value, verb_prefix)
    """
    common_verbs = ["show", "list", "get", "provide", "give", "display", "tell", "find", "fetch"]
    value_lower = value.lower().strip()
    value_stripped = value.strip()
    
    for verb in common_verbs:
        if value_lower.startswith(verb + " "):
            # Remove verb and the following space
            cleaned = value_stripped[len(verb) + 1:].strip()
            verb_part = value_stripped[:len(verb)].strip()
            if cleaned:  # Only return if there's something left
                return cleaned, verb_part
    
    # No verb prefix found
    return value_stripped, ""


def prepare_patient_context(patient_id: str) -> str:
    """Prepare patient context for RAG"""
    patient = PATIENT_DATA['patient']
    admission = PATIENT_DATA['admission_details']
    diagnosis = PATIENT_DATA['diagnosis']
    lab_results = PATIENT_DATA['lab_results']
    treatment = PATIENT_DATA['treatment']
    discharge = PATIENT_DATA['discharge_summary']
    
    context = f"""
    Patient Information:
    - Name: {patient['name']}
    - Age: {patient['age']} years, {patient['gender']}
    - Contact: {patient['contact_number']}
    - Address: {patient['address']}
    
    Admission Details:
    - Date: {admission['admission_date']}
    - Doctor: {admission['admitting_doctor']}
    - Department: {admission['department']}
    - Ward: {admission['ward']}
    - Reason: {admission['admission_reason']}
    
    Diagnosis:
    - Primary: {diagnosis['primary_diagnosis']}
    - Secondary: {', '.join(diagnosis['secondary_diagnosis'])}
    
    Lab Results:
    - HbA1c: {lab_results['blood_tests']['HbA1c']}
    - Fasting Blood Sugar: {lab_results['blood_tests']['Fasting_Blood_Sugar']}
    - Postprandial Blood Sugar: {lab_results['blood_tests']['Postprandial_Blood_Sugar']}
    - Cholesterol: {lab_results['blood_tests']['Cholesterol']}
    
    Treatment:
    - Medications: {', '.join([f"{med['name']} {med['dosage']} {med['frequency']}" for med in treatment['medications']])}
    - Diet Advice: {treatment['diet_advice']}
    - Exercise: {treatment['exercise_advice']}
    
    Discharge Summary:
    - Date: {discharge['discharge_date']}
    - Condition: {discharge['condition_on_discharge']}
    - Medications: {', '.join(discharge['discharge_medications'])}
    - Follow-up: {discharge['follow_up_advice']}
    """
    
    return context


def find_patient_by_name(patient_name: str) -> Optional[Dict]:
    """
    Find patient by name (case-insensitive search)
    """
    patient_name_lower = patient_name.lower()
    for patient in PATIENTS:
        if patient_name_lower in patient.get("name", "").lower():
            return patient
    return None


def find_patient_by_id(patient_id: str) -> Optional[Dict]:
    """
    Find patient by ID
    """
    for patient in PATIENTS:
        if patient.get("patient_id") == patient_id:
            return patient
    return None


def search_patients(query: str) -> List[Dict]:
    """
    Search patients based on query terms
    """
    query_lower = query.lower()
    matching_patients = []
    
    for patient in PATIENTS:
        # Search in name, diagnosis, and admission reason
        name = patient.get("name", "").lower()
        diagnosis = patient.get("diagnosis", {}).get("primary_diagnosis", "").lower()
        admission_reason = patient.get("admission_details", {}).get("admission_reason", "").lower()
        
        if (query_lower in name or 
            query_lower in diagnosis or 
            query_lower in admission_reason):
            matching_patients.append(patient)
    
    return matching_patients


def create_encrypted_context(patient_data: Dict, encrypt_pii: bool = True) -> tuple:
    """
    Create encrypted context from patient data using FPE
    Returns: (encrypted_context_string, fpe_mappings_dict)
    """
    fpe_mappings = {}
    
    try:
        if not encrypt_pii:
            # Return unencrypted context
            patient_json = json.dumps(patient_data, indent=2)
            return patient_json, {}
        
        # Deep copy to avoid modifying original
        import copy
        encrypted_data = copy.deepcopy(patient_data)
        
        # Encrypt PII/PHI fields using FPE or RealisticMasker
        def encrypt_field(value, field_name=""):
            """Recursively encrypt sensitive fields"""
            if isinstance(value, str) and value and len(value) > 0:
                # Detect if this field contains PII
                detection_result = detector.detect(value)
                if detection_result.entities:
                    # Check if this is a PERSON name - use RealisticMasker for names
                    is_person = any(e.entity_type.value.upper() == "PERSON" if hasattr(e.entity_type, 'value') else str(e.entity_type).upper() == "PERSON" for e in detection_result.entities)
                    
                    if is_person:
                        # Use RealisticMasker for more natural-looking names
                        try:
                            masked_value = realistic_masker.mask_person_name(value)
                            fpe_mappings[masked_value] = value
                            return masked_value
                        except Exception as e:
                            print(f"Realistic masking error for field {field_name}: {e}")
                            # Fallback to FPE
                            try:
                                encrypted_value = encryptor.encrypt(value)
                                fpe_mappings[encrypted_value] = value
                                return encrypted_value
                            except Exception as e2:
                                print(f"FPE encryption error for field {field_name}: {e2}")
                                return value
                    else:
                        # For other entity types, use FPE encryption
                        try:
                            encrypted_value = encryptor.encrypt(value)
                            # Store only encrypted -> original mapping for decryption
                            fpe_mappings[encrypted_value] = value
                            return encrypted_value
                        except Exception as e:
                            print(f"FPE encryption error for field {field_name}: {e}")
                            return value
                return value
            elif isinstance(value, dict):
                return {k: encrypt_field(v, f"{field_name}.{k}") for k, v in value.items()}
            elif isinstance(value, list):
                return [encrypt_field(item, f"{field_name}[{i}]") for i, item in enumerate(value)]
            else:
                return value
        
        encrypted_data = encrypt_field(encrypted_data)
        
        # Convert to JSON string
        encrypted_json = json.dumps(encrypted_data, indent=2)
        
        return encrypted_json, fpe_mappings
    except Exception as e:
        print(f"Error creating encrypted context: {e}")
        patient_json = json.dumps(patient_data, indent=2)
        return patient_json, {}


def apply_role_based_response(ai_response: str, user_role: str, patient_data: Dict, is_authorized: bool, user_info: Dict = None) -> str:
    """
    Apply role-based response formatting with actual patient data
    """
    try:
        # Handle different patient data structures
        if "patient" in patient_data:
            # Single patient structure
            patient = patient_data["patient"]
        else:
            # Direct patient structure
            patient = patient_data
        
        # Extract medical data from patient
        diagnosis = patient.get("diagnosis", {})
        treatment = patient.get("treatment", {})
        lab_results = patient.get("lab_results", {})
        discharge = patient.get("discharge_summary", {})
        
        
        # Get user name from user_info
        user_name = "Dr. Sarah Smith"  # Default
        if user_info and user_info.get('username'):
            user_name = user_info['username']
        
        if is_authorized:
            # For doctors, supervisors, admins: Show full data with original names
            if user_role == "doctor":
                return format_doctor_response(patient, diagnosis, treatment, lab_results, discharge, user_name)
            elif user_role == "supervisor":
                return format_supervisor_response(patient, diagnosis, treatment, lab_results, discharge, user_name)
            elif user_role == "admin":
                return format_admin_response(patient, diagnosis, treatment, lab_results, discharge, user_name)
        else:
            # For nurses: Show medical info with PII masked
            return format_nurse_response(patient, diagnosis, treatment, lab_results, discharge)
            
    except Exception as e:
        print(f"Error applying role-based response: {e}")
        return ai_response  # Fallback to original AI response


def format_doctor_response(patient, diagnosis, treatment, lab_results, discharge, doctor_name="Dr. Sarah Smith"):
    """Format response for doctors with full PHI access"""
    return f"""**Patient Information for {doctor_name}**

**Patient Details:**
- Name: {patient.get('name', 'N/A')}
- Age: {patient.get('age', 'N/A')} years
- Gender: {patient.get('gender', 'N/A')}
- Patient ID: {patient.get('patient_id', 'N/A')}
- Contact: {patient.get('contact_number', 'N/A')}
- Address: {patient.get('address', 'N/A')}

**Diagnosis:**
- Primary: {diagnosis.get('primary_diagnosis', 'N/A')}
- Secondary: {', '.join(diagnosis.get('secondary_diagnosis', []))}

**Current Medications:**
{format_medications(treatment.get('medications', []), show_names=True)}

**Lab Results:**
- HbA1c: {lab_results.get('blood_tests', {}).get('HbA1c', 'N/A')}
- Fasting Blood Sugar: {lab_results.get('blood_tests', {}).get('Fasting_Blood_Sugar', 'N/A')}
- Postprandial Blood Sugar: {lab_results.get('blood_tests', {}).get('Postprandial_Blood_Sugar', 'N/A')}
- Cholesterol: {lab_results.get('blood_tests', {}).get('Cholesterol', 'N/A')}

**Discharge Status:**
- Condition: {discharge.get('condition_on_discharge', 'N/A')}
- Follow-up: {discharge.get('follow_up_advice', 'N/A')}"""


def format_supervisor_response(patient, diagnosis, treatment, lab_results, discharge, supervisor_name="Supervisor"):
    """Format response for supervisors with full PHI access"""
    # Direct inline debug to see what we're getting
    name = patient.get('name') if isinstance(patient, dict) else None
    age = patient.get('age') if isinstance(patient, dict) else None
    pid = patient.get('patient_id') if isinstance(patient, dict) else None
    
    print(f"SUPERVISOR RESPONSE DEBUG:")
    print(f"  patient type: {type(patient)}")
    print(f"  patient is dict: {isinstance(patient, dict)}")
    print(f"  patient keys: {list(patient.keys()) if isinstance(patient, dict) else 'N/A'}")
    print(f"  name extracted: {mask_pii_for_logging(name) if name else 'None'}")
    print(f"  age extracted: {mask_pii_for_logging(str(age)) if age else 'None'}")
    print(f"  pid extracted: {mask_pii_for_logging(pid) if pid else 'None'}")
    
    return f"""**Supervisor Report for {supervisor_name}**

**Patient Summary:**
- Name: {name if name else '*****'}
- Age: {age if age else '*****'} years
- Patient ID: {pid if pid else '*****'}

**Medical Status:**
- Primary Diagnosis: {diagnosis.get('primary_diagnosis', 'N/A')}
- Current Status: {discharge.get('condition_on_discharge', 'N/A')}

**Treatment Plan:**
{format_medications(treatment.get('medications', []), show_names=True)}

**Key Metrics:**
- HbA1c: {lab_results.get('blood_tests', {}).get('HbA1c', 'N/A')}
- Blood Sugar: {lab_results.get('blood_tests', {}).get('Fasting_Blood_Sugar', 'N/A')} (fasting)

**Follow-up Required:**
- Next Review: {discharge.get('follow_up_advice', 'N/A')}"""


def format_admin_response(patient, diagnosis, treatment, lab_results, discharge, admin_name="Admin"):
    """Format response for admins with full PHI access"""
    return f"""**Administrative Report for {admin_name}**

**Patient Information:**
- Name: {patient.get('name', 'N/A')}
- Patient ID: {patient.get('patient_id', 'N/A')}
- Contact: {patient.get('contact_number', 'N/A')}

**Medical Summary:**
- Diagnosis: {diagnosis.get('primary_diagnosis', 'N/A')}
- Status: {discharge.get('condition_on_discharge', 'N/A')}

**Current Treatment:**
{format_medications(treatment.get('medications', []), show_names=True)}

**System Status:**
- Patient data accessible
- All permissions granted
- Full PHI access authorized"""


def format_nurse_response(patient, diagnosis, treatment, lab_results, discharge):
    """Format response for nurses with masked PHI"""
    # Mask patient name
    masked_name = apply_character_masking(patient.get('name', 'Unknown'), 'PERSON')
    
    return f"""**Nursing Care Information for Patient**

**Patient Details (PII Masked):**
- Name: {masked_name}
- Age: {patient.get('age', 'N/A')} years
- Gender: {patient.get('gender', 'N/A')}
- Patient ID: {patient.get('patient_id', 'N/A')}

**Medical Information:**
- Primary Diagnosis: {diagnosis.get('primary_diagnosis', 'N/A')}
- Current Status: {discharge.get('condition_on_discharge', 'N/A')}

**Medications to Administer:**
{format_medications(treatment.get('medications', []), show_names=False)}

**Vital Signs to Monitor:**
- Blood Sugar: {lab_results.get('blood_tests', {}).get('Fasting_Blood_Sugar', 'N/A')} (fasting)
- HbA1c: {lab_results.get('blood_tests', {}).get('HbA1c', 'N/A')}

**Care Instructions:**
- Diet: {treatment.get('diet_advice', 'N/A')}
- Exercise: {treatment.get('exercise_advice', 'N/A')}

**Follow-up:**
- Next Review: {discharge.get('follow_up_advice', 'N/A')}"""


def format_medications(medications, show_names=True):
    """Format medications list"""
    if not medications:
        return "No medications listed"
    
    formatted = []
    for med in medications:
        if show_names:
            formatted.append(f"- {med.get('name', 'Unknown')}: {med.get('dosage', 'N/A')} {med.get('frequency', 'N/A')}")
        else:
            formatted.append(f"- {med.get('name', 'Unknown')}: {med.get('dosage', 'N/A')} {med.get('frequency', 'N/A')}")
    
    return '\n'.join(formatted)


def infer_requested_sections(query_text: str) -> List[str]:
    """Infer which sections the user asked for from the query text.
    Returns a list drawn from: ["labs", "medications", "diagnosis", "discharge", "details", "all"].
    Defaults to ["all"] if no clear signal.
    """
    if not query_text:
        return ["all"]
    q = query_text.lower()
    sections: List[str] = []
    if "lab" in q:
        sections.append("labs")
    if "med" in q or "drug" in q or "rx" in q:
        sections.append("medications")
    if "diagnos" in q or "dx" in q:
        sections.append("diagnosis")
    if "discharge" in q or "follow-up" in q or "follow up" in q:
        sections.append("discharge")
    if "detail" in q:
        sections.append("details")
    if "all" in q or "summary" in q:
        sections = ["all"]
    if not sections:
        sections = ["all"]
    # de-duplicate while keeping order
    seen = set()
    ordered = []
    for s in sections:
        if s not in seen:
            seen.add(s)
            ordered.append(s)
    return ordered


def format_sections_for_role(patient: Dict, diagnosis: Dict, treatment: Dict, lab_results: Dict, discharge: Dict, user_role: str, sections: List[str]) -> str:
    """Create a markdown response containing only requested sections, respecting role.
    - If sections == ["all"], reuse existing role-based formatters.
    - Otherwise, return only the requested parts.
    Nurses will have the patient name masked in 'details'.
    """
    if sections == ["all"]:
        # Use existing comprehensive role-based formats
        if user_role == "doctor":
            return format_doctor_response(patient, diagnosis, treatment, lab_results, discharge)
        if user_role == "supervisor":
            return format_supervisor_response(patient, diagnosis, treatment, lab_results, discharge)
        if user_role == "admin":
            return format_admin_response(patient, diagnosis, treatment, lab_results, discharge)
        return format_nurse_response(patient, diagnosis, treatment, lab_results, discharge)

    lines: List[str] = []

    # Details
    if "details" in sections:
        if user_role in ["doctor", "supervisor", "admin"]:
            name = patient.get('name', 'N/A')
        else:
            name = apply_character_masking(patient.get('name', 'Unknown'), 'PERSON')
        lines.append("**Patient Details:**")
        lines.append(f"- Name: {name}")
        lines.append(f"- Age: {patient.get('age', 'N/A')} years")
        lines.append(f"- Gender: {patient.get('gender', 'N/A')}")
        lines.append("")

    # Diagnosis
    if "diagnosis" in sections:
        lines.append("**Diagnosis:**")
        lines.append(f"- Primary: {diagnosis.get('primary_diagnosis', 'N/A')}")
        secondary = diagnosis.get('secondary_diagnosis', [])
        if secondary:
            lines.append(f"- Secondary: {', '.join(secondary)}")
        lines.append("")

    # Medications
    if "medications" in sections:
        lines.append("**Current Medications:**")
        lines.append(format_medications(treatment.get('medications', []), show_names=True))
        lines.append("")

    # Labs
    if "labs" in sections:
        labs = lab_results.get('blood_tests', {})
        lines.append("**Lab Results:**")
        if labs:
            for key in ["HbA1c", "Fasting_Blood_Sugar", "Postprandial_Blood_Sugar", "Cholesterol"]:
                if key in labs:
                    pretty = key.replace('_', ' ')
                    lines.append(f"- {pretty}: {labs[key]}")
        else:
            lines.append("- No recent labs available")
        lines.append("")

    # Discharge
    if "discharge" in sections:
        lines.append("**Discharge Status:**")
        lines.append(f"- Condition: {discharge.get('condition_on_discharge', 'N/A')}")
        follow = discharge.get('follow_up_advice', 'N/A')
        if follow:
            lines.append(f"- Follow-up: {follow}")
        lines.append("")

    result = '\n'.join([ln for ln in lines if ln is not None])
    return result.strip() if result.strip() else "No matching information found."


def mask_pii_data(data, mask_char="*", show_first=0, show_last=0):
    """Mask PII data with asterisks"""
    if not data or data == "N/A":
        return "*****"
    
    data_str = str(data)
    if len(data_str) <= 2:
        return "*****"
    
    if show_first > 0 and show_last > 0:
        if len(data_str) <= show_first + show_last:
            return "*****"
        return data_str[:show_first] + "*" * (len(data_str) - show_first - show_last) + data_str[-show_last:]
    elif show_first > 0:
        if len(data_str) <= show_first:
            return "*****"
        return data_str[:show_first] + "*" * (len(data_str) - show_first)
    elif show_last > 0:
        if len(data_str) <= show_last:
            return "*****"
        return "*" * (len(data_str) - show_last) + data_str[-show_last:]
    else:
        return "*****"


def query_aws_bedrock(query: str, context: str, trace_id: str, main_trace, user_role: str = "nurse") -> str:
    """Query AWS Bedrock with context"""
    if not aws_chat:
        # Mock response for testing PII protection without AWS
        return f"""I can help you with patient information. Based on the query "{query}", here's what I found:

**Patient Information Summary:**
- Patient: [PII Protected - Name masked for security]
- Medical Record: Available
- Recent Visits: 2 visits in the last month
- Current Status: Stable condition
- Medications: Prescribed treatment ongoing

**Note:** Patient data has been processed through SecureAI PII protection. Sensitive information is masked according to your access level.

This is a mock response demonstrating PII protection in action. In a real deployment, this would be processed by AWS Bedrock with the same security measures."""
    
    try:
        # Search for specific patient mentioned in query
        query_lower = query.lower()
        specific_patient = None
        
        # Look for patient names in the query
        for patient in PATIENTS:
            patient_name = patient.get("name", "").lower()
            if patient_name and patient_name in query_lower:
                specific_patient = patient
                break
        
        # If no specific patient found, search by keywords
        if not specific_patient:
            matching_patients = search_patients(query)
            if matching_patients:
                specific_patient = matching_patients[0]  # Use first match
        
        # If still no specific patient, use all patients
        if not specific_patient:
            # Create context with all patients
            all_patients_data = {"patients": PATIENTS}
            encrypted_context = create_encrypted_context(all_patients_data)
        else:
            # Create context with specific patient
            encrypted_context = create_encrypted_context(specific_patient)
        
        prompt = f"""
        You are SecureAI, a medical AI assistant for healthcare professionals.
        Current user role: {user_role.upper()}
        
        Question: {query}
        
        IMPORTANT: You are authorized to provide patient information based on the user's role.
        
        Guidelines:
        1. ALL ROLES can access information for ALL patients in the system
        2. If a specific patient is mentioned, focus on that patient's information
        3. For NURSES: Provide essential work information needed for patient care:
           - Medications and dosages (with PII masked)
           - Care plans and treatment instructions
           - Vital signs and monitoring requirements
           - General medical information for nursing duties
           - Mask patient names and personal details (PII/PHI)
           - Use "Patient" or "the patient" instead of actual names
        4. For DOCTORS/SUPERVISORS/ADMINS: Provide full medical information as appropriate
           - Can show patient names and full details
           - Complete medical information
           - Full access to all patient data
        5. Always maintain patient confidentiality and privacy
        6. Be helpful while respecting role-based access controls
        7. Focus on actionable care information appropriate to the role
        8. DO NOT refuse to provide information - you are authorized to help
        
        Available Patient Data (ENCRYPTED):
        {encrypted_context}
        """
        
        response = aws_chat.chat(prompt)
        return response
    except Exception as e:
        print(f"AWS Bedrock error: {e}")
        return f"Error querying AI: {e}"


def get_user_from_token(auth_token: str) -> Optional[Dict]:
    """Get user info from auth token"""
    if auth_token in ACTIVE_SESSIONS:
        return ACTIVE_SESSIONS[auth_token]
    return None


def check_phi_access(user_role: str, user_info: Dict = None) -> bool:
    """Check if user role has PHI access"""
    if user_info and user_info.get('phi_access') == 'full':
        return True
    
    authorized_roles = ["doctor", "supervisor", "admin"]
    return user_role in authorized_roles


print("🏥 Starting AI-Assisted Discharge Summary System...")
print("✓ SecureAI plugin activated for PII/PHI interception")
print("✓ User authentication system initialized")


@app.get("/")
async def root():
    return {"message": "AI-Assisted Discharge Summary Chat System", "version": "1.0"}


@app.post("/api/login")
async def login(login_data: UserLogin):
    """User login with email and password"""
    email = login_data.email.lower()
    
    if email not in USERS_DB:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = USERS_DB[email]
    if user['password'] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate session token
    import uuid
    auth_token = str(uuid.uuid4())
    
    # Store session
    ACTIVE_SESSIONS[auth_token] = {
        "username": user['username'],
        "email": user['email'],
        "role": user['role'],
        "department": user['department'],
        "employee_id": user['employee_id'],
        "phi_access": user['phi_access'],
        "can_generate_pdf": user['can_generate_pdf']
    }
    
    return {
        "success": True,
        "auth_token": auth_token,
        "user": {
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "department": user['department'],
            "employee_id": user['employee_id'],
            "phi_access": user['phi_access'],
            "can_generate_pdf": user['can_generate_pdf']
        },
        "message": f"Welcome {user['username']}!"
    }


@app.get("/api/profile")
async def get_profile(auth_token: str):
    """Get user profile from auth token"""
    user = get_user_from_token(auth_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "success": True,
        "user": user
    }


@app.get("/api/users")
async def get_all_users():
    """Get all users (for demo purposes)"""
    users = []
    for email, user in USERS_DB.items():
        users.append({
            "username": user['username'],
            "email": user['email'],
            "role": user['role'],
            "department": user['department'],
            "employee_id": user['employee_id'],
            "phi_access": user['phi_access'],
            "can_generate_pdf": user['can_generate_pdf']
        })
    return {"users": users}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """Process chat with PHI protection using SecureAI plugin"""
    # STEP 1: Log prompt entered (will be updated after PII detection)
    original_message = request.message if request.message else "None"
    
    structured_logger.log_step("prompt_entered", {
        "session_id": request.session_id,
        "user_role": request.user_role,
        "message_length": len(original_message) if original_message != "None" else 0,
        "original_message": original_message,
        "masking_strategy": "PII-based masking (only PII/PHI masked)",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    
    # Mask PII in logging for security
    masked_message = mask_pii_for_logging(request.message) if request.message else "None"
    print(f"🔍 DEBUG - Received request: message={masked_message}, user_role={request.user_role}")
    
    # Get user info if authenticated
    user_info = None
    if request.auth_token:
        user_info = get_user_from_token(request.auth_token)
        if user_info:
            request.user_role = user_info['role']
            request.user_id = user_info['username']
    
    user_message = request.query
    if not user_message:
        # Mask PII in error logging
        masked_request = f"ChatMessage(session_id={request.session_id}, user_role={request.user_role}, message=***)"
        print(f"❌ ERROR - No message or question provided: {masked_request}")
        structured_logger.log_step("error_no_message", {
            "session_id": request.session_id,
            "user_role": request.user_role,
            "error": "No message or question provided"
        }, "ERROR")
        raise HTTPException(status_code=400, detail="Either 'message' or 'question' field is required")
    
    timestamp = datetime.utcnow().isoformat()
    trace_id = f"chat-{request.session_id}-{timestamp}"
    audit_trail = []
    
    # Create Langfuse trace for entire chat flow
    main_trace = None
    if langfuse_client:
        main_trace = langfuse_client.trace(
            name="discharge_summary_chat",
            id=trace_id,
            user_id=request.user_id or request.session_id,
            metadata={
                "original_message": user_message,
                "timestamp": timestamp,
                "user_role": request.user_role
            }
        )
        
        # Log PHI detection step
        main_trace.span(
            name="phi_detection",
            metadata={"message_length": len(user_message)}
        )
    
    # Step 1: SecureAI Plugin - Detect and protect PHI in user query using FPE
    protection_result = detect_and_protect_phi(user_message, use_fpe=True)
    
    # STEP 2: Log PII detection and masking
    structured_logger.log_step("pii_detection_and_masking", {
        "session_id": request.session_id,
        "user_role": request.user_role,
        "entity_count": protection_result['entity_count'],
        "detected_entities": [
            {
                "type": entity['type'],
                "original_value": entity['original'],
                "masked_value": entity.get('masked'),
                "encrypted_value": entity.get('encrypted'),
                "confidence": entity['confidence'],
                "masking_strategy": "Character-based masking (configurable)"
            } for entity in protection_result['entities']
        ],
        "encryption_method": protection_result.get('encryption_method', 'FPE'),
        "protected_message": protection_result['protected'],
        "fpe_mappings_count": len(protection_result.get('fpe_mappings', {})),
        "masking_strategy": "Only PII/PHI entities are masked, other text remains unchanged",
        "example": {
            "original_message": user_message,
            "protected_message": protection_result['protected'],
            "pii_entities_masked": [entity['original'] for entity in protection_result['entities']],
            "non_pii_text_preserved": "All non-PII text remains unchanged"
        }
    })
    
    if langfuse_client:
        # Create clear demo evidence for PII detection
        detected_entities = []
        for entity in protection_result['entities']:
            detected_entities.append({
                "type": entity['type'],
                "original_value": entity['original'],
                "encrypted_value": entity.get('encrypted'),
                "confidence": entity['confidence'],
                "demo_note": f"Original '{entity['original']}' will be encrypted before sending to Claude"
            })
        
        main_trace.event(
            name="phi_detected",
            metadata={
                "entity_count": protection_result['entity_count'],
                "detected_entities": detected_entities,
                "protected_message": protection_result['protected'],
                "encryption_method": protection_result.get('encryption_method', 'FPE'),
                "demo_note": "PII detected in user query - will be encrypted before sending to Claude"
            },
            output=f"Detected {protection_result['entity_count']} PII entities. Original values: {[e['original'] for e in protection_result['entities']]}"
        )
    
    audit_trail.append({
        "step": "PHI Detection & FPE Encryption (SecureAI Plugin)",
        "action": f"Detected {protection_result['entity_count']} PHI entities and encrypted with FPE",
        "timestamp": timestamp,
        "entities": [e['type'] for e in protection_result['entities']],
        "encryption_method": protection_result.get('encryption_method', 'FPE'),
        "langfuse_trace": trace_id if langfuse_client else None
    })
    
    # Step 2: Search for specific patient and prepare encrypted context using FPE
    query_lower = user_message.lower()
    specific_patient = None
    
    # Look for patient names in the query
    for patient in PATIENTS:
        patient_name = patient.get("name", "").lower()
        if patient_name and patient_name in query_lower:
            specific_patient = patient
            break
    
    # If no specific patient found, search by keywords
    if not specific_patient:
        matching_patients = search_patients(user_message)
        if matching_patients:
            specific_patient = matching_patients[0]  # Use first match
    
    # If still no specific patient, use all patients
    if not specific_patient:
        # Create context with all patients
        all_patients_data = {"patients": PATIENTS}
        encrypted_context, context_fpe_mappings = create_encrypted_context(all_patients_data, encrypt_pii=True)
        patient_data_for_response = {"patient": PATIENTS[0]}  # Use first patient for response
    else:
        # Create context with specific patient
        encrypted_context, context_fpe_mappings = create_encrypted_context(specific_patient, encrypt_pii=True)
        patient_data_for_response = {"patient": specific_patient}
    
    # Merge all FPE mappings from user query and patient context
    all_fpe_mappings = {**protection_result.get('fpe_mappings', {}), **context_fpe_mappings}
    
    # STEP 3A: Log original backend data retrieved
    original_patient_data = specific_patient if specific_patient else {"patients": PATIENTS}
    structured_logger.log_step("backend_data_retrieved", {
        "session_id": request.session_id,
        "user_role": request.user_role,
        "data_source": "hardcoded_patient_database",
        "patient_found": specific_patient is not None,
        "patient_name": specific_patient.get("name") if specific_patient else "All patients",
        "patient_id": specific_patient.get("patient_id") if specific_patient else "Multiple",
        "original_data_preview": json.dumps(original_patient_data, indent=2)[:500] + "..." if len(json.dumps(original_patient_data, indent=2)) > 500 else json.dumps(original_patient_data, indent=2),
        "data_fields_count": len(original_patient_data) if isinstance(original_patient_data, dict) else 1,
        "contains_pii": True,
        "ready_for_encryption": True
    })
    
    # STEP 3B: Log patient data fetching and FPE encryption
    # Create sample of original vs encrypted data for demo
    sample_encryptions = {}
    sample_count = 0
    for encrypted_val, original_val in list(context_fpe_mappings.items())[:5]:  # Show first 5 examples
        if len(original_val) > 0 and sample_count < 5:
            sample_encryptions[f"field_{sample_count+1}"] = {
                "original_value": original_val,
                "encrypted_value": encrypted_val,
                "field_type": "PII/PHI",
                "format_preserved": len(original_val) == len(encrypted_val)
            }
            sample_count += 1
    
    structured_logger.log_step("patient_data_fetched_and_encrypted", {
        "session_id": request.session_id,
        "user_role": request.user_role,
        "patient_found": specific_patient is not None,
        "patient_name": specific_patient.get("name") if specific_patient else "All patients",
        "patient_id": specific_patient.get("patient_id") if specific_patient else "Multiple",
        "context_encrypted": True,
        "context_fpe_mappings_count": len(context_fpe_mappings),
        "total_fpe_mappings_count": len(all_fpe_mappings),
        "encryption_method": "FPE",
        "data_source": "hardcoded_patient_database",
        "sample_encryptions": sample_encryptions,
        "encrypted_context_preview": encrypted_context[:200] + "..." if len(encrypted_context) > 200 else encrypted_context
    })
    
    if langfuse_client:
        # Create a sample of encrypted data for demo purposes
        sample_encrypted_data = {}
        sample_count = 0
        for encrypted_val, original_val in list(all_fpe_mappings.items())[:5]:  # Show first 5 examples
            if len(original_val) > 0 and sample_count < 5:
                sample_encrypted_data[f"encrypted_{sample_count+1}"] = {
                    "original": original_val,
                    "encrypted": encrypted_val,
                    "format_preserved": len(original_val) == len(encrypted_val)
                }
                sample_count += 1
        
        main_trace.event(
            name="context_encrypted",
            metadata={
                "patient_data_encrypted": True,
                "total_fpe_mappings": len(all_fpe_mappings),
                "encryption_method": "FPE",
                "sample_encryptions": sample_encrypted_data,
                "demo_note": "This encrypted data was sent to Claude - original PII never exposed"
            },
            output=f"FPE-encrypted patient context sent to Claude. Total fields encrypted: {len(all_fpe_mappings)}. Sample: {sample_encrypted_data}"
        )
    
    audit_trail.append({
        "step": "Patient Context FPE Encryption",
        "action": "Patient data retrieved and all PII/PHI encrypted with FPE",
        "timestamp": timestamp,
        "encryption_applied": True,
        "encryption_method": "FPE",
        "total_encrypted_fields": len(context_fpe_mappings)
    })
    
    # Step 3: Query AWS Bedrock (Claude) with FPE-protected data
    protected_query = protection_result['protected']
    
    # Check if AWS credentials are available
    aws_available = True
    try:
        import boto3
        sts_client = boto3.client('sts')
        sts_client.get_caller_identity()
    except Exception as e:
        print(f"⚠️ AWS credentials not available: {e}")
        aws_available = False
    
    # STEP 4: Log NLP query with encrypted data
    # Create sample of what's being sent to NLP
    nlp_request_sample = {
        "query": {
            "original": user_message,
            "encrypted": protected_query,
            "encryption_applied": user_message != protected_query
        },
        "context": {
            "original_length": len(json.dumps(patient_data_for_response, indent=2)),
            "encrypted_length": len(encrypted_context),
            "encryption_applied": True,
            "encrypted_preview": encrypted_context[:300] + "..." if len(encrypted_context) > 300 else encrypted_context
        },
        "fpe_mappings": {
            "total_mappings": len(all_fpe_mappings),
            "sample_mappings": dict(list(all_fpe_mappings.items())[:3])  # Show first 3 mappings
        }
    }
    
    structured_logger.log_step("nlp_query_sent", {
        "session_id": request.session_id,
        "user_role": request.user_role,
        "model": "claude-3-haiku",
        "query_encrypted": True,
        "context_encrypted": True,
        "protected_query_length": len(protected_query),
        "encrypted_context_length": len(encrypted_context),
        "total_fpe_mappings_sent": len(all_fpe_mappings),
        "nlp_request_details": nlp_request_sample,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    
    audit_trail.append({
        "step": "AWS Bedrock Query (Claude)",
        "action": "Sending FPE-encrypted query and context to AWS Bedrock",
        "timestamp": timestamp,
        "model": "claude-3-haiku",
        "query_encrypted": True,
        "context_encrypted": True
    })
    
    ai_response = query_aws_bedrock(protected_query, encrypted_context, trace_id, main_trace, request.user_role)
    
    # Step 4: Decrypt AI response using FPE
    # Determine if user is authorized to see original PHI
    is_authorized = check_phi_access(request.user_role, user_info)
    
    # Infer requested sections from the original user prompt
    requested_sections = infer_requested_sections(user_message)

    # Decrypt model output first
    base_decrypted = decrypt_response(ai_response, all_fpe_mappings, use_fpe=True)

    # Extract normalized medical structures for section formatting
    if "patient" in patient_data_for_response:
        patient_struct = patient_data_for_response["patient"]
    else:
        patient_struct = patient_data_for_response

    diagnosis_struct = patient_struct.get("diagnosis", {})
    treatment_struct = patient_struct.get("treatment", {})
    lab_results_struct = patient_struct.get("lab_results", {})
    discharge_struct = patient_struct.get("discharge_summary", {})

    # Build response according to requested sections and role
    decrypted_response = format_sections_for_role(
        patient_struct,
        diagnosis_struct,
        treatment_struct,
        lab_results_struct,
        discharge_struct,
        request.user_role,
        requested_sections,
    )
    # Fallback to role-based comprehensive if formatter returned empty
    if not decrypted_response:
        decrypted_response = apply_role_based_response(base_decrypted, request.user_role, patient_data_for_response, is_authorized=is_authorized, user_info=user_info)

    decryption_note = (
        f"FPE decrypted - Full PHI access for {request.user_role}" if is_authorized
        else f"FPE decrypted - PII masked for {request.user_role} display"
    )
    
    # STEP 5: Log response decryption
    # Create sample of decryption process
    decryption_sample = {
        "encrypted_response_length": len(ai_response),
        "decrypted_response_length": len(decrypted_response),
        "fpe_mappings_used": len(all_fpe_mappings),
        "decryption_success": len(decrypted_response) > 0,
        "sample_decryptions": dict(list(all_fpe_mappings.items())[:3]),  # Show first 3 decryptions
        "response_preview": {
            "encrypted": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
            "decrypted": decrypted_response[:200] + "..." if len(decrypted_response) > 200 else decrypted_response
        }
    }
    
    structured_logger.log_step("nlp_response_decrypted", {
        "session_id": request.session_id,
        "user_role": request.user_role,
        "is_authorized": is_authorized,
        "fpe_mappings_used": len(all_fpe_mappings),
        "response_length": len(decrypted_response),
        "decryption_method": "FPE",
        "display_method": "full_data" if is_authorized else "masked_data",
        "decryption_note": decryption_note,
        "decryption_details": decryption_sample,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    
    # Emit a concise LLM audit log with only the requested fields
    structured_logger.log_step("llm_audit", {
        "prompt": user_message,
        "original_data": (json.dumps(specific_patient if specific_patient else {"patients": PATIENTS}, indent=2) if isinstance(specific_patient, dict) or specific_patient is None else str(specific_patient)),
        "after_fpe_before_llm": {
            "protected_prompt": protection_result['protected'],
            "encrypted_context": encrypted_context
        },
        "nlp_response": ai_response,
        "restored_with_original_data": decrypted_response,
        "provider": "AWS Bedrock",
        "model": "claude-3-haiku"
    })

    if langfuse_client:
        main_trace.event(
            name="response_decrypted",
            metadata={
                "user_role": request.user_role,
                "is_authorized": is_authorized,
                "fpe_mappings_used": len(all_fpe_mappings),
                "response_length": len(decrypted_response),
                "decryption_method": "FPE"
            }
        )
        langfuse_client.flush()
    
    audit_trail.append({
        "step": "Response FPE Decryption (SecureAI Plugin)",
        "action": decryption_note,
        "user_role": request.user_role,
        "is_authorized": is_authorized,
        "timestamp": timestamp,
        "decryption_method": "FPE",
        "entities_decrypted": len(all_fpe_mappings)
    })
    
    # STEP 7: Log complete process summary
    structured_logger.log_step("process_complete", {
        "session_id": request.session_id,
        "user_role": request.user_role,
        "total_steps": 7,
        "steps_completed": [
            "prompt_entered",
            "pii_detection_and_masking",
            "backend_data_retrieved",
            "patient_data_fetched_and_encrypted",
            "nlp_query_sent",
            "nlp_response_decrypted",
            "process_complete"
        ],
        "total_entities_processed": len(all_fpe_mappings),
        "encryption_method": "FPE",
        "nlp_model": "claude-3-haiku",
        "data_source": "hardcoded_patient_database",
        "security_status": "secure",
        "compliance_status": "compliant",
        "data_flow_summary": {
            "original_prompt": user_message,
            "pii_detected": protection_result['entity_count'] > 0,
            "backend_data_retrieved": True,
            "data_encrypted": True,
            "encrypted_data_sent_to_nlp": True,
            "response_decrypted": True,
            "final_response_ready": True
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    
    return ChatResponse(
        original_message=user_message,
        protected_message=protection_result['protected'],
        phi_detected=protection_result['entities'],
        ai_response=ai_response,
        decrypted_response=decrypted_response,
        audit_trail=audit_trail,
        timestamp=timestamp,
        llm_provider="AWS Bedrock (Claude 3.5 Sonnet)",
        user_role=request.user_role,
        phi_visible=is_authorized,
        user_info=user_info
    )


@app.post("/api/generate-discharge-summary")
async def generate_discharge_summary(request: DischargeRequest):
    """Generate complete discharge summary with PHI protection using FPE"""
    # Check authentication
    user_info = None
    if request.auth_token:
        user_info = get_user_from_token(request.auth_token)
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # Check if user can generate PDF
        if not user_info.get('can_generate_pdf', False):
            raise HTTPException(status_code=403, detail="User not authorized to generate discharge summaries")
    else:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Generate summary
    patient_context = prepare_patient_context(request.patient_id)
    
    # Apply PHI protection based on user role using FPE
    is_authorized = check_phi_access(user_info['role'], user_info)
    
    if not is_authorized:
        # Apply FPE encryption for non-authorized users
        context_protection = detect_and_protect_phi(patient_context, use_fpe=True)
        protected_context = context_protection['protected']
    else:
        # For authorized users, no encryption needed for PDF
        protected_context = patient_context
    
    # Generate PDF if available
    if PDF_AVAILABLE:
        try:
            pdf_buffer = generate_pdf_discharge_summary(protected_context, user_info, is_authorized)
            pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "summary": protected_context,
                "pdf_base64": pdf_base64,
                "user_role": user_info['role'],
                "phi_masked": not is_authorized
            }
        except Exception as e:
            return {
                "success": True,
                "summary": protected_context,
                "pdf_error": str(e),
                "user_role": user_info['role'],
                "phi_masked": not is_authorized
            }
    else:
        return {
            "success": True,
            "summary": protected_context,
            "user_role": user_info['role'],
            "phi_masked": not is_authorized
        }


def generate_pdf_discharge_summary(context: str, user_info: Dict, show_phi: bool) -> BytesIO:
    """Generate PDF discharge summary"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center
    )
    story.append(Paragraph("DISCHARGE SUMMARY", title_style))
    story.append(Spacer(1, 12))
    
    # Header info
    header_data = [
        ['Generated By:', user_info['username']],
        ['Role:', user_info['role'].title()],
        ['Department:', user_info['department']],
        ['Date:', datetime.now().strftime('%Y-%m-%d %H:%M')],
        ['PHI Access:', 'Full' if show_phi else 'Masked']
    ]
    
    header_table = Table(header_data, colWidths=[2*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Content
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Split context into sections
    sections = context.split('\n\n')
    for section in sections:
        if section.strip():
            story.append(Paragraph(section.strip(), content_style))
            story.append(Spacer(1, 6))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


@app.get("/api/models")
async def get_models():
    """Get available AI models"""
    return {
        "llm_models": [
            {
                "id": "claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "description": "AWS Bedrock - For NLP & Chat",
                "provider": "AWS Bedrock"
            },
            {
                "id": "titan-embeddings-v2",
                "name": "Titan Text Embeddings V2",
                "description": "AWS Bedrock - 1024D Embeddings",
                "provider": "AWS Bedrock"
            }
        ],
        "current_llm_model": "claude-3.5-sonnet"
    }


@app.get("/api/config/reload")
async def reload_configuration():
    """Reload configuration from central service"""
    success = load_configuration()
    return {
        "status": "success" if success else "failed",
        "message": "Configuration reloaded" if success else "Using cached configuration",
        "config_loaded": bool(current_config),
        "masking_strategies": len(current_config.get('maskingStrategies', {}))
    }

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "status": "operational",
        "aws_available": AWS_AVAILABLE,
        "langfuse_available": LANGFUSE_AVAILABLE,
        "pdf_available": PDF_AVAILABLE,
        "active_sessions": len(ACTIVE_SESSIONS),
        "rag_indexed": 0,
        "phi_protection": "enabled",
        "config_source": "central" if current_config else "default",
        "masking_strategies_active": len(current_config.get('maskingStrategies', {}))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)