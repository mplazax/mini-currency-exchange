"""
Transaction model
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson.objectid import ObjectId


class Transaction:
    """Model for currency exchange transactions"""
    
    def __init__(
        self,
        from_user: str,
        to_user: str,
        from_value: float,
        from_currency: str,
        to_value: float,
        to_currency: str,
        transaction_id: str = None,
        date: datetime = None
    ):
        """
        Initialize a transaction
        
        Args:
            from_user: Email of user sending currency
            to_user: Email of user receiving currency
            from_value: Amount of currency sent
            from_currency: Currency code sent
            to_value: Amount of currency received
            to_currency: Currency code received
            transaction_id: MongoDB ID (optional, for existing transactions)
            date: Transaction date (defaults to now)
        """
        self.from_user = from_user
        self.to_user = to_user
        self.from_value = float(from_value)
        self.from_currency = from_currency
        self.to_value = float(to_value)
        self.to_currency = to_currency
        self.transaction_id = transaction_id
        self.date = date or datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert transaction to dictionary for storage
        
        Returns:
            Dictionary representation of transaction
        """
        transaction_dict = {
            'from_user': self.from_user,
            'to_user': self.to_user,
            'from_value': self.from_value,
            'from_currency': self.from_currency,
            'to_value': self.to_value,
            'to_currency': self.to_currency,
            'date': self.date
        }
        
        if self.transaction_id:
            transaction_dict['_id'] = ObjectId(self.transaction_id)
            
        return transaction_dict
    
    @classmethod
    def from_dict(cls, transaction_dict: Dict[str, Any]) -> 'Transaction':
        """
        Create a transaction from dictionary
        
        Args:
            transaction_dict: Dictionary representation of transaction
            
        Returns:
            Transaction instance
        """
        return cls(
            from_user=transaction_dict['from_user'],
            to_user=transaction_dict['to_user'],
            from_value=transaction_dict['from_value'],
            from_currency=transaction_dict['from_currency'],
            to_value=transaction_dict['to_value'],
            to_currency=transaction_dict['to_currency'],
            transaction_id=str(transaction_dict['_id']) if '_id' in transaction_dict else None,
            date=transaction_dict.get('date')
        )
    
    @classmethod
    def from_offer(
        cls,
        offer_dict: Dict[str, Any],
        to_user: str
    ) -> 'Transaction':
        """
        Create a transaction from an offer
        
        Args:
            offer_dict: Dictionary representation of offer
            to_user: Email of user accepting the offer
            
        Returns:
            Transaction instance
        """
        return cls(
            from_user=offer_dict['from_user'],
            to_user=to_user,
            from_value=offer_dict['from_value'],
            from_currency=offer_dict['from_currency'],
            to_value=offer_dict['to_value'],
            to_currency=offer_dict['to_currency']
        )
    
    @staticmethod
    def get_exchange_rate(transaction_dict: Dict[str, Any]) -> float:
        """
        Calculate exchange rate from transaction
        
        Args:
            transaction_dict: Dictionary representation of transaction
            
        Returns:
            Exchange rate
        """
        try:
            return transaction_dict['to_value'] / transaction_dict['from_value']
        except (KeyError, ZeroDivisionError):
            return 0.0 