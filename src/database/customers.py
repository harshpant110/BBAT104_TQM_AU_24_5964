import sqlite3

from database.connection import get_connection
from database.validators import validate_customer_name


def get_customers():
    """Return all customers ordered by name."""
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, name, phone, email
            FROM customers
            ORDER BY name
            """
        ).fetchall()
    finally:
        connection.close()


def add_customer(name, phone=None, email=None):
    """Add a customer to the database."""
    name = validate_customer_name(name)
    phone = phone.strip() or None if isinstance(phone, str) else phone
    email = email.strip() or None if isinstance(email, str) else email

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO customers (name, phone, email)
            VALUES (?, ?, ?)
            """,
            (name, phone, email),
        )
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def update_customer(customer_id, name, phone=None, email=None):
    """Update an existing customer's details."""
    name = validate_customer_name(name)
    phone = phone.strip() or None if isinstance(phone, str) else phone
    email = email.strip() or None if isinstance(email, str) else email

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE customers
            SET name = ?, phone = ?, email = ?
            WHERE id = ?
            """,
            (name, phone, email, customer_id),
        )
        connection.commit()
        return cursor.rowcount > 0

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def delete_customer(customer_id):
    """Delete a customer; linked orders retain their history."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM customers WHERE id = ?",
            (customer_id,),
        )
        connection.commit()
        return cursor.rowcount > 0

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
