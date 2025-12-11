import pytest
import json
from models import db, Order, OrderItem, MenuItem
from order import OrderHandler # The utility class tested by the original test_orders.py

# Using the common fixtures from test_auth.py for brevity (app, client, init_db, auth_headers, get_user_data)
# In a real project, these fixtures would be in conftest.py

@pytest.fixture
def active_menu_items(init_db):
    """Adds menu items specifically for order creation."""
    with db.session.begin():
        item1 = MenuItem(name='Pizza', price=10.00, category='main', is_available=True)
        item2 = MenuItem(name='Water', price=1.00, category='drink', is_available=True)
        db.session.add_all([item1, item2])
    db.session.commit()
    return item1, item2

@pytest.fixture
def created_order(get_user_data, active_menu_items):
    """Creates a sample order for testing."""
    student_user, _ = get_user_data('student')
    pizza, water = active_menu_items
    
    order = OrderHandler.create_order(student_user.id)
    OrderHandler.add_item(order.id, pizza.id, 2)
    OrderHandler.add_item(order.id, water.id, 1)
    
    return order, student_user.id

# --- Order API Tests ---

def test_create_order_success(client, auth_headers, active_menu_items, get_user_data):
    """A student can successfully create a new order."""
    pizza, water = active_menu_items
    
    order_data = {
        'items': [
            {'menu_item_id': pizza.id, 'quantity': 1},
            {'menu_item_id': water.id, 'quantity': 3}
        ],
        'instructions': 'Extra napkins please.'
    }
    
    response = client.post('/api/orders', json=order_data, headers=auth_headers['student'])
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['order']['total_amount'] == (10.00 * 1) + (1.00 * 3)
    assert data['order']['status'] == 'pending'
    assert len(data['order']['items']) == 2
    
def test_create_order_unauthenticated_forbidden(client, active_menu_items):
    """Unauthenticated users cannot create an order."""
    pizza, _ = active_menu_items
    response = client.post('/api/orders', json={'items': [{'menu_item_id': pizza.id, 'quantity': 1}]})
    assert response.status_code == 401

def test_student_get_own_order_success(client, auth_headers, created_order):
    """A student can view their own order."""
    order, student_id = created_order
    response = client.get(f'/api/orders/{order.id}', headers=auth_headers['student'])
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['order']['user_id'] == student_id
    assert len(data['order']['items']) == 2

def test_student_get_other_user_order_forbidden(client, auth_headers, created_order, get_user_data):
    """A student cannot view another user's order (e.g., admin's order)."""
    # Create an admin order
    admin_user, _ = get_user_data('admin')
    admin_order = OrderHandler.create_order(admin_user.id)
    
    # Student tries to access admin's order
    response = client.get(f'/api/orders/{admin_order.id}', headers=auth_headers['student'])
    assert response.status_code == 403

def test_staff_update_order_status_success(client, auth_headers, created_order):
    """Staff can update an order's status."""
    order, _ = created_order
    response = client.patch(f'/api/orders/{order.id}/status', json={
        'new_status': 'preparing'
    }, headers=auth_headers['staff'])
    assert response.status_code == 200
    assert json.loads(response.data)['order']['status'] == 'preparing'

def test_admin_mark_order_paid_success(client, auth_headers, created_order):
    """Admin/Staff can mark an order as paid (assuming this is the staff/admin route)."""
    order, _ = created_order
    
    # Check initial state
    assert Order.query.get(order.id).is_paid is False
    
    response = client.patch(f'/api/orders/{order.id}/pay', json={
        'is_paid': True
    }, headers=auth_headers['admin'])
    
    assert response.status_code == 200
    assert json.loads(response.data)['order']['is_paid'] is True

def test_student_cancel_order_success(client, auth_headers, created_order):
    """A student can cancel their own order if it's still 'pending'."""
    order, _ = created_order
    
    response = client.delete(f'/api/orders/{order.id}', headers=auth_headers['student'])
    assert response.status_code == 204
    
    # Verify status changed to 'cancelled'
    assert Order.query.get(order.id).status == 'cancelled'

def test_student_cancel_processed_order_failure(client, auth_headers, created_order):
    """A student cannot cancel an order that is already being processed."""
    order, _ = created_order
    OrderHandler.update_status(order.id, 'ready') # Staff/Admin mark it as ready
    
    response = client.delete(f'/api/orders/{order.id}', headers=auth_headers['student'])
    assert response.status_code == 400
    assert 'Order cannot be cancelled' in json.loads(response.data)['error']