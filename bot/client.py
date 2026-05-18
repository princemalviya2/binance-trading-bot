"""
Binance Futures Testnet API client wrapper.
Handles authentication, request signing, and raw HTTP communication.
"""

import time
import hmac
import hashlib
import logging
import httpx
from urllib.parse import urlencode
from typing import Any

logger = logging.getLogger(__name__)

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error [{code}]: {message}")


class BinanceFuturesClient:
    """
    Thin client for Binance Futures Testnet REST API.
    Separates authentication / transport concerns from order logic.
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=10.0,
        )
        logger.debug("BinanceFuturesClient initialised (base_url=%s)", self.base_url)

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: httpx.Response) -> Any:
        logger.debug("HTTP %s %s -> %d", response.request.method, response.url, response.status_code)
        try:
            data = response.json()
        except Exception:
            response.raise_for_status()
            raise

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceClientError(data["code"], data.get("msg", "Unknown error"))

        if not response.is_success:
            response.raise_for_status()

        return data

    def get_exchange_info(self) -> dict:
        resp = self._http.get("/fapi/v1/exchangeInfo")
        return self._handle_response(resp)

    def get_account(self) -> dict:
        params = self._sign({})
        resp = self._http.get("/fapi/v2/account", params=params)
        return self._handle_response(resp)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        time_in_force: str = "GTC",
    ) -> dict:
        params: dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
        }

        if order_type.upper() == "LIMIT":
            if price is None:
                raise ValueError("price is required for LIMIT orders")
            params["price"] = price
            params["timeInForce"] = time_in_force

        params = self._sign(params)

        logger.info(
            "Placing order: symbol=%s side=%s type=%s qty=%s price=%s",
            params["symbol"], params["side"], params["type"], quantity, price,
        )

        resp = self._http.post("/fapi/v1/order", data=params)
        result = self._handle_response(resp)
        logger.info("Order accepted: orderId=%s status=%s", result.get("orderId"), result.get("status"))
        return result

    def get_order(self, symbol: str, order_id: int) -> dict:
        params = self._sign({"symbol": symbol.upper(), "orderId": order_id})
        resp = self._http.get("/fapi/v1/order", params=params)
        return self._handle_response(resp)

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()