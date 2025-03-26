"""
Custom decorators
"""
from functools import wraps
from flask import session, jsonify, request
import logging

logger = logging.getLogger(__name__)


def login_required(f):
    """
    Decorator to require login for routes
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function that checks for login
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return jsonify({'message': 'Unauthorized, please login'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin access for routes
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function that checks for admin status
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return jsonify({'message': 'Unauthorized, please login'}), 401
            
        # This would need to be expanded with actual admin checking logic
        # For now, we'll assume no admin functionality
        # if not is_admin(session['user_id']):
        #     logger.warning(f"Non-admin access attempt to {request.path}")
        #     return jsonify({'message': 'Admin access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function


def validate_json(required_fields):
    """
    Decorator to validate JSON request body
    
    Args:
        required_fields: List of fields that must be present in the request
        
    Returns:
        Decorated function that validates request JSON
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({'message': 'No data provided'}), 400
                
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                logger.warning(f"Missing fields in request: {missing_fields}")
                return jsonify({
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator 