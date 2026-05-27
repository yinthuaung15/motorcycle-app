from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from functools import wraps
from config import Config
from models import motorcycle_db, order_db
from datetime import datetime

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Simple login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ===== AUTH =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            user = User(1)
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ===== ADMIN PANEL =====
@app.route('/admin')
@login_required
def admin_dashboard():
    bikes = motorcycle_db.get_all()
    orders = order_db.get_all()
    
    total_bikes = len(bikes)
    total_stock = sum(b['stock'] for b in bikes)
    total_orders = len(orders)
    total_revenue = sum(o['total'] for o in orders if o['status'] == 'confirmed')
    
    return render_template('admin.html',
        bikes=bikes,
        orders=orders,
        total_bikes=total_bikes,
        total_stock=total_stock,
        total_orders=total_orders,
        total_revenue=total_revenue
    )

# ===== API ENDPOINTS =====
@app.route('/api/bikes', methods=['GET'])
def api_get_bikes():
    bikes = motorcycle_db.get_all()
    return jsonify(bikes)

@app.route('/api/bikes/<int:bike_id>', methods=['GET'])
def api_get_bike(bike_id):
    bike = motorcycle_db.get_by_id(bike_id)
    if bike:
        return jsonify(bike)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/bikes', methods=['POST'])
@login_required
def api_add_bike():
    data = request.json
    bike = motorcycle_db.add(data)
    return jsonify(bike)

@app.route('/api/bikes/<int:bike_id>', methods=['PUT'])
@login_required
def api_update_bike(bike_id):
    data = request.json
    bike = motorcycle_db.update(bike_id, data)
    if bike:
        return jsonify(bike)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/bikes/<int:bike_id>', methods=['DELETE'])
@login_required
def api_delete_bike(bike_id):
    motorcycle_db.delete(bike_id)
    return jsonify({'success': True})

@app.route('/api/bikes/<int:bike_id>/stock', methods=['POST'])
@login_required
def api_update_stock(bike_id):
    data = request.json
    quantity = data.get('quantity', 0)
    operation = data.get('operation', 'add')
    
    new_stock = motorcycle_db.update_stock(bike_id, quantity, operation)
    if new_stock is not None:
        return jsonify({'stock': new_stock})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    orders = order_db.get_all()
    return jsonify(orders)

@app.route('/api/orders/<int:order_id>/status', methods=['POST'])
@login_required
def api_update_order_status(order_id):
    data = request.json
    status = data.get('status', 'pending')
    order = order_db.update_status(order_id, status)
    if order:
        return jsonify(order)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/stats', methods=['GET'])
@login_required
def api_get_stats():
    bikes = motorcycle_db.get_all()
    orders = order_db.get_all()
    
    return jsonify({
        'total_bikes': len(bikes),
        'total_stock': sum(b['stock'] for b in bikes),
        'total_orders': len(orders),
        'total_revenue': sum(o['total'] for o in orders if o['status'] == 'confirmed'),
        'out_of_stock': len([b for b in bikes if b['stock'] == 0]),
        'low_stock': len([b for b in bikes if 0 < b['stock'] <= 5])
    })

# ===== MINI APP =====
@app.route('/')
def mini_app():
    """Telegram Mini App"""
    bikes = motorcycle_db.get_available()
    return render_template('mini_app.html', bikes=bikes, shop_name=Config.SHOP_NAME)

@app.route('/api/mini-app/bikes')
def api_mini_app_bikes():
    """API for Mini App"""
    bikes = motorcycle_db.get_available()
    return jsonify(bikes)

@app.route('/api/mini-app/order', methods=['POST'])
def api_mini_app_order():
    """Create order from Mini App"""
    data = request.json
    
    bike = motorcycle_db.get_by_id(data['bike_id'])
    if not bike or bike['stock'] <= 0:
        return jsonify({'error': 'Out of stock'}), 400
    
    # Reduce stock
    motorcycle_db.update_stock(data['bike_id'], 1, 'remove')
    
    # Create order
    order = {
        'user_id': data.get('user_id', 0),
        'user_name': data.get('user_name', 'Mini App User'),
        'username': data.get('username', ''),
        'bike_id': bike['id'],
        'brand': bike['brand'],
        'model': bike['model'],
        'price': bike['price'],
        'quantity': 1,
        'total': bike['price'],
        'payment_method': data.get('payment', 'Cash'),
        'customer_name': data.get('name', ''),
        'phone': data.get('phone', ''),
        'address': data.get('address', ''),
        'status': 'confirmed'
    }
    
    order_record = order_db.add(order)
    return jsonify({'success': True, 'order_id': order_record['id']})

# ===== MAIN =====
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)