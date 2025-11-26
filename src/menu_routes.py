from flask import Blueprint, request, jsonify
from models import db, MenuItem, Category
import os
from werkzeug.utils import secure_filename

menu_bp = Blueprint("menu", __name__, url_prefix="/menu")

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# getting all the menu items

@menu_bp.route("/", methods=["GET"])
def get_menu():
    items = MenuItem.query.all()
    return jsonify([item.to_dict() for item in items]), 200


# creating menu item (ADMIN)

@menu_bp.route("/", methods=["POST"])
def create_item():
    data = request.form

    name = data.get("name")
    price = data.get("price")
    category_name = data.get("category")

    if not name or not price or not category_name:
        return jsonify({"error": "Missing required fields"}), 400

    # Get or create category
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        category = Category(name=category_name)
        db.session.add(category)
        db.session.commit()

    # Handle image upload
    picture_url = None
    if "image" in request.files:
        file = request.files["image"]
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            picture_url = "/" + path
        else:
            return jsonify({"error": "Invalid file type"}), 400

    item = MenuItem(
        name=name,
        description=data.get("description"),
        price=float(price),
        picture_url=picture_url,
        category_id=category.id,
        stock=int(data.get("stock", 0)),
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


# updating item

@menu_bp.route("/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.json or {}

    if "name" in data:
        item.name = data["name"]

    if "description" in data:
        item.description = data["description"]

    if "price" in data:
        item.price = float(data["price"])

    if "available" in data:
        item.available = bool(data["available"])

    if "stock" in data:
        item.stock = int(data["stock"])

    if "category" in data:
        cat = Category.query.filter_by(name=data["category"]).first()
        if not cat:
            cat = Category(name=data["category"])
            db.session.add(cat)
            db.session.commit()

        item.category_id = cat.id

    db.session.commit()
    return jsonify(item.to_dict()), 200


# deleting item

@menu_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"}), 200



# Searching items by name

@menu_bp.route("/search", methods=["GET"])
def search_items():
    q = request.args.get("q", "").lower()
    results = MenuItem.query.filter(MenuItem.name.ilike(f"%{q}%")).all()
    return jsonify([i.to_dict() for i in results]), 200



# Filtering items by category

@menu_bp.route("/category/<category>", methods=["GET"])
def filter_by_category(category):
    cat = Category.query.filter_by(name=category).first()
    if not cat:
        return jsonify([]), 200

    return jsonify([i.to_dict() for i in cat.items]), 200
