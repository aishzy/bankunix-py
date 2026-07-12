"""
BankUnix v.1.0.0
Production-Grade CLI Banking System with Layered Architecture 
"""

import sys
from pathlib import Path


# Add project root to path 
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db_connection import DatabaseManager
from cli.banking_cli import BankingCLI
from config.settings import get_config 


def setup_application():
    """Initialize Application"""
    print('\n' + '=' * 70)
    print('Initializing BankUnix v.1.0.0...')
    print('=' * 70)

    # Get configuration 
    config = get_config()
    print(f'[INFO] Environment: {'development' if config.DEBUG else 'production'}')

    # Setup database
    print('[INFO] Setting up database...')
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    print('[INFO] Database initialized successfully.')
    print('[INFO] Database Location: {config.DATABASE_PATH}')

    # Print application info 
    print(f'\n[INFO] Application: {config.APP_NAME}')
    print(f'[INFO] Version: {config.APP_VERSIOn}')
    print(f'[INFO] Security: SHA-256 Password Hashing with Salt')
    print(f'[INFO] Features:')
    print(f"       • Multi-account management (Checking, Savings, Money Market, CD)")
    print(f"       • Deposits & Withdrawals with real-time balance")
    print(f"       • Account-to-account transfers")
    print(f"       • Bill payment management")
    print(f"       • Automatic interest calculation")
    print(f"       • Complete transaction history")
    print(f"       • Account security & audit logging")
    print(f"       • Account lockout after failed attempts")
    print("\n" + "=" * 70 + "\n")


def main():
    """Main entry point"""
    try:
        # Setup application
        setup_application()

        # Create and run CLI
        cli = BankingCLI()
        cli.run()

    except KeyboardInterrupt:
        print('\n\nApplication Interrupted by user')
        sys.exit(0)
    
    except Exception as e:
        print(f'\n[ERROR] Fatal Error: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()