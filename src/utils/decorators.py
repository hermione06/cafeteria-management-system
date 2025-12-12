from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from src.models import User, db


def admin_required():
    """Decorator to require admin role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != 'admin':
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def staff_required():
    """Decorator to require staff role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != 'staff':
                return jsonify({"error": "Staff access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def staff_or_admin_required():
    """Decorator to require staff or admin role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in ['staff', 'admin']:
                return jsonify({"error": "Staff or admin access required"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def role_required(required_role):
    """Decorator to require a specific role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            # Admin can access everything
            if user_role == 'admin':
                return fn(*args, **kwargs)
            
            if user_role != required_role:
                return jsonify({
                    "error": f"{required_role.capitalize()} access required"
                }), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def active_user_required():
    """Decorator to ensure user account is active"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            if not user.is_active:
                return jsonify({"error": "Account is inactive"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def verified_user_required():
    """Decorator to ensure user email is verified"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            if not user.is_verified:
                return jsonify({"error": "Please verify your email"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper