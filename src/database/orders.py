import sqlite3

from database.connection import get_connection
from database.validators import validate_id, validate_money, validate_quantity


def create_order(customer_id=None):
    """Create a pending order for an optional existing customer."""
    if customer_id is not None:
        validate_id(customer_id, "Customer ID")
    connection = get_connection()

    try:
        if customer_id is not None:
            customer = connection.execute(
                "SELECT id FROM customers WHERE id = ?",
                (customer_id,),
            ).fetchone()

            if customer is None:
                raise ValueError("The selected customer does not exist.")

        cursor = connection.execute(
            """
            INSERT INTO orders (customer_id, status)
            VALUES (?, 'Pending')
            """,
            (customer_id,),
        )
        order_id = cursor.lastrowid
        connection.commit()
        return order_id

    except (sqlite3.Error, ValueError):
        connection.rollback()
        raise

    finally:
        connection.close()


def _insert_order_item(connection, order_id, menu_item_id, quantity):
    """Insert one available menu item using the current transaction."""
    menu_item = connection.execute(
        """
        SELECT price FROM menu_items
        WHERE id = ? AND available = 1
        """,
        (menu_item_id,),
    ).fetchone()

    if menu_item is None:
        raise ValueError("Menu item does not exist or is unavailable.")

    unit_price = validate_money(menu_item[0], "Menu price")
    connection.execute(
        """
        INSERT INTO order_items
            (order_id, menu_item_id, quantity, unit_price)
        VALUES (?, ?, ?, ?)
        """,
        (order_id, menu_item_id, quantity, unit_price),
    )


def create_completed_order(
    customer_id, items, tax, discount, payment_method
):
    """Create and complete an order within one database transaction."""
    if customer_id is not None:
        validate_id(customer_id, "Customer ID")

    try:
        items = list(items)
    except TypeError:
        raise ValueError("Order items must be an iterable.") from None

    if not items:
        raise ValueError("An order must contain at least one item.")

    validated_items = []
    for item in items:
        try:
            menu_item_id, quantity = item
        except (TypeError, ValueError):
            raise ValueError("Order items must contain an item ID and quantity.") from None
        validate_id(menu_item_id, "Menu item ID")
        validated_items.append((menu_item_id, validate_quantity(quantity)))

    tax = validate_money(tax, "Tax")
    discount = validate_money(discount, "Discount")

    if not isinstance(payment_method, str) or not payment_method.strip():
        raise ValueError("Payment method is required.")
    payment_method = payment_method.strip()

    connection = get_connection()

    try:
        if customer_id is not None:
            customer = connection.execute(
                "SELECT id FROM customers WHERE id = ?",
                (customer_id,),
            ).fetchone()
            if customer is None:
                raise ValueError("The selected customer does not exist.")

        cursor = connection.execute(
            """
            INSERT INTO orders (customer_id, status)
            VALUES (?, 'Pending')
            """,
            (customer_id,),
        )
        order_id = cursor.lastrowid

        for menu_item_id, quantity in validated_items:
            _insert_order_item(connection, order_id, menu_item_id, quantity)

        totals = _update_order_totals(
            connection, order_id, tax=tax, discount=discount
        )

        connection.execute(
            """
            UPDATE orders
            SET payment_method = ?, status = 'Completed'
            WHERE id = ?
            """,
            (payment_method, order_id),
        )
        connection.commit()
        return order_id, totals

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_order(order_id):
    """Return an order and its line items, or None if it does not exist."""
    validate_id(order_id, "Order ID")
    connection = get_connection()

    try:
        order = connection.execute(
            """
            SELECT id, customer_id, subtotal, tax, discount, total,
                   payment_method, status, created_at
            FROM orders
            WHERE id = ?
            """,
            (order_id,),
        ).fetchone()

        if order is None:
            return None

        items = connection.execute(
            """
            SELECT oi.id, oi.menu_item_id, mi.name, oi.quantity,
                   oi.unit_price, ROUND(oi.quantity * oi.unit_price, 2)
            FROM order_items AS oi
            JOIN menu_items AS mi ON mi.id = oi.menu_item_id
            WHERE oi.order_id = ?
            ORDER BY oi.id
            """,
            (order_id,),
        ).fetchall()

        return {"order": order, "items": items}

    finally:
        connection.close()


def _update_order_totals(connection, order_id, tax=None, discount=None):
    """Recalculate an order's totals using the current transaction."""
    order = connection.execute(
        "SELECT tax, discount, status FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()

    if order is None:
        raise ValueError("Order does not exist.")

    current_tax, current_discount, status = order

    if status != "Pending":
        raise ValueError("Only pending orders can be modified.")

    tax = validate_money(
        current_tax if tax is None else tax, "Tax"
    )
    discount = validate_money(
        current_discount if discount is None else discount, "Discount"
    )

    subtotal = connection.execute(
        """
        SELECT COALESCE(SUM(quantity * unit_price), 0)
        FROM order_items
        WHERE order_id = ?
        """,
        (order_id,),
    ).fetchone()[0]

    subtotal = round(subtotal, 2)

    if discount > subtotal + tax:
        raise ValueError("Discount cannot exceed subtotal plus tax.")

    total = round(subtotal + tax - discount, 2)

    connection.execute(
        """
        UPDATE orders
        SET subtotal = ?, tax = ?, discount = ?, total = ?
        WHERE id = ?
        """,
        (subtotal, tax, discount, total, order_id),
    )

    return {
        "subtotal": subtotal,
        "tax": tax,
        "discount": discount,
        "total": total,
    }


def recalculate_order_totals(order_id, tax=0, discount=0):
    """Set tax and discount, then recalculate the order totals."""
    validate_id(order_id, "Order ID")
    tax = validate_money(tax, "Tax")
    discount = validate_money(discount, "Discount")
    connection = get_connection()

    try:
        totals = _update_order_totals(
            connection, order_id, tax=tax, discount=discount
        )
        connection.commit()
        return totals

    except (sqlite3.Error, ValueError):
        connection.rollback()
        raise

    finally:
        connection.close()


def add_order_item(order_id, menu_item_id, quantity):
    """Add an available menu item to a pending order."""
    validate_id(order_id, "Order ID")
    validate_id(menu_item_id, "Menu item ID")
    quantity = validate_quantity(quantity)
    connection = get_connection()

    try:
        order = connection.execute(
            "SELECT status FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()

        if order is None:
            raise ValueError("Order does not exist.")

        if order[0] != "Pending":
            raise ValueError("Items can only be added to pending orders.")

        _insert_order_item(connection, order_id, menu_item_id, quantity)

        totals = _update_order_totals(connection, order_id)
        connection.commit()
        return totals["subtotal"]

    except (sqlite3.Error, ValueError):
        connection.rollback()
        raise

    finally:
        connection.close()


def update_order_item_quantity(order_item_id, quantity):
    """Change an item quantity and update its order totals."""
    validate_id(order_item_id, "Order item ID")
    quantity = validate_quantity(quantity)
    connection = get_connection()

    try:
        item = connection.execute(
            """
            SELECT oi.order_id
            FROM order_items AS oi
            JOIN orders AS o ON o.id = oi.order_id
            WHERE oi.id = ? AND o.status = 'Pending'
            """,
            (order_item_id,),
        ).fetchone()

        if item is None:
            raise ValueError("Order item does not exist or is not editable.")

        order_id = item[0]

        connection.execute(
            "UPDATE order_items SET quantity = ? WHERE id = ?",
            (quantity, order_item_id),
        )

        totals = _update_order_totals(connection, order_id)
        connection.commit()
        return totals["subtotal"]

    except (sqlite3.Error, ValueError):
        connection.rollback()
        raise

    finally:
        connection.close()


def remove_order_item(order_item_id):
    """Remove an item and update its order totals."""
    validate_id(order_item_id, "Order item ID")
    connection = get_connection()

    try:
        item = connection.execute(
            """
            SELECT oi.order_id
            FROM order_items AS oi
            JOIN orders AS o ON o.id = oi.order_id
            WHERE oi.id = ? AND o.status = 'Pending'
            """,
            (order_item_id,),
        ).fetchone()

        if item is None:
            raise ValueError("Order item does not exist or is not editable.")

        order_id = item[0]

        connection.execute(
            "DELETE FROM order_items WHERE id = ?",
            (order_item_id,),
        )

        totals = _update_order_totals(connection, order_id)
        connection.commit()
        return totals["subtotal"]

    except (sqlite3.Error, ValueError):
        connection.rollback()
        raise

    finally:
        connection.close()


def get_orders():
    """Return orders newest first, including customer names."""
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT o.id, o.customer_id, c.name, o.subtotal, o.tax,
                   o.discount, o.total, o.payment_method, o.status,
                   o.created_at
            FROM orders AS o
            LEFT JOIN customers AS c ON c.id = o.customer_id
            ORDER BY o.created_at DESC, o.id DESC
            """
        ).fetchall()

    finally:
        connection.close()


def complete_order(order_id, payment_method):
    """Complete a pending order after validating its payment method."""
    validate_id(order_id, "Order ID")
    if not isinstance(payment_method, str) or not payment_method.strip():
        raise ValueError("Payment method is required.")

    payment_method = payment_method.strip()
    connection = get_connection()

    try:
        order = connection.execute(
            "SELECT status FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()

        if order is None:
            raise ValueError("Order does not exist.")

        if order[0] != "Pending":
            raise ValueError("Only pending orders can be completed.")

        item_count = connection.execute(
            "SELECT COUNT(*) FROM order_items WHERE order_id = ?",
            (order_id,),
        ).fetchone()[0]

        if item_count == 0:
            raise ValueError("Cannot complete an order without items.")

        _update_order_totals(connection, order_id)

        connection.execute(
            """
            UPDATE orders
            SET payment_method = ?, status = 'Completed'
            WHERE id = ?
            """,
            (payment_method, order_id),
        )

        connection.commit()

    except (sqlite3.Error, ValueError):
        connection.rollback()
        raise

    finally:
        connection.close()
