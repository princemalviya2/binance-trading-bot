#!/usr/bin/env python3
"""
cli.py — CLI entry point for the Binance Futures Testnet trading bot.

Usage examples:
  python cli.py place --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.001
  python cli.py place --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.001 --price 60000
  python cli.py place --symbol ETHUSDT --side BUY  --type STOP_MARKET --quantity 0.01
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.orders import place_order

load_dotenv()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet — simplified trading bot",
    )
    parser.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    place_p = subparsers.add_parser("place", help="Place a new futures order")
    place_p.add_argument("--symbol",     required=True, help="Trading pair, e.g. BTCUSDT")
    place_p.add_argument("--side",       required=True, choices=["BUY", "SELL"], type=str.upper)
    place_p.add_argument("--type",       dest="order_type", required=True,
                         choices=["MARKET", "LIMIT", "STOP_MARKET", "STOP"], type=str.upper)
    place_p.add_argument("--quantity",   required=True, type=float)
    place_p.add_argument("--price",      type=float, default=None,
                         help="Required for LIMIT / STOP orders")
    place_p.add_argument("--stop-price", type=float, default=None, dest="stop_price",
                         help="Trigger price for STOP_MARKET / STOP orders")

    return parser


def get_credentials() -> tuple[str, str]:
    api_key    = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    missing = [n for n, v in [("BINANCE_API_KEY", api_key), ("BINANCE_API_SECRET", api_secret)] if not v]
    if missing:
        print(
            f"\n[ERROR] Missing environment variable(s): {', '.join(missing)}\n"
            "Set them in your shell or in a .env file:\n"
            "  BINANCE_API_KEY=your_key\n"
            "  BINANCE_API_SECRET=your_secret\n"
        )
        sys.exit(1)

    return api_key, api_secret


def cmd_place(args: argparse.Namespace, client: BinanceFuturesClient) -> int:
    result = place_order(
        client=client,
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
    )
    return 0 if result is not None else 1


def main() -> int:
    parser = build_parser()
    args   = parser.parse_args()

    setup_logging(args.log_level)

    api_key, api_secret = get_credentials()

    with BinanceFuturesClient(api_key=api_key, api_secret=api_secret) as client:
        if args.command == "place":
            return cmd_place(args, client)

    return 0


if __name__ == "__main__":
    sys.exit(main())