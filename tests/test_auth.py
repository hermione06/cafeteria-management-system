# cafeteria-management-system/tests/test_auth_routes.py

import json
import pytest
from models import User
from datetime import datetime, timedelta, timezone

# Note: Fixtures from conftest.py are automatically available (client, setup_users, auth_headers, users_data, init_db)

# --- Registration and Login ---

def test_registration_success(client, users_data, init_db):
    """Test successful user registration and check for unverified status."""
    data = {'username': 'newuser', 'email': 'new@user.com', 'password': 'TestPassword123'}
    response = client.post('/api/auth/register', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    assert b'Registration successful' in response.data
    
    with init_db.app.app_context():
        user = init_db.session.scalars(init_db.select(User).filter_by(username='newuser')).first()
        assert user is not None
        assert user.is_verified is False # Must be unverified upon registration

def test_login_success(client, users_data):
    """Test successful login for a verified user."""
    data = {'username': users_data['student']['username'], 'password': users_data['student']['password']}
    response = client.post('/api/auth/login', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_login_unverified_user(client, setup_users):
    """Test login for an unverified user (should fail)."""
    user = setup_users['unverified']
    data = {'username': user.username, 'password': 'Password123!'}
    response = client.post('/api/auth/login', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 401
    assert b'Email not verified' in response.data

# --- Email Verification Tests ---

def test_verify_email_success(client, init_db, setup_users):
    """Test successful email verification."""
    user = setup_users['unverified']
    with init_db.app.app_context():
        verification_token = user.generate_verification_token()
        init_db.session.commit()
    
    response = client.post(f'/api/auth/verify-email/{verification_token}')
    assert response.status_code == 200
    
    with init_db.app.app_context():
        assert init_db.session.get(User, user.id).is_verified is True

# --- Password Management Tests (Change, Forgot, Reset) ---

def test_change_password_success(client, setup_users, auth_headers):
    """Test successful password change for a logged-in user."""
    old_password = setup_users['student'].password_hash # get hash before change
    response = client.post('/api/auth/change-password', 
                           data=json.dumps({'old_password': 'Password123!', 'new_password': 'NewPassword123!'}),
                           headers=auth_headers['student'])
    assert response.status_code == 200
    
    # Check that the password hash in DB has been updated
    # (Requires a re-check via login, as accessing hash directly is bad practice)
    login_data = {'username': setup_users['student'].username, 'password': 'NewPassword123!'}
    login_response = client.post('/api/auth/login', data=json.dumps(login_data), content_type='application/json')
    assert login_response.status_code == 200

def test_forgot_password_success(client, setup_users, init_db):
    """Test request for password reset, checks if token is generated."""
    user = setup_users['student']
    response = client.post('/api/auth/forgot-password', data=json.dumps({'email': user.email}), content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'reset_token' in data
    
    with init_db.app.app_context():
        assert init_db.session.get(User, user.id).reset_token is not None

def test_reset_password_success(client, setup_users, init_db):
    """Test successful password reset using the token."""
    user = setup_users['student']
    
    # Arrange: Generate a valid reset token
    with init_db.app.app_context():
        reset_token = user.generate_reset_token()
        init_db.session.commit()

    # Act: Reset password
    new_password = 'BrandNewPassword123!'
    response = client.post(f'/api/auth/reset-password/{reset_token}', 
                           data=json.dumps({'password': new_password}), 
                           content_type='application/json')
    assert response.status_code == 200
    
    # Assert: Verify the user can log in with the new password
    login_data = {'username': user.username, 'password': new_password}
    login_response = client.post('/api/auth/login', data=json.dumps(login_data), content_type='application/json')
    assert login_response.status_code == 200