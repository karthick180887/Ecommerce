import unittest
from flask import session
from app import app, get_db_connection

class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.test_request_context():
            # Clear the session after each test within a request context
            session.clear()

    def test_search_functionality(self):
        # Populate the database with test data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, price) VALUES ('Test Product', 10.0)")
        conn.commit()
        cur.close()
        conn.close()

        response = self.client.post('/search', data={'keyword': 'Test Product'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product', response.data)

    def test_add_to_cart(self):
        # Populate the database with test data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, price) VALUES ('Test Product', 10.0) RETURNING id")
        product_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        response = self.client.post(f'/add_to_cart/{product_id}')
        self.assertEqual(response.status_code, 302)  # Should redirect to the cart page

        with self.client.session_transaction() as sess:
            self.assertIn('cart', sess)
            self.assertEqual(len(sess['cart']), 1)
            self.assertEqual(sess['cart'][0]['name'], 'Test Product')
            self.assertEqual(sess['cart'][0]['price'], 10.0)

    def test_cart_total_price(self):
        # Populate the database with test data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, price) VALUES ('Test Product', 10.0) RETURNING id")
        product_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        self.client.post(f'/add_to_cart/{product_id}')

        response = self.client.get('/cart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Total: $10.0', response.data)

    def test_checkout_process(self):
        # Populate the database with test data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, price) VALUES ('Test Product', 10.0) RETURNING id")
        product_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        self.client.post(f'/add_to_cart/{product_id}')

        response = self.client.post('/checkout', data={
            'shipping_info': '123 Test St',
            'payment_info': '4111111111111111'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect to the index page

        with self.client.session_transaction() as sess:
            self.assertNotIn('cart', sess)  # Cart should be cleared after checkout

if __name__ == '__main__':
    unittest.main()
