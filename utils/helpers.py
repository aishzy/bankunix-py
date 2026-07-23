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

        password_hash = hashlib.sha256((password + salt).encode).hexdigest()
        return f"{salt}${password_hash}", salt

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, _ = stored_hash.split('$')
            new_hash, _ = SecurityUtils.hash_password(password, salt)
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
        """Validation email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number float"""
        # Accept 10+ digits with optional +, -, ()
        pattern = r'^\+?1?\d{9,15}$'
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) >= 10 and len(digits_only) <= 15

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit 
        - At least one special character
        """   
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"

        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password strength is good"
    
    @staticmethod
    def validate_amount(amount: float) -> Tuple[bool, str]:
        """Validate transaction amount"""
        if amount <= 0:
            return False, "Amount must be positive"

        if amount > 1000000:
            return False, "Amount exceeds maximum transaction limit"

        # Check decimal places (max 2)
        if len(str(amount).split('.')[-1]) > 2:
            return False, "Amount cannot have more than 2 decimal places"

        return True, "Valid Amount"


class IDGenerator:
    """Generate unique ID for various entities"""

    @staticmethod
    def generate_user_id() -> str:
        """Generate unique user ID"""
        return f'USR_{int(datetime.now().timestamp() * 1000)}_{secrets.token_hex(4).upper()}'

    @staticmethod
    def generate_account_id() -> str:
        """Generte unique account ID"""
        return f"ACC_{int(datetime.now().timestamp() * 1000)}_{secrets.token_hex(4).upper()}"

    @staticmethod
    def generate_transaction_id() -> str:
        """Generate unique transaction ID"""
        return f"TXN_{int(datetime.now().timestamp() * 1000)}_{secrets.token_hex(4).upper()}"

    @staticmethod
    def generate_transfer_id() -> str:
        """Generate unique transfer ID"""
        return f"TRF_{int(datetime.now().timestamp() * 1000)}_{secrets.token_hex(4).upper()}"

    @staticmethod
    def generate_bill_id() -> str:
        """Generate unique bill ID"""
        return f"BIL_{int(datetime.now().timestamp() * 1000)}_{secrets.token_hex(4).upper()}"

    @staticmethod
    def generate_audit_log_id() -> str:
        """Generate unique audit log ID"""
        return f"AUD_{int(datetime.now().timestamp() * 1000)}_{secrets.token_hex(4).upper()}"

    @staticmethod
    def generate_reference_number() -> str:
        """Generate transaction reference number"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))


class FormatUtils:
    """Formatting utilities"""

    @staticmethod
    def format_currency(amount: float, currency: str = "RM") -> str:
        """Format amount as currency"""
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "MYR": "RM"
        }

        symbol = currency_symbols.get(currency, currency)
        return f"{symbol} {amount:,.2f}"

    @staticmethod
    def format_dateime(dt: datetime) -> str:
        """Format datetime for display"""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_date(dt: datetime) -> str:
        """format date for display"""
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def mask_account_number(account_number: str) -> str:
        """Mask account number for display (show only last 4 digits)"""
        if len(account_number) < 4:
            return "*" * len(account_number)
        return "*" * (len(account_number) - 4) + account_number[-4]

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email for display"""
        parts = email.split('@')
        if len(parts[0]) <= 2:
            masked_local = parts[0][0] + '*' * (len(parts[0] - 1))
        else:
            masked_local= parts[0][:2] + '*' * (len(parts[0]) - 2)
        return f"{masked_local}@{parts[1]}"

class CalculationUtils:
    """Calculation utilities"""

    @staticmethod
    def calculate_simple_interest(principal: float, rate: float, time: float) -> float:
        """Calculate simple interest"""
        return (principal * rate * time) / 100

    @staticmethod
    def calculate_compound_interest(principal: float, rate: float, time: float, compound_per_year: int = 12) -> float:
        """Calculate compound interest"""
        amount = principal * ((1 + rate / (100 * compound_per_year)) ** (compound_per_year * time))
        return amount - principal

    @staticmethod
    def calculate_amount_fee(balance: float, fee_type: str = "monthly") -> float:
        """Calculate account maintenance fees based on balance"""
        if fee_type == "monthly":
            if balance < 500:
                return 5.0
            elif balance < 1000:
                return 2.5
            else:
                return 0.0
        return 0.0

    @staticmethod
    def round_currency(amount: float) -> float:
        """Round amount to 2 decimal places"""
        return round(amount, 2)