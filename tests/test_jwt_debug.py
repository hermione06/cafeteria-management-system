"""
Create this file as tests/test_jwt_debug.py
"""
import pytest
import json
from flask_jwt_extended import create_access_token, decode_token
from src.models import User, db


def test_jwt_debug_info(app):
    """Debug JWT configuration and token creation"""
    with app.app_context():
        print("\n" + "="*60)
        print("JWT CONFIGURATION DEBUG")
        print("="*60)
        print(f"TESTING: {app.config.get('TESTING')}")
        print(f"SECRET_KEY: {app.config.get('SECRET_KEY')}")
        print(f"JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY')}")
        print(f"Are they equal? {app.config.get('SECRET_KEY') == app.config.get('JWT_SECRET_KEY')}")
        print(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
        print("="*60)


def test_token_creation_and_validation(app, client):
    """Test creating and using a token"""
    with app.app_context():
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com',
            role='admin',
            is_active=True,
            is_verified=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        print("\n" + "="*60)
        print("TOKEN CREATION TEST")
        print("="*60)
        print(f"User ID: {user.id}")
        print(f"User role: {user.role}")
        
        # Create token
        token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role, 'username': user.username}
        )
        print(f"Token created: {token[:50]}...")
        
        # Try to decode it
        try:
            decoded = decode_token(token)
            print(f"Token decoded successfully!")
            print(f"Identity: {decoded.get('sub')}")
            print(f"Role: {decoded.get('role')}")
        except Exception as e:
            print(f"ERROR decoding token: {e}")
        
        print("="*60)
        
        # Now try to use it in a request
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/auth/me', headers=headers)
        
        print("\n" + "="*60)
        print("API REQUEST TEST")
        print("="*60)
        print(f"Request to: GET /api/auth/me")
        print(f"Headers: {headers}")
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data.decode()}")
        print("="*60 + "\n")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.data}"


def test_admin_user_fixture_token(app, client, admin_user, admin_token):
    """Test the actual fixtures being used in tests"""
    print("\n" + "="*60)
    print("FIXTURE TOKEN TEST")
    print("="*60)
    print(f"Admin user fixture: {admin_user}")
    print(f"Admin user type: {type(admin_user)}")
    print(f"Admin token: {admin_token[:50] if admin_token else 'None'}...")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/auth/me', headers=headers)
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response data: {response.data.decode()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"