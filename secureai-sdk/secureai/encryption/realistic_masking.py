"""
Realistic Masking for Healthcare/Medical Contexts
Generates realistic-looking fake data instead of random encrypted values
"""

import hashlib
from typing import Dict, List
from secureai.detection.entities import EntityType


class RealisticMasker:
    """
    Generate realistic fake data for masking sensitive information.
    Uses deterministic mapping so same input always gets same fake value.
    """
    
    # Indian names for realistic substitution
    INDIAN_FIRST_NAMES_MALE = [
        "Arjun", "Rahul", "Amit", "Vikram", "Rajesh", "Suresh", "Anil", "Ravi",
        "Karthik", "Sanjay", "Manoj", "Deepak", "Nikhil", "Rohan", "Ashwin",
        "Vivek", "Anand", "Harish", "Prakash", "Ganesh"
    ]
    
    INDIAN_FIRST_NAMES_FEMALE = [
        "Priya", "Anjali", "Neha", "Kavita", "Sunita", "Rekha", "Meena", "Asha",
        "Divya", "Pooja", "Swati", "Nisha", "Ritu", "Geeta", "Smita",
        "Shweta", "Anita", "Maya", "Radha", "Sita"
    ]
    
    INDIAN_LAST_NAMES = [
        "Kumar", "Singh", "Sharma", "Patel", "Reddy", "Nair", "Iyer", "Rao",
        "Gupta", "Verma", "Menon", "Shah", "Desai", "Joshi", "Agarwal",
        "Chopra", "Malhotra", "Kapoor", "Mehta", "Pillai"
    ]
    
    DOCTOR_NAMES = [
        "Dr. Priya Mehta", "Dr. Rajesh Kumar", "Dr. Anita Sharma", "Dr. Vikram Singh",
        "Dr. Sunita Patel", "Dr. Anil Reddy", "Dr. Kavita Nair", "Dr. Manoj Iyer",
        "Dr. Neha Gupta", "Dr. Arjun Rao", "Dr. Pooja Verma", "Dr. Rahul Desai"
    ]
    
    def __init__(self):
        self._name_cache: Dict[str, str] = {}
        self._doctor_cache: Dict[str, str] = {}
    
    def _deterministic_index(self, value: str, max_idx: int) -> int:
        """Get deterministic index from hash of value"""
        hash_val = int(hashlib.md5(value.encode()).hexdigest(), 16)
        return hash_val % max_idx
    
    def mask_person_name(self, name: str) -> str:
        """
        Mask person name with realistic Indian name.
        Deterministic: same input always produces same output.
        
        Args:
            name: Original name (e.g., "Ramesh Kumar")
        
        Returns:
            Realistic fake name (e.g., "Arjun Sharma")
        """
        if name in self._name_cache:
            return self._name_cache[name]
        
        # Split name into parts
        parts = name.strip().split()
        
        if len(parts) == 1:
            # Single name - just use first name
            idx = self._deterministic_index(name, len(self.INDIAN_FIRST_NAMES_MALE))
            fake_name = self.INDIAN_FIRST_NAMES_MALE[idx]
        elif len(parts) == 2:
            # First + Last name
            first_idx = self._deterministic_index(parts[0], len(self.INDIAN_FIRST_NAMES_MALE))
            last_idx = self._deterministic_index(parts[1], len(self.INDIAN_LAST_NAMES))
            
            fake_first = self.INDIAN_FIRST_NAMES_MALE[first_idx]
            fake_last = self.INDIAN_LAST_NAMES[last_idx]
            fake_name = f"{fake_first} {fake_last}"
        else:
            # Multiple names - use first and last part
            first_idx = self._deterministic_index(parts[0], len(self.INDIAN_FIRST_NAMES_MALE))
            last_idx = self._deterministic_index(parts[-1], len(self.INDIAN_LAST_NAMES))
            
            fake_first = self.INDIAN_FIRST_NAMES_MALE[first_idx]
            fake_last = self.INDIAN_LAST_NAMES[last_idx]
            fake_name = f"{fake_first} {fake_last}"
        
        self._name_cache[name] = fake_name
        return fake_name
    
    def mask_doctor_name(self, name: str) -> str:
        """
        Mask doctor name with realistic doctor name.
        
        Args:
            name: Original doctor name (e.g., "Dr. Priya Mehta")
        
        Returns:
            Realistic fake doctor name (e.g., "Dr. Anita Sharma")
        """
        if name in self._doctor_cache:
            return self._doctor_cache[name]
        
        idx = self._deterministic_index(name, len(self.DOCTOR_NAMES))
        fake_name = self.DOCTOR_NAMES[idx]
        
        self._doctor_cache[name] = fake_name
        return fake_name
    
    def mask_phone_number(self, phone: str) -> str:
        """
        Mask phone number while preserving format.
        
        Args:
            phone: Original phone (e.g., "+91-9876543210")
        
        Returns:
            Fake phone with same format (e.g., "+91-8765432109")
        """
        # Extract digits
        digits = ''.join(c for c in phone if c.isdigit())
        
        # Generate fake digits deterministically
        hash_val = int(hashlib.md5(phone.encode()).hexdigest(), 16)
        fake_digits = str(hash_val % (10 ** len(digits))).zfill(len(digits))
        
        # Preserve original format
        result = ""
        digit_idx = 0
        for char in phone:
            if char.isdigit():
                result += fake_digits[digit_idx]
                digit_idx += 1
            else:
                result += char
        
        return result
    
    def mask_address(self, address: str) -> str:
        """
        Mask address with realistic fake address.
        
        Args:
            address: Original address
        
        Returns:
            Fake address with similar structure
        """
        addresses = [
            "45, MG Road, Koramangala, Bengaluru, Karnataka, India",
            "23, Residency Road, Jayanagar, Bengaluru, Karnataka, India",
            "67, Infantry Road, Ashok Nagar, Bengaluru, Karnataka, India",
            "89, Brigade Road, Shantinagar, Bengaluru, Karnataka, India",
            "34, Richmond Road, Indiranagar, Bengaluru, Karnataka, India"
        ]
        
        idx = self._deterministic_index(address, len(addresses))
        return addresses[idx]
    
    def mask_patient_id(self, patient_id: str) -> str:
        """
        Mask patient ID while preserving format.
        
        Args:
            patient_id: Original ID (e.g., "HSP20251007-1452")
        
        Returns:
            Fake ID with same format (e.g., "HSP20251012-3784")
        """
        # Extract pattern
        hash_val = int(hashlib.md5(patient_id.encode()).hexdigest(), 16)
        
        # Preserve prefix and generate fake numbers
        result = ""
        for char in patient_id:
            if char.isdigit():
                result += str(hash_val % 10)
                hash_val //= 10
            else:
                result += char
        
        return result
    
    def mask_value(self, value: str, entity_type: EntityType) -> str:
        """
        Mask value based on entity type with realistic data.
        
        Args:
            value: Original value
            entity_type: Type of entity
        
        Returns:
            Realistic fake value
        """
        if entity_type == EntityType.PERSON:
            # Check if it's a doctor name
            if value.lower().startswith("dr.") or value.lower().startswith("doctor"):
                return self.mask_doctor_name(value)
            return self.mask_person_name(value)
        
        elif entity_type == EntityType.PHONE:
            return self.mask_phone_number(value)
        
        elif entity_type == EntityType.ADDRESS:
            return self.mask_address(value)
        
        elif "patient" in str(entity_type).lower() or "id" in str(entity_type).lower():
            return self.mask_patient_id(value)
        
        else:
            # For other types, use FPE or default masking
            return value
    
    def get_reverse_mapping(self) -> Dict[str, str]:
        """
        Get reverse mapping (fake → original) for decryption.
        
        Returns:
            Dictionary mapping fake values to original values
        """
        reverse_map = {}
        
        # Reverse name mappings
        for original, fake in self._name_cache.items():
            reverse_map[fake] = original
        
        for original, fake in self._doctor_cache.items():
            reverse_map[fake] = original
        
        return reverse_map

