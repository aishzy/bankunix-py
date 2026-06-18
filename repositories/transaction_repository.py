from datetime import datetime
from typing import Optional, List
import sqlite3
from models.domain_models import Transaction, TransactionType, TransactionStatus
from database.db_connection import DatabaseManager


class TransactionRepository:
    """Repository for transaction data access."""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def create_transaction(self, transaction: Transaction) -> bool:
        """Create new transaction"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (transaction_id, account_id, transaction_type, amount, description, balance_after, timestamp, status,
                                reference_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (transaction.transaction_id, transaction.account_id, transaction.transaction_type.value, transaction.amount, 
                  transaction.description, transaction.balance_after, transaction.timestamp, transaction.status.value, transaction.reference_number))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
    
    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Retrieve transaction by ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE transaction_id = ?', (transaction_id,))
        row = cursor.fetchone()
        return self._map_to_transaction(row) if row else None

    def get_transactions_by_account(self, account_id: str, limit: int=100) -> Optional[Transaction]:
        """Get transactions for an account (most recent first)"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions
            WHERE account_id = ?
            ORDER BY timestamp DESC
            LIMIT ?      
        ''', (account_id, limit))
        rows = cursor.fetchcall()
        return [self._map_to_transaction(row) for row in rows]
            
        
