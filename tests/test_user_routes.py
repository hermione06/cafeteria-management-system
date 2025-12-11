# cafeteria-management-system/tests/test_user_routes.py

import json
import pytest
from models import User, UserRole

# Note: Fixtures from conftest.py are automatically available (client, setup_users, auth_headers, init_db)

# --- User Profile Management ---

def test_get_current_user_profile_success(client, auth_headers, setup_users):
    """Test getting the logged-in user's own profile."""
    student_id = setup_users['student'].id
    response = client.get('/api/users/profile', headers=auth_headers['student'])
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == student_id
    assert 'password_hash' not in data # Security check

def test_update_current_user_profile_success(client, auth_headers, setup_users, init_db):
    """Test updating the logged-in user's profile information."""
    new_username = 'new_student_name'
    update_data = {'username': new_username, 'email': 'new_student_email@test.com'}
    response = client.put('/api/users/profile', 
                          data=json.dumps(update_data), 
                          headers=auth_headers['student'])
    assert response.status_code == 200
    
    with init_db.app.app_context():
        user = init_db.session.get(User, setup_users['student'].id)
        assert user.username == new_username

# --- Admin User Management ---

def test_admin_get_all_users_success(client, auth_headers, setup_users):
    """Test Admin getting the paginated list of all users."""
    response = client.get('/api/users', headers=auth_headers['admin'])
    assert response.status_code == 200
    data = json.loads(response.data)
    # Check count: student, staff, admin, unverified
    assert len(data['items']) >= 4 

def test_staff_get_all_users_forbidden(client, auth_headers):
    """Test Staff getting the list of all users (should fail, Admin only)."""
    response = client.get('/api/users', headers=auth_headers['staff'])
    assert response.status_code == 403 # Forbidden

def test_admin_update_user_role_success(client, auth_headers, setup_users, init_db):
    """Test Admin updating a user's role."""
    student_id = setup_users['student'].id
    update_data = {'role': UserRole.STAFF.value}
    
    response = client.patch(f'/api/users/{student_id}', 
                            data=json.dumps(update_data), 
                            headers=auth_headers['admin'])
    assert response.status_code == 200
    assert json.loads(response.data)['role'] == UserRole.STAFF.value

def test_admin_delete_user_success(client, auth_headers, setup_users, init_db):
    """Test Admin deleting a user."""
    staff_id = setup_users['staff'].id
    
    response = client.delete(f'/api/users/{staff_id}', headers=auth_headers['admin'])
    assert response.status_code == 204 # No Content
    
    with init_db.app.app_context():
        assert init_db.session.get(User, staff_id) is None

def test_admin_delete_self_forbidden(client, auth_headers, setup_users):
    """Test Admin attempting to delete their own account (should fail)."""
    admin_id = setup_users['admin'].id
    response = client.delete(f'/api/users/{admin_id}', headers=auth_headers['admin'])
    assert response.status_code == 400
    assert b'Cannot delete your own account' in response.data