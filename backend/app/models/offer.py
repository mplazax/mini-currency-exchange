"""
Offer model
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson.objectid import ObjectId


class Offer:
    """Model for currency exchange offers"""
    
    def __init__(
        self,
        from_user: str,
        from_value: float,
        from_currency: str,
        to_value: float,
        to_currency: str,
        offer_id: str = None,
        date: datetime = None
    ):
        """
        Initialize an offer
        
        Args:
            from_user: Email of user creating the offer
            from_value: Amount of currency to exchange
            from_currency: Currency code to exchange
            to_value: Amount of currency requested
            to_currency: Currency code requested
            offer_id: MongoDB ID (optional, for existing offers)
            date: Creation date (defaults to now)
        """
        self.from_user = from_user
        self.from_value = float(from_value)
        self.from_currency = from_currency
        self.to_value = float(to_value)
        self.to_currency = to_currency
        self.offer_id = offer_id
        self.date = date or datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert offer to dictionary for storage
        
        Returns:
            Dictionary representation of offer
        """
        offer_dict = {
            'from_user': self.from_user,
            'from_value': self.from_value,
            'from_currency': self.from_currency,
            'to_value': self.to_value,
            'to_currency': self.to_currency,
            'date': self.date
        }
        
        if self.offer_id:
            offer_dict['_id'] = ObjectId(self.offer_id)
            
        return offer_dict
    
    @classmethod
    def from_dict(cls, offer_dict: Dict[str, Any]) -> 'Offer':
        """
        Create an offer from dictionary
        
        Args:
            offer_dict: Dictionary representation of offer
            
        Returns:
            Offer instance
        """
        return cls(
            from_user=offer_dict['from_user'],
            from_value=offer_dict['from_value'],
            from_currency=offer_dict['from_currency'],
            to_value=offer_dict['to_value'],
            to_currency=offer_dict['to_currency'],
            offer_id=str(offer_dict['_id']) if '_id' in offer_dict else None,
            date=offer_dict.get('date')
        )
    
    @staticmethod
    def validate_offer(
        from_value: float,
        from_currency: str,
        to_value: float,
        to_currency: str
    ) -> Dict[str, Any]:
        """
        Validate offer data
        
        Args:
            from_value: Amount of currency to exchange
            from_currency: Currency code to exchange
            to_value: Amount of currency requested
            to_currency: Currency code requested
            
        Returns:
            Dict with validation status and errors if any
        """
        errors = {}
        
        # Validate values
        if from_value <= 0:
            errors['from_value'] = 'Value must be greater than 0'
            
        if to_value <= 0:
            errors['to_value'] = 'Value must be greater than 0'
            
        # Validate currency codes
        if not from_currency:
            errors['from_currency'] = 'Currency code is required'
            
        if not to_currency:
            errors['to_currency'] = 'Currency code is required'
            
        # Same currency check
        if from_currency == to_currency:
            errors['currency'] = 'Cannot exchange the same currency'
            
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        } 