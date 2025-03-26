"""
Database service for MongoDB interactions
"""
from pymongo import MongoClient
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for MongoDB database operations"""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern for database connections"""
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance
    
    def _init_db(self):
        """Initialize database connection"""
        try:
            # Get MongoDB URI from environment or use default
            mongo_uri = os.getenv('MONGO_URI')
            
            if not mongo_uri:
                logger.warning("MONGO_URI not set, using localhost")
                self.client = MongoClient('localhost', 27017)
            else:
                self.client = MongoClient(mongo_uri)
                
            self.db = self.client.get_database(os.getenv('MONGO_DB', 'total_records'))
            
            # Initialize collections
            self.users = self.db.register
            self.offers = self.db.offers
            self.wallets = self.db.wallets  
            self.transactions = self.db.transactions
            
            logger.info("Database connection established")
            
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    def close(self):
        """Close the database connection"""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("Database connection closed")
    
    # User operations
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return self.users.find_one({"email": email})
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        from bson.objectid import ObjectId
        return self.users.find_one({"_id": ObjectId(user_id)})
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        result = self.users.insert_one(user_data)
        return str(result.inserted_id)
    
    # Wallet operations
    def get_wallet_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get wallet by user ID"""
        return self.wallets.find_one({"user": user_id})
    
    def create_wallet(self, wallet_data: Dict[str, Any]) -> str:
        """Create a new wallet"""
        result = self.wallets.insert_one(wallet_data)
        return str(result.inserted_id)
    
    def update_wallet(self, user_id: str, wallet_data: Dict[str, Any]) -> bool:
        """Update a wallet"""
        result = self.wallets.update_one(
            {"user": user_id},
            {"$set": wallet_data}
        )
        return result.modified_count > 0
    
    # Offer operations
    def get_offer_by_id(self, offer_id: str) -> Optional[Dict[str, Any]]:
        """Get offer by ID"""
        from bson.objectid import ObjectId
        return self.offers.find_one({"_id": ObjectId(offer_id)})
    
    def get_all_offers(self) -> List[Dict[str, Any]]:
        """Get all offers"""
        return list(self.offers.find())
    
    def create_offer(self, offer_data: Dict[str, Any]) -> str:
        """Create a new offer"""
        result = self.offers.insert_one(offer_data)
        return str(result.inserted_id)
    
    def delete_offer(self, offer_id: str) -> bool:
        """Delete an offer"""
        from bson.objectid import ObjectId
        result = self.offers.delete_one({"_id": ObjectId(offer_id)})
        return result.deleted_count > 0
    
    def find_matching_offers(
        self,
        to_currency: str,
        from_currency: str,
        from_value: float
    ) -> List[Dict[str, Any]]:
        """Find offers matching the given criteria"""
        return list(self.offers.find({
            "from_currency": to_currency,
            "to_currency": from_currency,
            "to_value": {"$lte": from_value}
        }).sort([("to_value", -1)]))
    
    # Transaction operations
    def create_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Create a new transaction"""
        result = self.transactions.insert_one(transaction_data)
        return str(result.inserted_id)
    
    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all transactions"""
        return list(self.transactions.find())
    
    def get_user_transactions(self, email: str) -> List[Dict[str, Any]]:
        """Get transactions for a specific user"""
        return list(self.transactions.find({
            "$or": [
                {"from_user": email},
                {"to_user": email}
            ]
        })) 