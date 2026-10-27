from database.connection import get_connection


def get_dashboard_stats():
    """Return summary statistics for the restaurant dashboard."""
    connection = get_connection()

    try:
        order_stats = connection.execute(
            """
            SELECT
                COUNT(*) AS total_orders,
                COALESCE(SUM(
                    CASE WHEN status = 'Completed' THEN 1 ELSE 0 END
                ), 0) AS completed_orders,
                COALESCE(SUM(
                    CASE WHEN status = 'Pending' THEN 1 ELSE 0 END
                ), 0) AS pending_orders,
                COALESCE(SUM(
                    CASE WHEN status = 'Completed' THEN total ELSE 0 END
                ), 0) AS completed_revenue
            FROM orders
            """
        ).fetchone()

        menu_count = connection.execute(
            "SELECT COUNT(*) FROM menu_items"
        ).fetchone()[0]

        customer_count = connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        return {
            "total_orders": order_stats[0],
            "completed_orders": order_stats[1],
            "pending_orders": order_stats[2],
            "completed_revenue": round(order_stats[3], 2),
            "menu_items": menu_count,
            "customers": customer_count,
        }

    finally:
        connection.close()


def get_daily_revenue(days=7):
    """Return daily revenue from completed orders for the requested period."""
    if isinstance(days, bool) or not isinstance(days, int) or days < 1:
        raise ValueError("Days must be a positive whole number.")

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                DATE(created_at) AS order_date,
                ROUND(SUM(total), 2) AS revenue
            FROM orders
            WHERE status = 'Completed'
              AND DATE(created_at) >= DATE('now', ?)
            GROUP BY DATE(created_at)
            ORDER BY order_date
            """,
            (f"-{days - 1} days",),
        ).fetchall()

    finally:
        connection.close()


def get_popular_items(limit=5):
    """Return menu items ranked by total quantity sold."""
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("Limit must be a positive whole number.")

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                m.name,
                SUM(oi.quantity) AS quantity_sold
            FROM order_items AS oi
            JOIN menu_items AS m ON m.id = oi.menu_item_id
            GROUP BY m.id, m.name
            ORDER BY quantity_sold DESC, m.name COLLATE NOCASE ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    finally:
        connection.close()
