from flask import Flask, request, redirect, url_for, render_template, session
import psycopg2

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'
    return app

app = create_app()

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        port = 5433,
        user="postgres",
        password="root"
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM products WHERE name ILIKE %s', ('%' + keyword + '%',))
        products = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('search.html', products=products)
    return render_template('search.html')

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cur.fetchone()
    cur.close()
    conn.close()

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        'id': product[0],
        'name': product[1],
        'price': float(product[2])  # Ensure the price is a float
    })
    session.modified = True

    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    print(f"Cart items: {cart_items}")  # Debugging line
    try:
        total_price = sum(float(item['price']) for item in cart_items)  # Calculate total price as a float
        print(f"Total price: {total_price}")  # Debugging line
    except Exception as e:
        print(f"Error calculating total price: {e}")  # Debugging line
        total_price = 0.0
    return render_template('cart.html', cart=cart_items, total=total_price)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        shipping_info = request.form['shipping_info']
        payment_info = request.form['payment_info']
        # Process checkout logic here (e.g., save to database, send email, etc.)
        session.pop('cart', None)  # Clear the cart
        return redirect(url_for('index'))
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(debug=True)
