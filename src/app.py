from flask import Flask, jsonify, request

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)