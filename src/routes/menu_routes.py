from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db, MenuItem
from utils.decorators import admin_required, staff_or_admin_required
from utils.pagination import paginate

menu_bp = Blueprint('menu', __name__)


@menu_bp.route('', methods=['GET'])
def get_menu():
    """Get all menu items with optional filtering and pagination"""
    try:
        # Get query parameters
        category = request.args.get('category')
        available_only = request.args.get('available', 'true').lower() == 'true'
        search = request.args.get('search', '').strip()
        
        # Build query
        query = MenuItem.query
        
        if category:
            query = query.filter_by(category=category.lower())
        
        if available_only:
            query = query.filter_by(is_available=True)
        
        if search:
            query = query.filter(MenuItem.name.ilike(f'%{search}%'))
        
        # Order by name
        query = query.order_by(MenuItem.name)
        
        # Paginate results
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = paginate(query, page, per_page)
        
        return jsonify({
            "items": [item.to_dict() for item in result['items']],
            "pagination": result['pagination']
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch menu: {str(e)}"}), 500


@menu_bp.route('/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    """Get a specific menu item by ID"""
    try:
        item = db.session.get(MenuItem, item_id)
        
        if not item:
            return jsonify({"error": "Menu item not found"}), 404
        
        return jsonify(item.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch menu item: {str(e)}"}), 500


@menu_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    try:
        categories = db.session.query(MenuItem.category).distinct().all()
        return jsonify({
            "categories": [cat[0] for cat in categories]
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch categories: {str(e)}"}), 500


@menu_bp.route('', methods=['POST'])
@jwt_required()
@admin_required()
def create_menu_item():
    """Create a new menu item (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'price', 'category']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Name, price, and category are required"}), 400
        
        # Validate price
        try:
            price = float(data['price'])
            if price < 0:
                return jsonify({"error": "Price must be non-negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid price format"}), 400
        
        # Validate category
        category = data['category'].lower()
        if not MenuItem.validate_category(category):
            return jsonify({
                "error": "Invalid category. Must be: beverages, food, snacks, or desserts"
            }), 400
        
        # Create menu item
        item = MenuItem(
            name=data['name'],
            description=data.get('description'),
            price=price,
            category=category,
            image_url=data.get('image_url'),
            is_available=data.get('is_available', True),
            stock_quantity=data.get('stock_quantity', 0)
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            "message": "Menu item created successfully",
            "item": item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create menu item: {str(e)}"}), 500


@menu_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
@staff_or_admin_required()
def update_menu_item(item_id):
    """Update an existing menu item"""
    try:
        item = db.session.get(MenuItem, item_id)
        
        if not item:
            return jsonify({"error": "Menu item not found"}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            item.name = data['name']
        
        if 'description' in data:
            item.description = data['description']
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return jsonify({"error": "Price must be non-negative"}), 400
                item.price = price
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid price format"}), 400
        
        if 'category' in data:
            category = data['category'].lower()
            if not MenuItem.validate_category(category):
                return jsonify({
                    "error": "Invalid category. Must be: beverages, food, snacks, or desserts"
                }), 400
            item.category = category
        
        if 'image_url' in data:
            item.image_url = data['image_url']
        
        if 'is_available' in data:
            item.is_available = bool(data['is_available'])
        
        if 'stock_quantity' in data:
            item.stock_quantity = int(data['stock_quantity'])
        
        db.session.commit()
        
        return jsonify({
            "message": "Menu item updated successfully",
            "item": item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update menu item: {str(e)}"}), 500


@menu_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_menu_item(item_id):
    """Delete a menu item (Admin only)"""
    try:
        item = db.session.get(MenuItem, item_id)
        
        if not item:
            return jsonify({"error": "Menu item not found"}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({"message": "Menu item deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete menu item: {str(e)}"}), 500


@menu_bp.route('/<int:item_id>/availability', methods=['PATCH'])
@jwt_required()
@staff_or_admin_required()
def toggle_availability(item_id):
    """Toggle menu item availability"""
    try:
        item = db.session.get(MenuItem, item_id)
        
        if not item:
            return jsonify({"error": "Menu item not found"}), 404
        
        data = request.get_json()
        
        if 'is_available' not in data:
            return jsonify({"error": "is_available field is required"}), 400
        
        item.is_available = bool(data['is_available'])
        db.session.commit()
        
        status = "available" if item.is_available else "unavailable"
        
        return jsonify({
            "message": f"Menu item marked as {status}",
            "item": item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update availability: {str(e)}"}), 500