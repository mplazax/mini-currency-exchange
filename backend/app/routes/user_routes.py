"""
User routes for wallet and transaction operations
"""
from flask import Blueprint, request, jsonify, session
from app.services.user_service import UserService
from app.utils.decorators import login_required

user_bp = Blueprint('user', __name__)
user_service = UserService()


@user_bp.route('/wallet', methods=['GET'])
@login_required
def wallet():
    """Get user wallet and transactions"""
    user_id = session.get('user_id')
    
    result = user_service.get_user_wallet(user_id)
    
    if result['success']:
        return jsonify({
            'wallet': result['wallet'],
            'transactions': result['transactions'],
            'email': result['email']
        }), 200
        
    return jsonify({'message': result['message']}), 400


@user_bp.route('/all_transactions', methods=['GET'])
@login_required
def all_transactions():
    """Get all transactions"""
    result = user_service.get_transactions()
    
    if result['success']:
        return jsonify(result['transactions']), 200
        
    return jsonify({'message': result['message']}), 400


@user_bp.route('/my_transactions', methods=['GET'])
@login_required
def my_transactions():
    """Get user's transactions"""
    user_email = session.get('email')
    
    result = user_service.get_transactions(user_email=user_email)
    
    if result['success']:
        return jsonify(result['transactions']), 200
        
    return jsonify({'message': result['message']}), 400 