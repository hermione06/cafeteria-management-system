"""
Tests for User Management API endpoints (excluding auth)
"""
import pytest
import json


class TestGetUsers:
    """Test GET /api/users endpoint"""
    
    def test_get_users_as_admin(self, client, admin_headers, regular_user, staff_user):
        """Test admin can get all users"""
        response = client.get('/api/users', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert len(data['users']) >= 3  # admin, regular, staff
    
    def test_get_users_as_regular_user(self, client, auth_headers):
        """Test regular user cannot get all users"""
        response = client.get('/api/users', headers=auth_headers)
        assert response.status_code == 403
    
    def test_get_users_without_auth(self, client):
        """Test getting users without authentication"""
        response = client.get('/api/users')
        assert response.status_code == 401
    
    def test_filter_users_by_role(self, client, admin_headers, regular_user, staff_user):
        """Test filtering users by role"""
        response = client.get('/api/users?role=staff', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        for user in data['users']:
            assert user['role'] == 'staff'
    
    def test_filter_users_by_active_status(self, client, admin_headers, inactive_user):
        """Test filtering users by active status"""
        response = client.get('/api/users?is_active=false', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        for user in data['users']:
            assert user['is_active'] is False
    
    def test_search_users(self, client, admin_headers, regular_user):
        """Test searching users by username or email"""
        response = client.get(f'/api/users?search={regular_user.username}', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['users']) >= 1
        assert any(u['username'] == regular_user.username for u in data['users'])
    
    def test_users_pagination(self, client, admin_headers):
        """Test user pagination"""
        response = client.get('/api/users?per_page=2', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'pagination' in data
        assert data['pagination']['per_page'] == 2


class TestGetUser:
    """Test GET /api/users/<id> endpoint"""
    
    def test_get_own_profile(self, client, auth_headers, regular_user):
        """Test user can get their own profile"""
        response = client.get(f'/api/users/{regular_user.id}', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == regular_user.id
        assert data['username'] == regular_user.username
    
    def test_get_other_user_as_regular_user(self, client, auth_headers, admin_user):
        """Test regular user cannot get other user's profile"""
        response = client.get(f'/api/users/{admin_user.id}', headers=auth_headers)
        assert response.status_code == 403
    
    def test_get_any_user_as_admin(self, client, admin_headers, regular_user):
        """Test admin can get any user's profile"""
        response = client.get(f'/api/users/{regular_user.id}', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == regular_user.id
    
    def test_get_nonexistent_user(self, client, admin_headers):
        """Test getting non-existent user"""
        response = client.get('/api/users/9999', headers=admin_headers)
        assert response.status_code == 404


class TestUpdateUser:
    """Test PUT /api/users/<id> endpoint"""
    
    def test_update_own_username(self, client, auth_headers, regular_user):
        """Test user can update their own username"""
        update_data = {'username': 'newusername'}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['username'] == 'newusername'
    
    def test_update_own_email(self, client, auth_headers, regular_user):
        """Test user can update their own email"""
        update_data = {'email': 'newemail@test.com'}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['email'] == 'newemail@test.com'
        # Email change should reset verification
        assert data['user']['is_verified'] is False
    
    def test_update_other_user_as_regular_user(self, client, auth_headers, admin_user):
        """Test regular user cannot update other user"""
        update_data = {'username': 'hacked'}
        response = client.put(
            f'/api/users/{admin_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_update_user_role_as_regular_user(self, client, auth_headers, regular_user):
        """Test regular user cannot change their own role"""
        update_data = {'role': 'admin'}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_update_user_role_as_admin(self, client, admin_headers, regular_user):
        """Test admin can change user role"""
        update_data = {'role': 'staff'}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['role'] == 'staff'
    
    def test_update_user_active_status_as_admin(self, client, admin_headers, regular_user):
        """Test admin can change user active status"""
        update_data = {'is_active': False}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['is_active'] is False
    
    def test_update_user_active_status_as_regular_user(self, client, auth_headers, regular_user):
        """Test regular user cannot change active status"""
        update_data = {'is_active': False}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_update_username_duplicate(self, client, auth_headers, regular_user, admin_user):
        """Test cannot update to existing username"""
        update_data = {'username': admin_user.username}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already exists' in data['error']
    
    def test_update_email_duplicate(self, client, auth_headers, regular_user, admin_user):
        """Test cannot update to existing email"""
        update_data = {'email': admin_user.email}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 409
    
    def test_update_email_invalid_format(self, client, auth_headers, regular_user):
        """Test cannot update to invalid email"""
        update_data = {'email': 'not-an-email'}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == 400
    
    def test_update_invalid_role(self, client, admin_headers, regular_user):
        """Test cannot update to invalid role"""
        update_data = {'role': 'superadmin'}
        response = client.put(
            f'/api/users/{regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=admin_headers
        )
        assert response.status_code == 400


class TestDeleteUser:
    """Test DELETE /api/users/<id> endpoint"""
    
    def test_delete_user_as_admin(self, client, admin_headers, regular_user):
        """Test admin can delete user"""
        response = client.delete(
            f'/api/users/{regular_user.id}',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message']
        
        # Verify user is deleted
        get_response = client.get(
            f'/api/users/{regular_user.id}',
            headers=admin_headers
        )
        assert get_response.status_code == 404
    
    def test_delete_self_as_admin(self, client, admin_headers, admin_user):
        """Test admin cannot delete themselves"""
        response = client.delete(
            f'/api/users/{admin_user.id}',
            headers=admin_headers
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'own account' in data['error']
    
    def test_delete_user_as_regular_user(self, client, auth_headers, staff_user):
        """Test regular user cannot delete users"""
        response = client.delete(
            f'/api/users/{staff_user.id}',
            headers=auth_headers
        )
        assert response.status_code == 403
    
    def test_delete_nonexistent_user(self, client, admin_headers):
        """Test deleting non-existent user"""
        response = client.delete(
            '/api/users/9999',
            headers=admin_headers
        )
        assert response.status_code == 404


class TestGetUserStats:
    """Test GET /api/users/stats endpoint"""
    
    def test_get_stats_as_admin(self, client, admin_headers, regular_user, staff_user, inactive_user):
        """Test admin can get user statistics"""
        response = client.get('/api/users/stats', headers=admin_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_users' in data
        assert 'active_users' in data
        assert 'verified_users' in data
        assert 'users_by_role' in data
        assert data['total_users'] >= 4
    
    def test_get_stats_as_regular_user(self, client, auth_headers):
        """Test regular user cannot get user stats"""
        response = client.get('/api/users/stats', headers=auth_headers)
        assert response.status_code == 403
    
    def test_get_stats_without_auth(self, client):
        """Test getting stats without authentication"""
        response = client.get('/api/users/stats')
        assert response.status_code == 401