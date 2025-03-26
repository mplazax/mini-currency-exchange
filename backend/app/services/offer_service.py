"""
Offer service for business logic related to offers
"""
from typing import Dict, Any, List, Optional, Tuple
import logging
from app.models.offer import Offer
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.services.database import DatabaseService

logger = logging.getLogger(__name__)


class OfferService:
    """Service for offer-related operations"""
    
    def __init__(self):
        """Initialize with a database service"""
        self.db = DatabaseService()
    
    def create_offer(
        self,
        from_user_email: str,
        from_value: float,
        from_currency: str,
        to_value: float,
        to_currency: str
    ) -> Dict[str, Any]:
        """
        Create a new offer and handle automatic matching
        
        Args:
            from_user_email: Email of user creating the offer
            from_value: Amount of currency offered
            from_currency: Currency code offered
            to_value: Amount of currency requested
            to_currency: Currency code requested
            
        Returns:
            Dict with status and message
        """
        # Validate offer
        validation = Offer.validate_offer(
            from_value=from_value,
            from_currency=from_currency,
            to_value=to_value,
            to_currency=to_currency
        )
        
        if not validation['is_valid']:
            return {
                'success': False,
                'message': 'Invalid offer',
                'errors': validation['errors']
            }
        
        # Find user 
        from_user = self.db.get_user_by_email(from_user_email)
        if not from_user:
            return {
                'success': False,
                'message': 'User not found'
            }
        
        # Get user wallet
        from_user_wallet_data = self.db.get_wallet_by_user_id(str(from_user['_id']))
        if not from_user_wallet_data:
            return {
                'success': False,
                'message': 'Wallet not found'
            }
        
        # Check if user has enough balance
        has_enough = False
        for currency in from_user_wallet_data['currencies']:
            if currency['currency'] == from_currency and currency['value'] >= from_value:
                has_enough = True
                # Deduct the offered value
                currency['value'] -= from_value
                break
                
        if not has_enough:
            return {
                'success': False,
                'message': f'Not enough {from_currency} in wallet'
            }
        
        # Find matching offers
        matching_offers = self.db.find_matching_offers(
            to_currency=to_currency,
            from_currency=from_currency,
            from_value=from_value
        )
        
        # Try to match with existing offers
        result = self._match_with_existing_offers(
            matching_offers=matching_offers,
            from_user=from_user,
            from_user_wallet_data=from_user_wallet_data,
            from_currency=from_currency,
            to_currency=to_currency,
            to_value=to_value
        )
        
        if result['matched']:
            # Update wallet
            self.db.update_wallet(
                user_id=str(from_user['_id']),
                wallet_data=from_user_wallet_data
            )
            return {
                'success': True,
                'message': 'Transaction completed successfully'
            }
        
        # If no matching offer, create new offer
        offer = Offer(
            from_user=from_user_email,
            from_value=from_value,
            from_currency=from_currency,
            to_value=to_value,
            to_currency=to_currency
        )
        
        try:
            # Update wallet to reflect locked funds
            self.db.update_wallet(
                user_id=str(from_user['_id']),
                wallet_data=from_user_wallet_data
            )
            
            # Create the offer
            self.db.create_offer(offer.to_dict())
            
            return {
                'success': True,
                'message': 'Offer added successfully'
            }
        except Exception as e:
            logger.error(f"Error creating offer: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }
    
    def _match_with_existing_offers(
        self,
        matching_offers: List[Dict[str, Any]],
        from_user: Dict[str, Any],
        from_user_wallet_data: Dict[str, Any],
        from_currency: str,
        to_currency: str,
        to_value: float
    ) -> Dict[str, Any]:
        """
        Try to match an offer with existing offers
        
        Args:
            matching_offers: List of potentially matching offers
            from_user: User creating the offer
            from_user_wallet_data: User's wallet data
            from_currency: Currency code offered
            to_currency: Currency code requested
            to_value: Amount of currency requested
            
        Returns:
            Dict with match status and any transactions created
        """
        if not matching_offers:
            return {'matched': False}
            
        total_to_value = 0
        offers_to_use = []
        
        # Find combination of offers that matches or is more beneficial
        for offer in matching_offers:
            offers_to_use.append(offer)
            total_to_value += offer['to_value']
            
            if total_to_value >= to_value:
                break
                
        if total_to_value < to_value:
            return {'matched': False}
        
        # Execute transactions for matching offers
        transactions_created = []
        
        for offer in offers_to_use:
            to_user_email = offer['from_user']
            to_user = self.db.get_user_by_email(to_user_email)
            
            if not to_user:
                continue
                
            to_user_wallet_data = self.db.get_wallet_by_user_id(str(to_user['_id']))
            if not to_user_wallet_data:
                continue
                
            # Add/subtract values to wallets
            from_wallet = Wallet(
                user_id=str(from_user['_id']),
                currencies=from_user_wallet_data['currencies']
            )
            
            to_wallet = Wallet(
                user_id=str(to_user['_id']),
                currencies=to_user_wallet_data['currencies']
            )
            
            # Update wallets
            to_wallet.update_currency_balance(
                currency_code=to_currency,
                amount=offer['to_value'],
                operation='add'
            )
            
            to_wallet.update_currency_balance(
                currency_code=from_currency,
                amount=offer['from_value'],
                operation='subtract'
            )
            
            # Update wallets in database
            self.db.update_wallet(
                user_id=str(to_user['_id']),
                wallet_data=to_wallet.to_dict()
            )
            
            # Create transaction
            transaction = Transaction.from_offer(
                offer_dict=offer,
                to_user=from_user['email']
            )
            
            self.db.create_transaction(transaction.to_dict())
            transactions_created.append(transaction.to_dict())
            
            # Remove the matched offer
            self.db.delete_offer(str(offer['_id']))
        
        return {
            'matched': True,
            'transactions': transactions_created
        }
    
    def get_all_offers(self) -> List[Dict[str, Any]]:
        """
        Get all active offers
        
        Returns:
            List of offer dictionaries
        """
        try:
            offers = self.db.get_all_offers()
            
            # Convert ObjectId to string
            for offer in offers:
                offer['_id'] = str(offer['_id'])
                
            return offers
        except Exception as e:
            logger.error(f"Error getting offers: {str(e)}")
            return []
    
    def cancel_offer(self, offer_id: str, user_email: str) -> Dict[str, Any]:
        """
        Cancel an offer and refund the locked funds
        
        Args:
            offer_id: ID of the offer to cancel
            user_email: Email of user cancelling the offer
            
        Returns:
            Dict with status and message
        """
        try:
            # Find the offer
            offer_data = self.db.get_offer_by_id(offer_id)
            
            if not offer_data:
                return {
                    'success': False,
                    'message': 'Offer not found'
                }
                
            # Check if user owns the offer
            if offer_data['from_user'] != user_email:
                return {
                    'success': False,
                    'message': 'Not authorized to cancel this offer'
                }
                
            # Get user and wallet
            user = self.db.get_user_by_email(user_email)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }
                
            wallet_data = self.db.get_wallet_by_user_id(str(user['_id']))
            if not wallet_data:
                return {
                    'success': False,
                    'message': 'Wallet not found'
                }
                
            # Refund the locked funds
            wallet = Wallet(
                user_id=str(user['_id']),
                currencies=wallet_data['currencies']
            )
            
            wallet.update_currency_balance(
                currency_code=offer_data['from_currency'],
                amount=offer_data['from_value'],
                operation='add'
            )
            
            # Update wallet and delete offer
            self.db.update_wallet(
                user_id=str(user['_id']),
                wallet_data=wallet.to_dict()
            )
            
            self.db.delete_offer(offer_id)
            
            return {
                'success': True,
                'message': 'Offer cancelled and funds returned'
            }
        except Exception as e:
            logger.error(f"Error cancelling offer: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            }
            
    def execute_transaction(self, offer_id: str, user_email: str) -> Dict[str, Any]:
        """
        Execute a transaction based on an offer
        
        Args:
            offer_id: ID of the offer to execute
            user_email: Email of user executing the transaction
            
        Returns:
            Dict with status and message
        """
        try:
            # Find the offer
            offer_data = self.db.get_offer_by_id(offer_id)
            
            if not offer_data:
                return {
                    'success': False,
                    'message': 'Offer not found'
                }
                
            # Check if user is trying to execute their own offer
            if offer_data['from_user'] == user_email:
                return {
                    'success': False,
                    'message': 'Cannot execute your own offer'
                }
                
            # Get both users and wallets
            from_user = self.db.get_user_by_email(offer_data['from_user'])
            to_user = self.db.get_user_by_email(user_email)
            
            if not from_user or not to_user:
                return {
                    'success': False,
                    'message': 'User not found'
                }
                
            from_wallet_data = self.db.get_wallet_by_user_id(str(from_user['_id']))
            to_wallet_data = self.db.get_wallet_by_user_id(str(to_user['_id']))
            
            if not from_wallet_data or not to_wallet_data:
                return {
                    'success': False,
                    'message': 'Wallet not found'
                }
                
            # Check if to_user has enough of the requested currency
            has_enough = False
            for currency in to_wallet_data['currencies']:
                if (currency['currency'] == offer_data['to_currency'] and 
                    currency['value'] >= offer_data['to_value']):
                    has_enough = True
                    break
                    
            if not has_enough:
                return {
                    'success': False,
                    'message': f'Not enough {offer_data["to_currency"]} in your wallet'
                }
                
            # Update wallets
            to_wallet = Wallet(
                user_id=str(to_user['_id']),
                currencies=to_wallet_data['currencies']
            )
            
            # Subtract to_currency from to_user
            to_wallet.update_currency_balance(
                currency_code=offer_data['to_currency'],
                amount=offer_data['to_value'],
                operation='subtract'
            )
            
            # Add from_currency to to_user
            to_wallet.update_currency_balance(
                currency_code=offer_data['from_currency'],
                amount=offer_data['from_value'],
                operation='add'
            )
            
            # Save the updated wallet
            self.db.update_wallet(
                user_id=str(to_user['_id']),
                wallet_data=to_wallet.to_dict()
            )
            
            # Create transaction
            transaction = Transaction(
                from_user=offer_data['from_user'],
                to_user=user_email,
                from_value=offer_data['from_value'],
                from_currency=offer_data['from_currency'],
                to_value=offer_data['to_value'],
                to_currency=offer_data['to_currency']
            )
            
            self.db.create_transaction(transaction.to_dict())
            
            # Delete the offer
            self.db.delete_offer(offer_id)
            
            return {
                'success': True,
                'message': 'Transaction executed successfully'
            }
        except Exception as e:
            logger.error(f"Error executing transaction: {str(e)}")
            return {
                'success': False,
                'message': 'Internal server error'
            } 