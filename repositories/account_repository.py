from datetime import datetime
from typing import Optional, List
import sqlite3
from models.domain_models import Account, AccountType
from database.db_connection import DatabaseManager


class AccountRepository:
    """Repository for account data access."""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def create_account(self, account: Account) -> bool:
        """Create new account"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accounts (account_id, user_id, account_type, account_number,
                                        balance, currency, created_at, is_active, interest_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (account.account_id, account.user_id, account.account_number, account.balance, account.currency, account.created_at, 
                  account.is_active, account.interest_rate))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        
    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        """Retrieve account by ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE accound_id = ?', (account_id,))
        row = cursor.fetchone()
        return self.map_to_account(row) if row else None
    
    def get_account_by_number(self, account_number: str) -> Optional[Account]:
        """Retrieve account by account number"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM WHERE account_number = ?', (account_number,))
        row = cursor.fetchone()
        return self._map_to_account(row) if row else None
    
    def get_accounts_by_user(self, user_id: str) -> List[Account]:
        """Retrieve all accounts for a user"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM WHERE user_id = ? AND is_active = 1', (user_id,))
        rows = cursor.fetchall()
        return [self._map_to_account(row) for row in rows]
    
    