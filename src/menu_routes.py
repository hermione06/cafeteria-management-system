from flask import Blueprint, request, jsonify
from models import db, MenuItem, Category
from werkzeug.utils import secure_filename
import os

menu_bp = Blueprint("menu", __name__, url_prefix="/menu")

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg"}


def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# ============================
# GET ALL MENU ITEMS
# ============================

@menu_bp.route("/", methods=["GET"])
def get_menu():
    items = MenuItem.query.all()
    # Return empty list [] with 200 OK if no items exist, instead of 404
    return jsonify([item.to_dict() for item in items]), 200


# ============================
# GET SINGLE ITEM
# ============================

@menu_bp.route("/<int:item_id>", methods=["GET"])
def get_menu_item(item_id):
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item.to_dict()), 200


# ============================
# CREATE ITEM
# ============================

@menu_bp.route("/", methods=["POST"])
def create_item():
    data = request.form if request.form else request.get_json(silent=True) or {}

    name = data.get("name")
    price = data.get("price")
    category = data.get("category")

    if not name or not price or not category:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        price = float(price)
    except:
        return jsonify({"error": "Invalid price"}), 400

    # image
    picture_url = None
    if "image" in request.files:
        file = request.files["image"]
        if allowed(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            picture_url = "/" + path
        else:
            return jsonify({"error": "Invalid file type"}), 400

    item = MenuItem(
        name=name,
        description=data.get("description"),
        price=price,
        stock=int(data.get("stock", 0)),
        picture_url=picture_url,
        category=category,
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


# ============================
# UPDATE ITEM
# ============================

@menu_bp.route("/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        item.name = data["name"]
    if "description" in data:
        item.description = data["description"]
    if "price" in data:
        try:
            item.price = float(data["price"])
        except:
            return jsonify({"error": "Invalid price"}), 400
    if "available" in data:
        item.available = bool(data["available"])
    if "stock" in data:
        try:
            item.stock = int(data["stock"])
        except:
            return jsonify({"error": "Invalid stock"}), 400
    if "category" in data:
        cat = Category.query.filter_by(name=data["category"]).first()
        if not cat:
            cat = Category(name=data["category"])
            db.session.add(cat)
            db.session.flush()
        item.category_id = cat.id

    db.session.commit()
    return jsonify(item.to_dict()), 200


# ============================
# DELETE ITEM
# ============================

@menu_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"}), 200


# ============================
# SEARCH
# ============================

@menu_bp.route("/search", methods=["GET"])
def search_items():
    q = request.args.get("q", "").strip()
    results = MenuItem.query.filter(MenuItem.name.ilike(f"%{q}%")).all()
    return jsonify([item.to_dict() for item in results]), 200


# ============================
# FILTER BY CATEGORY
# ============================

@menu_bp.route("/category/<category>", methods=["GET"])
def filter_by_category(category):
    cat = Category.query.filter_by(name=category).first()
    if not cat:
        return jsonify([]), 200
    return jsonify([item.to_dict() for item in cat.items]), 200
