"""
Unit tests for Transaction model
"""
import unittest
from unittest.mock import patch
from datetime import datetime
from app.models.transaction import Transaction
from bson.objectid import ObjectId


class TestTransactionModel(unittest.TestCase):
    def test_transaction_initialization(self):
        """Test Transaction model initialization"""
        test_date = datetime(2023, 1, 1, 12, 0, 0)
        transaction = Transaction(
            from_user="user1@example.com",
            to_user="user2@example.com",
            from_value=100.0,
            from_currency="USD",
            to_value=85.0,
            to_currency="EUR",
            transaction_id="123",
            date=test_date
        )
        
        self.assertEqual(transaction.from_user, "user1@example.com")
        self.assertEqual(transaction.to_user, "user2@example.com")
        self.assertEqual(transaction.from_value, 100.0)
        self.assertEqual(transaction.from_currency, "USD")
        self.assertEqual(transaction.to_value, 85.0)
        self.assertEqual(transaction.to_currency, "EUR")
        self.assertEqual(transaction.transaction_id, "123")
        self.assertEqual(transaction.date, test_date)
    
    def test_transaction_initialization_without_id_date(self):
        """Test Transaction model initialization without ID and date"""
        with patch('app.models.transaction.datetime') as mock_datetime:
            test_date = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = test_date
            
            transaction = Transaction(
                from_user="user1@example.com",
                to_user="user2@example.com",
                from_value=100.0,
                from_currency="USD",
                to_value=85.0,
                to_currency="EUR"
            )
            
            self.assertEqual(transaction.from_user, "user1@example.com")
            self.assertEqual(transaction.to_user, "user2@example.com")
            self.assertEqual(transaction.from_value, 100.0)
            self.assertEqual(transaction.from_currency, "USD")
            self.assertEqual(transaction.to_value, 85.0)
            self.assertEqual(transaction.to_currency, "EUR")
            self.assertIsNone(transaction.transaction_id)
            self.assertEqual(transaction.date, test_date)
    
    def test_to_dict_without_id(self):
        """Test converting transaction to dictionary without ID"""
        test_date = datetime(2023, 1, 1, 12, 0, 0)
        transaction = Transaction(
            from_user="user1@example.com",
            to_user="user2@example.com",
            from_value=100.0,
            from_currency="USD",
            to_value=85.0,
            to_currency="EUR",
            date=test_date
        )
        
        transaction_dict = transaction.to_dict()
        
        self.assertEqual(transaction_dict['from_user'], "user1@example.com")
        self.assertEqual(transaction_dict['to_user'], "user2@example.com")
        self.assertEqual(transaction_dict['from_value'], 100.0)
        self.assertEqual(transaction_dict['from_currency'], "USD")
        self.assertEqual(transaction_dict['to_value'], 85.0)
        self.assertEqual(transaction_dict['to_currency'], "EUR")
        self.assertEqual(transaction_dict['date'], test_date)
        self.assertNotIn('_id', transaction_dict)
    
    def test_to_dict_with_id(self):
        """Test converting transaction to dictionary with ID"""
        test_date = datetime(2023, 1, 1, 12, 0, 0)
        transaction = Transaction(
            from_user="user1@example.com",
            to_user="user2@example.com",
            from_value=100.0,
            from_currency="USD",
            to_value=85.0,
            to_currency="EUR",
            transaction_id="60f1e5b5c358f3b8a9f3b3a1",
            date=test_date
        )
        
        transaction_dict = transaction.to_dict()
        
        self.assertEqual(transaction_dict['from_user'], "user1@example.com")
        self.assertEqual(transaction_dict['to_user'], "user2@example.com")
        self.assertEqual(transaction_dict['from_value'], 100.0)
        self.assertEqual(transaction_dict['from_currency'], "USD")
        self.assertEqual(transaction_dict['to_value'], 85.0)
        self.assertEqual(transaction_dict['to_currency'], "EUR")
        self.assertEqual(transaction_dict['date'], test_date)
        self.assertIn('_id', transaction_dict)
        self.assertIsInstance(transaction_dict['_id'], ObjectId)
        self.assertEqual(str(transaction_dict['_id']), "60f1e5b5c358f3b8a9f3b3a1")
    
    def test_from_dict(self):
        """Test creating transaction from dictionary"""
        test_date = datetime(2023, 1, 1, 12, 0, 0)
        transaction_dict = {
            '_id': ObjectId("60f1e5b5c358f3b8a9f3b3a1"),
            'from_user': "user1@example.com",
            'to_user': "user2@example.com",
            'from_value': 100.0,
            'from_currency': "USD",
            'to_value': 85.0,
            'to_currency': "EUR",
            'date': test_date
        }
        
        transaction = Transaction.from_dict(transaction_dict)
        
        self.assertEqual(transaction.from_user, "user1@example.com")
        self.assertEqual(transaction.to_user, "user2@example.com")
        self.assertEqual(transaction.from_value, 100.0)
        self.assertEqual(transaction.from_currency, "USD")
        self.assertEqual(transaction.to_value, 85.0)
        self.assertEqual(transaction.to_currency, "EUR")
        self.assertEqual(transaction.transaction_id, "60f1e5b5c358f3b8a9f3b3a1")
        self.assertEqual(transaction.date, test_date)
    
    def test_from_offer(self):
        """Test creating transaction from offer"""
        offer_dict = {
            'from_user': "user1@example.com",
            'from_value': 100.0,
            'from_currency': "USD",
            'to_value': 85.0,
            'to_currency': "EUR",
        }
        
        transaction = Transaction.from_offer(offer_dict, "user2@example.com")
        
        self.assertEqual(transaction.from_user, "user1@example.com")
        self.assertEqual(transaction.to_user, "user2@example.com")
        self.assertEqual(transaction.from_value, 100.0)
        self.assertEqual(transaction.from_currency, "USD")
        self.assertEqual(transaction.to_value, 85.0)
        self.assertEqual(transaction.to_currency, "EUR")
    
    def test_get_exchange_rate(self):
        """Test calculating exchange rate"""
        transaction_dict = {
            'from_value': 100.0,
            'to_value': 85.0
        }
        
        rate = Transaction.get_exchange_rate(transaction_dict)
        
        self.assertEqual(rate, 0.85)
    
    def test_get_exchange_rate_zero_division(self):
        """Test calculating exchange rate with zero division"""
        transaction_dict = {
            'from_value': 0.0,
            'to_value': 85.0
        }
        
        rate = Transaction.get_exchange_rate(transaction_dict)
        
        self.assertEqual(rate, 0.0)
    
    def test_get_exchange_rate_missing_keys(self):
        """Test calculating exchange rate with missing keys"""
        transaction_dict = {
            'some_other_key': 'value'
        }
        
        rate = Transaction.get_exchange_rate(transaction_dict)
        
        self.assertEqual(rate, 0.0)


if __name__ == '__main__':
    unittest.main() 