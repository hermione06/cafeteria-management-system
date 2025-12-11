import pytest
import json
@pytest.fixture
def menu_items(init_db):
    """Adds initial menu items to the database."""
    from src.models import db, MenuItem
    with db.session.begin():
        item1 = MenuItem(name='Burger', description='Classic beef patty', price=12.50, category='main', is_available=True)
        item2 = MenuItem(name='Fries', description='Side of fries', price=3.00, category='side', is_available=False)
        item3 = MenuItem(name='Soda', description='Carbonated drink', price=2.00, category='drink', is_available=True)
        db.session.add_all([item1, item2, item3])
    yield {'burger': item1, 'fries': item2, 'soda': item3}
    # Teardown handled by init_db

# --- Menu Tests ---

def test_get_all_menu_items_unauthenticated(client, menu_items):
    """Unauthenticated users can view all menu items (but only available ones by default)."""
    response = client.get('/api/dishes')
    assert response.status_code == 200
    data = json.loads(response.data)
    # By default, only available items are returned
    assert data['total_items'] == 2
    assert 'Fries' not in [item['name'] for item in data['items']]

def test_get_all_menu_items_admin_with_all_filter(client, auth_headers, menu_items):
    """Admin can view all items, including unavailable ones, using a filter."""
    response = client.get('/api/dishes?available=all', headers=auth_headers['admin'])
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_items'] == 3
    assert 'Fries' in [item['name'] for item in data['items']]

def test_create_menu_item_admin_success(client, auth_headers):
    """Admin can successfully create a new menu item."""
    new_item_data = {
        'name': 'Pizza',
        'description': 'Pepperoni pizza',
        'price': 15.00,
        'category': 'main',
        'is_available': True
    }
    response = client.post('/api/dishes', json=new_item_data, headers=auth_headers['admin'])
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['item']['name'] == 'Pizza'
    assert data['item']['id'] is not None

def test_create_menu_item_student_forbidden(client, auth_headers):
    """Students cannot create menu items."""
    new_item_data = {'name': 'Forbidden', 'price': 1.00, 'category': 'main'}
    response = client.post('/api/dishes', json=new_item_data, headers=auth_headers['student'])
    assert response.status_code == 403

def test_update_menu_item_staff_success(client, auth_headers, menu_items):
    """Staff can successfully update an existing menu item."""
    item_id = menu_items['fries'].id
    update_data = {
        'price': 3.50,
        'is_available': True # Staff often just toggle availability
    }
    response = client.put(f'/api/dishes/{item_id}', json=update_data, headers=auth_headers['staff'])
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['item']['price'] == 3.50
    assert data['item']['is_available'] is True

def test_delete_menu_item_admin_success(client, auth_headers, menu_items):
    """Admin can successfully delete a menu item."""
    from src.models import MenuItem
    item_id = menu_items['soda'].id
    
    response = client.delete(f'/api/dishes/{item_id}', headers=auth_headers['admin'])
    assert response.status_code == 204
    
    # Verify deletion
    assert MenuItem.query.get(item_id) is None

def test_delete_menu_item_staff_forbidden(client, auth_headers, menu_items):
    """Staff cannot delete menu items (assuming only admin can)."""
    item_id = menu_items['burger'].id
    response = client.delete(f'/api/dishes/{item_id}', headers=auth_headers['staff'])
    assert response.status_code == 403