"""
User service for authentication and user operations
"""
from typing import Dict, Any, Optional
import logging
from app.models.user import User
from app.models.wallet import Wallet
from app.services.database import DatabaseService

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related operations"""
    
    def __init__(self):
        """Initialize with a database service"""
        self.db = DatabaseService()
    
    def register(
        self,
        email: str,
        password: str,
        name: str
    ) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            email: User email
            password: User password
            name: User name
            
        Returns:
            Dict with registration status and message
        """
        # Validate user data
        validation = User.validate_registration(
            email=email,
            password=password,
            name=name
        )
        
        if not validation['is_valid']:
            return {
                'success': False,
                'message': 'Invalid registration data',
                'errors': validation['errors']
            }
        
        # Check if user already exists
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            return {
                'success': False,
                'message': 'Email already registered'
            }
        
        # Create user
        hashed_password = User.hash_password(password)
        
        user_data = {
            'email': email,
            'name': name,
            'password': hashed_password
        }
        
        try:
            user_id = self.db.create_user(user_data)
            
            # Create wallet with default currencies
            wallet = Wallet.create_default_wallet(user_id)
            self.db.create_wallet(wallet.to_dict())
            
            return {
                'success': True,
                'message': 'User created successfully',
                'user_id': user_id
            }
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }
    
    def login(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate a user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict with login status and user info if successful
        """
        # Get user
        user_data = self.db.get_user_by_email(email)
        
        if not user_data:
            return {
                'success': False,
                'message': 'Invalid email or password'
            }
        
        # Check password
        if not User.check_password(user_data['password'], password):
            return {
                'success': False,
                'message': 'Invalid email or password'
            }
        
        # Create user model
        user = User.from_db_record(user_data)
        
        return {
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        }
    
    def get_user_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's wallet
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with wallet data
        """
        try:
            wallet_data = self.db.get_wallet_by_user_id(user_id)
            
            if not wallet_data:
                return {
                    'success': False,
                    'message': 'Wallet not found'
                }
                
            user_data = self.db.get_user_by_id(user_id)
            
            if not user_data:
                return {
                    'success': False,
                    'message': 'User not found'
                }
                
            # Get user transactions
            transactions = self.db.get_user_transactions(user_data['email'])
            
            # Convert ObjectId to string
            for transaction in transactions:
                if '_id' in transaction:
                    transaction['_id'] = str(transaction['_id'])
                    
            return {
                'success': True,
                'wallet': wallet_data,
                'transactions': transactions,
                'email': user_data['email']
            }
        except Exception as e:
            logger.error(f"Error getting wallet: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }
    
    def get_transactions(self, user_email: str = None) -> Dict[str, Any]:
        """
        Get transactions, optionally filtered by user
        
        Args:
            user_email: Optional user email to filter by
            
        Returns:
            Dict with transactions
        """
        try:
            if user_email:
                transactions = self.db.get_user_transactions(user_email)
            else:
                transactions = self.db.get_all_transactions()
                
            # Convert ObjectId to string
            for transaction in transactions:
                if '_id' in transaction:
                    transaction['_id'] = str(transaction['_id'])
                    
            return {
                'success': True,
                'transactions': transactions
            }
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            } 