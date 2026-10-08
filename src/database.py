import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "restaurant.db"


def get_connection():
    """Create and return a connection to the SQLite database."""
    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """Create the initial database tables if they do not exist."""
    connection = get_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                available INTEGER NOT NULL DEFAULT 1
                    CHECK (available IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                subtotal REAL NOT NULL DEFAULT 0 CHECK (subtotal >= 0),
                tax REAL NOT NULL DEFAULT 0 CHECK (tax >= 0),
                discount REAL NOT NULL DEFAULT 0 CHECK (discount >= 0),
                total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
                payment_method TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price REAL NOT NULL CHECK (unit_price >= 0),
                FOREIGN KEY (order_id) REFERENCES orders(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
                    ON DELETE RESTRICT
            );
            """
        )

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_menu_items():
    """Return all menu items."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            SELECT id, name, category, price, available
            FROM menu_items
            ORDER BY name
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def add_menu_item(name, category, price, available=True):
    """Add a new menu item."""
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO menu_items (name, category, price, available)
            VALUES (?, ?, ?, ?)
            """,
            (name, category, price, int(available)),
        )

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def update_menu_item(item_id, name, category, price, available):
    """Update an existing menu item."""
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE menu_items
            SET name = ?, category = ?, price = ?, available = ?
            WHERE id = ?
            """,
            (name, category, price, int(available), item_id),
        )

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def delete_menu_item(item_id):
    """Delete a menu item."""
    connection = get_connection()

    try:
        connection.execute(
            """
            DELETE FROM menu_items
            WHERE id = ?
            """,
            (item_id,),
        )

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()