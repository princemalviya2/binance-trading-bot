from binance.client import Client
from config import API_KEY, API_SECRET

client = Client(
    API_KEY,
    API_SECRET,
    testnet=True
)

try:
    account = client.futures_account()
    print("Connected successfully")
except Exception as e:
    print("Error:", e)