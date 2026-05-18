"""
Order placement logic — sits between the CLI and the raw API client.
Formats request summaries and response output for display.
"""

import logging
from typing import Any

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.validators import (
    validate_symbol, validate_side, validate_order_type,
    validate_quantity, validate_price
)

logger = logging.getLogger(__name__)


def _print_summary(label: str, data: dict[str, Any]):
    print(f"\n{'─' * 50}")
    print(f"  {label}")
    print(f"{'─' * 50}")
    for k, v in data.items():
        print(f"  {k:<20}: {v}")
    print(f"{'─' * 50}\n")


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
) -> dict | None:
    # --- Validation ---
    try:
        symbol     = validate_symbol(symbol)
        side       = validate_side(side)
        order_type = validate_order_type(order_type)
        quantity   = validate_quantity(quantity)
        price      = validate_price(price, order_type)
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        print(f"\n[ERROR] Validation failed: {exc}\n")
        return None

    # --- Print request summary ---
    request_info: dict[str, Any] = {
        "symbol": symbol, "side": side,
        "type": order_type, "quantity": quantity,
    }
    if price is not None:
        request_info["price"] = price

    _print_summary("ORDER REQUEST", request_info)
    logger.info("Order request: %s", request_info)

    # --- Call API ---
    try:
        response = client.place_order(
            symbol=symbol, side=side, order_type=order_type,
            quantity=quantity, price=price,
        )
    except BinanceClientError as exc:
        logger.error("API error: %s", exc)
        print(f"[FAILED] {exc}\n")
        return None
    except Exception as exc:
        logger.exception("Unexpected error while placing order: %s", exc)
        print(f"[FAILED] Unexpected error: {exc}\n")
        return None

    # --- Print response summary ---
    response_info: dict[str, Any] = {
        "orderId":     response.get("orderId", "N/A"),
        "status":      response.get("status", "N/A"),
        "symbol":      response.get("symbol", "N/A"),
        "side":        response.get("side", "N/A"),
        "type":        response.get("type", "N/A"),
        "executedQty": response.get("executedQty", "N/A"),
        "avgPrice":    response.get("avgPrice", "N/A"),
        "origQty":     response.get("origQty", "N/A"),
    }
    if "price" in response:
        response_info["price"] = response["price"]

    _print_summary("ORDER RESPONSE", response_info)
    logger.info("Order response: %s", response_info)
    print("[SUCCESS] Order placed successfully.\n")
    return response 
  