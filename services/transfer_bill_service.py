from datetime import datetime
from typing import Optional, List, Tuple
from models.domain_models import Transfer, TransferStatus, Bill, BillStatus, Transaction, TransactionType, TransactionStatus
from repositories.account_repository import AccountRepository
from repositories.audit_repository import TransferRepository, BillRepository
from repositories.transaction_repository import TransactionRepository
from utils.helpers import IDGenerator, ValidationUtils


class TransferService:
    """Service for money transfers between accounts"""
    def __init__(self):
        self.transfer_repo = TransferRepository()
        self.account_repo = AccountRepository()
        self.transacation_repo = TransactionRepository()

    def transfer_money(self, from_account_id: str, to_account_id: str, amount: float, description: str = 'Transfer') -> Tuple[bool, str]:
        """
        Transfer money from one account to another
        Returns: (success, message)    
        """ 

        # Validate amount
        is_valid, msg = ValidationUtils.validate_amount(amount)
        if not is_valid:
            return False, msg

        # Get accounts 
        from_account = self.account_repo.get_account_by_id(from_account_id)
        to_account = self.account_repo.get_account_by_id(to_account_id)

        if not from_account or not to_account:
            return False, "Invalid account(s)"
        
        if not from_account.is_active or not to_account.is_active:
            return False, "One or both accounts are inactive."
        
        if from_account_id == to_account_id:
            return False, "Cannot transfer to the same account"
        
        # Check sufficient balance 
        if from_account.balance < amount:
            return False, "Insufficient balance"
        
        # Create transfer record 
        transfer_id = IDGenerator.generate_transfer_id()
        transfer = transfer(
            transfer_id = transfer_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            description=description,
            created_at=datetime.now(),
            status=TransferStatus.PENDING
        )
