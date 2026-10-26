import sqlite3

from database.connection import get_connection
from database.validators import (
    validate_menu_price,
    validate_id,
    validate_menu_text,
    validate_availability,
)


def get_menu_items():
    """Return all menu items ordered by name."""
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, category, price, available
            FROM menu_items
            ORDER BY name
            """
        ).fetchall()
    finally:
        connection.close()


def add_menu_item(name, category, price, available=True):
    """Add a new menu item."""
    name = validate_menu_text(name, "Menu item name")
    category = validate_menu_text(category, "Category")
    price = validate_menu_price(price)
    available = validate_availability(available)

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO menu_items (name, category, price, available)
            VALUES (?, ?, ?, ?)
            """,
            (name, category, price, available),
        )
        connection.commit()

    except (sqlite3.Error, ValueError, TypeError):
        connection.rollback()
        raise

    finally:
        connection.close()


def update_menu_item(item_id, name, category, price, available):
    """Update an existing menu item."""
    validate_id(item_id, "Menu item ID")
    name = validate_menu_text(name, "Menu item name")
    category = validate_menu_text(category, "Category")
    price = validate_menu_price(price)
    available = validate_availability(available)

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE menu_items
            SET name = ?, category = ?, price = ?, available = ?
            WHERE id = ?
            """,
            (name, category, price, available, item_id),
        )
        connection.commit()
        return cursor.rowcount > 0

    except (sqlite3.Error, ValueError, TypeError):
        connection.rollback()
        raise

    finally:
        connection.close()


def delete_menu_item(item_id):
    """Delete a menu item."""
    validate_id(item_id, "Menu item ID")
    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM menu_items WHERE id = ?",
            (item_id,),
        )
        connection.commit()
        return cursor.rowcount > 0

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
