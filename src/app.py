import os
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from models import db, User
from config import config
from auth import auth_bp
from decorators import admin_required

app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
# Map 'production' to 'default' if not explicitly set
if config_name not in config:
    config_name = 'default'
app.config.from_object(config[config_name])

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp)

# In-memory storage for menu items (will be replaced with database later)
menu_items = [
    {"id": 1, "name": "Coffee", "price": 2.50, "category": "Beverages"},
    {"id": 2, "name": "Sandwich", "price": 5.00, "category": "Food"},
    {"id": 3, "name": "Salad", "price": 4.50, "category": "Food"}
]

@app.route('/')
def index():
    """Homepage route"""
    return jsonify({
        "message": "Welcome to Cafeteria Management System",
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/menu', methods=['GET'])
def get_menu():
    """Get all menu items"""
    return jsonify({"menu": menu_items}), 200

@app.route('/menu/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    """Get a specific menu item by ID"""
    item = next((item for item in menu_items if item["id"] == item_id), None)
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404

@app.route('/menu/category/<category>', methods=['GET'])
def get_menu_by_category(category):
    """Get menu items filtered by category"""
    filtered_items = [item for item in menu_items if item["category"].lower() == category.lower()]
    if filtered_items:
        return jsonify({"category": category, "items": filtered_items}), 200
    return jsonify({"message": f"No items found in category: {category}"}), 200

# User Management Endpoints (Protected)

@app.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
def get_users():
    """Get all users (Admin only)"""
    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]}), 200

@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user by ID (Users can view their own, admins can view all)"""
    from flask_jwt_extended import get_jwt_identity
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    # Allow if admin or viewing own profile
    if claims.get('role') != 'admin' and current_user_id != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    user = db.session.get(User, user_id)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('email'):
        return jsonify({"error": "Username and email are required"}), 400
    
    # Validate role if provided
    role = data.get('role', 'user')
    if not User.validate_role(role):
        return jsonify({"error": "Invalid role. Must be: user, or admin"}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409
    
    try:
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            role=role,
        )
        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "message": "User created successfully",
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    # Validate role if provided
    if 'role' in data and not User.validate_role(data['role']):
        return jsonify({"error": "Invalid role. Must be: customer, staff, or admin"}), 400
    
    try:
        # Update user fields
        if 'username' in data:
            # Check if new username already exists
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({"error": "Username already exists"}), 409
            user.username = data['username']
        
        if 'email' in data:
            # Check if new email already exists
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({"error": "Email already exists"}), 409
            user.email = data['email']
        
        if 'role' in data:
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create tables if they don't exist (useful for Docker)
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)