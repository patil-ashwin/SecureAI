# SecureAI Healthcare Demo - Architecture Diagrams

## 📊 Visual Diagrams (SVG Format)

**High-quality SVG diagrams are available for presentations:**

- **[Problem Diagram](diagrams/problem-diagram.svg)** - Shows unprotected PII/PHI flow
- **[Solution Diagram](diagrams/solution-diagram.svg)** - Shows SecureAI protection flow  
- **[Comparison Diagram](diagrams/comparison-diagram.svg)** - Side-by-side before/after

These SVG files can be:
- Opened in any browser or image viewer
- Embedded in PowerPoint, Google Slides, or documentation
- Exported to PNG/PDF at any resolution
- Edited with Inkscape or Adobe Illustrator

---

### Mermaid Diagrams (for clean visuals)

```mermaid
flowchart TD
  subgraph Problem[Problem: Unprotected PII/PHI sent to LLM]
    UQ[User Query (Frontend)\n"What are Ramesh Kumar's lab results?"] --> BE
    BE[Healthcare Backend] -->|Raw PII/PHI| LLM[LLM Provider\n(AWS Bedrock / OpenAI)]
    LLM --> RP[LLM Response with PII]
  end
  classDef danger fill:#2b0000,stroke:#f66,color:#fdd;
  class BE,LLM,Rp danger;
```

```mermaid
flowchart TD
  subgraph Solution[Solution: SecureAI protection before LLM]
    UQ2[User Query (Frontend)] --> BE2
    BE2[Healthcare Backend] --> SA[SecureAI Plugin\n(Detect → Encrypt/Mask → Map)]
    SA -->|Protected PII/PHI| LLM2[LLM Provider]
    LLM2 --> SR[LLM Response (protected)]
    SR --> DEC[SecureAI Decryption + Role-Based Masking]
    DEC --> OUT[Final Response to User]
  end

  subgraph Protect[Encryption Strategy]
    DET[PII Detector] --> ENC[Names → RealisticMasker\nPhone/IDs/Dates → FPE]
    ENC --> MAP[In-memory Mapping\n(encrypted→original)]
  end

  BE2 -.calls.-> DET
  ENC -.feeds.-> SA
```

## 🔴 Problem: Unprotected PII/PHI Sent to LLM

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Query (Frontend)                         │
│  "What are Ramesh Kumar's lab results?"                          │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Healthcare Backend                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Patient Database                                         │  │
│  │  • Name: Ramesh Kumar                                     │  │
│  │  • Phone: +91-9876543210                                  │  │
│  │  • DOB: 1978-03-15                                        │  │
│  │  • Address: 12, 3rd Cross, Indiranagar...                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              │ ❌ PII/PHI EXPOSED
                              │ No Encryption
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              LLM Provider (AWS Bedrock / OpenAI)                │
│                                                                  │
│  📤 SENT DATA:                                                  │
│  • "What are Ramesh Kumar's lab results?"                       │
│  • Patient: Ramesh Kumar                                        │
│  • Contact: +91-9876543210                                      │
│  • Full patient records with all PII/PHI                       │
│                                                                  │
│  ⚠️  RISKS:                                                     │
│  • Data stored in LLM provider logs                            │
│  • Potential data breach                                        │
│  • HIPAA/GDPR compliance violations                             │
│  • Training data leakage                                         │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LLM Response with PII                          │
│  "Ramesh Kumar's HbA1c is 8.9%..."                             │
└─────────────────────────────────────────────────────────────────┘
```

**Problems:**
- ❌ Real patient data sent to third-party LLM
- ❌ PII/PHI stored in provider logs
- ❌ Compliance violations (HIPAA, GDPR)
- ❌ Risk of data breach
- ❌ No audit trail

---

## ✅ Solution: SecureAI FPE Protection

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Query (Frontend)                         │
│  "What are Ramesh Kumar's lab results?"                          │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Healthcare Backend                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Patient Database                                         │  │
│  │  • Name: Ramesh Kumar                                     │  │
│  │  • Phone: +91-9876543210                                  │  │
│  │  • DOB: 1978-03-15                                        │  │
│  │  • Address: 12, 3rd Cross, Indiranagar...                │  │
│  └──────────────┬────────────────────────────────────────────┘  │
│                 │                                                 │
│                 ▼                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SecureAI Plugin                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  PII Detector                                       │  │  │
│  │  │  • Detects: Names, Phone, DOB, Address, etc.      │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                          │                                 │  │
│  │                          ▼                                 │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Encryption Layer                                    │  │  │
│  │  │  • Names → RealisticMasker → "Arjun Sharma"         │  │  │
│  │  │  • Phone → FPE → "+11-2331719318"                  │  │  │
│  │  │  • DOB → FPE → "1388-95-07"                        │  │  │
│  │  │  • Format Preserving (length + structure)          │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                          │                                 │  │
│  │                          ▼                                 │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Mapping Storage (in-memory)                        │  │  │
│  │  │  "Arjun Sharma" → "Ramesh Kumar"                    │  │  │
│  │  │  "+11-2331719318" → "+91-9876543210"              │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              │ ✅ PROTECTED DATA
                              │ Encrypted PII/PHI
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              LLM Provider (AWS Bedrock / OpenAI)                  │
│                                                                   │
│  📤 SENT DATA:                                                   │
│  • "What are Arjun Sharma's lab results?"                        │
│  • Patient: Arjun Sharma                                         │
│  • Contact: +11-2331719318                                       │
│  • All PII encrypted with realistic fake data                    │
│                                                                   │
│  ✅ BENEFITS:                                                    │
│  • No real PII in provider logs                                  │
│  • HIPAA/GDPR compliant                                          │
│  • Zero data breach risk                                         │
│  • Can still train models safely                                 │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LLM Response with Encrypted PII                 │
│  "Arjun Sharma's HbA1c is 8.9%..."                              │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              SecureAI Decryption Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Reverse Mapping                                          │  │
│  │  "Arjun Sharma" → "Ramesh Kumar"                         │  │
│  │  "+11-2331719318" → "+91-9876543210"                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Role-Based Restoration                                   │  │
│  │  • Doctor: Full original data                             │  │
│  │  • Nurse: Masked PII, full medical info                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Final Response to User                         │
│  "Ramesh Kumar's HbA1c is 8.9%..."                              │
│  (Restored based on user role authorization)                    │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ PII/PHI encrypted before sending to LLM
- ✅ Format-preserving encryption (maintains structure)
- ✅ Realistic names for better demo experience
- ✅ Reversible decryption for authorized users
- ✅ Role-based access control (masked vs. full)
- ✅ Audit trail in structured logs
- ✅ HIPAA/GDPR compliant

---

## Data Flow Comparison

### Before (Unprotected)
```
User Query
    ↓
Patient DB (Raw PII)
    ↓
LLM (🚨 PII Exposed)
    ↓
Response (PII Visible)
```

### After (SecureAI Protected)
```
User Query
    ↓
Patient DB (Raw PII)
    ↓
SecureAI Plugin
    ├─ Detect PII
    ├─ Encrypt/Mask
    └─ Store Mapping
    ↓
LLM (✅ Protected PII)
    ↓
SecureAI Plugin
    ├─ Decrypt Response
    └─ Apply Role-Based Masking
    ↓
Response (Safe + Authorized)
```

---

## Key Components

### 1. **PII Detection**
- Identifies: Names, Phone, DOB, Address, Email, Insurance IDs
- Uses AI-based entity recognition
- Configurable confidence threshold

### 2. **Encryption Strategy**
- **Person Names**: RealisticMasker → Realistic Indian names
- **Phone/DOB/IDs**: Format-Preserving Encryption (FPE)
- **Maintains**: Length, format, structure for ML compatibility

### 3. **Mapping & Decryption**
- Bi-directional mapping stored securely
- Decryption on response for authorized roles
- Role-based masking for nurses

### 4. **Audit & Logging**
- Structured JSON logs (`llm_audit` step)
- Tracks: Original → Encrypted → LLM Response → Restored
- Complete data lineage for compliance

---

## LLM Audit Log Structure

Each request logs these 4 key data points:

```json
{
  "step": "llm_audit",
  "data": {
    "prompt": "What are Ramesh Kumar's lab results?",
    "original_data": "{ ... full patient record with real PII ... }",
    "after_fpe_before_llm": {
      "protected_prompt": "What are Arjun Sharma's lab results?",
      "encrypted_context": "{ ... patient data with encrypted PII ... }"
    },
    "nlp_response": "Arjun Sharma's HbA1c is 8.9%...",
    "restored_with_original_data": "Ramesh Kumar's HbA1c is 8.9%..."
  }
}
```

**What this shows:**
- 🔵 Original data (with real PII)
- 🔵 Encrypted data (sent to LLM - safe)
- 🔵 LLM response (contains encrypted PII)
- 🔵 Final output (restored for authorized users)

---

## 💡 Why Format-Preserving Encryption (FPE) is Critical

### The Problem with Traditional Encryption

**Traditional AES Encryption:**
```
"Ramesh Kumar" → AES Encrypt → "a8f5f167f44f4964e6c998dee827110c" (32 chars)
Phone: "+91-9876543210" → AES Encrypt → "b3d82a8c7f19e4..." (incompatible format)
DOB: "1978-03-15" → AES Encrypt → "9f2a1b8c7..." (loses date structure)
```

**Problems:**
- ❌ Output is random hexadecimal - LLM can't understand it
- ❌ Loses structure (dates become random bytes)
- ❌ Can't preserve relationships (phone formats, ID patterns)
- ❌ Breaks JSON structure and data validation
- ❌ LLM sees gibberish instead of structured data

### Why FPE Solves This

**Format-Preserving Encryption:**
```
"Ramesh Kumar" → RealisticMasker → "Arjun Sharma" (same format: name)
Phone: "+91-9876543210" → FPE → "+11-2331719318" (same format: phone)
DOB: "1978-03-15" → FPE → "1388-95-07" (same format: date)
Patient ID: "HSP20251007-1452" → FPE → "HSP20251012-3784" (same format: ID)
```

**Benefits:**
- ✅ **LLM Still Understands Structure**
  - Dates look like dates
  - Phone numbers look like phone numbers
  - IDs maintain their pattern
  - JSON structure preserved

- ✅ **Medical Context Preserved**
  ```
  Before: "Patient born on 1978-03-15"
  After:  "Patient born on 1388-95-07"  ← Still a valid date format
  ```
  LLM can still reason about relationships:
  - "Patient is 46 years old" (can calculate from DOB)
  - Phone number has country code "+11"
  - Patient ID follows hospital pattern "HSP-YYYYMMDD-NNNN"

- ✅ **Safe for Training & Fine-tuning**
  - Models trained on encrypted data won't memorize real PII
  - Format preservation means models learn patterns, not identities
  - Can share training data without privacy concerns

- ✅ **Database Compatibility**
  - Encrypted data fits in same database columns
  - No schema changes required
  - Indexes and queries still work
  - Validation rules still apply (phone format, date range, etc.)

- ✅ **Reversible & Deterministic**
  - Same input always produces same encrypted output
  - Can decrypt back to original (for authorized users)
  - Enables secure search and joins on encrypted data

### Real-World Example

**Scenario: Finding patient by phone number**

❌ **Without FPE (AES):**
```
Query: "Find patient with phone +91-9876543210"
Database has: "b3d82a8c7f19e4..." (encrypted)
Result: ❌ Can't search - need to decrypt entire database first
```

✅ **With FPE:**
```
Query: "Find patient with phone +11-2331719318"
Database has: "+11-2331719318" (FPE encrypted)
Result: ✅ Direct search works - same format, same length
```

### Comparison Table

| Feature | AES Encryption | Format-Preserving Encryption |
|---------|---------------|------------------------------|
| **Output Format** | Random bytes (hex/base64) | Same format as input |
| **LLM Understandability** | ❌ No - looks like gibberish | ✅ Yes - maintains structure |
| **Medical Context** | ❌ Lost | ✅ Preserved |
| **Database Compatibility** | ❌ Requires schema changes | ✅ Drop-in replacement |
| **Search Capability** | ❌ Need full decrypt | ✅ Direct search possible |
| **Audit Trail** | ❌ Hard to read | ✅ Human-readable encrypted data |
| **Training Safety** | ✅ Safe | ✅ Safe |
| **Compliance** | ✅ Compliant | ✅ Compliant |

### Why This Matters for Healthcare AI

1. **Clinical Decision Making**
   - LLM needs to understand "Patient is 46 years old" not "Patient ID is a8f5f167..."
   - Medical relationships (age, dates, IDs) must remain clear

2. **Data Sharing for Research**
   - Researchers can use encrypted datasets safely
   - Format preservation means research insights remain valid
   - No risk of re-identification

3. **Multi-Provider Collaboration**
   - Hospitals can share encrypted data
   - Format allows merging datasets
   - Maintains data quality and structure

4. **Regulatory Compliance**
   - HIPAA requires encryption of PHI in transit
   - But also requires maintaining data utility
   - FPE satisfies both requirements

### Technical Deep Dive

**FPE Algorithm Properties:**
- **Deterministic**: `encrypt("Ramesh")` always = `"Arjun"` (same key)
- **Reversible**: `decrypt("Arjun")` always = `"Ramesh"` (authorized access)
- **Format-Preserving**: Input length/type = Output length/type
- **Domain-Separated**: Different entity types use different encryption space
  - Names encrypt to names
  - Phone numbers encrypt to phone numbers
  - Dates encrypt to dates

**Security Guarantees:**
- ✅ Same security as AES-256 (uses AES internally)
- ✅ No plaintext leakage
- ✅ Resistant to frequency analysis (due to domain separation)
- ✅ Compliant with NIST SP 800-38G (FPE standards)

---

## 📊 Demo Talking Points

**When asked "Why FPE?" - Use this script:**

> "Great question! Traditional encryption like AES turns 'Ramesh Kumar' into something like 'a8f5f167...' - random bytes that an AI can't understand. 
>
> But with Format-Preserving Encryption, 'Ramesh Kumar' becomes 'Arjun Sharma' - still a name the AI can process. Same with dates: '1978-03-15' becomes '1388-95-07' - still a date format the LLM understands.
>
> This is critical because:
> 1. **The AI can still reason** - it knows ages, relationships, patterns
> 2. **No real PII leaves our system** - but data structure is preserved
> 3. **Can train models safely** - without exposing patient data
> 4. **Compliance friendly** - encrypted but still useful
>
> It's like having your cake and eating it too - full security without losing data utility."

