"""
Unit tests for Offer model
"""
import unittest
from unittest.mock import patch
from datetime import datetime
from app.models.offer import Offer
from bson.objectid import ObjectId


class TestOfferModel(unittest.TestCase):
    def test_offer_initialization(self):
        """Test Offer model initialization"""
        test_date = datetime(2023, 1, 1, 12, 0, 0)
        offer = Offer(
            from_user="user1@example.com",
            from_value=100.0,
            from_currency="USD",
            to_value=85.0,
            to_currency="EUR",
            offer_id="123",
            date=test_date
        )
        
        self.assertEqual(offer.from_user, "user1@example.com")
        self.assertEqual(offer.from_value, 100.0)
        self.assertEqual(offer.from_currency, "USD")
        self.assertEqual(offer.to_value, 85.0)
        self.assertEqual(offer.to_currency, "EUR")
        self.assertEqual(offer.offer_id, "123")
        self.assertEqual(offer.date, test_date)
    
    def test_offer_initialization_without_id_date(self):
        """Test Offer model initialization without id and date"""
        with patch('app.models.offer.datetime') as mock_datetime:
            test_date = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = test_date
            
            offer = Offer(
                from_user="user1@example.com",
                from_value=100.0,
                from_currency="USD",
                to_value=85.0,
                to_currency="EUR"
            )
            
            self.assertEqual(offer.from_user, "user1@example.com")
            self.assertEqual(offer.from_value, 100.0)
            self.assertEqual(offer.from_currency, "USD")
            self.assertEqual(offer.to_value, 85.0)
            self.assertEqual(offer.to_currency, "EUR")
            self.assertIsNone(offer.offer_id)
            self.assertEqual(offer.date, test_date)
    
    def test_to_dict_without_id(self):
        """Test converting offer to dictionary without ID"""
        test_date = datetime(2023, 1, 1, 12, 0, 0)
        offer = Offer(
            from_user="user1@example.com",
            from_value=100.0,
            from_currency="USD",
            to_value=85.0,
            to_currency="EUR",
            date=test_date
        )
        
        offer_dict = offer.to_dict()
        
        self.assertEqual(offer_dict['from_user'], "user1@example.com")
        self.assertEqual(offer_dict['from_value'], 100.0)
        self.assertEqual(offer_dict['from_currency'], "USD")
        self.assertEqual(offer_dict['to_value'], 85.0)
        self.assertEqual(offer_dict['to_currency'], "EUR")
        self.assertEqual(offer_dict['date'], test_date)
        self.assertNotIn('_id', offer_dict)
    
    def test_to_dict_with_id(self):
        """Test converting offer to dictionary with ID"""
        test_date = datetime(2023, 1, 1, 12, 0, 0)
        offer = Offer(
            from_user="user1@example.com",
            from_value=100.0,
            from_currency="USD",
            to_value=85.0,
            to_currency="EUR",
            offer_id="60f1e5b5c358f3b8a9f3b3a1",
            date=test_date
        )
        
        offer_dict = offer.to_dict()
        
        self.assertEqual(offer_dict['from_user'], "user1@example.com")
        self.assertEqual(offer_dict['from_value'], 100.0)
        self.assertEqual(offer_dict['from_currency'], "USD")
        self.assertEqual(offer_dict['to_value'], 85.0)
        self.assertEqual(offer_dict['to_currency'], "EUR")
        self.assertEqual(offer_dict['date'], test_date)
        self.assertIn('_id', offer_dict)
        self.assertIsInstance(offer_dict['_id'], ObjectId)
        self.assertEqual(str(offer_dict['_id']), "60f1e5b5c358f3b8a9f3b3a1")
    
    def test_from_dict(self):
        """Test creating offer from dictionary"""
        test_date = datetime(2023, 1, 1, 12, 0, 0)
        offer_dict = {
            '_id': ObjectId("60f1e5b5c358f3b8a9f3b3a1"),
            'from_user': "user1@example.com",
            'from_value': 100.0,
            'from_currency': "USD",
            'to_value': 85.0,
            'to_currency': "EUR",
            'date': test_date
        }
        
        offer = Offer.from_dict(offer_dict)
        
        self.assertEqual(offer.from_user, "user1@example.com")
        self.assertEqual(offer.from_value, 100.0)
        self.assertEqual(offer.from_currency, "USD")
        self.assertEqual(offer.to_value, 85.0)
        self.assertEqual(offer.to_currency, "EUR")
        self.assertEqual(offer.offer_id, "60f1e5b5c358f3b8a9f3b3a1")
        self.assertEqual(offer.date, test_date)
    
    def test_validate_offer_valid(self):
        """Test validating a valid offer"""
        result = Offer.validate_offer(
            from_value=100.0,
            from_currency="USD",
            to_value=85.0,
            to_currency="EUR"
        )
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_offer_negative_values(self):
        """Test validating an offer with negative values"""
        result = Offer.validate_offer(
            from_value=-100.0,
            from_currency="USD",
            to_value=85.0,
            to_currency="EUR"
        )
        
        self.assertFalse(result['is_valid'])
        self.assertIn('from_value', result['errors'])
    
    def test_validate_offer_zero_values(self):
        """Test validating an offer with zero values"""
        result = Offer.validate_offer(
            from_value=100.0,
            from_currency="USD",
            to_value=0.0,
            to_currency="EUR"
        )
        
        self.assertFalse(result['is_valid'])
        self.assertIn('to_value', result['errors'])
    
    def test_validate_offer_missing_currency(self):
        """Test validating an offer with missing currency"""
        result = Offer.validate_offer(
            from_value=100.0,
            from_currency="",
            to_value=85.0,
            to_currency="EUR"
        )
        
        self.assertFalse(result['is_valid'])
        self.assertIn('from_currency', result['errors'])
    
    def test_validate_offer_same_currency(self):
        """Test validating an offer with same currency"""
        result = Offer.validate_offer(
            from_value=100.0,
            from_currency="USD",
            to_value=85.0,
            to_currency="USD"
        )
        
        self.assertFalse(result['is_valid'])
        self.assertIn('currency', result['errors'])


if __name__ == '__main__':
    unittest.main() 