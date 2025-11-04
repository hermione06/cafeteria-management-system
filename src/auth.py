from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from models import db, User
from email_validator import validate_email, EmailNotValidError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Username, email, and password are required"}), 400
    
    # Validate email format
    try:
        email_info = validate_email(data['email'], check_deliverability=False)
        email = email_info.normalized
    except EmailNotValidError as e:
        return jsonify({"error": f"Invalid email: {str(e)}"}), 400
    
    # Validate password strength
    password = data['password']
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    # Check if username exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 409
    
    # Check if email exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    
    try:
        # Create new user
        user = User(
            username=data['username'],
            email=email,
            role=data.get('role', 'user')
        )
        user.set_password(password)
        
        # Generate verification token
        verification_token = user.generate_verification_token()
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "User registered successfully. Please verify your email.",
            "user": user.to_dict(),
            "verification_token": verification_token  # In production, send via email
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/verify-email/<token>', methods=['POST'])
def verify_email(token):
    """Verify user's email with token"""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return jsonify({"error": "Invalid or expired verification token"}), 400
    
    if user.is_verified:
        return jsonify({"message": "Email already verified"}), 200
    
    try:
        user.verify_email()
        db.session.commit()
        
        return jsonify({
            "message": "Email verified successfully",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403
    
    # Check if email is verified
    if not user.is_verified:
        return jsonify({"error": "Please verify your email before logging in"}), 403
    
    try:
        # Update last login
        user.update_last_login()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role}
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    identity = get_jwt_identity()
    
    user = User.query.get(identity)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Create new access token
    access_token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role}
    )
    
    return jsonify({
        "access_token": access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard tokens)"""
    # In a production app, you'd add the token to a blocklist
    return jsonify({
        "message": "Logout successful. Please discard your tokens."
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged-in user's information"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({"error": "Email is required"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    # Don't reveal if user exists (security best practice)
    if not user:
        return jsonify({
            "message": "If the email exists, a reset link has been sent."
        }), 200
    
    try:
        reset_token = user.generate_reset_token()
        db.session.commit()
        
        # In production, send this via email
        return jsonify({
            "message": "Password reset link sent to your email.",
            "reset_token": reset_token  # Only for development/testing
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset password with token"""
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({"error": "New password is required"}), 400
    
    # Validate password strength
    password = data['password']
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    # Find user with valid token
    from datetime import datetime
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expiry:
        return jsonify({"error": "Invalid or expired reset token"}), 400
    
    if user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Reset token has expired"}), 400
    
    try:
        user.set_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        return jsonify({
            "message": "Password reset successfully. You can now login."
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for logged-in user"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({"error": "Old password and new password are required"}), 400
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Verify old password
    if not user.check_password(data['old_password']):
        return jsonify({"error": "Invalid old password"}), 401
    
    # Validate new password strength
    new_password = data['new_password']
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    try:
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            "message": "Password changed successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500