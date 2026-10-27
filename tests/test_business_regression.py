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
    def test_atomic_multi_item_order_completes_successfully(self):
        menu.add_menu_item("Meal One", "Meals", 100)
        menu.add_menu_item("Meal Two", "Meals", 50)
        menu_ids = dict(
            self.keepalive.execute(
                "SELECT name, id FROM menu_items"
            ).fetchall()
        )

        order_id, totals = orders.create_completed_order(
            None,
            (
                item
                for item in (
                    (menu_ids["Meal One"], 2),
                    (menu_ids["Meal Two"], 3),
                )
            ),
            tax=10,
            discount=5,
            payment_method="  Card  ",
        )

        record = orders.get_order(order_id)
        self.assertEqual(record["order"][2:8], (350.0, 10.0, 5.0, 355.0, "Card", "Completed"))
        self.assertEqual(len(record["items"]), 2)
        self.assertEqual(totals, {
            "subtotal": 350.0,
            "tax": 10.0,
            "discount": 5.0,
            "total": 355.0,
        })

    def test_empty_item_generator_does_not_create_order(self):
        with self.assertRaises(ValueError):
            orders.create_completed_order(
                None,
                (item for item in ()),
                tax=0,
                discount=0,
                payment_method="Cash",
            )

        self.assertEqual(
            self.keepalive.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            0,
        )
        self.assertEqual(
            self.keepalive.execute("SELECT COUNT(*) FROM order_items").fetchone()[0],
            0,
        )

    def test_atomic_order_rolls_back_when_second_item_fails(self):
        menu.add_menu_item("Meal One", "Meals", 100)
        menu.add_menu_item("Meal Two", "Meals", 50)
        menu_ids = dict(
            self.keepalive.execute(
                "SELECT name, id FROM menu_items"
            ).fetchall()
        )
        original_insert = orders._insert_order_item
        insert_count = 0

        def fail_on_second_insert(connection, order_id, menu_item_id, quantity):
            nonlocal insert_count
            insert_count += 1
            if insert_count == 2:
                raise RuntimeError("injected second item failure")
            return original_insert(connection, order_id, menu_item_id, quantity)

        with patch(
            "database.orders._insert_order_item",
            side_effect=fail_on_second_insert,
        ):
            with self.assertRaises(RuntimeError):
                orders.create_completed_order(
                    None,
                    [
                        (menu_ids["Meal One"], 1),
                        (menu_ids["Meal Two"], 1),
                    ],
                    tax=0,
                    discount=0,
                    payment_method="Cash",
                )

        self.assertEqual(insert_count, 2)
        self.assertEqual(
            self.keepalive.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            0,
        )
        self.assertEqual(
            self.keepalive.execute("SELECT COUNT(*) FROM order_items").fetchone()[0],
            0,
        )

    def test_atomic_order_rolls_back_when_totals_calculation_fails(self):
        menu.add_menu_item("Totals Failure Meal", "Meals", 100)
        item_id = self.keepalive.execute(
            "SELECT id FROM menu_items WHERE name = 'Totals Failure Meal'"
        ).fetchone()[0]

        with patch(
            "database.orders._update_order_totals",
            side_effect=RuntimeError("injected totals calculation failure"),
        ):
            with self.assertRaisesRegex(
                RuntimeError, "injected totals calculation failure"
            ):
                orders.create_completed_order(
                    None,
                    [(item_id, 1)],
                    tax=0,
                    discount=0,
                    payment_method="Cash",
                )

        self.assertEqual(
            self.keepalive.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            0,
        )
        self.assertEqual(
            self.keepalive.execute(
                "SELECT COUNT(*) FROM order_items"
            ).fetchone()[0],
            0,
        )

    def test_atomic_order_rolls_back_when_completion_update_fails(self):
        menu.add_menu_item("Completion Failure Meal", "Meals", 100)
        item_id = self.keepalive.execute(
            "SELECT id FROM menu_items WHERE name = 'Completion Failure Meal'"
        ).fetchone()[0]

        original_get_connection = orders.get_connection

        class CompletionFailureConnection:
            def __init__(self, connection):
                self.connection = connection

            def execute(self, sql, parameters=()):
                if "SET payment_method = ?, status = 'Completed'" in sql:
                    raise RuntimeError("injected completion update failure")
                return self.connection.execute(sql, parameters)

            def commit(self):
                return self.connection.commit()

            def rollback(self):
                return self.connection.rollback()

            def close(self):
                return self.connection.close()

        def get_wrapped_connection():
            return CompletionFailureConnection(original_get_connection())

        with patch(
            "database.orders.get_connection",
            side_effect=get_wrapped_connection,
        ):
            with self.assertRaisesRegex(
                RuntimeError, "injected completion update failure"
            ):
                orders.create_completed_order(
                    None,
                    [(item_id, 1)],
                    tax=0,
                    discount=0,
                    payment_method="Cash",
                )

        self.assertEqual(
            self.keepalive.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            0,
        )
        self.assertEqual(
            self.keepalive.execute(
                "SELECT COUNT(*) FROM order_items"
            ).fetchone()[0],
            0,
        )

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

    def test_daily_revenue_counts_only_completed_orders(self):
        self.keepalive.execute(
            """
            INSERT INTO orders (subtotal, total, status, created_at)
            VALUES
                (100, 100, 'Completed', DATE('now')),
                (50, 50, 'Pending', DATE('now')),
                (75, 75, 'Completed', DATE('now', '-10 days'))
            """
        )
        self.keepalive.commit()

        revenue = reports.get_daily_revenue(days=7)

        self.assertEqual(len(revenue), 1)
        self.assertEqual(revenue[0][1], 100.0)

    def test_popular_items_are_ranked_by_quantity_sold(self):
        self.keepalive.execute(
            """
            INSERT INTO menu_items (name, category, price, available)
            VALUES
                ('Paneer', 'Main Course', 180, 1),
                ('Burger', 'Fast Food', 120, 1),
                ('Pizza', 'Fast Food', 250, 1)
            """
        )
        self.keepalive.execute(
            "INSERT INTO orders (subtotal, total) VALUES (1000, 1000)"
        )
        order_id = self.keepalive.execute(
            "SELECT id FROM orders"
        ).fetchone()[0]
        menu_ids = dict(
            self.keepalive.execute(
                "SELECT name, id FROM menu_items"
            ).fetchall()
        )

        self.keepalive.executemany(
            """
            INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
            """,
            [
                (order_id, menu_ids["Paneer"], 2, 180),
                (order_id, menu_ids["Burger"], 5, 120),
                (order_id, menu_ids["Pizza"], 3, 250),
            ],
        )
        self.keepalive.commit()

        self.assertEqual(
            reports.get_popular_items(),
            [("Burger", 5), ("Pizza", 3), ("Paneer", 2)],
        )

    def test_popular_items_respect_limit(self):
        self.keepalive.execute(
            """
            INSERT INTO menu_items (name, category, price, available)
            VALUES ('A', 'Test', 10, 1), ('B', 'Test', 10, 1),
                   ('C', 'Test', 10, 1)
            """
        )
        self.keepalive.execute(
            "INSERT INTO orders (subtotal, total) VALUES (30, 30)"
        )
        order_id = self.keepalive.execute(
            "SELECT id FROM orders"
        ).fetchone()[0]
        menu_ids = self.keepalive.execute(
            "SELECT id FROM menu_items ORDER BY name"
        ).fetchall()

        self.keepalive.executemany(
            """
            INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price)
            VALUES (?, ?, 1, 10)
            """,
            [(order_id, row[0]) for row in menu_ids],
        )
        self.keepalive.commit()

        self.assertEqual(len(reports.get_popular_items(limit=2)), 2)

    def test_popular_items_empty_result(self):
        self.assertEqual(reports.get_popular_items(), [])

    def test_invalid_popular_item_limits_are_rejected(self):
        for limit in (0, -1, True, 1.5, "5", None):
            with self.subTest(limit=limit):
                with self.assertRaises((ValueError, TypeError)):
                    reports.get_popular_items(limit=limit)



if __name__ == "__main__":
    unittest.main(verbosity=2)

    def test_daily_revenue_counts_only_completed_orders(self):
        self.keepalive.execute(
            """
            INSERT INTO orders (subtotal, total, status, created_at)
            VALUES
                (100, 100, 'Completed', DATE('now')),
                (50, 50, 'Pending', DATE('now')),
                (75, 75, 'Completed', DATE('now', '-10 days'))
            """
        )
        self.keepalive.commit()

        revenue = reports.get_daily_revenue(days=7)

        self.assertEqual(len(revenue), 1)
        self.assertEqual(revenue[0][1], 100.0)


class OrderQueryRegressionTests(IsolatedDatabaseTestCase):
    def test_get_orders_includes_customer_names_and_orders_newest_first(self):
        customers.add_customer("Asha")
        customer_id = self.keepalive.execute(
            "SELECT id FROM customers WHERE name = 'Asha'"
        ).fetchone()[0]

        self.keepalive.execute(
            """
            INSERT INTO orders (customer_id, total, status, created_at)
            VALUES
                (?, 100, 'Completed', '2026-01-01 10:00:00'),
                (NULL, 50, 'Pending', '2026-01-02 10:00:00')
            """,
            (customer_id,),
        )
        self.keepalive.commit()

        result = orders.get_orders()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][2], None)
        self.assertEqual(result[0][6], 50.0)
        self.assertEqual(result[1][2], "Asha")
        self.assertEqual(result[1][6], 100.0)


class SchemaInitializationRegressionTests(IsolatedDatabaseTestCase):
    def test_database_initialization_is_idempotent(self):
        customers.add_customer("Existing Customer")
        before = self.keepalive.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        from database import schema
        schema.initialize_database()
        schema.initialize_database()

        after = self.keepalive.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        self.assertEqual(before, 1)
        self.assertEqual(after, 1)

        tables = {
            row[0]
            for row in self.keepalive.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        self.assertTrue(
            {"customers", "menu_items", "orders", "order_items"}.issubset(tables)
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
