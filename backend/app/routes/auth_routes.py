"""
Authentication routes
"""
from flask import Blueprint, request, jsonify, session
from app.services.user_service import UserService
from app.utils.decorators import login_required

auth_bp = Blueprint('auth', __name__)
user_service = UserService()


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
        
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    result = user_service.register(
        email=email,
        password=password,
        name=name
    )
    
    if result['success']:
        return jsonify({
            'message': result['message'],
            'user_id': result['user_id']
        }), 201
        
    return jsonify({'message': result['message']}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    result = user_service.login(
        email=email,
        password=password
    )
    
    if result['success']:
        # Set session
        session['user_id'] = result['user']['id']
        session['email'] = result['user']['email']
        
        return jsonify({
            'message': result['message'],
            'user': result['user']
        }), 200
        
    return jsonify({'message': result['message']}), 401


@auth_bp.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    """Logout the current user"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/logged_in', methods=['GET'])
@login_required
def logged_in():
    """Check if user is logged in"""
    return jsonify({
        'logged_in': True,
        'user_id': session.get('user_id'),
        'email': session.get('email')
    }), 200 