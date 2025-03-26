"""
Integration tests for API routes
"""
import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.services.database import DatabaseService
from bson.objectid import ObjectId


class TestAPI(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Create a patcher for the DatabaseService
        self.db_patcher = patch('app.services.database.DatabaseService')
        self.mock_db_class = self.db_patcher.start()
        
        # Create a mock instance
        self.mock_db = MagicMock()
        self.mock_db_class.return_value = self.mock_db
        
        # Initialize collections
        self.mock_db.users = MagicMock()
        self.mock_db.wallets = MagicMock()
        self.mock_db.offers = MagicMock()
        self.mock_db.transactions = MagicMock()
        
        # Create app
        self.app = create_app('testing')
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up after tests"""
        self.db_patcher.stop()
    
    def test_register_route(self):
        """Test register route"""
        # Mock responses
        user_id = str(ObjectId())
        self.mock_db.get_user_by_email.return_value = None
        self.mock_db.create_user.return_value = user_id
        
        # Define test data
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User'
        }
        
        # Make request
        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'User created successfully')
    
    def test_register_route_existing_email(self):
        """Test register route with existing email"""
        # Mock responses
        self.mock_db.get_user_by_email.return_value = {'email': 'test@example.com'}
        
        # Define test data
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User'
        }
        
        # Make request
        response = self.client.post(
            '/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Email already registered')
    
    @patch('app.models.user.User.check_password')
    def test_login_route_success(self, mock_check_password):
        """Test login route success"""
        # Mock responses
        user_id = str(ObjectId())
        user_data = {
            '_id': ObjectId(user_id),
            'email': 'test@example.com',
            'name': 'Test User',
            'password': b'hashed_password'
        }
        self.mock_db.get_user_by_email.return_value = user_data
        mock_check_password.return_value = True
        
        # Define test data
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        # Make request
        response = self.client.post(
            '/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Login successful')
        self.assertEqual(response_data['user']['email'], 'test@example.com')
    
    def test_login_route_invalid_email(self):
        """Test login route with invalid email"""
        # Mock responses
        self.mock_db.get_user_by_email.return_value = None
        
        # Define test data
        data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        
        # Make request
        response = self.client.post(
            '/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Invalid email or password')
    
    def test_get_offers_route_unauthorized(self):
        """Test get_offers route unauthorized"""
        # Make request without login
        response = self.client.get('/get_offers')
        
        # Assertions
        self.assertEqual(response.status_code, 401)
    
    def test_get_offers_route_authorized(self):
        """Test get_offers route when authorized"""
        # Mock offers
        offer_id = ObjectId()
        offers = [
            {
                '_id': offer_id,
                'from_user': 'user1@example.com',
                'from_value': 100.0,
                'from_currency': 'USD',
                'to_value': 85.0,
                'to_currency': 'EUR'
            }
        ]
        self.mock_db.get_all_offers.return_value = offers
        
        # Login with session
        with self.client.session_transaction() as session:
            session['user_id'] = str(ObjectId())
            session['email'] = 'test@example.com'
        
        # Make request
        response = self.client.get('/get_offers')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['_id'], str(offer_id))
    
    def test_add_offer_route_authorized(self):
        """Test add_offer route when authorized"""
        # Mock database responses
        user_id = str(ObjectId())
        user = {'_id': ObjectId(user_id)}
        wallet = {
            'user': user_id,
            'currencies': [
                {'currency': 'USD', 'value': 200.0}
            ]
        }
        
        self.mock_db.get_user_by_email.return_value = user
        self.mock_db.get_wallet_by_user_id.return_value = wallet
        self.mock_db.find_matching_offers.return_value = []
        
        # Login with session
        with self.client.session_transaction() as session:
            session['user_id'] = user_id
            session['email'] = 'test@example.com'
        
        # Define test data
        data = {
            'fromValue': 100.0,
            'fromCurrency': 'USD',
            'toValue': 85.0,
            'toCurrency': 'EUR'
        }
        
        # Make request
        response = self.client.post(
            '/add_offer',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Offer added successfully')


if __name__ == '__main__':
    unittest.main() 