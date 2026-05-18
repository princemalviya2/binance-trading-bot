# Binance Futures Testnet Trading Bot

## Features
- Supports BUY and SELL orders
- Supports MARKET and LIMIT orders
- Input validation
- Logging and error handling
- Binance Futures Testnet integration

## Setup

Install dependencies:
pip install -r requirements.txt

Create .env file:

BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

## Example Commands

Market order:
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

Limit order:
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 90000