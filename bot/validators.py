"""
Input validation helpers for CLI arguments.
All validation errors raise ValueError with a human-readable message.
"""

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
VALID_STOP_TYPES = {"STOP_MARKET", "STOP"}


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValueError(f"Invalid symbol '{symbol}'. Use alphanumeric characters only, e.g. BTCUSDT.")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    all_valid = VALID_ORDER_TYPES | VALID_STOP_TYPES
    if order_type not in all_valid:
        raise ValueError(f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(all_valid))}.")
    return order_type


def validate_quantity(quantity: str | float) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be > 0, got {qty}.")
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    if order_type.upper() in {"LIMIT", "STOP"}:
        if price is None:
            raise ValueError(f"--price is required for {order_type} orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
        if p <= 0:
            raise ValueError(f"Price must be > 0, got {p}.")
        return p
    return None