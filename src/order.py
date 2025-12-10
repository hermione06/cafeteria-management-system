from models import db, Order, OrderItem, MenuItem, User

class OrderHandler:
    """High-level manager for Order and OrderItem operations"""

    # ---------------------------------------------------
    # INTERNAL — DO NOT USE OUTSIDE THIS CLASS
    # ---------------------------------------------------
    @staticmethod
    def _get_order(order_id):
        """Internal: return Order object or raise error"""
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} does not exist")
        return order

    @staticmethod
    def _get_user(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} does not exist")
        return user

    @staticmethod
    def _get_menu_item(menu_item_id):
        item = MenuItem.query.get(menu_item_id)
        if not item:
            raise ValueError(f"MenuItem {menu_item_id} does not exist")
        return item

    # ---------------------------------------------------
    # CREATE ORDER
    # ---------------------------------------------------
    @staticmethod
    def create_order(user_id):
        user = OrderHandler._get_user(user_id)

        order = Order(user_id=user.id)
        db.session.add(order)
        db.session.commit()

        return order

    # ---------------------------------------------------
    # ADD ITEM
    # ---------------------------------------------------
    @staticmethod
    def add_item(order_id, menu_item_id, quantity=1):
        order = OrderHandler._get_order(order_id)
        menu_item = OrderHandler._get_menu_item(menu_item_id)

        existing = OrderItem.query.filter_by(
            order_id=order.id,
            menu_item_id=menu_item.id
        ).first()

        if existing:
            existing.quantity += quantity
        else:
            db.session.add(OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=quantity
            ))

        db.session.commit()
        return order

    # ---------------------------------------------------
    # REMOVE ITEM
    # ---------------------------------------------------
    @staticmethod
    def remove_item(order_id, menu_item_id, quantity=None):
        order = OrderHandler._get_order(order_id)

        item = OrderItem.query.filter_by(
            order_id=order.id,
            menu_item_id=menu_item_id
        ).first()

        if not item:
            raise ValueError("Order item does not exist")

        if quantity is None or quantity >= item.quantity:
            db.session.delete(item)
        else:
            item.quantity -= quantity

        db.session.commit()
        return order

    # ---------------------------------------------------
    # UPDATE STATUS
    # ---------------------------------------------------
    @staticmethod
    def update_status(order_id, new_status):
        order = OrderHandler._get_order(order_id)

        if not Order.validate_status(new_status):
            raise ValueError("Invalid status")

        order.status = new_status
        db.session.commit()
        return order

    # ---------------------------------------------------
    # MARK PAID / UNPAID
    # ---------------------------------------------------
    @staticmethod
    def mark_paid(order_id):
        order = OrderHandler._get_order(order_id)
        order.is_paid = True
        db.session.commit()
        return order

    @staticmethod
    def mark_unpaid(order_id):
        order = OrderHandler._get_order(order_id)
        order.is_paid = False
        db.session.commit()
        return order

    # ---------------------------------------------------
    # PUBLIC GETTERS (UNIFIED)
    # ---------------------------------------------------
    @staticmethod
    def get_order(order_id, include_items=True, include_user=False):
        order = OrderHandler._get_order(order_id)
        return order.to_dict(
            include_items=include_items,
            include_user=include_user
        )

    @staticmethod
    def get_orders_by_user(user_id):
        user = OrderHandler._get_user(user_id)
        orders = Order.query.filter_by(user_id=user.id).all()

        # All use the get_order serializer
        return [
            OrderHandler.get_order(o.id, include_items=True)
            for o in orders
        ]

    @staticmethod
    def get_all_orders(include_items=True):
        orders = Order.query.all()

        return [
            OrderHandler.get_order(o.id, include_items=include_items)
            for o in orders
        ]

    # ---------------------------------------------------
    # DELETE
    # ---------------------------------------------------
    @staticmethod
    def delete_order(order_id):
        order = OrderHandler._get_order(order_id)

        db.session.delete(order)
        db.session.commit()
        return True
