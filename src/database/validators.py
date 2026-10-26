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


def validate_id(value, field_name="ID"):
    """Ensure a database ID is a positive integer, excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")

    return value


def validate_menu_text(value, field_name):
    """Ensure menu text fields are non-empty strings."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required.")

    return value.strip()


def validate_availability(value):
    """Accept only booleans or integer 0/1 for availability."""
    if isinstance(value, bool):
        return int(value)

    if type(value) is int and value in (0, 1):
        return value

    raise ValueError("Availability must be True, False, 0, or 1.")
