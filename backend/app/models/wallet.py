"""
Wallet model
"""
from typing import Dict, List, Any, Optional
import random


class Wallet:
    """Wallet model for user currency holdings"""
    
    DEFAULT_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'PLN']
    
    def __init__(
        self, 
        user_id: str, 
        currencies: List[Dict[str, Any]] = None
    ):
        """
        Initialize a wallet
        
        Args:
            user_id: MongoDB user ID
            currencies: List of currency holdings
        """
        self.user_id = str(user_id)
        self.currencies = currencies or []
    
    @classmethod
    def create_default_wallet(cls, user_id: str) -> 'Wallet':
        """
        Create a wallet with default currencies
        
        Args:
            user_id: MongoDB user ID
            
        Returns:
            New wallet with random amounts of default currencies
        """
        currencies = []
        
        for currency in cls.DEFAULT_CURRENCIES:
            currencies.append({
                'currency': currency,
                'value': round(random.uniform(100, 1000), 2)
            })
            
        return cls(user_id=user_id, currencies=currencies)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert wallet to dictionary for storage
        
        Returns:
            Dictionary representation of wallet
        """
        return {
            'user': self.user_id,
            'currencies': self.currencies
        }
    
    def get_currency_balance(self, currency_code: str) -> float:
        """
        Get balance of specific currency
        
        Args:
            currency_code: Currency code (USD, EUR, etc.)
            
        Returns:
            Currency balance or 0 if not found
        """
        for currency in self.currencies:
            if currency['currency'] == currency_code:
                return currency['value']
                
        return 0.0
    
    def update_currency_balance(
        self, 
        currency_code: str, 
        amount: float, 
        operation: str
    ) -> bool:
        """
        Update currency balance
        
        Args:
            currency_code: Currency code
            amount: Amount to add or subtract
            operation: 'add' or 'subtract'
            
        Returns:
            True if operation succeeded, False otherwise
        """
        for currency in self.currencies:
            if currency['currency'] == currency_code:
                if operation == 'add':
                    currency['value'] += amount
                    return True
                elif operation == 'subtract':
                    if currency['value'] >= amount:
                        currency['value'] -= amount
                        return True
                    else:
                        return False
                    
        # If we get here, the currency wasn't found
        if operation == 'add':
            self.currencies.append({
                'currency': currency_code,
                'value': amount
            })
            return True
            
        return False 