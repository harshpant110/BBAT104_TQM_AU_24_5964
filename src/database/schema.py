import sqlite3

from database.connection import get_connection


def initialize_database():
    """Create application tables if they do not already exist."""
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
                status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK (status IN ('Pending', 'Completed')),
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

            CREATE TRIGGER IF NOT EXISTS orders_status_insert_guard
            BEFORE INSERT ON orders
            WHEN NEW.status NOT IN ('Pending', 'Completed')
            BEGIN
                SELECT RAISE(ABORT, 'Invalid order status');
            END;

            CREATE TRIGGER IF NOT EXISTS orders_status_update_guard
            BEFORE UPDATE OF status ON orders
            WHEN NEW.status NOT IN ('Pending', 'Completed')
            BEGIN
                SELECT RAISE(ABORT, 'Invalid order status');
            END;
            """
        )
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
