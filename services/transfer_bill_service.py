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

        if not self.transfer_repo.create_transfer(transfer):
            return False, "Error creating transfer"
        
        # Process transfer - deduct from source 
        from_new_balance = from_account.balance - amount
        if not self.account_repo.update_balance(from_account_id, from_new_balance):
            return False, "Error processing transfer (debit)"
        
        # Add to destination 
        to_new_balance = to_account.balance + amount
        if not self.account_repo.update_balance(to_account_id, to_new_balance):
            # Rollback source debit
            self.account_repo.update_balance(from_account_id, from_account.balance)
            return False, "Error processing transfer (credit)"

        # Update transfer status to completed 
        self.transfer_repo.update_transfer_status(transfer_id, TransferStatus.COMPLETED)

        # Record Transaction 
        # Outgoing transaction
        out_transaction = Transaction (
            transaction_id = IDGenerator.generate_transfer_id(),
            accound_id = from_account_id, 
            transaction_type = TransactionType.TRANSFER_OUT,
            amount = amount,
            description = f"Transfer to account {to_account.account_number[-4:]}",
            balance_after = to_new_balance,
            timestamp = datetime.now(),
            status = TransactionStatus.COMPLETED,
            reference_number = transfer_id
        )

        # Incoming transaction
        in_transaction = Transaction (
            transaction_id = IDGenerator.generate_transfer_id(),
            account_id = to_account_id,
            transaction_type = TransactionType.TRANSFER_IN, 
            amount = amount, 
            description = f"Transfer from account {from_account.account_number [-4:]}",
            balance_after = to_new_balance, 
            timestamp = datetime.now(),
            status = TransactionStatus.COMPLETED,
            reference_number = transfer_id
        )

        self.transaction_repo.create_transaction(out_transaction)
        self.transaction_repo.create_transaction(in_transaction)

        return True, f"Transfer amount {amount} completed successfully. Reference: {transfer_id}"
    
    def get_transfer_status(self, transfer_id: str) -> Optional[str]:
        """Get transfer status"""
        transfer = self.transfer_repo.get_transfer_by_id(transfer_id)
        return transfer.status.value if transfer else None
    
    def get_transfer_history(self, account_id: str) -> List[Transfer]:
        """Get transfer history for an account."""
        return self.transfer_repo.get_transfers_by_account(account_id)
    
    def get_sent_transfers(self, account_id: str) -> List[Transfer]:
        """Get sent transfers"""
        return self.transfer_repo.get_sent_transfers(account_id)
    
    def get_received_transfers(self, account_id: str) -> List[Transfer]:
        """Get received transfers"""
        return self.transfer_repo.get_received_transfers(account_id)
    

class BillPaymentService:
    """"Service for bill management and payments"""    

    def __init__(self):
        self.bill_repo = BillRepository()
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionRepository()

    def add_bill(self, account_id: str, biller_name: str, amount: float, due_date: datetime) -> Tuple[bool, str]:
        """
        Add bill to an account
        Returns: (success, message)
        """

        # Validate amount
        is_valid, msg = ValidationUtils.validate_amount(amount)
        if not is_valid:
            return False, msg
        
        account = self.account_repo.get_account_by_id(account_id)
        if not account:
            return False, "Account not found"
        
        bill = bill (
            bill_id = IDGenerator.generate_bill_id(),
            account_id = account_id, 
            biller_name = biller_name, 
            amount = amount,
            due_date = due_date,
            status = BillStatus.PENDING,
            created_at = datetime.now()
        )

        if self.bill_repo.create_bill(bill):
            return True, f"Bill from {biller_name} added successfully."
        else:
            return False, "Error adding bill"
        
    def pay_bill(self, bill_id: str) -> Tuple[bool, str]:
        """
        Pay a bill
        Returns: (success, message)
        """

        bill = self.bill_repo.get_bill_by_id(bill_id),
        if not bill:
            return False, "Bill not found"
        
        if bill.status != BillStatus.PENDING:
            return False, f'Bill is already {bill.status.value}'
        
        account = self.account_repo.get_account_by_id(bill.account_id)
        if not account:
            return False, "Account not found"
        
        # Check sufficient balance
        if account.balance < bill.amount:
            return False, "Insufficient balance to pay bill"
        
        # Deduct amount from account
        new_balance = account.balance - bill.amount
        if not self.account_repo.update_balance(bill.account_id, new_balance):
            return False, "Error processing bill payment"
        
        # Update bill status
        if not self.bill_repo.pay_bill(bill_id):
            # Rollback balance 
            self.account_repo.update_balance(bill.account_id, account.balance)
            return False, "Error updating bill status"
        
        # Record transaction 
        transaction = Transaction (
            transaction_id = IDGenerator.generate_transaction_id(),
            account_id = bill.account_id, 
            transaction_type = TransactionType.BILL_PAYMENT, 
            amount = bill.amount, 
            description = f"Bill payment to {bill.biller_name}",
            balance_after = new_balance, 
            timestamp = datetime.now(),
            status = TransactionStatus.COMPLETED, 
            reference_number = bill_id
        )

        self.transaction_repo.create_transaction(transaction)

        return True, f"Bill payment of {bill.amount} to {bill.biller_name} completed"
    
    def get_pending_bills(self, account_id: str) -> List[Bill]:
        """Get pending bills for an account"""
        return self.bill_repo.get_pending_bills(account_id)
    
    def get_bill_history(self, account_id: str) -> List[Bill]:
        """Get all bills for an account"""
        return self.bill_repo.get_bills_by_account(account_id)
    
    def get_overdue_bills(self, account_id: str) -> List[Bill]:
        """Get overdue bills"""
        return self.bill_repo.get_overdue_bills(account_id)
    
    def get_total_pending_amount(self, account_id: str) -> float:
        """Get total amount of pending bills."""
        return self.bill_repo.get_total_pending_amount(account_id)
    
    def check_and_mark_overdue(self, account_id: str) -> int:
        """Check and mark bills as overdue if due date has passed"""
        bills = self.get_pending_bills(account_id)
        overdue_count = 0

        for bill in bills:
            if bill.due_date < datetime.now() and bill.status == BillStatus.PENDING:
                self.bill_repo.update_bill_status(bill.bill_id, BillStatus.OVERDUE)
                overdue_count = 1

        return overdue_count 