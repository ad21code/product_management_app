from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app
from .models import Product, Order, db
import stripe

main = Blueprint('main', __name__)

# --- HELPERS ---
def get_cart_items():
    """Retrieve product objects based on IDs in session cart."""
    cart = session.get('cart', {})
    if not cart:
        return []
    
    # Fetch products that are in the cart
    products = Product.query.filter(Product.id.in_(cart.keys())).all()
    items = []
    
    for p in products:
        quantity = cart[str(p.id)]
        items.append({
            'product': p, 
            'quantity': quantity, 
            'total': round(p.price * quantity, 2)
        })
    return items

# --- PUBLIC ROUTES ---

@main.route('/')
def index():
    """Home page: Lists all products."""
    products = Product.query.all()
    cart_size = sum(session.get('cart', {}).values())
    return render_template('index.html', products=products, cart_size=cart_size)

@main.route('/cart')
def view_cart():
    """Cart page: Shows items and grand total."""
    items = get_cart_items()
    grand_total = sum(item['total'] for item in items)
    return render_template('cart.html', items=items, grand_total=round(grand_total, 2))

@main.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    """Simple route to add item from Home Page."""
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    session.modified = True
    return redirect(url_for('main.index'))

@main.route('/clear_cart')
def clear_cart():
    """Empties the cart."""
    session.pop('cart', None)
    return redirect(url_for('main.view_cart'))

# --- ADMIN ROUTES ---

@main.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    """Admin page to add new items to the database."""
    if request.method == 'POST':
        title = request.form.get('title')
        image_url = request.form.get('image_url')
        price = request.form.get('price')
        
        if title and image_url and price:
            new_product = Product(
                title=title, 
                image_url=image_url, 
                price=float(price)
            )
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('main.index'))
            
    return render_template('add_product.html')

@main.route('/admin/transactions')
def view_transactions():
    """Admin page to view all successful orders."""
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    return render_template('transactions.html', transactions=orders)

# --- API (AJAX) ROUTES ---

@main.route('/api/update_cart', methods=['POST'])
def update_cart_api():
    """Handles + and - clicks without reloading the page."""
    data = request.get_json()
    product_id = str(data.get('product_id'))
    action = data.get('action') # 'increase' or 'decrease'
    
    if 'cart' not in session:
        return jsonify({'error': 'No cart'}), 400

    cart = session['cart']
    
    if product_id in cart:
        if action == 'increase':
            cart[product_id] += 1
        elif action == 'decrease':
            cart[product_id] -= 1
            if cart[product_id] <= 0:
                del cart[product_id]
    
    session.modified = True
    
    # Recalculate totals for the response
    cart_count = sum(cart.values())
    
    products = Product.query.filter(Product.id.in_(cart.keys())).all()
    grand_total = 0
    item_total = 0
    
    for p in products:
        qty = cart.get(str(p.id), 0) # Safety .get
        grand_total += p.price * qty
        if str(p.id) == product_id:
            item_total = p.price * qty

    return jsonify({
        'success': True,
        'new_quantity': cart.get(product_id, 0),
        'item_total': round(item_total, 2),
        'grand_total': round(grand_total, 2),
        'cart_count': cart_count
    })

# --- STRIPE PAYMENT ROUTES ---

@main.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    items = get_cart_items()

    if not items:
        return jsonify(error="Cart is empty"), 400

    line_items = []
    for item in items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': item['product'].title},
                'unit_amount': int(item['product'].price * 100), # Cents
            },
            'quantity': item['quantity'],
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            # Redirects user back to our site after payment
            success_url=url_for('main.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.view_cart', _external=True),
        )
        return jsonify(id=checkout_session.id)
    except Exception as e:
        return jsonify(error=str(e)), 403

@main.route('/success')
def payment_success():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    session_id = request.args.get('session_id')
    
    # Verify transaction with Stripe
    try:
        sess = stripe.checkout.Session.retrieve(session_id)
        if sess.payment_status == 'paid':
            # Save Order to DB
            order = Order(
                stripe_session_id=sess.id,
                amount_total=sess.amount_total / 100,
                status='Paid'
            )
            db.session.add(order)
            db.session.commit()
            
            # Clear Cart
            session.pop('cart', None)
            return render_template('success.html')
    except Exception as e:
        print(e)
        
    return "Payment Verification Failed"