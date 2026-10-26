import sqlite3
import unittest
from unittest.mock import patch

from database import customers, menu, orders, reports, schema, validators


class IsolatedDatabaseTestCase(unittest.TestCase):
    """Use a shared in-memory database; never open the production database."""

    def setUp(self):
        self.db_uri = f"file:test_{id(self)}?mode=memory&cache=shared"
        self.keepalive = sqlite3.connect(self.db_uri, uri=True)
        self.keepalive.execute("PRAGMA foreign_keys = ON")

        def memory_connection():
            connection = sqlite3.connect(self.db_uri, uri=True)
            connection.execute("PRAGMA foreign_keys = ON")
            return connection

        self.connection_patches = [
            patch.object(module, "get_connection", side_effect=memory_connection)
            for module in (customers, menu, orders, reports, schema)
        ]

        for connection_patch in self.connection_patches:
            connection_patch.start()

        schema.initialize_database()

    def tearDown(self):
        for connection_patch in reversed(self.connection_patches):
            connection_patch.stop()
        self.keepalive.close()


class ValidationTests(unittest.TestCase):
    def test_positive_integer_ids_are_accepted(self):
        self.assertEqual(validators.validate_id(1), 1)
        self.assertEqual(validators.validate_id(42, "Order ID"), 42)

    def test_invalid_ids_are_rejected(self):
        for value in (0, -1, True, False, 1.5, "1", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validators.validate_id(value)

    def test_menu_text_is_trimmed(self):
        self.assertEqual(validators.validate_menu_text("  Burger  ", "Name"), "Burger")

    def test_empty_menu_text_is_rejected(self):
        for value in ("", "   ", None, 12, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validators.validate_menu_text(value, "Name")

    def test_availability_accepts_boolean_and_integer_flags(self):
        for value, expected in ((True, 1), (False, 0), (1, 1), (0, 0)):
            with self.subTest(value=value):
                self.assertEqual(validators.validate_availability(value), expected)

    def test_invalid_availability_is_rejected(self):
        for value in (2, -1, "1", 1.0, None, []):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validators.validate_availability(value)


class SchemaIntegrityTests(IsolatedDatabaseTestCase):
    def test_invalid_order_status_is_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.keepalive.execute(
                "INSERT INTO orders (status) VALUES (?)",
                ("Cancelled",),
            )

    def test_valid_order_statuses_are_accepted(self):
        for status in ("Pending", "Completed"):
            with self.subTest(status=status):
                self.keepalive.execute(
                    "INSERT INTO orders (status) VALUES (?)",
                    (status,),
                )

    def test_foreign_keys_are_enforced(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.keepalive.execute(
                """
                INSERT INTO order_items
                    (order_id, menu_item_id, quantity, unit_price)
                VALUES (999, 999, 1, 10.0)
                """
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
