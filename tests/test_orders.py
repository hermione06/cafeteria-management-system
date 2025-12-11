# cafeteria-management-system/tests/test_order_routes.py

import json
import pytest
from models import Order, OrderStatus
from order import OrderHandler 

# Note: Fixtures from conftest.py are automatically available (client, setup_users, auth_headers, setup_menu, setup_orders)

def get_item_id(setup_menu, item_name):
    return setup_menu[item_name].id

# --- Create Order (POST /api/orders) ---

def test_create_order_success_and_check_stock(client, auth_headers, setup_menu, init_db):
    """Test creating an order and verify stock is reduced."""
    burger_id = get_item_id(setup_menu, 'Burger')
    
    order_data = {'items': [{'dish_id': burger_id, 'quantity': 2}]}
    response = client.post('/api/orders', data=json.dumps(order_data), headers=auth_headers['student'])
    
    assert response.status_code == 201
    
    # Verify stock reduction
    with init_db.app.app_context():
        burger = init_db.session.get(OrderHandler.MenuItem, burger_id)
        assert burger.stock == 8 # Initial stock was 10. 10 - 2 = 8

def test_create_order_unavailable_item(client, auth_headers, setup_menu):
    """Test creating an order with an unavailable item (should fail)."""
    soda_id = get_item_id(setup_menu, 'Soda') 
    order_data = {'items': [{'dish_id': soda_id, 'quantity': 1}]}

    response = client.post('/api/orders', data=json.dumps(order_data), headers=auth_headers['student'])
    assert response.status_code == 400
    assert b'is currently unavailable' in response.data

# --- Get Orders (GET /api/orders) ---

def test_get_user_orders_only_own_orders(client, auth_headers, setup_orders):
    """Test a student only sees their own orders."""
    # Since all setup orders belong to the student, we check the count
    response = client.get('/api/orders', headers=auth_headers['student'])
    assert response.status_code == 200
    assert len(json.loads(response.data)['items']) == 2

def test_get_admin_all_orders(client, auth_headers, setup_orders):
    """Test Admin retrieving all orders in the system."""
    response = client.get('/api/orders', headers=auth_headers['admin'])
    assert response.status_code == 200
    assert len(json.loads(response.data)['items']) == 2

# --- Update Order Status (PATCH /api/orders/<id>/status) ---

def test_update_status_staff_success(client, auth_headers, setup_orders, init_db):
    """Test a staff member updating order status."""
    order_id = setup_orders[0].id
    new_status = OrderStatus.PREPARING.value
    
    response = client.patch(f'/api/orders/{order_id}/status', 
                            data=json.dumps({'status': new_status}), 
                            headers=auth_headers['staff'])
    assert response.status_code == 200
    assert json.loads(response.data)['status'] == new_status

def test_update_status_student_forbidden(client, auth_headers, setup_orders):
    """Test a student trying to update order status (should fail)."""
    order_id = setup_orders[0].id
    response = client.patch(f'/api/orders/{order_id}/status', 
                            data=json.dumps({'status': 'preparing'}), 
                            headers=auth_headers['student'])
    assert response.status_code == 403 # Forbidden

# --- Mark Paid (PATCH /api/orders/<id>/paid) ---

def test_mark_paid_admin_success(client, auth_headers, setup_orders):
    """Test Admin marking an unpaid order as paid."""
    order_id = setup_orders[0].id # Order 1 is unpaid
    response = client.patch(f'/api/orders/{order_id}/paid', 
                            data=json.dumps({'is_paid': True}), 
                            headers=auth_headers['admin'])
    assert response.status_code == 200
    assert json.loads(response.data)['is_paid'] is True