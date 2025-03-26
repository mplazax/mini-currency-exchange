"""
Offer and transaction routes
"""
from flask import Blueprint, request, jsonify, session
from app.services.offer_service import OfferService
from app.utils.decorators import login_required, validate_json

offer_bp = Blueprint('offer', __name__)
offer_service = OfferService()


@offer_bp.route('/add_offer', methods=['POST'])
@login_required
@validate_json(['fromValue', 'fromCurrency', 'toValue', 'toCurrency'])
def add_offer():
    """Create a new offer"""
    data = request.get_json()
    
    # Get user email from session
    from_user_email = session.get('email')
    
    result = offer_service.create_offer(
        from_user_email=from_user_email,
        from_value=float(data.get('fromValue')),
        from_currency=data.get('fromCurrency'),
        to_value=float(data.get('toValue')),
        to_currency=data.get('toCurrency')
    )
    
    if result['success']:
        return jsonify({'message': result['message']}), 201
        
    return jsonify({'message': result['message']}), 400


@offer_bp.route('/get_offers', methods=['GET'])
@login_required
def get_offers():
    """Get all offers"""
    offers = offer_service.get_all_offers()
    return jsonify(offers), 200


@offer_bp.route('/cancel_offer/<offer_id>', methods=['DELETE'])
@login_required
def cancel_offer(offer_id):
    """Cancel an offer"""
    user_email = session.get('email')
    
    result = offer_service.cancel_offer(
        offer_id=offer_id,
        user_email=user_email
    )
    
    if result['success']:
        return jsonify({'message': result['message']}), 200
        
    return jsonify({'message': result['message']}), 400


@offer_bp.route('/make_transaction/<offer_id>', methods=['POST'])
@login_required
def make_transaction(offer_id):
    """Execute a transaction for an offer"""
    user_email = session.get('email')
    
    result = offer_service.execute_transaction(
        offer_id=offer_id,
        user_email=user_email
    )
    
    if result['success']:
        return jsonify({'message': result['message']}), 200
        
    return jsonify({'message': result['message']}), 400 