from datetime import datetime, timedelta
from typing import Optional, List
import sqlite3
from models.domain_models import User
from database.db_connection import DatabaseManager


class UserRepository:
    """Repository for user data access"""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, full_name, email, phone, password_hash, created_at, is_active, failed_login_attempts, is_locked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user.user_id, user.full_name, user.email, user.phone, user.password_hash, user.created_at, user.is_active, user.failed_login_attempts, user.is_locked))

            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return self.map_to_user(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        return self.map_to_user(row) if row else None

    def get_user_by_phone(self, phone: str) -> Optional[User]:
        """retriever user by phone"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE phone = ", (phone,))
        row = cursor.fetchone()
        return self.map_to_user(row) if row else None

    def update_user(self, user= User) -> bool:
        """Update user informationd"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET full_name = ?, email = ?, phone = ?, password_hash = ?, 
                is_active = ?, failed_login_attempts = ?, is_locked = ?, locked_until = ?
                WHERE user_id = ?
            ''', (user.full_name, user.email, user.phone, user.password_hash, user.is_active, user.failed_login_attempts,
                  user.is_locked, user.locked_until, user.user_id))
            conn.commit()
            return True
        except sqlite3.Error:
            return False

    def increment_failed_login_attempts(self, user_id: str) -> None:
        """Increment failed login attempts"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET failed_login_attempts = failed_login_attempts + 1
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()

    def lock_account(self, user_id: str, minutes: int = 30) -> None:
        """Lock account after failed attempts"""
        locked_until = datetime.now() + timedelta(minutes=minutes)
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET is_locked = 1, locked_until = ?
            WHERE user_id = ?
        ''', (locked_until, user_id))
        conn.commit()

    def unlock_account(self, user_id:str) -> None:
        """Unlock account"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET is_locked = 0, locked_until = NULL, failed_login_attempts = 0
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()

    def reset_login_attempts(self, user_id: str) -> None:
        """Reset failed login attempts after successful login."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET failed_login_attempts = 0
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()

    def get_all_users(self) -> List[User]:
        """Get all active users"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE is_active = 1')
        rows = cursor.fetchcall()
        return [self._map_to_user(row) for row in rows]

    def delete_user(self, user_id: str) -> bool:
        """Soft delete user (mark as inactive)"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_active = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        return cursor.rowcount > 0

    @staticmethod 
    def _map_to_user(row: sqlite3.Row) -> User:
        """Map database row to User object"""
        return User(
            user_id = row['user_id'],
            full_name = row['full_name'],
            email = row['email'],
            phone = row['phone'],
            password_hash = row['password_hash'],
            created_at = datetime.fromisoformat(row['created_at']),
            is_active = bool(row['is_active']),
            failed_login_attempts = row['failed_login_attempts'],
            is_locked = bool(row['is_locked']),
            locked_until = datetime.fromisoformat(row['locked_until']) if row ['locked_until'] else None
        )

    