import yfinance as yf
import time
import sys
import sqlite3
import telegram

TELEGRAM_BOT_TOKEN = 'העתק-והדבק-כאן-את-הטוקן-שלך' 
TELEGRAM_CHAT_ID = 'העתק-והדבק-כאן-את-ה-ID-שלך'
DATABASE_FILE = 'stocks.db'
CHECK_INTERVAL_SECONDS = 60
notified_stocks = set()

def send_telegram_message(message):
    if TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE' or TELEGRAM_CHAT_ID == 'YOUR_TELEGRAM_CHAT_ID_HERE':
        print("!!! WARNING: Telegram bot details are not set in checker.py. Skipping notification.")
        return
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print(f"Telegram message sent: {message}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def get_stocks_to_track():
    stocks = []
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stocks')
        rows = cursor.fetchall()
        for row in rows:
            stocks.append(dict(row))
        conn.close()
    except Exception as e:
        print(f"Error reading from database: {e}")
    return stocks

def get_stock_price(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        price_data = stock.history(period='1d')
        if price_data.empty:
            print(f"No data found for ticker '{ticker_symbol}'.")
            return None
        return price_data['Close'].iloc[-1]
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None

def main_loop():
    print("--- Stock checker started in the background (with Telegram notifications) ---")
    
    while True:
        print(f"\n--- Starting new check ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---")
        stocks_to_check = get_stocks_to_track()

        if not stocks_to_check:
            print("No stocks to track in the database.")
        
        for stock in stocks_to_check:
            ticker = stock['ticker']
            
            if ticker in notified_stocks:
                continue

            current_price = get_stock_price(ticker)
            if current_price is None:
                continue

            target_price = stock['target_price']
            alert_type = stock['condition_type']
            
            print(f"Checking {ticker}: Current price = ${current_price:.2f}, Target = {alert_type} ${target_price:.2f}")

            alert_triggered = False
            if alert_type == 'above' and current_price > target_price:
                alert_triggered = True
            elif alert_type == 'below' and current_price < target_price:
                alert_triggered = True

            if alert_triggered:
                message = f"🔔 Stock Alert: {ticker} 🔔\nThe price has reached ${current_price:.2f} (Your target was {alert_type} ${target_price:.2f})"
                send_telegram_message(message)
                notified_stocks.add(ticker)
        
        print(f"--- Check finished. Waiting for {CHECK_INTERVAL_SECONDS} seconds. ---")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n--- Stopping the stock checker. ---")
        sys.exit(0)