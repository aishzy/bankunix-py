from datetime import datetime
from typing import Optional, Tuple
from models.domain_models import User
from repositories.user_repository import UserRepository
from utils.helpers import SecurityUtils, ValidationUtils, IDGenerator


class AuthenticationService:
    """Service for authentication service"""

    def __init__(self):
        self.user_repo = UserRepository()
        self.max_failed_attempts = 5

    def register_user(self, full_name: str, email: str, phone: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """Register a new User
            Returns: (success, message, user_object)
        """
        # Validate inputs 
        if not ValidationUtils.validate_email(email):
            return False, "Invalid Email Format", None
        
        if not ValidationUtils.validate_phone(phone):
            return False, "Invalid Phone Format", None
        
        is_strong, msg = ValidationUtils.validate_password_strength(password)
        if not is_strong:
            return False, msg, None
        
        # Check if user already exists
        if self.user_repo.get_user_by_email(email):
            return False, "Email already registered", None
        
        if self.user_repo.get_user_by_phone(phone):
            return False, "Phone number already registered", None
        
        # Create new user
        user_id = IDGenerator.generate_user_id()
        password_hash, _ = SecurityUtils.hash_password(password)

        user = User(
            user_id = user_id,
            full_name = full_name,
            email = email,
            phone = phone,
            password_hash = password_hash,
            created_at = datetime.now()
        )

        if self.user_repo.create_user(user):
            return True, "User registered successfully", user
        else:
            return False, "Error registering user", None
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticate User
        Returns: (success, message, user_object)
        """
        user = self.user_repo.get_user_by_email(email)

        if not user:
            return False, "Invalid Email or Password", None
        
        # Check if account is locked
        if user.is_account_locked():
            return False, "Account is locked, Try again later.", None
        
        # Verify password 
        if not  SecurityUtils.verify_password(password, user.password_hash):
            self.user_repo.increment_failed_login_attempts(user.user_id)

            # Lock account after max attempts 
            if user.failed_login_attempts + 1 >= self.max_failed_attempts:
                self.user_repo.lock_account(user.user_id)
                return False, "Too many failed attempts, Account locked for 30 minutes", None
            
            return False, "Invalid Email or Password", None
        
        # Reset failed attempts on successful login
        self.user_repo.reset_login_attempts(user.user_id)

        if not user.is_active:
            return False, "Account is inactive", None
        return True, "Login successful", user
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password
            Returns: (success, message)
        """
        user = self.user_repo.get_user_by_id(user_id)

        if not user:
            return False, "User not found"
        
        # Verify old password 
        if not SecurityUtils.verify_password(old_password, user.password_hash):
            return False, "Current password is incorrect"
        
        # Validate new password
        is_strong, msg = ValidationUtils.validate_password_strength(new_password)
        if not is_strong:
            return False, msg
        
        # Update password
        user.password_hash, _ = SecurityUtils.hash_password(new_password)

        if self.user_repo.update_user(user):
            return True, "Password changed successfully"
        else:
            return False, "Error changing password"
    
    def reset_password(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Reset user password and return temporary password
        Returns: (success, mesage, temp_password)
        """
        user = self.user_repo.get_user_by_email(email)

        if not user:
            return False, "Email not found", None
        
        # Generate temporary password 
        temp_password = SecurityUtils.generate_secure_password(12)
        user.password_hash, _ = SecurityUtils.hash_password(temp_password)

        if self.user_repo.update_user(user):
            return True, "Temporary password generated, Please check your email", temp_password
        else:
            return False, "Error resetting password", None
        
    def verify_email(self, user_id: str) -> Tuple[bool, str]:
        """Verify user email (mark as verified)"""
        user = self.user_repo.get_user_by_id(user_id)

        if not user:
            return False, "User not found"
        
        # In production, this would be a proper email verification flow
        return True, "Email Verified successfully"
    
    def unlock_account(self, user_id: str) -> Tuple[bool, str]:
        """Unlock a locked account (admin function)"""
        user = self.user_repo.get_user_by_id(user_id)

        if not user:
            return False, "User not found"
        
        self.user_repo.unlock_account(user_id)
        return True, "Account unlocked successfully"
    
    def get_user_profile(self, user_id: str) -> Optional[dict]:
        """Get user profile information"""
        user = self.user_repo.get_user_by_id(user_id)

        if not user:
            return None
        
        return {
            'user_id': user.user_id,
            'full_name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'created_at': user.created_at,
            'is_active': user.is_active,
            'is_locked': user.is_account_locked()
        }