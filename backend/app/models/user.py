"""
User model
"""
from flask_login import UserMixin
from bson.objectid import ObjectId
import bcrypt
from typing import Dict, Any, Optional


class User(UserMixin):
    """User model for Flask-Login"""
    
    def __init__(self, user_id: str, email: str, name: str = None):
        """
        Initialize a user
        
        Args:
            user_id: MongoDB user ID
            email: User email
            name: User name (optional)
        """
        self.id = str(user_id)
        self.email = email
        self.name = name
    
    @staticmethod
    def validate_registration(email: str, password: str, name: str) -> Dict[str, Any]:
        """
        Validate user registration data
        
        Args:
            email: User email
            password: User password
            name: User name
            
        Returns:
            Dict with validation status and errors if any
        """
        errors = {}
        
        # Validate email
        if not email or '@' not in email:
            errors['email'] = 'Valid email is required'
            
        # Validate password
        if not password or len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long'
            
        # Validate name
        if not name:
            errors['name'] = 'Name is required'
            
        return {
            'is_valid': len(errors) == 0, 
            'errors': errors
        }
    
    @staticmethod
    def hash_password(password: str) -> bytes:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def check_password(hashed_password: bytes, password: str) -> bool:
        """
        Check if a password matches a hash
        
        Args:
            hashed_password: Hashed password
            password: Plain text password to check
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    @classmethod
    def from_db_record(cls, user_record: Dict[str, Any]) -> Optional['User']:
        """
        Create a User instance from a database record
        
        Args:
            user_record: User record from database
            
        Returns:
            User instance or None if record is invalid
        """
        if not user_record:
            return None
            
        return cls(
            user_id=str(user_record['_id']),
            email=user_record['email'],
            name=user_record.get('name')
        ) 