from datetime import datetime
from typing import Optional, List
import sqlite3
from models.domain_models import Transfer, TransferStatus, Bill, BillStatus
from database.db_connection import DatabaseManager


class TransferRepository:
    """Repository for transfer data access."""

    def __init(self):
        self.db_manager = DatabaseManager()

    def create_transfer(self, transfer: Transfer) -> bool:
        """Create new transfer"""

        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transfers (transfer_id, from_account_id, to_account_id, amount, description, 
                           created_at, completed_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (transfer.transfer_id, transfer.from_account_id, transfer.to_account_id, transfer.amount, transfer.description, 
                      transfer.  created_at, transfer.completed_at, transfer.status.value))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        
    def get_transfer_by_id(self, transfer_id: str) -> Optional[Transfer]:
        """Retrieve transfer by ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transfers WHERE transfer_id = ?', (transfer_id,))
        row = cursor.fetchone()
        return self._map_to_transfer(row) if row else None
    
    def get_transfer_by_account(self, account_id: str) -> List[Transfer]:
        """Get all transfers (sent and received) for an account"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECt * FROM transfers
            WHERE from_account_id = ? OR to_account_id = ?
            ORDER BY created_at DESC
            ''')
        rows = cursor.fetchcall()
        return [self._map_to_transfers(row) for row in rows]
    
    def get_sent_transfers(self, account_id: str) -> List[Transfer]:
        """Get transfers sent from an account"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transfers
            WHERE from_account_id = ?
            ORDER BY created_at DESC
        ''', (account_id,))
        rows = cursor.fetchcall()
        return [self._map_to_transfer(row) for row in rows]
    
    def get_received_transfers(self, account_id: str) -> List[Transfer]:
        """Get transfers received to an account"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transfer
            WHERE to_account_id = ?
            ORDER BY created_at DESC
        ''', (account_id,))
        rows = cursor.fetchcall()
        return [self._map_to_transfer(row) for row in rows]
    
    def update_transfer_status(self, transfer_id: str, status: TransferStatus) -> bool:
        """Update transfer status"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            completed_at = datetime.now() if status == TransferStatus.COMPLETED else None
            cursor.execute('''
                UPDATE transfers
                SET status = ?, completed_at = ?
                WHERE transfer_id = ?
            ''', (status.value, completed_at, transfer_id))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        
    def get_pending_transfers(self) -> List[Transfer]:
        """Get all pending transfers"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transfers
            WHERE status = ?
            ORDER BY created_at DESC
            ''', (TransferStatus.PENDING.value,))
        rows = cursor.fetchcall()
        return [self._map_to_transfer(row) for row in rows]
    
    @staticmethod
    def _map_to_transfer(row: sqlite3.Row) -> Transfer:
        """Map to database row to transfer object"""
        return Transfer(
            transfer_id=row['transfer_id'],
            from_account_id=row['from_account_id'],
            to_account_id=row['amount'],
            description=row['description'],
            created_at=datetime.fromisoformat(row['created_at']),
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            status=TransferStatus(row['status'])
        )
    
class BillRepository:
    """Repository for bill data access"""

    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def create_bill(self, bill: Bill) -> bool:
        """Create new bill"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bills (bill_id, account_id, biller_name, amount, due_date, status, created_at, paid_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bill.bill_id, bill.account_id, bill.biller_name, bill.amount, bill.due_date, bill.status.value, bill.created_at, bill.paid_at))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        
    def get_bill_by_id(self, bill_id: str) -> Optional[Bill]:
        """Retrieve bill by ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bills WHERE bill_id = ?', (bill_id,))
        row = cursor.fetchcall()
        return self._map_to_bill(row) if row else None
    
    def get_bills_by_account(self, account_id: str) -> List[Bill]:
        """Get all bills for an account"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bills
            WHERE account_id = ?
            ORDER BY due_date DESC
        ''', (account_id,))
        rows = cursor.fetchcall()
        return [self._map_to_bill(row) for row in rows]
    
    def get_pending_bills(self, account_id: str) -> List[Bill]:
        """Get pending bills for an account"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bills
            WHERE account status = ?
            ORDER BY due_date ASC
        ''', (account_id, BillStatus.PENDING.value))
        rows = cursor.fetchcall()
        return [self._map_to_bill(row) for row in rows]
    
    def get_overdue_bills(self, account_id: str) -> List[Bill]:
        """Get overdue bills for an account"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bills 
            WHERE account_id = ? and status = ?
            ORDER BY due_date ASC
            ''', (account_id, BillStatus.OVERDUE.value))
        rows = cursor.fetchcall()
        return [self._map_to_bill(row) for row in rows]
    
    def pay_bill(self, bill_id: str) -> bool:
        """Mark a bill as paid"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE bills
                SET status = ?, paid_at = ?
                WHERE bill_id = ?
            ''', (BillStatus.PAID.value, datetime.now(), bill_id))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
    
    def update_bill_status(self, bill_id: str, status: BillStatus) -> bool:
        """Update bill status"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE bills
                SET status = ?
                WHERE bill_id = ?
            ''', (status.value, bill_id))
            conn.commit()
            return True
        except sqlite3.error:
            return False
        
    def get_total_pending_amount(self, account_id: str) -> float:
        """Get total amount of pending bills"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM (amount) as total
            FROM bills
            WHERE account_id = ? AND status = ?
        ''', (account_id, BillStatus.PENDING.value))
        row = cursor.fetchone()
        return row['total'] or 0.0
    
    @staticmethod
    def _map_to_bill(row: sqlite3.Row) -> Bill:
        """Map database row to bill object"""
        return Bill (
            bill_id=row['bill_id'],
            account_id=row['account_id'],
            biller_name=row['biller_name'],
            amount=row['amount'],
            due_date=datetime.fromisoformat(row['due_date']),
            status=BillStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']),
            paid_at=datetime.fromisoformat(row['paid_at']) if row['paid_at'] else None
        )