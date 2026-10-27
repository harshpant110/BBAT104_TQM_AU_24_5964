from database.connection import DATABASE_PATH, DATA_DIR, get_connection

from database.schema import initialize_database

from database.validators import (
    validate_menu_price,
    validate_customer_name,
    validate_quantity,
    validate_money,
)

from database.menu import (
    get_menu_items,
    add_menu_item,
    update_menu_item,
    delete_menu_item,
)

from database.customers import (
    get_customers,
    add_customer,
    update_customer,
    delete_customer,
)

from database.orders import (
    create_order,
    create_completed_order,
    get_order,
    recalculate_order_totals,
    add_order_item,
    update_order_item_quantity,
    remove_order_item,
    get_orders,
    complete_order,
)

from database.reports import (
    get_dashboard_stats,
    get_daily_revenue,
    get_popular_items,
)


__all__ = [
    "DATABASE_PATH",
    "DATA_DIR",
    "get_connection",
    "initialize_database",
    "validate_menu_price",
    "validate_customer_name",
    "validate_quantity",
    "validate_money",
    "get_menu_items",
    "add_menu_item",
    "update_menu_item",
    "delete_menu_item",
    "get_customers",
    "add_customer",
    "update_customer",
    "delete_customer",
    "create_order",
    "create_completed_order",
    "get_order",
    "recalculate_order_totals",
    "add_order_item",
    "update_order_item_quantity",
    "remove_order_item",
    "get_orders",
    "complete_order",
    "get_dashboard_stats",
    "get_daily_revenue",
]
