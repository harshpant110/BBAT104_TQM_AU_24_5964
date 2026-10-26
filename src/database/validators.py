import math


def validate_menu_price(price):
    """Ensure a menu item's price is a finite number greater than zero."""
    if isinstance(price, bool):
        raise ValueError("Price must be a valid number.")

    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValueError("Price must be a valid number.") from None

    if not math.isfinite(price) or price <= 0:
        raise ValueError("Price must be greater than zero.")

    return price


def validate_customer_name(name):
    """Ensure a customer's name is not empty."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Customer name is required.")

    return name.strip()


def validate_quantity(quantity):
    """Validate an order-item quantity as a positive integer."""
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Quantity must be a positive whole number.")

    if quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")

    return quantity


def validate_money(amount, field_name="Amount"):
    """Validate a finite, non-negative monetary amount and round to two decimals."""
    if isinstance(amount, bool):
        raise ValueError(f"{field_name} must be a valid number.")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number.") from None

    if not math.isfinite(amount) or amount < 0:
        raise ValueError(
            f"{field_name} must be a finite, non-negative number."
        )

    return round(amount, 2)
