# cafeteria-management-system/tests/test_menu_routes.py

import json
import pytest
from models import MenuItem

# Note: Fixtures from conftest.py are automatically available (client, setup_menu, auth_headers, init_db)

# --- GET Menu Items (Public/Student Access) ---

def test_get_menu_public_only_available(client, setup_menu):
    """Test public access to menu only shows available items."""
    response = client.get('/api/dishes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 3 # Burger, Fries, Salad (Soda is unavailable)
    assert not any(item['name'] == 'Soda' for item in data)

# --- Admin/Staff CRUD Operations ---

def test_create_menu_item_success_admin(client, auth_headers, init_db):
    """Test creating a new menu item as Admin."""
    new_item_data = {"name": "Pizza Slice", "price": 3.50, "category": "Main", "is_available": True}
    response = client.post('/api/dishes', data=json.dumps(new_item_data), headers=auth_headers['admin'])
    assert response.status_code == 201
    
    with init_db.app.app_context():
        assert init_db.session.query(MenuItem).filter_by(name='Pizza Slice').count() == 1

def test_update_menu_item_success_staff(client, auth_headers, setup_menu):
    """Test updating a menu item as Staff (e.g., toggling availability)."""
    fries_id = setup_menu['Fries'].id
    update_data = {"is_available": False, "stock": 0}
    response = client.patch(f'/api/dishes/{fries_id}', data=json.dumps(update_data), headers=auth_headers['staff'])
    assert response.status_code == 200
    assert json.loads(response.data)['is_available'] is False

def test_delete_menu_item_success_admin(client, auth_headers, setup_menu, init_db):
    """Test deleting a menu item as Admin."""
    salad_id = setup_menu['Salad'].id
    response = client.delete(f'/api/dishes/{salad_id}', headers=auth_headers['admin'])
    assert response.status_code == 204 # No Content

    with init_db.app.app_context():
        assert init_db.session.get(MenuItem, salad_id) is None

# --- Authorization Boundary Tests ---

def test_create_menu_item_unauthorized_student(client, auth_headers):
    """Test Student trying to create a menu item (should fail)."""
    new_item_data = {"name": "Forbidden", "price": 1.00, "category": "Side"}
    response = client.post('/api/dishes', data=json.dumps(new_item_data), headers=auth_headers['student'])
    assert response.status_code == 403 # Forbidden

def test_delete_menu_item_unauthorized_student(client, auth_headers, setup_menu):
    """Test Student trying to delete a menu item (should fail)."""
    burger_id = setup_menu['Burger'].id
    response = client.delete(f'/api/dishes/{burger_id}', headers=auth_headers['student'])
    assert response.status_code == 403 # Forbidden