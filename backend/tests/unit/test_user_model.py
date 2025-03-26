"""
Unit tests for User model
"""
import unittest
from app.models.user import User
import bcrypt


class TestUserModel(unittest.TestCase):
    def test_user_initialization(self):
        """Test User model initialization"""
        user = User(user_id="123", email="test@example.com", name="Test User")
        
        self.assertEqual(user.id, "123")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "Test User")
    
    def test_validate_registration_valid(self):
        """Test valid registration data validation"""
        result = User.validate_registration(
            email="test@example.com",
            password="password123",
            name="Test User"
        )
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_registration_invalid_email(self):
        """Test invalid email validation"""
        result = User.validate_registration(
            email="invalid-email",
            password="password123",
            name="Test User"
        )
        
        self.assertFalse(result['is_valid'])
        self.assertIn('email', result['errors'])
    
    def test_validate_registration_short_password(self):
        """Test short password validation"""
        result = User.validate_registration(
            email="test@example.com",
            password="short",
            name="Test User"
        )
        
        self.assertFalse(result['is_valid'])
        self.assertIn('password', result['errors'])
    
    def test_validate_registration_no_name(self):
        """Test missing name validation"""
        result = User.validate_registration(
            email="test@example.com",
            password="password123",
            name=""
        )
        
        self.assertFalse(result['is_valid'])
        self.assertIn('name', result['errors'])
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "password123"
        hashed = User.hash_password(password)
        
        self.assertIsInstance(hashed, bytes)
        self.assertNotEqual(hashed, password.encode('utf-8'))
        self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), hashed))
    
    def test_check_password(self):
        """Test password verification"""
        password = "password123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        self.assertTrue(User.check_password(hashed, password))
        self.assertFalse(User.check_password(hashed, "wrongpassword"))
    
    def test_from_db_record(self):
        """Test creating User from DB record"""
        record = {
            '_id': "123",
            'email': "test@example.com",
            'name': "Test User"
        }
        
        user = User.from_db_record(record)
        
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, "123")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "Test User")
    
    def test_from_db_record_none(self):
        """Test creating User from None record"""
        user = User.from_db_record(None)
        self.assertIsNone(user)


if __name__ == '__main__':
    unittest.main() 