"""
Test runner for unit tests
"""
import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from tests.unit.test_user_model import TestUserModel
from tests.unit.test_wallet_model import TestWalletModel
from tests.unit.test_offer_model import TestOfferModel
from tests.unit.test_transaction_model import TestTransactionModel
from tests.unit.test_user_service import TestUserService
from tests.unit.test_offer_service import TestOfferService
from tests.unit.test_database_service import TestDatabaseService


def create_test_suite():
    """Create a test suite with all unit tests"""
    test_suite = unittest.TestSuite()
    test_loader = unittest.TestLoader()
    
    # Add model tests
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestUserModel))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestWalletModel))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestOfferModel))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestTransactionModel))
    
    # Add service tests
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestUserService))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestOfferService))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestDatabaseService))
    
    return test_suite


if __name__ == '__main__':
    # Create the test suite
    suite = create_test_suite()
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = runner.run(suite)
    
    # Set exit code based on test result
    sys.exit(not result.wasSuccessful()) 