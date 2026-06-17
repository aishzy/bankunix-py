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
