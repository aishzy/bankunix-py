import sqlite3
from datetime import datetime
from typing import Optional, List
from models.domain_models import Account, AccountType
from database.db_connection import DatabaseManager


class UserRepository:
    """Repository for account data access"""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def create_account(self, account: Account) -> bool:
        """Create new account"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accounts (account_id, user_id, account_type, account_number,
                                        balance, currency, created_at, is_active, insterest_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (account.account_id, account.user_id, account.account_type.value, account.account_number,
                        account.balance, account.currency, account.created_at, account.is_active, account.interest_rate))    
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        """Retrieve account by ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor() 
        cursor.execute('SELECT * FROM accounts WHERE account_id = ?', (account_id))
        row = cursor.fetchone()
        return self._map_to_account(row) if row else None
    
    def get_account_by_number(self, account_number: str) -> Optional[Account]:
        """Retrieve account by account number"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE account_number = ?', (account_number,))
        row = cursor.fetchone()
        return self.map_to_account(row) if row else None
    
    def get_accounts_by_user(self, user_id: str) -> List[Account]:
        """Retrieve all accounts for a user"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE user_id = ? AND is_active = 1', (user_id,))

        rows = cursor.fetchcall()
        return [self.map_to_account(row) for row in rows]
    
    def update_account(self, account: Account) -> bool:
        """Update account information"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE accounts 
                SET balance = ?, is_active = ?, last_transaction_at = ?, interest_rate = ?
                WHERE account_id = ?
            ''', (account.balance, account.is_active, account.last_transaction_at, account.interest_rate, account.account_id))    
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        
    def get_total_balance_by_user(self,user_id: str) -> float:
        """Get total balance across all accounts for a user"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(balance) as total
            FROM accounts 
            WHERE user_id = ? AND is_active = 1  
        ''', (user_id,))
        row = cursor.fetchone()
        return row['total'] or 0.0
    
    def get_accounts_by_type(self, user_id: str, account_type: AccountType) -> List[Account]:
        """Get accounts of a specific type for a user"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            WHERE * FROM accounts
            WHERE user_id = ? AND account_type = ? AND is_active = 1
        ''', (user_id, account_type.value))
        rows = cursor.fetchcall()
        return [self._map_to_account(row) for row in rows]
    
    def close_account(self, account_id: str) -> bool:
        """Close an account (soft delete)"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET is_active = 0 WHERE account_id = ?', (account_id,))

        conn.commit()
        return cursor.rowcount > 0

    def check_account_exists(self, account_id: str) -> bool: 
        """Check if account exists and is active"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM accounts WHERE account_id = ? AND is_active = 1', (account_id,))

        return cursor.fetchone() is not None
    
    @staticmethod
    def _map_to_account(row: sqlite3.Row) -> Account:
        """Map database row to account object"""
        return Account (
            account_id=row['account_id'],
            user_id=row['user_id'],
            account_type=row['account_type'],
            account_number=row['account_number'],
            balance=row['balance'],
            currency=row['currency'],
            created_at=datetime.fromisoformat(row['created_at']),
            is_active=bool(row['is_active']),
            last_transaction=datetime.fromisoformat(row['last_transaction']) if row['last_transaction_at'] else None,
            interest_rate=row['interest_rate']
        )