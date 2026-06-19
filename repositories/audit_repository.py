from datetime import datetime
from typing import Optional, List
import sqlite3
from models.domain_models import Transfer, TransferStatus, Bill, TransactionStatus
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
        
