from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE_FILE = 'stocks.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    stocks = conn.execute('SELECT * FROM stocks').fetchall()
    conn.close()
    return render_template('index.html', stocks=stocks)

@app.route('/add', methods=['POST'])
def add_stock():
    ticker = request.form['ticker'].upper()
    condition = request.form['condition']
    price = request.form['price']

    if not ticker or not condition or not price:
        return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO stocks (ticker, condition_type, target_price) VALUES (?, ?, ?)'
            ' ON CONFLICT(ticker) DO UPDATE SET condition_type=excluded.condition_type, target_price=excluded.target_price',
            (ticker, condition, float(price))
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"שגיאת בסיס נתונים: {e}")
    finally:
        conn.close()
        
    return redirect(url_for('index'))

@app.route('/delete/<int:stock_id>')
def delete_stock(stock_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM stocks WHERE id = ?', (stock_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)