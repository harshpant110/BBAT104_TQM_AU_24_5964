import unittest
from unittest.mock import patch

from test_database_integrity import IsolatedDatabaseTestCase
from database import customers, menu, orders, reports


class CustomerRegressionTests(IsolatedDatabaseTestCase):
    def test_customer_crud_and_optional_text(self):
        customers.add_customer("  Asha  ", " 98765 ", " asha@example.com ")
        customer_id = self.keepalive.execute(
            "SELECT id FROM customers WHERE name = 'Asha'"
        ).fetchone()[0]
        record = next(c for c in customers.get_customers() if c[0] == customer_id)
        self.assertEqual(record[1:], ("Asha", "98765", "asha@example.com"))

        self.assertTrue(
            customers.update_customer(customer_id, "Asha Sharma", None, " ")
        )
        record = next(c for c in customers.get_customers() if c[0] == customer_id)
        self.assertEqual(record[1], "Asha Sharma")
        self.assertIsNone(record[2])
        self.assertIsNone(record[3])

        with self.assertRaises(ValueError):
            customers.update_customer(customer_id, "Asha", 123, None)

        self.assertTrue(customers.delete_customer(customer_id))
        self.assertFalse(customers.delete_customer(customer_id))

    def test_invalid_customer_ids_rejected(self):
        for value in (True, False, 0, -1, "1"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    customers.delete_customer(value)


class MenuRegressionTests(IsolatedDatabaseTestCase):
    def test_menu_crud_and_normalization(self):
        menu.add_menu_item("  Burger ", " Fast Food ", 100, True)
        item_id = self.keepalive.execute(
            "SELECT id FROM menu_items WHERE name = 'Burger'"
        ).fetchone()[0]

        record = next(item for item in menu.get_menu_items() if item[0] == item_id)
        self.assertEqual(record[1:], ("Burger", "Fast Food", 100.0, 1))

        self.assertTrue(menu.update_menu_item(item_id, "Pizza", "Meals", 150, False))
        record = next(item for item in menu.get_menu_items() if item[0] == item_id)
        self.assertEqual(record[1], "Pizza")
        self.assertEqual(record[4], 0)

        self.assertTrue(menu.delete_menu_item(item_id))
        self.assertFalse(menu.delete_menu_item(item_id))

    def test_invalid_menu_input_does_not_create_item(self):
        for name in ("", "  ", None, 12):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    menu.add_menu_item(name, "Meals", 100)
        self.assertEqual(menu.get_menu_items(), [])


class OrderRegressionTests(IsolatedDatabaseTestCase):
    def test_order_totals_and_completion(self):
        menu.add_menu_item("Meal", "Meals", 100)
        item_id = self.keepalive.execute(
            "SELECT id FROM menu_items WHERE name = 'Meal'"
        ).fetchone()[0]
        order_id = orders.create_order()
        orders.add_order_item(order_id, item_id, 2)
        orders.recalculate_order_totals(order_id, tax=10, discount=5)

        record = orders.get_order(order_id)
        self.assertEqual(record["order"][2], 200)
        self.assertAlmostEqual(record["order"][3], 10)
        self.assertEqual(record["order"][4], 5)
        self.assertAlmostEqual(record["order"][5], 205)

        orders.complete_order(order_id, "  Card  ")
        record = orders.get_order(order_id)
        self.assertEqual(record["order"][6], "Card")
        self.assertEqual(record["order"][7], "Completed")

        with self.assertRaises(ValueError):
            orders.complete_order(order_id, "Cash")

    def test_empty_order_cannot_be_completed(self):
        order_id = orders.create_order()
        with self.assertRaises(ValueError):
            orders.complete_order(order_id, "Cash")
        self.assertEqual(orders.get_order(order_id)["order"][7], "Pending")

    def test_invalid_quantity_does_not_change_order(self):
        menu.add_menu_item("Meal", "Meals", 100)
        item_id = self.keepalive.execute(
            "SELECT id FROM menu_items WHERE name = 'Meal'"
        ).fetchone()[0]
        order_id = orders.create_order()
        orders.add_order_item(order_id, item_id, 2)
        before = orders.get_order(order_id)["order"]

        with self.assertRaises(ValueError):
            orders.add_order_item(order_id, item_id, 0)

        after = orders.get_order(order_id)["order"]
        self.assertEqual(after[2], before[2])
        self.assertEqual(after[5], before[5])

    def test_completed_order_items_cannot_be_modified(self):
        menu.add_menu_item("Locked Meal", "Meals", 100)
        item_id = self.keepalive.execute(
            "SELECT id FROM menu_items WHERE name = 'Locked Meal'"
        ).fetchone()[0]
        order_id = orders.create_order()
        orders.add_order_item(order_id, item_id, 2)
        orders.complete_order(order_id, "Cash")

        order_item_id = self.keepalive.execute(
            "SELECT id FROM order_items WHERE order_id = ?",
            (order_id,),
        ).fetchone()[0]
        before_order = orders.get_order(order_id)["order"]
        before_quantity = self.keepalive.execute(
            "SELECT quantity FROM order_items WHERE id = ?",
            (order_item_id,),
        ).fetchone()[0]

        operations = (
            lambda: orders.add_order_item(order_id, item_id, 1),
            lambda: orders.update_order_item_quantity(order_item_id, 3),
            lambda: orders.remove_order_item(order_item_id),
        )
        for operation in operations:
            with self.subTest(operation=operation):
                with self.assertRaises(ValueError):
                    operation()

        after_order = orders.get_order(order_id)["order"]
        after_quantity = self.keepalive.execute(
            "SELECT quantity FROM order_items WHERE id = ?",
            (order_item_id,),
        ).fetchone()[0]
        self.assertEqual(after_order, before_order)
        self.assertEqual(after_quantity, before_quantity)

    def test_failed_order_item_write_rolls_back(self):
        menu.add_menu_item("Rollback Meal", "Meals", 100)
        item_id = self.keepalive.execute(
            "SELECT id FROM menu_items WHERE name = 'Rollback Meal'"
        ).fetchone()[0]
        order_id = orders.create_order()
        before = orders.get_order(order_id)["order"]

        with patch(
            "database.orders._update_order_totals",
            side_effect=TypeError("injected recalculation failure"),
        ):
            with self.assertRaises(TypeError):
                orders.add_order_item(order_id, item_id, 1)

        item_count = self.keepalive.execute(
            "SELECT COUNT(*) FROM order_items WHERE order_id = ?",
            (order_id,),
        ).fetchone()[0]
        self.assertEqual(item_count, 0)

        after = orders.get_order(order_id)["order"]
        self.assertEqual(after[2], before[2])
        self.assertEqual(after[5], before[5])

    def test_nonexistent_order_operations_are_handled_safely(self):
        nonexistent_order_id = 999999

        self.assertIsNone(orders.get_order(nonexistent_order_id))

        with self.assertRaises(ValueError):
            orders.recalculate_order_totals(nonexistent_order_id)

        with self.assertRaises(ValueError):
            orders.add_order_item(nonexistent_order_id, 1, 1)

        with self.assertRaises(ValueError):
            orders.complete_order(nonexistent_order_id, "Cash")

        with self.assertRaises(ValueError):
            orders.update_order_item_quantity(nonexistent_order_id, 1)

        with self.assertRaises(ValueError):
            orders.remove_order_item(nonexistent_order_id)

    def test_invalid_payment_is_rejected(self):
        order_id = orders.create_order()
        for payment in ("", "  ", None, 123, True):
            with self.subTest(payment=payment):
                with self.assertRaises(ValueError):
                    orders.complete_order(order_id, payment)


class ReportingRegressionTests(IsolatedDatabaseTestCase):
    def test_empty_dashboard_has_zero_counts(self):
        stats = reports.get_dashboard_stats()
        self.assertTrue(stats)
        for value in stats.values():
            if isinstance(value, (int, float)):
                self.assertEqual(value, 0)

    def test_invalid_report_day_counts_are_rejected(self):
        for days in (0, -1, True, 1.5, "7", None):
            with self.subTest(days=days):
                with self.assertRaises((ValueError, TypeError)):
                    reports.get_daily_revenue(days=days)


if __name__ == "__main__":
    unittest.main(verbosity=2)
