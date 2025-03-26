import unittest
from unittest.mock import patch, MagicMock
from app import app
import json
from bson.objectid import ObjectId

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.records')
    @patch('app.wallets')
    def test_register(self, mock_wallets, mock_records):
        # Setup mocks
        mock_records.find_one.return_value = None
        mock_records.insert_one.return_value = MagicMock(inserted_id=ObjectId("60f1e5b5c358f3b8a9f3b3a1"))
        mock_wallets.insert_one.return_value = None

        # Test registration
        response = self.app.post('/register', 
                                json={
                                    'email': 'test@example.com',
                                    'name': 'Test User',
                                    'password': 'password123'
                                })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User created successfully')

    @patch('app.records')
    @patch('app.bcrypt')
    def test_login(self, mock_bcrypt, mock_records):
        # Setup mocks
        mock_user = {
            '_id': ObjectId("60f1e5b5c358f3b8a9f3b3a1"),
            'email': 'test@example.com',
            'name': 'Test User',
            'password': b'hashed_password'
        }
        mock_records.find_one.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        # Test login
        response = self.app.post('/login', 
                                json={
                                    'email': 'test@example.com',
                                    'password': 'password123'
                                })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Login successful')

    @patch('app.offers')
    def test_get_offers(self, mock_offers):
        # Setup mocks
        mock_offers.find.return_value = [
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

        # Test get offers
        response = self.app.get('/get_offers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['from_currency'], 'USD')

if __name__ == '__main__':
    unittest.main() 