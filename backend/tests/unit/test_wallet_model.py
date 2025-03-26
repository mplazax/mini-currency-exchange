"""
Unit tests for Wallet model
"""
import unittest
from unittest.mock import patch
from app.models.wallet import Wallet


class TestWalletModel(unittest.TestCase):
    def test_wallet_initialization_empty(self):
        """Test Wallet model initialization with empty currencies"""
        wallet = Wallet(user_id="123")
        
        self.assertEqual(wallet.user_id, "123")
        self.assertEqual(wallet.currencies, [])
    
    def test_wallet_initialization_with_currencies(self):
        """Test Wallet model initialization with currencies"""
        currencies = [
            {"currency": "USD", "value": 100.0},
            {"currency": "EUR", "value": 85.0}
        ]
        wallet = Wallet(user_id="123", currencies=currencies)
        
        self.assertEqual(wallet.user_id, "123")
        self.assertEqual(wallet.currencies, currencies)
    
    @patch('random.uniform')
    def test_create_default_wallet(self, mock_uniform):
        """Test creating a default wallet with random values"""
        # Mock random.uniform to return predictable values
        mock_uniform.return_value = 500.0
        
        wallet = Wallet.create_default_wallet("123")
        
        self.assertEqual(wallet.user_id, "123")
        self.assertEqual(len(wallet.currencies), len(Wallet.DEFAULT_CURRENCIES))
        
        # Check each currency has the correct format and value
        for currency in wallet.currencies:
            self.assertIn(currency['currency'], Wallet.DEFAULT_CURRENCIES)
            self.assertEqual(currency['value'], 500.0)
    
    def test_to_dict(self):
        """Test converting wallet to dictionary"""
        currencies = [
            {"currency": "USD", "value": 100.0},
            {"currency": "EUR", "value": 85.0}
        ]
        wallet = Wallet(user_id="123", currencies=currencies)
        
        wallet_dict = wallet.to_dict()
        
        self.assertEqual(wallet_dict['user'], "123")
        self.assertEqual(wallet_dict['currencies'], currencies)
    
    def test_get_currency_balance_existing(self):
        """Test getting balance of existing currency"""
        currencies = [
            {"currency": "USD", "value": 100.0},
            {"currency": "EUR", "value": 85.0}
        ]
        wallet = Wallet(user_id="123", currencies=currencies)
        
        balance = wallet.get_currency_balance("USD")
        
        self.assertEqual(balance, 100.0)
    
    def test_get_currency_balance_nonexistent(self):
        """Test getting balance of nonexistent currency"""
        currencies = [
            {"currency": "USD", "value": 100.0},
        ]
        wallet = Wallet(user_id="123", currencies=currencies)
        
        balance = wallet.get_currency_balance("EUR")
        
        self.assertEqual(balance, 0.0)
    
    def test_update_currency_balance_add_existing(self):
        """Test adding to existing currency balance"""
        currencies = [
            {"currency": "USD", "value": 100.0},
        ]
        wallet = Wallet(user_id="123", currencies=currencies)
        
        result = wallet.update_currency_balance("USD", 50.0, "add")
        
        self.assertTrue(result)
        self.assertEqual(wallet.currencies[0]["value"], 150.0)
    
    def test_update_currency_balance_add_new(self):
        """Test adding new currency to wallet"""
        wallet = Wallet(user_id="123")
        
        result = wallet.update_currency_balance("USD", 50.0, "add")
        
        self.assertTrue(result)
        self.assertEqual(len(wallet.currencies), 1)
        self.assertEqual(wallet.currencies[0]["currency"], "USD")
        self.assertEqual(wallet.currencies[0]["value"], 50.0)
    
    def test_update_currency_balance_subtract_sufficient(self):
        """Test subtracting from currency with sufficient funds"""
        currencies = [
            {"currency": "USD", "value": 100.0},
        ]
        wallet = Wallet(user_id="123", currencies=currencies)
        
        result = wallet.update_currency_balance("USD", 50.0, "subtract")
        
        self.assertTrue(result)
        self.assertEqual(wallet.currencies[0]["value"], 50.0)
    
    def test_update_currency_balance_subtract_insufficient(self):
        """Test subtracting from currency with insufficient funds"""
        currencies = [
            {"currency": "USD", "value": 100.0},
        ]
        wallet = Wallet(user_id="123", currencies=currencies)
        
        result = wallet.update_currency_balance("USD", 150.0, "subtract")
        
        self.assertFalse(result)
        self.assertEqual(wallet.currencies[0]["value"], 100.0)  # No change
    
    def test_update_currency_balance_subtract_nonexistent(self):
        """Test subtracting from nonexistent currency"""
        wallet = Wallet(user_id="123")
        
        result = wallet.update_currency_balance("USD", 50.0, "subtract")
        
        self.assertFalse(result)
        self.assertEqual(len(wallet.currencies), 0)  # No change


if __name__ == '__main__':
    unittest.main() 