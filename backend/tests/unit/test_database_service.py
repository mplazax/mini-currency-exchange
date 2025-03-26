"""
Unit tests for DatabaseService
"""
import unittest
from unittest.mock import patch, MagicMock
import os
from app.services.database import DatabaseService
from bson.objectid import ObjectId


class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        # Reset singleton instance before each test
        DatabaseService._instance = None

    @patch('app.services.database.MongoClient')
    def test_singleton_pattern(self, mock_mongo_client):
        """Test DatabaseService singleton pattern"""
        # Setup mock
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # Create two instances
        db1 = DatabaseService()
        db2 = DatabaseService()
        
        # Assert they are the same instance
        self.assertIs(db1, db2)
        
        # Mongo client should be created only once
        mock_mongo_client.assert_called_once()
    
    @patch('app.services.database.MongoClient')
    @patch('app.services.database.os.getenv')
    def test_init_with_uri(self, mock_getenv, mock_mongo_client):
        """Test initialization with MongoDB URI"""
        # Setup mocks
        mock_getenv.side_effect = lambda key, default=None: {
            'MONGO_URI': 'mongodb://test:27017',
            'MONGO_DB': 'test_db'
        }.get(key, default)
        
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # Create instance
        db = DatabaseService()
        
        # Assert correct connection
        mock_mongo_client.assert_called_once_with('mongodb://test:27017')
        mock_client.get_database.assert_called_once_with('test_db')
    
    @patch('app.services.database.MongoClient')
    @patch('app.services.database.os.getenv')
    def test_init_without_uri(self, mock_getenv, mock_mongo_client):
        """Test initialization without MongoDB URI"""
        # Setup mocks
        mock_getenv.side_effect = lambda key, default=None: {
            'MONGO_URI': None,
            'MONGO_DB': 'test_db'
        }.get(key, default)
        
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # Create instance
        db = DatabaseService()
        
        # Assert correct connection to localhost
        mock_mongo_client.assert_called_once_with('localhost', 27017)
        mock_client.get_database.assert_called_once_with('test_db')
    
    @patch('app.services.database.MongoClient')
    def test_close(self, mock_mongo_client):
        """Test closing database connection"""
        # Setup mock
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # Create instance and close
        db = DatabaseService()
        # Manually set the client to ensure we're testing the right instance
        db.client = mock_client
        db.close()
        
        # Assert client was closed
        mock_client.close.assert_called_once()
    
    @patch('app.services.database.MongoClient')
    def test_get_user_by_email(self, mock_mongo_client):
        """Test getting user by email"""
        # Setup mocks
        mock_users = MagicMock()
        mock_client = MagicMock()
        mock_client.get_database().register = mock_users
        mock_mongo_client.return_value = mock_client
        
        # Create instance
        db = DatabaseService()
        db.users = mock_users
        
        # Call method
        db.get_user_by_email('test@example.com')
        
        # Assert query
        mock_users.find_one.assert_called_once_with({'email': 'test@example.com'})
    
    @patch('app.services.database.MongoClient')
    def test_get_user_by_id(self, mock_mongo_client):
        """Test getting user by ID"""
        # Setup mocks
        mock_users = MagicMock()
        mock_client = MagicMock()
        mock_client.get_database().register = mock_users
        mock_mongo_client.return_value = mock_client
        
        # Create instance
        db = DatabaseService()
        db.users = mock_users
        
        # Call method
        user_id = '60f1e5b5c358f3b8a9f3b3a1'
        db.get_user_by_id(user_id)
        
        # Assert query
        mock_users.find_one.assert_called_once_with({'_id': ObjectId(user_id)})
    
    @patch('app.services.database.MongoClient')
    def test_create_user(self, mock_mongo_client):
        """Test creating a user"""
        # Setup mocks
        mock_users = MagicMock()
        mock_client = MagicMock()
        mock_client.get_database().register = mock_users
        mock_mongo_client.return_value = mock_client
        
        # Mock insert result
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId('60f1e5b5c358f3b8a9f3b3a1')
        mock_users.insert_one.return_value = mock_result
        
        # Create instance
        db = DatabaseService()
        db.users = mock_users
        
        # Call method
        user_data = {'email': 'test@example.com', 'name': 'Test User'}
        result = db.create_user(user_data)
        
        # Assert result
        self.assertEqual(result, '60f1e5b5c358f3b8a9f3b3a1')
        mock_users.insert_one.assert_called_once_with(user_data)
    
    @patch('app.services.database.MongoClient')
    def test_get_wallet_by_user_id(self, mock_mongo_client):
        """Test getting wallet by user ID"""
        # Setup mocks
        mock_wallets = MagicMock()
        mock_client = MagicMock()
        mock_client.get_database().wallets = mock_wallets
        mock_mongo_client.return_value = mock_client
        
        # Create instance
        db = DatabaseService()
        db.wallets = mock_wallets
        
        # Call method
        user_id = '60f1e5b5c358f3b8a9f3b3a1'
        db.get_wallet_by_user_id(user_id)
        
        # Assert query
        mock_wallets.find_one.assert_called_once_with({'user': user_id})
    
    @patch('app.services.database.MongoClient')
    def test_update_wallet(self, mock_mongo_client):
        """Test updating a wallet"""
        # Setup mocks
        mock_wallets = MagicMock()
        mock_client = MagicMock()
        mock_client.get_database().wallets = mock_wallets
        mock_mongo_client.return_value = mock_client
        
        # Mock update result
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_wallets.update_one.return_value = mock_result
        
        # Create instance
        db = DatabaseService()
        db.wallets = mock_wallets
        
        # Call method
        user_id = '60f1e5b5c358f3b8a9f3b3a1'
        wallet_data = {
            'user': user_id,
            'currencies': [{'currency': 'USD', 'value': 100.0}]
        }
        result = db.update_wallet(user_id, wallet_data)
        
        # Assert result
        self.assertTrue(result)
        mock_wallets.update_one.assert_called_once_with(
            {'user': user_id},
            {'$set': wallet_data}
        )
    
    @patch('app.services.database.MongoClient')
    def test_get_offer_by_id(self, mock_mongo_client):
        """Test getting offer by ID"""
        # Setup mocks
        mock_offers = MagicMock()
        mock_client = MagicMock()
        mock_client.get_database().offers = mock_offers
        mock_mongo_client.return_value = mock_client
        
        # Create instance
        db = DatabaseService()
        db.offers = mock_offers
        
        # Call method
        offer_id = '60f1e5b5c358f3b8a9f3b3a1'
        db.get_offer_by_id(offer_id)
        
        # Assert query
        mock_offers.find_one.assert_called_once_with({'_id': ObjectId(offer_id)})
    
    @patch('app.services.database.MongoClient')
    def test_find_matching_offers(self, mock_mongo_client):
        """Test finding matching offers"""
        # Setup mocks
        mock_offers = MagicMock()
        mock_client = MagicMock()
        mock_client.get_database().offers = mock_offers
        mock_mongo_client.return_value = mock_client
        
        # Create instance
        db = DatabaseService()
        db.offers = mock_offers
        
        # Call method
        db.find_matching_offers(
            to_currency='USD',
            from_currency='EUR',
            from_value=100.0
        )
        
        # Assert query
        mock_offers.find.assert_called_once()
        args, kwargs = mock_offers.find.call_args
        query = args[0]
        self.assertEqual(query['from_currency'], 'USD')
        self.assertEqual(query['to_currency'], 'EUR')
        self.assertIn('to_value', query)


if __name__ == '__main__':
    unittest.main() 