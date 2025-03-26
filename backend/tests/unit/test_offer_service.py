"""
Unit tests for OfferService
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
from app.services.offer_service import OfferService
from app.models.offer import Offer
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from bson.objectid import ObjectId


class TestOfferService(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Create a patcher for the DatabaseService
        self.db_patcher = patch('app.services.offer_service.DatabaseService')
        self.mock_db_class = self.db_patcher.start()
        
        # Create a mock instance
        self.mock_db = MagicMock()
        self.mock_db_class.return_value = self.mock_db
        
        # Create the service
        self.offer_service = OfferService()
    
    def tearDown(self):
        """Clean up after tests"""
        self.db_patcher.stop()
    
    @patch('app.models.offer.Offer.validate_offer')
    def test_create_offer_invalid(self, mock_validate):
        """Test creating an invalid offer"""
        # Setup mocks
        mock_validate.return_value = {
            'is_valid': False,
            'errors': {'from_value': 'Value must be greater than 0'}
        }
        
        # Call the method
        result = self.offer_service.create_offer(
            from_user_email='user1@example.com',
            from_value=-100.0,
            from_currency='USD',
            to_value=85.0,
            to_currency='EUR'
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Invalid offer')
        self.assertIn('errors', result)
        
        # Verify that other methods weren't called
        self.mock_db.get_user_by_email.assert_not_called()
    
    def test_create_offer_user_not_found(self):
        """Test creating an offer with non-existent user"""
        # Setup mocks for validation
        with patch('app.models.offer.Offer.validate_offer') as mock_validate:
            mock_validate.return_value = {'is_valid': True, 'errors': {}}
            
            # Setup mocks for database
            self.mock_db.get_user_by_email.return_value = None
            
            # Call the method
            result = self.offer_service.create_offer(
                from_user_email='nonexistent@example.com',
                from_value=100.0,
                from_currency='USD',
                to_value=85.0,
                to_currency='EUR'
            )
            
            # Assertions
            self.assertFalse(result['success'])
            self.assertEqual(result['message'], 'User not found')
    
    def test_create_offer_wallet_not_found(self):
        """Test creating an offer when wallet doesn't exist"""
        # Setup mocks for validation
        with patch('app.models.offer.Offer.validate_offer') as mock_validate:
            mock_validate.return_value = {'is_valid': True, 'errors': {}}
            
            # Setup mocks for database
            user_id = str(ObjectId())
            self.mock_db.get_user_by_email.return_value = {'_id': ObjectId(user_id)}
            self.mock_db.get_wallet_by_user_id.return_value = None
            
            # Call the method
            result = self.offer_service.create_offer(
                from_user_email='user1@example.com',
                from_value=100.0,
                from_currency='USD',
                to_value=85.0,
                to_currency='EUR'
            )
            
            # Assertions
            self.assertFalse(result['success'])
            self.assertEqual(result['message'], 'Wallet not found')
    
    def test_create_offer_insufficient_funds(self):
        """Test creating an offer with insufficient funds"""
        # Setup mocks for validation
        with patch('app.models.offer.Offer.validate_offer') as mock_validate:
            mock_validate.return_value = {'is_valid': True, 'errors': {}}
            
            # Setup mocks for database
            user_id = str(ObjectId())
            user = {'_id': ObjectId(user_id)}
            wallet = {
                'user': user_id,
                'currencies': [
                    {'currency': 'USD', 'value': 50.0}  # Not enough USD
                ]
            }
            
            self.mock_db.get_user_by_email.return_value = user
            self.mock_db.get_wallet_by_user_id.return_value = wallet
            
            # Call the method
            result = self.offer_service.create_offer(
                from_user_email='user1@example.com',
                from_value=100.0,  # Trying to offer more than we have
                from_currency='USD',
                to_value=85.0,
                to_currency='EUR'
            )
            
            # Assertions
            self.assertFalse(result['success'])
            self.assertEqual(result['message'], 'Not enough USD in wallet')
    
    @patch('app.models.offer.Offer')
    def test_create_offer_no_matching_offers(self, mock_offer_class):
        """Test creating an offer with no matching offers"""
        # Setup mocks for validation
        with patch('app.models.offer.Offer.validate_offer') as mock_validate:
            mock_validate.return_value = {'is_valid': True, 'errors': {}}
            
            # Setup mocks for database
            user_id = str(ObjectId())
            user = {'_id': ObjectId(user_id)}
            wallet = {
                'user': user_id,
                'currencies': [
                    {'currency': 'USD', 'value': 200.0}  # Enough USD
                ]
            }
            
            self.mock_db.get_user_by_email.return_value = user
            self.mock_db.get_wallet_by_user_id.return_value = wallet
            self.mock_db.find_matching_offers.return_value = []  # No matching offers
            
            # Mock offer creation
            mock_offer = MagicMock()
            mock_offer_class.return_value = mock_offer
            mock_offer.to_dict.return_value = {
                'from_user': 'user1@example.com',
                'from_value': 100.0,
                'from_currency': 'USD',
                'to_value': 85.0,
                'to_currency': 'EUR',
                'date': ANY
            }
            
            # Call the method
            result = self.offer_service.create_offer(
                from_user_email='user1@example.com',
                from_value=100.0,
                from_currency='USD',
                to_value=85.0,
                to_currency='EUR'
            )
            
            # Assertions
            self.assertTrue(result['success'])
            self.assertEqual(result['message'], 'Offer added successfully')
            
            # Verify the correct methods were called
            self.mock_db.update_wallet.assert_called_once()
            self.mock_db.create_offer.assert_called_once_with(mock_offer.to_dict())
            
            # Check that the currency was deducted from the wallet
            self.assertEqual(wallet['currencies'][0]['value'], 100.0)  # 200 - 100
    
    def test_get_all_offers(self):
        """Test getting all offers"""
        # Setup mocks
        offer1_id = ObjectId()
        offer2_id = ObjectId()
        
        offers = [
            {'_id': offer1_id, 'from_user': 'user1@example.com'},
            {'_id': offer2_id, 'from_user': 'user2@example.com'}
        ]
        
        self.mock_db.get_all_offers.return_value = offers
        
        # Call the method
        result = self.offer_service.get_all_offers()
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['_id'], str(offer1_id))
        self.assertEqual(result[1]['_id'], str(offer2_id))
        
        # Verify the correct methods were called
        self.mock_db.get_all_offers.assert_called_once()
    
    def test_cancel_offer_not_found(self):
        """Test cancelling a non-existent offer"""
        # Setup mocks
        self.mock_db.get_offer_by_id.return_value = None
        
        # Call the method
        result = self.offer_service.cancel_offer(
            offer_id='nonexistent',
            user_email='user1@example.com'
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Offer not found')
    
    def test_cancel_offer_not_owner(self):
        """Test cancelling an offer that doesn't belong to the user"""
        # Setup mocks
        offer = {
            '_id': ObjectId(),
            'from_user': 'owner@example.com',  # Different from canceller
            'from_value': 100.0,
            'from_currency': 'USD'
        }
        
        self.mock_db.get_offer_by_id.return_value = offer
        
        # Call the method
        result = self.offer_service.cancel_offer(
            offer_id=str(offer['_id']),
            user_email='different@example.com'  # Not the owner
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Not authorized to cancel this offer')
    
    def test_cancel_offer_success(self):
        """Test successfully cancelling an offer"""
        # Setup mocks
        user_id = str(ObjectId())
        offer = {
            '_id': ObjectId(),
            'from_user': 'user1@example.com',
            'from_value': 100.0,
            'from_currency': 'USD'
        }
        
        user = {'_id': ObjectId(user_id)}
        wallet_data = {
            'user': user_id,
            'currencies': [
                {'currency': 'USD', 'value': 50.0}
            ]
        }
        
        self.mock_db.get_offer_by_id.return_value = offer
        self.mock_db.get_user_by_email.return_value = user
        self.mock_db.get_wallet_by_user_id.return_value = wallet_data
        
        # Call the method directly - focus on testing the result
        result = self.offer_service.cancel_offer(
            offer_id=str(offer['_id']),
            user_email='user1@example.com'
        )
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Offer cancelled and funds returned')
        
        # Verify the correct methods were called
        self.mock_db.get_offer_by_id.assert_called_once_with(str(offer['_id']))
        self.mock_db.update_wallet.assert_called_once()
        self.mock_db.delete_offer.assert_called_once_with(str(offer['_id']))
        
        # Check that the wallet update was called with the expected data
        call_args = self.mock_db.update_wallet.call_args
        updated_wallet_data = call_args[1]['wallet_data']
        
        # Find the USD balance in the updated wallet
        usd_found = False
        for currency in updated_wallet_data['currencies']:
            if currency['currency'] == 'USD':
                self.assertEqual(currency['value'], 150.0)  # 50 + 100
                usd_found = True
                break
        
        self.assertTrue(usd_found, "USD currency not found in updated wallet")
    
    def test_execute_transaction_offer_not_found(self):
        """Test executing a transaction with non-existent offer"""
        # Setup mocks
        self.mock_db.get_offer_by_id.return_value = None
        
        # Call the method
        result = self.offer_service.execute_transaction(
            offer_id='nonexistent',
            user_email='user1@example.com'
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Offer not found')
    
    def test_execute_transaction_own_offer(self):
        """Test executing a transaction on user's own offer"""
        # Setup mocks
        offer = {
            '_id': ObjectId(),
            'from_user': 'user1@example.com',  # Same as executing user
            'from_value': 100.0,
            'from_currency': 'USD',
            'to_value': 85.0,
            'to_currency': 'EUR'
        }
        
        self.mock_db.get_offer_by_id.return_value = offer
        
        # Call the method
        result = self.offer_service.execute_transaction(
            offer_id=str(offer['_id']),
            user_email='user1@example.com'  # Same as offer creator
        )
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Cannot execute your own offer')


if __name__ == '__main__':
    unittest.main() 