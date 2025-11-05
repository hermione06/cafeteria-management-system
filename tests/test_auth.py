import sys
import os
import json


# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest

# Set testing config BEFORE importing app
os.environ['FLASK_ENV'] = 'testing'

from app import app, db
from models import User

@pytest.fixture
def client():
    """Create a test client with in-memory database"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'test-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.test_client() as test_client:
        with app.app_context():
            db.create_all()
            yield test_client
            db.session.remove()
            db.drop_all()

# ===== Registration Tests =====

def test_register_success(client):
    """Test successful user registration"""
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePass123'
    }
    response = client.post('/auth/register',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User registered successfully. Please verify your email.'
    assert data['user']['username'] == 'testuser'
    assert data['user']['is_verified'] is False
    assert 'verification_token' in data


def test_register_missing_fields(client):
    """Test registration with missing required fields"""
    user_data = {'username': 'testuser'}
    response = client.post('/auth/register',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'required' in data['error'].lower()


def test_register_invalid_email(client):
    """Test registration with invalid email"""
    user_data = {
        'username': 'testuser',
        'email': 'invalid-email',
        'password': 'SecurePass123'
    }
    response = client.post('/auth/register',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid email' in data['error']


def test_register_weak_password(client):
    """Test registration with weak password"""
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'weak'
    }
    response = client.post('/auth/register',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'at least 8 characters' in data['error']


def test_register_duplicate_username(client):
    """Test registration with existing username"""
    user_data = {
        'username': 'testuser',
        'email': 'test1@example.com',
        'password': 'SecurePass123'
    }
    client.post('/auth/register',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Try to register with same username
    user_data2 = {
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'SecurePass123'
    }
    response = client.post('/auth/register',
                          data=json.dumps(user_data2),
                          content_type='application/json')
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'Username already exists' in data['error']


def test_register_duplicate_email(client):
    """Test registration with existing email"""
    user_data = {
        'username': 'user1',
        'email': 'test@example.com',
        'password': 'SecurePass123'
    }
    client.post('/auth/register',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Try to register with same email
    user_data2 = {
        'username': 'user2',
        'email': 'test@example.com',
        'password': 'SecurePass123'
    }
    response = client.post('/auth/register',
                          data=json.dumps(user_data2),
                          content_type='application/json')
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'Email already registered' in data['error']


# ===== Email Verification Tests =====

def test_verify_email_success(client):
    """Test successful email verification"""
    # Register user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePass123'
    }
    register_response = client.post('/auth/register',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
    token = json.loads(register_response.data)['verification_token']
    
    # Verify email
    response = client.post(f'/auth/verify-email/{token}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Email verified successfully'
    assert data['user']['is_verified'] is True


def test_verify_email_invalid_token(client):
    """Test email verification with invalid token"""
    response = client.post('/auth/verify-email/invalid-token')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid or expired' in data['error']


# ===== Login Tests =====

def test_login_success(client):
    """Test successful login"""
    # Register and verify user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePass123'
    }
    register_response = client.post('/auth/register',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
    token = json.loads(register_response.data)['verification_token']
    client.post(f'/auth/verify-email/{token}')
    
    # Login
    login_data = {
        'username': 'testuser',
        'password': 'SecurePass123'
    }
    response = client.post('/auth/login',
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Login successful'
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['username'] == 'testuser'


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        'username': 'nonexistent',
        'password': 'WrongPass123'
    }
    response = client.post('/auth/login',
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Invalid username or password' in data['error']


def test_login_unverified_email(client):
    """Test login with unverified email"""
    # Register user but don't verify
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePass123'
    }
    client.post('/auth/register',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Try to login
    login_data = {
        'username': 'testuser',
        'password': 'SecurePass123'
    }
    response = client.post('/auth/login',
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'verify your email' in data['error']


# ===== Protected Route Tests =====

def test_get_current_user(client):
    """Test getting current user info with valid token"""
    # Register, verify, and login
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePass123'
    }
    register_response = client.post('/auth/register',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
    token = json.loads(register_response.data)['verification_token']
    client.post(f'/auth/verify-email/{token}')
    
    login_response = client.post('/auth/login',
                                data=json.dumps({
                                    'username': 'testuser',
                                    'password': 'SecurePass123'
                                }),
                                content_type='application/json')
    access_token = json.loads(login_response.data)['access_token']
    
    # Get current user
    response = client.get('/auth/me',
                         headers={'Authorization': f'Bearer {access_token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == 'testuser'


def test_protected_route_without_token(client):
    """Test accessing protected route without token"""
    response = client.get('/auth/me')
    
    assert response.status_code == 401


# ===== Password Reset Tests =====

def test_forgot_password(client):
    """Test forgot password request"""
    # Register user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePass123'
    }
    client.post('/auth/register',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Request password reset
    response = client.post('/auth/forgot-password',
                          data=json.dumps({'email': 'test@example.com'}),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'reset_token' in data


def test_reset_password_success(client):
    """Test successful password reset"""
    # Register user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'OldPass123'
    }
    client.post('/auth/register',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Request reset
    reset_request = client.post('/auth/forgot-password',
                               data=json.dumps({'email': 'test@example.com'}),
                               content_type='application/json')
    reset_token = json.loads(reset_request.data)['reset_token']
    
    # Reset password
    response = client.post(f'/auth/reset-password/{reset_token}',
                          data=json.dumps({'password': 'NewPass123'}),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Password reset successfully' in data['message']


def test_change_password(client):
    """Test changing password for logged-in user"""
    # Register, verify, and login
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'OldPass123'
    }
    register_response = client.post('/auth/register',
                                   data=json.dumps(user_data),
                                   content_type='application/json')
    token = json.loads(register_response.data)['verification_token']
    client.post(f'/auth/verify-email/{token}')
    
    login_response = client.post('/auth/login',
                                data=json.dumps({
                                    'username': 'testuser',
                                    'password': 'OldPass123'
                                }),
                                content_type='application/json')
    access_token = json.loads(login_response.data)['access_token']
    
    # Change password
    response = client.post('/auth/change-password',
                          data=json.dumps({
                              'old_password': 'OldPass123',
                              'new_password': 'NewPass123'
                          }),
                          headers={'Authorization': f'Bearer {access_token}'},
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Password changed successfully' in data['message']