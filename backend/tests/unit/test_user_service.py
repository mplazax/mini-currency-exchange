"""
Unit tests for UserService
"""
import unittest
from unittest.mock import patch, MagicMock
from app.services.user_service import UserService
from app.models.user import User
from app.models.wallet import Wallet
from bson.objectid import ObjectId


class TestUserService(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Create a patcher for the DatabaseService
        self.db_patcher = patch('app.services.user_service.DatabaseService')
        self.mock_db_class = self.db_patcher.start()
        
        # Create a mock instance
        self.mock_db = MagicMock()
        self.mock_db_class.return_value = self.mock_db
        
        # Create the service
        self.user_service = UserService()
    
    def tearDown(self):
        """Clean up after tests"""
        self.db_patcher.stop()
    
    @patch('app.models.user.User.validate_registration')
    @patch('app.models.user.User.hash_password')
    @patch('app.models.wallet.Wallet.create_default_wallet')
    def test_register_success(self, mock_create_wallet, mock_hash_password, mock_validate):
        """Test successful user registration"""
        # Setup mocks
        mock_validate.return_value = {'is_valid': True, 'errors': {}}
        mock_hash_password.return_value = b'hashed_password'
        
        user_id = str(ObjectId())
        self.mock_db.get_user_by_email.return_value = None
        self.mock_db.create_user.return_value = user_id
        
        mock_wallet = MagicMock()
        mock_create_wallet.return_value = mock_wallet
        mock_wallet.to_dict.return_value = {'user': user_id, 'currencies': []}
        
        # Call the method
        result = self.user_service.register(
            email='test@example.com',
            password='password123',
            name='Test User'
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'User created successfully')
        self.assertEqual(result['user_id'], user_id)
        
        # Verify the mocks were called correctly
        mock_validate.assert_called_once_with(
            email='test@example.com',
            password='password123',
            name='Test User'
        )
        mock_hash_password.assert_called_once_with('password123')
        self.mock_db.get_user_by_email.assert_called_once_with('test@example.com')
        self.mock_db.create_user.assert_called_once()
        mock_create_wallet.assert_called_once_with(user_id)
        self.mock_db.create_wallet.assert_called_once_with(mock_wallet.to_dict())
    
    @patch('app.models.user.User.validate_registration')
    def test_register_invalid_data(self, mock_validate):
        """Test registration with invalid data"""
        # Setup mocks
        mock_validate.return_value = {
            'is_valid': False, 
            'errors': {'email': 'Invalid email'}
        }
        
        # Call the method
        result = self.user_service.register(
            email='invalid-email',
            password='password123',
            name='Test User'
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Invalid registration data')
        self.assertIn('errors', result)
        
        # Verify that database wasn't called
        self.mock_db.get_user_by_email.assert_not_called()
        self.mock_db.create_user.assert_not_called()
    
    def test_register_existing_user(self):
        """Test registration with existing email"""
        # Setup mocks
        self.mock_db.get_user_by_email.return_value = {'email': 'test@example.com'}
        
        # Call the method
        result = self.user_service.register(
            email='test@example.com',
            password='password123',
            name='Test User'
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Email already registered')
        
        # Verify that create_user wasn't called
        self.mock_db.create_user.assert_not_called()
    
    @patch('app.models.user.User.check_password')
    def test_login_success(self, mock_check_password):
        """Test successful login"""
        # Setup mocks
        user_data = {
            '_id': ObjectId('60f1e5b5c358f3b8a9f3b3a1'),
            'email': 'test@example.com',
            'name': 'Test User',
            'password': b'hashed_password'
        }
        self.mock_db.get_user_by_email.return_value = user_data
        mock_check_password.return_value = True
        
        # Call the method
        result = self.user_service.login(
            email='test@example.com',
            password='password123'
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Login successful')
        self.assertIn('user', result)
        self.assertEqual(result['user']['email'], 'test@example.com')
        
        # Verify the mocks were called correctly
        self.mock_db.get_user_by_email.assert_called_once_with('test@example.com')
        mock_check_password.assert_called_once_with(b'hashed_password', 'password123')
    
    def test_login_user_not_found(self):
        """Test login with non-existent email"""
        # Setup mocks
        self.mock_db.get_user_by_email.return_value = None
        
        # Call the method
        result = self.user_service.login(
            email='nonexistent@example.com',
            password='password123'
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Invalid email or password')
    
    @patch('app.models.user.User.check_password')
    def test_login_wrong_password(self, mock_check_password):
        """Test login with wrong password"""
        # Setup mocks
        user_data = {
            '_id': ObjectId('60f1e5b5c358f3b8a9f3b3a1'),
            'email': 'test@example.com',
            'name': 'Test User',
            'password': b'hashed_password'
        }
        self.mock_db.get_user_by_email.return_value = user_data
        mock_check_password.return_value = False
        
        # Call the method
        result = self.user_service.login(
            email='test@example.com',
            password='wrong_password'
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Invalid email or password')
    
    def test_get_user_wallet_success(self):
        """Test getting user wallet successfully"""
        # Setup mocks
        user_id = "60f1e5b5c358f3b8a9f3b3a1"
        user_data = {
            '_id': ObjectId(user_id),
            'email': 'test@example.com',
            'name': 'Test User'
        }
        wallet_data = {
            'user': user_id,
            'currencies': [
                {'currency': 'USD', 'value': 100.0}
            ]
        }
        transactions = [
            {'_id': ObjectId(), 'from_user': 'test@example.com'}
        ]
        
        self.mock_db.get_wallet_by_user_id.return_value = wallet_data
        self.mock_db.get_user_by_id.return_value = user_data
        self.mock_db.get_user_transactions.return_value = transactions
        
        # Call the method
        result = self.user_service.get_user_wallet(user_id)
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['wallet'], wallet_data)
        self.assertEqual(result['transactions'], transactions)
        self.assertEqual(result['email'], 'test@example.com')
        
        # Verify the mocks were called correctly
        self.mock_db.get_wallet_by_user_id.assert_called_once_with(user_id)
        self.mock_db.get_user_by_id.assert_called_once_with(user_id)
        self.mock_db.get_user_transactions.assert_called_once_with('test@example.com')
    
    def test_get_user_wallet_not_found(self):
        """Test getting non-existent wallet"""
        # Setup mocks
        user_id = "60f1e5b5c358f3b8a9f3b3a1"
        self.mock_db.get_wallet_by_user_id.return_value = None
        
        # Call the method
        result = self.user_service.get_user_wallet(user_id)
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Wallet not found')
    
    def test_get_transactions_all(self):
        """Test getting all transactions"""
        # Setup mocks
        transactions = [
            {'_id': ObjectId(), 'from_user': 'user1@example.com'},
            {'_id': ObjectId(), 'from_user': 'user2@example.com'}
        ]
        self.mock_db.get_all_transactions.return_value = transactions
        
        # Call the method
        result = self.user_service.get_transactions()
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['transactions'], transactions)
        
        # Verify the mocks were called correctly
        self.mock_db.get_all_transactions.assert_called_once()
        self.mock_db.get_user_transactions.assert_not_called()
    
    def test_get_transactions_user_specific(self):
        """Test getting user-specific transactions"""
        # Setup mocks
        user_email = 'test@example.com'
        transactions = [
            {'_id': ObjectId(), 'from_user': user_email}
        ]
        self.mock_db.get_user_transactions.return_value = transactions
        
        # Call the method
        result = self.user_service.get_transactions(user_email)
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['transactions'], transactions)
        
        # Verify the mocks were called correctly
        self.mock_db.get_all_transactions.assert_not_called()
        self.mock_db.get_user_transactions.assert_called_once_with(user_email)


if __name__ == '__main__':
    unittest.main() 