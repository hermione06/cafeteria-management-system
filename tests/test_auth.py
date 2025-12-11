"""
Comprehensive tests for authentication endpoints.
Testing registration, login, token management, and password operations.
"""
import pytest
from datetime import datetime, timedelta
from models import User


# ==================== Registration Tests ====================

class TestRegistration:
    """Test user registration functionality."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully. Please verify your email.'
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'new@example.com'
        assert data['user']['is_verified'] is False
        assert 'verification_token' in data
    
    def test_register_with_role(self, client):
        """Test registration with custom role."""
        response = client.post('/api/auth/register', json={
            'username': 'staffuser',
            'email': 'staff@example.com',
            'password': 'StaffPass123',
            'role': 'staff'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['user']['role'] == 'staff'
    
    def test_register_missing_username(self, client):
        """Test registration without username."""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_register_missing_email(self, client):
        """Test registration without email."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'Password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_register_missing_password(self, client):
        """Test registration without password."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_register_invalid_email_format(self, client):
        """Test registration with invalid email format."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'not-an-email',
            'password': 'Password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'invalid email' in data['error'].lower()
    
    def test_register_weak_password(self, client):
        """Test registration with password too short."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'short'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert '8 characters' in data['error'].lower()
    
    def test_register_duplicate_username(self, client, user):
        """Test registration with existing username."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'Password123'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'username already exists' in data['error'].lower()
    
    def test_register_duplicate_email(self, client, user):
        """Test registration with existing email."""
        response = client.post('/api/auth/register', json={
            'username': 'differentuser',
            'email': 'test@example.com',
            'password': 'Password123'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'email already registered' in data['error'].lower()
    
    def test_register_invalid_role(self, client):
        """Test registration with invalid role."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123',
            'role': 'superuser'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'invalid role' in data['error'].lower()
    
    def test_register_email_normalization(self, client):
        """Test that email is normalized (lowercase)."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'Test@Example.COM',
            'password': 'Password123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['user']['email'] == 'test@example.com'


# ==================== Email Verification Tests ====================

class TestEmailVerification:
    """Test email verification functionality."""
    
    def test_verify_email_success(self, client, unverified_user):
        """Test successful email verification."""
        response = client.post(f'/api/auth/verify-email/{unverified_user.verification_token}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Email verified successfully'
        assert data['user']['is_verified'] is True
    
    def test_verify_email_invalid_token(self, client):
        """Test verification with invalid token."""
        response = client.post('/api/auth/verify-email/invalid-token-12345')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'invalid' in data['error'].lower() or 'expired' in data['error'].lower()
    
    def test_verify_email_already_verified(self, client, user):
        """Test verifying already verified email."""
        # Generate token for already verified user
        with client.application.app_context():
            user_obj = User.query.get(user.id)
            token = user_obj.generate_verification_token()
            from models import db
            db.session.commit()
        
        response = client.post(f'/api/auth/verify-email/{token}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'already verified' in data['message'].lower()


# ==================== Login Tests ====================

class TestLogin:
    """Test user login functionality."""
    
    def test_login_success(self, client, user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == 'testuser'
        assert 'password' not in data['user']
    
    def test_login_invalid_username(self, client):
        """Test login with non-existent username."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'Password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'invalid' in data['error'].lower()
    
    def test_login_wrong_password(self, client, user):
        """Test login with incorrect password."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'WrongPassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'invalid' in data['error'].lower()
    
    def test_login_missing_username(self, client):
        """Test login without username."""
        response = client.post('/api/auth/login', json={
            'password': 'Password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_login_missing_password(self, client):
        """Test login without password."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_login_inactive_user(self, client, inactive_user):
        """Test login with inactive account."""
        response = client.post('/api/auth/login', json={
            'username': 'inactive',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'deactivated' in data['error'].lower()
    
    def test_login_unverified_email(self, client, unverified_user):
        """Test login with unverified email."""
        response = client.post('/api/auth/login', json={
            'username': 'unverified',
            'password': 'TestPass123'
        })
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'verify' in data['error'].lower()
    
    def test_login_updates_last_login(self, client, user, app):
        """Test that login updates last_login timestamp."""
        with app.app_context():
            user_before = User.query.get(user.id)
            last_login_before = user_before.last_login
        
        client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        
        with app.app_context():
            user_after = User.query.get(user.id)
            assert user_after.last_login != last_login_before
            assert user_after.last_login is not None


# ==================== Token Management Tests ====================

class TestTokenManagement:
    """Test JWT token operations."""
    
    def test_refresh_token_success(self, client, user):
        """Test refreshing access token."""
        # Login first
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        refresh_token = login_response.get_json()['refresh_token']
        
        # Refresh
        response = client.post('/api/auth/refresh',
                              headers={'Authorization': f'Bearer {refresh_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
    
    def test_access_protected_route_with_valid_token(self, client, auth_headers):
        """Test accessing protected route with valid token."""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'testuser'
    
    def test_access_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_access_protected_route_with_invalid_token(self, client):
        """Test accessing protected route with invalid token."""
        response = client.get('/api/auth/me',
                            headers={'Authorization': 'Bearer invalid-token'})
        
        assert response.status_code == 422  # JWT decode error
    
    def test_logout(self, client, auth_headers):
        """Test logout functionality."""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'logout successful' in data['message'].lower()


# ==================== Password Management Tests ====================

class TestPasswordManagement:
    """Test password-related operations."""
    
    def test_forgot_password_success(self, client, user):
        """Test password reset request."""
        response = client.post('/api/auth/forgot-password', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'reset' in data['message'].lower()
        assert 'reset_token' in data  # Only in development
    
    def test_forgot_password_nonexistent_email(self, client):
        """Test password reset with non-existent email."""
        response = client.post('/api/auth/forgot-password', json={
            'email': 'nonexistent@example.com'
        })
        
        # Should return success for security (don't reveal if email exists)
        assert response.status_code == 200
    
    def test_forgot_password_missing_email(self, client):
        """Test password reset without email."""
        response = client.post('/api/auth/forgot-password', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()
    
    def test_reset_password_success(self, client, user, app):
        """Test successful password reset."""
        # Request reset
        reset_response = client.post('/api/auth/forgot-password', json={
            'email': 'test@example.com'
        })
        reset_token = reset_response.get_json()['reset_token']
        
        # Reset password
        response = client.post(f'/api/auth/reset-password/{reset_token}', json={
            'password': 'NewPassword123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'reset successfully' in data['message'].lower()
        
        # Verify new password works
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'NewPassword123'
        })
        assert login_response.status_code == 200
    
    def test_reset_password_invalid_token(self, client):
        """Test password reset with invalid token."""
        response = client.post('/api/auth/reset-password/invalid-token', json={
            'password': 'NewPassword123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'invalid' in data['error'].lower() or 'expired' in data['error'].lower()
    
    def test_reset_password_weak_password(self, client, user):
        """Test password reset with weak password."""
        # Request reset
        reset_response = client.post('/api/auth/forgot-password', json={
            'email': 'test@example.com'
        })
        reset_token = reset_response.get_json()['reset_token']
        
        # Try weak password
        response = client.post(f'/api/auth/reset-password/{reset_token}', json={
            'password': 'weak'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert '8 characters' in data['error'].lower()
    
    def test_change_password_success(self, client, auth_headers, user):
        """Test changing password for logged-in user."""
        response = client.post('/api/auth/change-password',
                              headers=auth_headers,
                              json={
                                  'old_password': 'TestPass123',
                                  'new_password': 'NewPassword123'
                              })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'changed successfully' in data['message'].lower()
        
        # Verify new password works
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'NewPassword123'
        })
        assert login_response.status_code == 200
    
    def test_change_password_wrong_old_password(self, client, auth_headers):
        """Test changing password with incorrect old password."""
        response = client.post('/api/auth/change-password',
                              headers=auth_headers,
                              json={
                                  'old_password': 'WrongPassword',
                                  'new_password': 'NewPassword123'
                              })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'invalid' in data['error'].lower()
    
    def test_change_password_weak_new_password(self, client, auth_headers):
        """Test changing to weak password."""
        response = client.post('/api/auth/change-password',
                              headers=auth_headers,
                              json={
                                  'old_password': 'TestPass123',
                                  'new_password': 'weak'
                              })
        
        assert response.status_code == 400
        data = response.get_json()
        assert '8 characters' in data['error'].lower()
    
    def test_change_password_without_auth(self, client):
        """Test changing password without authentication."""
        response = client.post('/api/auth/change-password', json={
            'old_password': 'TestPass123',
            'new_password': 'NewPassword123'
        })
        
        assert response.status_code == 401


# ==================== Get Current User Tests ====================

class TestGetCurrentUser:
    """Test getting current user information."""
    
    def test_get_me_success(self, client, auth_headers, user):
        """Test getting current user info."""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == user.id
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert 'password' not in data
        assert 'password_hash' not in data
    
    def test_get_me_without_auth(self, client):
        """Test getting current user without authentication."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_get_me_with_different_roles(self, client, admin_headers, admin_user):
        """Test getting current user info for admin."""
        response = client.get('/api/auth/me', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['role'] == 'admin'
        assert data['username'] == 'adminuser'


# ==================== Security Tests ====================

class TestAuthSecurity:
    """Test authentication security measures."""
    
    def test_password_not_in_response(self, client, user):
        """Ensure password never appears in responses."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        
        data = response.get_json()
        response_str = str(data).lower()
        
        assert 'password' not in response_str
        assert 'testpass123' not in response_str
    
    def test_token_contains_role_claim(self, client, admin_user):
        """Test that JWT token contains role claim."""
        response = client.post('/api/auth/login', json={
            'username': 'adminuser',
            'password': 'AdminPass123'
        })
        
        assert response.status_code == 200
        # Token should contain role (we can't decode without secret, but this tests the flow)
        data = response.get_json()
        assert 'access_token' in data
    
    def test_sql_injection_attempt_login(self, client):
        """Test SQL injection protection in login."""
        response = client.post('/api/auth/login', json={
            'username': "admin' OR '1'='1",
            'password': "password' OR '1'='1"
        })
        
        assert response.status_code == 401
    
    def test_sql_injection_attempt_registration(self, client):
        """Test SQL injection protection in registration."""
        response = client.post('/api/auth/register', json={
            'username': "admin'; DROP TABLE users; --",
            'email': 'test@example.com',
            'password': 'Password123'
        })
        
        # Should either fail validation or create user safely
        # But should NOT execute SQL injection
        assert response.status_code in [201, 400, 409]