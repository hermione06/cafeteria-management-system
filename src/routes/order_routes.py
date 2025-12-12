from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.models import db, Order, OrderItem, MenuItem
from src.utils.decorators import admin_required, staff_or_admin_required
from src.utils.pagination import paginate
from datetime import datetime, timezone

order_bp = Blueprint('orders', __name__)


@order_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get orders - users see their own, staff/admin see all"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role')
        
        # Build query
        query = Order.query
        
        # Filter by user for regular users
        if role not in ['admin', 'staff']:
            query = query.filter_by(user_id=user_id)
        else:
            # Allow filtering by user_id for staff/admin
            filter_user_id = request.args.get('user_id', type=int)
            if filter_user_id:
                query = query.filter_by(user_id=filter_user_id)
        
        # Filter by status
        status = request.args.get('status')
        if status:
            if not Order.validate_status(status):
                return jsonify({"error": "Invalid status"}), 400
            query = query.filter_by(status=status)
        
        # Filter by payment status
        is_paid = request.args.get('is_paid')
        if is_paid is not None:
            query = query.filter_by(is_paid=is_paid.lower() == 'true')
        
        # Order by creation date (newest first)
        query = query.order_by(Order.created_at.desc())
        
        # Paginate
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = paginate(query, page, per_page)
        
        return jsonify({
            "orders": [order.to_dict(include_items=True, include_user=(role in ['admin', 'staff'])) 
                      for order in result['items']],
            "pagination": result['pagination']
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch orders: {str(e)}"}), 500


@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a specific order"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role')
        
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Check authorization
        if role not in ['admin', 'staff'] and order.user_id != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        return jsonify(order.to_dict(include_items=True, include_user=(role in ['admin', 'staff']))), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch order: {str(e)}"}), 500


@order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate items
        if not data or 'items' not in data or not data['items']:
            return jsonify({"error": "Order items are required"}), 400
        
        # Create order
        order = Order(
            user_id=user_id,
            status='pending',
            special_instructions=data.get('special_instructions')
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID before adding items
        
        # Add order items
        for item_data in data['items']:
            if 'menu_item_id' not in item_data or 'quantity' not in item_data:
                db.session.rollback()
                return jsonify({"error": "Each item must have menu_item_id and quantity"}), 400
            
            menu_item = db.session.get(MenuItem, item_data['menu_item_id'])
            
            if not menu_item:
                db.session.rollback()
                return jsonify({"error": f"Menu item {item_data['menu_item_id']} not found"}), 404
            
            if not menu_item.is_available:
                db.session.rollback()
                return jsonify({"error": f"{menu_item.name} is currently unavailable"}), 400
            
            quantity = int(item_data['quantity'])
            if quantity <= 0:
                db.session.rollback()
                return jsonify({"error": "Quantity must be positive"}), 400
            
            # Create order item with current price
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=quantity,
                unit_price=menu_item.price
            )
            
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            "message": "Order created successfully",
            "order": order.to_dict(include_items=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create order: {str(e)}"}), 500


@order_bp.route('/<int:order_id>/items', methods=['POST'])
@jwt_required()
def add_order_item(order_id):
    """Add an item to an existing order"""
    try:
        user_id = get_jwt_identity()
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Check authorization
        if order.user_id != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        # Can only modify pending orders
        if order.status != 'pending':
            return jsonify({"error": "Can only modify pending orders"}), 400
        
        data = request.get_json()
        
        if not data or 'menu_item_id' not in data or 'quantity' not in data:
            return jsonify({"error": "menu_item_id and quantity are required"}), 400
        
        menu_item = db.session.get(MenuItem, data['menu_item_id'])
        
        if not menu_item:
            return jsonify({"error": "Menu item not found"}), 404
        
        if not menu_item.is_available:
            return jsonify({"error": f"{menu_item.name} is currently unavailable"}), 400
        
        quantity = int(data['quantity'])
        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400
        
        # Check if item already exists in order
        existing_item = OrderItem.query.filter_by(
            order_id=order.id,
            menu_item_id=menu_item.id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=quantity,
                unit_price=menu_item.price
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            "message": "Item added to order",
            "order": order.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add item: {str(e)}"}), 500


@order_bp.route('/<int:order_id>/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_order_item(order_id, item_id):
    """Remove an item from an order"""
    try:
        user_id = get_jwt_identity()
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        if order.user_id != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        if order.status != 'pending':
            return jsonify({"error": "Can only modify pending orders"}), 400
        
        order_item = db.session.get(OrderItem, item_id)
        
        if not order_item or order_item.order_id != order_id:
            return jsonify({"error": "Order item not found"}), 404
        
        db.session.delete(order_item)
        db.session.commit()
        
        return jsonify({
            "message": "Item removed from order",
            "order": order.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to remove item: {str(e)}"}), 500


@order_bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
@staff_or_admin_required()
def update_order_status(order_id):
    """Update order status (Staff/Admin only)"""
    try:
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({"error": "Status is required"}), 400
        
        new_status = data['status']
        
        if not Order.validate_status(new_status):
            return jsonify({"error": "Invalid status"}), 400
        
        order.status = new_status
        
        # Set completed_at when order is completed
        if new_status == 'completed':
            order.completed_at = datetime.now(timezone.utc)
        
        # Add admin notes if provided
        if 'admin_notes' in data:
            order.admin_notes = data['admin_notes']
        
        db.session.commit()
        
        return jsonify({
            "message": f"Order status updated to {new_status}",
            "order": order.to_dict(include_items=True, include_user=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update status: {str(e)}"}), 500


@order_bp.route('/<int:order_id>/payment', methods=['PATCH'])
@jwt_required()
@staff_or_admin_required()
def update_payment_status(order_id):
    """Update payment status (Staff/Admin only)"""
    try:
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        data = request.get_json()
        
        if not data or 'is_paid' not in data:
            return jsonify({"error": "is_paid is required"}), 400
        
        order.is_paid = bool(data['is_paid'])
        
        if 'payment_method' in data:
            order.payment_method = data['payment_method']
        
        db.session.commit()
        
        payment_status = "paid" if order.is_paid else "unpaid"
        
        return jsonify({
            "message": f"Order marked as {payment_status}",
            "order": order.to_dict(include_items=True, include_user=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update payment: {str(e)}"}), 500


@order_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    """Delete an order (user can delete own pending orders, admin can delete any)"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        role = claims.get('role')
        
        order = db.session.get(Order, order_id)
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Check authorization
        if role != 'admin' and order.user_id != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        # Users can only delete pending orders
        if role != 'admin' and order.status != 'pending':
            return jsonify({"error": "Can only delete pending orders"}), 400
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({"message": "Order deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete order: {str(e)}"}), 500