"""
Tests for the Flask application
"""
import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from app.services.database import DatabaseService
import json
from bson.objectid import ObjectId


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app.testing = True
        
        # Mock the database service
        self.db_patcher = patch('app.services.database.DatabaseService')
        self.mock_db = self.db_patcher.start()
        
        # Set up database service as a mock
        self.mock_db_instance = MagicMock()
        self.mock_db.return_value = self.mock_db_instance
        
        # Set up users collection mock
        self.mock_db_instance.users = MagicMock()
        self.mock_db_instance.wallets = MagicMock()
        self.mock_db_instance.offers = MagicMock()
        self.mock_db_instance.transactions = MagicMock()
    
    def tearDown(self):
        self.db_patcher.stop()

    def test_register(self):
        # Setup mocks
        self.mock_db_instance.get_user_by_email.return_value = None
        self.mock_db_instance.create_user.return_value = str(ObjectId("60f1e5b5c358f3b8a9f3b3a1"))
        self.mock_db_instance.create_wallet.return_value = None

        # Test registration
        response = self.client.post('/register', 
                                json={
                                    'email': 'test@example.com',
                                    'name': 'Test User',
                                    'password': 'password123'
                                })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User created successfully')

    @patch('app.models.user.User.check_password')
    def test_login(self, mock_check_password):
        # Setup mocks
        mock_user = {
            '_id': ObjectId("60f1e5b5c358f3b8a9f3b3a1"),
            'email': 'test@example.com',
            'name': 'Test User',
            'password': b'hashed_password'
        }
        self.mock_db_instance.get_user_by_email.return_value = mock_user
        mock_check_password.return_value = True

        # Test login
        response = self.client.post('/login', 
                                json={
                                    'email': 'test@example.com',
                                    'password': 'password123'
                                })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Login successful')

    def test_get_offers(self):
        # Setup mock session
        with self.client.session_transaction() as session:
            session['user_id'] = 'test_user_id'
            session['email'] = 'test@example.com'
            
        # Setup mocks
        mock_offers = [
            {
                '_id': ObjectId("60f1e5b5c358f3b8a9f3b3a1"),
                'from_user': 'user1@example.com',
                'from_value': 100,
                'from_currency': 'USD',
                'to_value': 85,
                'to_currency': 'EUR',
                'date': '2023-01-01T12:00:00Z'
            }
        ]
        self.mock_db_instance.get_all_offers.return_value = mock_offers

        # Test get offers
        response = self.client.get('/get_offers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['from_currency'], 'USD')


if __name__ == '__main__':
    unittest.main() 