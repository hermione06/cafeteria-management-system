import pytest
from app import app, db
from models import User, MenuItem, Order, OrderItem
from order import OrderHandler  # adjust path if different


# -------------------------------------------------------------
# TEST FIXTURES
# -------------------------------------------------------------
@pytest.fixture
def client():
    """Test client with fresh in-memory DB."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        # Setup test user + menu items
        user = User(username="testuser", email="t@t.com")
        user.set_password("testpassword")
        db.session.add(user)

        item1 = MenuItem(name="Burger", price=5.0)
        item2 = MenuItem(name="Cola", price=2.0)
        db.session.add_all([item1, item2])

        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


# -------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------
def get_ids():
    """Small helper to retrieve DB IDs."""
    return (
        User.query.first().id,
        [item.id for item in MenuItem.query.all()]
    )


# -------------------------------------------------------------
# TESTS
# -------------------------------------------------------------
def test_create_order(client):
    user_id, _ = get_ids()

    order = OrderHandler.create_order(user_id)

    assert order.id is not None
    assert order.user_id == user_id
    assert order.status == "pending"  # if your default


def test_add_item(client):
    user_id, item_ids = get_ids()
    item1, item2 = item_ids

    order = OrderHandler.create_order(user_id)

    OrderHandler.add_item(order.id, item1, quantity=2)
    OrderHandler.add_item(order.id, item2, quantity=1)

    oi = OrderItem.query.filter_by(order_id=order.id).all()
    assert len(oi) == 2
    assert oi[0].quantity == 2
    assert oi[1].quantity == 1


def test_add_item_existing_increments(client):
    user_id, item_ids = get_ids()
    item = item_ids[0]

    order = OrderHandler.create_order(user_id)

    OrderHandler.add_item(order.id, item, 1)
    OrderHandler.add_item(order.id, item, 3)

    oi = OrderItem.query.filter_by(order_id=order.id).first()
    assert oi.quantity == 4


def test_remove_item_partial(client):
    user_id, item_ids = get_ids()
    item = item_ids[0]

    order = OrderHandler.create_order(user_id)
    OrderHandler.add_item(order.id, item, 5)

    OrderHandler.remove_item(order.id, item, quantity=2)

    oi = OrderItem.query.filter_by(order_id=order.id).first()
    assert oi.quantity == 3


def test_remove_item_entire(client):
    user_id, item_ids = get_ids()
    item = item_ids[0]

    order = OrderHandler.create_order(user_id)
    OrderHandler.add_item(order.id, item, 3)

    OrderHandler.remove_item(order.id, item)  # remove all

    assert OrderItem.query.count() == 0


def test_update_status(client):
    user_id, _ = get_ids()
    order = OrderHandler.create_order(user_id)

    OrderHandler.update_status(order.id, "completed")

    updated = Order.query.get(order.id)
    assert updated.status == "completed"


def test_mark_paid(client):
    user_id, _ = get_ids()
    order = OrderHandler.create_order(user_id)

    OrderHandler.mark_paid(order.id)

    updated = Order.query.get(order.id)
    assert updated.is_paid is True


def test_mark_unpaid(client):
    user_id, _ = get_ids()
    order = OrderHandler.create_order(user_id)

    OrderHandler.mark_unpaid(order.id)

    updated = Order.query.get(order.id)
    assert updated.is_paid is False


def test_get_order(client):
    user_id, item_ids = get_ids()
    item = item_ids[0]

    order = OrderHandler.create_order(user_id)
    OrderHandler.add_item(order.id, item, 2)

    data = OrderHandler.get_order(order.id)

    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2


def test_get_orders_by_user(client):
    user_id, _ = get_ids()

    o1 = OrderHandler.create_order(user_id)
    o2 = OrderHandler.create_order(user_id)

    orders = OrderHandler.get_orders_by_user(user_id)

    assert len(orders) == 2
    assert {o["id"] for o in orders} == {o1.id, o2.id}


def test_get_all_orders(client):
    user_id, _ = get_ids()

    OrderHandler.create_order(user_id)
    OrderHandler.create_order(user_id)

    orders = OrderHandler.get_all_orders()

    assert len(orders) == 2


def test_delete_order(client):
    user_id, _ = get_ids()
    order = OrderHandler.create_order(user_id)

    assert Order.query.count() == 1

    OrderHandler.delete_order(order.id)

    assert Order.query.count() == 0
