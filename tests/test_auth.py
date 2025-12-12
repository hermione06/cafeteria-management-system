import pytest
import json
from datetime import datetime, timedelta

@pytest.fixture(scope='session')
def app():
    """Fixture for the main Flask application."""
    
    from src.app import create_app
    from src.config import TestingConfig
    app = create_app(TestingConfig)
    return app

@pytest.fixture
def client(app):
    """Test client instance."""
    return app.test_client()

@pytest.fixture
def init_db(app):
    """Initializes and tears down the in-memory database."""
    from src.models import db, User, MenuItem
    with app.app_context():
        db.create_all()

        # Create Admin User (id=1)
        admin = User(username='admin', email='admin@c.com', role='admin')
        admin.set_password('admin123')
        admin.is_verified = True
        db.session.add(admin)

        # Create Staff User (id=2)
        staff = User(username='staff', email='staff@c.com', role='staff')
        staff.set_password('staff123')
        staff.is_verified = True
        db.session.add(staff)

        # Create Student User (id=3)
        student = User(username='student', email='student@c.com', role='student')
        student.set_password('student123')
        student.is_verified = True
        db.session.add(student)

        db.session.commit()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def get_user_data(init_db):
    """Helper to get user objects and tokens."""
    from src.models import User
    def _get_user_data(role):
        user = User.query.filter_by(role=role).first()
        assert user is not None
        # Assuming User.get_token() or similar exists, otherwise generate manually
        login_data = {'username': user.username, 'password': f'{role}123'}
        return user, login_data
    return _get_user_data

@pytest.fixture
def auth_headers(client, get_user_data):
    """Generates JWT authentication headers for different roles."""
    headers = {}
    for role in ['admin', 'staff', 'student']:
        user, login_data = get_user_data(role)
        response = client.post('/api/auth/login', json=login_data)
        token = json.loads(response.data)['access_token']
        headers[role] = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    return headers

# --- Test Cases ---

def test_register_user_success(client, init_db):
    """Test successful user registration."""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'new@user.com',
        'password': 'StrongPassword123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'verification_token' in data
    assert data['user']['username'] == 'newuser'

def test_register_user_invalid_data(client, init_db):
    """Test registration with missing or invalid fields."""
    # Missing password
    response = client.post('/api/auth/register', json={'username': 'a', 'email': 'a@a.com'})
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)

def test_register_user_duplicate(client, init_db):
    """Test registration with existing username/email."""
    # Register first user
    client.post('/api/auth/register', json={'username': 'test', 'email': 'test@test.com', 'password': 'p'})
    # Register same user again
    response = client.post('/api/auth/register', json={'username': 'test', 'email': 'another@test.com', 'password': 'p'})
    assert response.status_code == 409
    assert 'Username or email already exists' in json.loads(response.data)['error']

def test_login_success(client, get_user_data):
    """Test successful login."""
    _, login_data = get_user_data('admin')
    response = client.post('/api/auth/login', json=login_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert data['user']['role'] == 'admin'

def test_login_failure(client):
    """Test login with incorrect credentials."""
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert 'Invalid username or password' in json.loads(response.data)['error']

def test_change_password_success(client, auth_headers, get_user_data):
    """Test successful password change for a logged-in user."""
    from src.models import User
    
    # Get initial student user and check password
    student_user, _ = get_user_data('student')
    assert student_user.check_password('student123') is True

    # Perform password change
    response = client.post('/api/auth/change-password', json={
        'old_password': 'student123',
        'new_password': 'NewPassword456'
    }, headers=auth_headers['student'])
    assert response.status_code == 200
    assert 'Password reset successfully' in json.loads(response.data)['message']

    # Verify new password works and old one doesn't
    student_user_after = User.query.get(student_user.id)
    assert student_user_after.check_password('student123') is False
    assert student_user_after.check_password('NewPassword456') is True

def test_change_password_invalid_old_password(client, auth_headers):
    """Test password change with incorrect old password."""
    response = client.post('/api/auth/change-password', json={
        'old_password': 'WrongOldPassword',
        'new_password': 'NewPassword456'
    }, headers=auth_headers['student'])
    assert response.status_code == 401
    assert 'Invalid old password' in json.loads(response.data)['error']

def test_admin_get_all_users_success(client, auth_headers):
    """Admin can view all users."""
    response = client.get('/api/users', headers=auth_headers['admin'])
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['users']) >= 3 # admin, staff, student fixtures

def test_staff_get_all_users_forbidden(client, auth_headers):
    """Staff cannot view all users (assuming only admin can)."""
    response = client.get('/api/users', headers=auth_headers['staff'])
    assert response.status_code == 403

def test_student_update_self_success(client, auth_headers, get_user_data):
    """A user can update their own profile (e.g., email)."""
    student_user, _ = get_user_data('student')
    response = client.put(f'/api/users/{student_user.id}', json={
        'email': 'new_student_email@c.com',
        'first_name': 'Test'
    }, headers=auth_headers['student'])
    assert response.status_code == 200
    data = json.loads(response.data)['user']
    assert data['email'] == 'new_student_email@c.com'
    assert data['first_name'] == 'Test'
    # Ensure role update is ignored
    assert data['role'] == 'student'

def test_student_update_other_user_forbidden(client, auth_headers, get_user_data):
    """A user cannot update another user's profile."""
    admin_user, _ = get_user_data('admin')
    response = client.put(f'/api/users/{admin_user.id}', json={
        'email': 'hacked@c.com'
    }, headers=auth_headers['student'])
    assert response.status_code == 403

def test_admin_update_user_role_success(client, auth_headers, get_user_data):
    """Admin can update any user's role."""
    student_user, _ = get_user_data('student')
    response = client.put(f'/api/users/{student_user.id}', json={
        'role': 'staff'
    }, headers=auth_headers['admin'])
    assert response.status_code == 200
    data = json.loads(response.data)['user']
    assert data['role'] == 'staff'

def test_admin_delete_user_success(client, auth_headers, get_user_data):
    """Admin can delete a user."""
    from src.models import User
    staff_user, _ = get_user_data('staff')
    staff_id = staff_user.id
    response = client.delete(f'/api/users/{staff_id}', headers=auth_headers['admin'])
    assert response.status_code == 204
    
    deleted_user = User.query.get(staff_id)
    assert deleted_user is None