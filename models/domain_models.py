from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AccountType(Enum):
    CHECKING = 'CHECKING'
    SAVINGS = 'SAVINGS'
    MONEY_MARKET = 'MONEY_MARKET'
    CERTIFICATE_OF_DEPOSIT = 'CERTIFICATE_OF_DEPOSIT'

class TransactionType(Enum):
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'
    TRANSFER_OUT = 'TRANSFER_OUT'
    TRANSFER_IN = 'TRANSFER_IN'
    INTEREST = 'INTEREST'
    BILL_PAYMENT = 'BILL_PAYMENT'
    FEE = 'FEE'

class TransactionStatus(Enum):
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELLED ='CANCELLED'

class TransferStatus(Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    OVERDUE = 'OVERDUE'
    CANCELLED = 'CANCELLED'

class BillStatus(Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    OVERDUE = 'OVERDUE'
    CANCELLED = 'CANCELLED'

@dataclass 
class User:
    """Represents a bank user"""
    user_id: str
    full_name: str
    email: str
    phone: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    failed_login_attempts: int = 0
    is_locked: bool = False
    locked_until: Optional[datetime] = None

    def is_account_locked(self) -> bool:
        if not self.is_locked:
            return False
        if self.locked_until and datetime.now() > self.locked_until:
            return False
        return True
    
@dataclass 
class Account:
    """Represents a bank account"""
    account_id: str
    user_id: str
    account_type: AccountType
    account_number: str
    balance: float
    currency: str = 'MYR'
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    last_transaction_at: Optional[datetime] = None
    interest_rate: float = 0.0

    def get_account_type_display(self) -> str:
        type_display = {
            AccountType.CHECKING: 'Checking Account',
            AccountType.SAVINGS: 'Savings Account',
            AccountType.MONEY_MARKET: 'Money Market Account',
            AccountType.CERTIFICATE_OF_DEPOSIT: 'Certificate of Deposit'
        }
        return type_display.get(self.account_type, str(self.account_type))
    
@dataclass 
class Transaction:
    """Represents a transaction"""
    transaction_id: str
    account_id: str
    transaction_type: TransactionType
    amount: float
    description: str
    balance_after: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: TransactionStatus = TransactionStatus.COMPLETED
    reference_number: Optional[str] = None

@dataclass
class Transfer:
    """Represents a transfer between accounts"""
    transfer_id: str
    from_account_id: str
    to_account_id: str
    amount: float
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: TransferStatus = TransferStatus.PENDING

@dataclass
class Bill:
    """Represents a bill payment"""
    bill_id: str
    account_id: str
    biler_name: str
    amount: float
    due_date: datetime
    status: BillStatus = BillStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None

@dataclass
class AuditLog:
    """Represents an audit log entry"""    
    log_id: str
    user_id: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    changes: Optional[str]
    timestamp: datetime = field(default_factory=datetime.now)
    ip_address: Optional[str] = None
    status: str = 'SUCCESS'
    