import hashlib
import secrets
import string
from datetime import datetime
from typing import Tuple
import uuid
import re

class SecurityUtils:
    """Security utilities for password hashing and validation"""

    @staticmethod
    def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password using SHA-256 with salt"""
        if salt is None:
            salt = secrets.token_hex(16)

        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f'{salt}{password_hash}', salt
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""

        try:
            salt, _ = stored_hash.split('$')
            new_hash, _ = SecurityUtils.hash_password(salt, password)
            return new_hash == stored_hash
        except ValueError:
            return False
    
    @staticmethod
    def generate_secure_password(length: int = 12) -> str:
        """Generate a secure random password"""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))


class ValidationUtils:
    """Validation utilities"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""

        # Accept 10+ digits with optional +, -, ()
        pattern = r'^\+?1?\d{9, 15}$'
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) >= 10 and len(digits_only) <= 15
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength
            Requirements:
                - minimum 8 characters
                - at least one uppercase letter
                - at least one lowercase letter
                - at least one digit
                - at least one special character
        """
        if len(password) < 8:
            return False, 'Password must be at least 8 characters long'
        
        if not not re.search(r'[A-Z]', password):
            return False, 'Password must contain at least one uppercase letter'
        
        if not re.search(r'[a-z]', password):
            return False, 'Password must contain at least one lowercase letter'
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, 'Password must contain at least one special character'
        
        return True, 'Password strength is good'
    
    @staticmethod
    def validate_amount(amount: float) -> Tuple[bool, str]:
        """Validate transaction amount"""
        if amount <= 0:
            return False, 'Amount must be positive'
        
        if amount > 100000:
            return False, 'Amount exceeds maximum transaction limit'
        
        # Check decimal places (max 2)
        if len(str(amount).split('.')[-1]) > 2:
            return False, 'Amount cannot have more than 2 decimal places'
        
        return True, 'Valid amount'
    
