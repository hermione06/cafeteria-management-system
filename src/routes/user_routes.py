from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.models import db, User
from src.utils.decorators import admin_required
from src.utils.pagination import paginate

user_bp = Blueprint('users', __name__)


@user_bp.route('', methods=['GET'])
@jwt_required()
@admin_required()
def get_users():
    """Get all users (Admin only)"""
    try:
        # Get query parameters
        role = request.args.get('role')
        is_active = request.args.get('is_active')
        search = request.args.get('search', '').strip()
        
        # Build query
        query = User.query
        
        if role:
            if not User.validate_role(role):
                return jsonify({"error": "Invalid role"}), 400
            query = query.filter_by(role=role)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active.lower() == 'true')
        
        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                db.or_(
                    User.username.ilike(search_filter),
                    User.email.ilike(search_filter)
                )
            )
        
        # Order by creation date
        query = query.order_by(User.created_at.desc())
        
        # Paginate
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = paginate(query, page, per_page)
        
        return jsonify({
            "users": [user.to_dict() for user in result['items']],
            "pagination": result['pagination']
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch users: {str(e)}"}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user - users can view own profile, admins can view all"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role')
        
        # Check authorization
        if role != 'admin' and current_user_id != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch user: {str(e)}"}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user - users can update own profile, admins can update any"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role')
        
        # Check authorization
        if role != 'admin' and current_user_id != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        
        # Validate role change (only admins can change roles)
        if 'role' in data:
            if role != 'admin':
                return jsonify({"error": "Only admins can change user roles"}), 403
            
            if not User.validate_role(data['role']):
                return jsonify({"error": "Invalid role"}), 400
            
            user.role = data['role']
        
        # Update username
        if 'username' in data:
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({"error": "Username already exists"}), 409
            user.username = data['username']
        
        # Update email
        if 'email' in data:
            from email_validator import validate_email, EmailNotValidError
            
            try:
                email_info = validate_email(data['email'], check_deliverability=False)
                email = email_info.normalized
                
                existing = User.query.filter_by(email=email).first()
                if existing and existing.id != user_id:
                    return jsonify({"error": "Email already exists"}), 409
                
                user.email = email
                # Reset verification when email changes
                user.is_verified = False
                user.generate_verification_token()
                
            except EmailNotValidError as e:
                return jsonify({"error": f"Invalid email: {str(e)}"}), 400
        
        # Only admins can change active status
        if 'is_active' in data:
            if role != 'admin':
                return jsonify({"error": "Only admins can change active status"}), 403
            user.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_user(user_id):
    """Delete a user (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent self-deletion
        if current_user_id == user_id:
            return jsonify({"error": "Cannot delete your own account"}), 400
        
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500


@user_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required()
def get_user_stats():
    """Get user statistics (Admin only)"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        verified_users = User.query.filter_by(is_verified=True).count()
        
        users_by_role = db.session.query(
            User.role, 
            db.func.count(User.id)
        ).group_by(User.role).all()
        
        return jsonify({
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "users_by_role": {role: count for role, count in users_by_role}
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch stats: {str(e)}"}), 500