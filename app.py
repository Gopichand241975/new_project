from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'carcare_secret_key_2024'
CORS(app)

DB_PATH = 'carcare.db'

# ─── Database Setup ───────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            duration TEXT,
            icon TEXT
        );

        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            car_make TEXT NOT NULL,
            car_model TEXT NOT NULL,
            car_year TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            address TEXT NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'pending',
            payment_status TEXT DEFAULT 'unpaid',
            payment_method TEXT,
            total_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES users(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            method TEXT NOT NULL,
            transaction_id TEXT,
            status TEXT DEFAULT 'pending',
            paid_at TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            booking_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES users(id),
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        );
    ''')

    # Seed services
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        services = [
            ('Basic Service', 'Maintenance', 'Oil change, filter replacement, 20-point inspection', 1999, '2-3 hrs', 'fa-wrench'),
            ('Full Service', 'Maintenance', 'Comprehensive 50-point check, all fluids, spark plugs', 3999, '4-5 hrs', 'fa-cogs'),
            ('AC Repair', 'Repair', 'AC gas refill, compressor check, vent cleaning', 2499, '2-3 hrs', 'fa-snowflake'),
            ('Denting & Painting', 'Body Work', 'Professional dent removal and scratch-free paint job', 4999, '1-2 days', 'fa-paint-brush'),
            ('Wheel Alignment', 'Tyres', 'Computer-aided 4-wheel alignment and balancing', 999, '1 hr', 'fa-circle'),
            ('Battery Replacement', 'Electrical', 'Battery health check and replacement with warranty', 3499, '30 mins', 'fa-battery-full'),
            ('Car Wash & Spa', 'Cleaning', 'Interior & exterior deep cleaning, wax polish', 1499, '2-3 hrs', 'fa-tint'),
            ('Brake Service', 'Safety', 'Brake pad replacement, disc inspection, fluid change', 2999, '2 hrs', 'fa-stop-circle'),
            ('Engine Diagnostics', 'Diagnostics', 'Computer-aided engine fault scanning & report', 499, '1 hr', 'fa-search'),
            ('Suspension Repair', 'Repair', 'Shock absorber, spring, and linkage inspection & fix', 3999, '3-4 hrs', 'fa-car'),
            ('Windshield Repair', 'Glass', 'Chip filling, crack repair, or full replacement', 1999, '1-2 hrs', 'fa-window-maximize'),
            ('Car Detailing', 'Cleaning', 'Premium ceramic coating, engine bay cleaning, tyre dressing', 7999, '6-8 hrs', 'fa-star'),
        ]
        c.executemany("INSERT INTO services (name, category, description, price, duration, icon) VALUES (?,?,?,?,?,?)", services)

    # Seed owner account
    c.execute("SELECT COUNT(*) FROM users WHERE role='owner'")
    if c.fetchone()[0] == 0:
        pwd = hashlib.sha256('owner123'.encode()).hexdigest()
        c.execute("INSERT INTO users (name, email, phone, password, role) VALUES (?,?,?,?,?)",
                  ('Admin Owner', 'owner@carcare.com', '9999999999', pwd, 'owner'))

    conn.commit()
    conn.close()

# ─── Helpers ─────────────────────────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def owner_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'owner':
            return jsonify({'error': 'Owner access required'}), 403
        return f(*args, **kwargs)
    return decorated

# ─── Page Routes ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services_page():
    return render_template('services.html')

@app.route('/booking')
def booking_page():
    return render_template('booking.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    if session.get('role') == 'owner':
        return render_template('owner_dashboard.html')
    return render_template('customer_dashboard.html')

# ─── Auth API ─────────────────────────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (name,email,phone,password) VALUES (?,?,?,?)",
                     (data['name'], data['email'], data['phone'], hash_pw(data['password'])))
        conn.commit()
        return jsonify({'success': True, 'message': 'Registration successful!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already registered.'})
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
                        (data['email'], hash_pw(data['password']))).fetchone()
    conn.close()
    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['role'] = user['role']
        return jsonify({'success': True, 'role': user['role'], 'name': user['name']})
    return jsonify({'success': False, 'message': 'Invalid credentials.'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/me')
def me():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'name': session['user_name'], 'role': session['role'], 'id': session['user_id']})
    return jsonify({'logged_in': False})

# ─── Services API ─────────────────────────────────────────────────────────────
@app.route('/api/services')
def get_services():
    conn = get_db()
    rows = conn.execute("SELECT * FROM services ORDER BY category").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ─── Bookings API ─────────────────────────────────────────────────────────────
@app.route('/api/book', methods=['POST'])
@login_required
def create_booking():
    data = request.json
    conn = get_db()
    svc = conn.execute("SELECT price FROM services WHERE id=?", (data['service_id'],)).fetchone()
    if not svc:
        return jsonify({'success': False, 'message': 'Service not found'})
    cur = conn.execute(
        "INSERT INTO bookings (customer_id,service_id,car_make,car_model,car_year,booking_date,booking_time,address,notes,total_amount) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (session['user_id'], data['service_id'], data['car_make'], data['car_model'],
         data['car_year'], data['booking_date'], data['booking_time'],
         data['address'], data.get('notes', ''), svc['price'])
    )
    booking_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'booking_id': booking_id, 'amount': svc['price']})

@app.route('/api/my-bookings')
@login_required
def my_bookings():
    conn = get_db()
    rows = conn.execute("""
        SELECT b.*, s.name as service_name, s.category, s.icon
        FROM bookings b JOIN services s ON b.service_id=s.id
        WHERE b.customer_id=? ORDER BY b.created_at DESC
    """, (session['user_id'],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/booking/<int:bid>')
@login_required
def get_booking(bid):
    conn = get_db()
    row = conn.execute("""
        SELECT b.*, s.name as service_name, u.name as customer_name, u.phone
        FROM bookings b JOIN services s ON b.service_id=s.id JOIN users u ON b.customer_id=u.id
        WHERE b.id=?
    """, (bid,)).fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(row))

# ─── Payment API ──────────────────────────────────────────────────────────────
@app.route('/api/pay', methods=['POST'])
@login_required
def process_payment():
    data = request.json
    booking_id = data['booking_id']
    method = data['method']
    conn = get_db()
    booking = conn.execute("SELECT * FROM bookings WHERE id=? AND customer_id=?",
                           (booking_id, session['user_id'])).fetchone()
    if not booking:
        conn.close()
        return jsonify({'success': False, 'message': 'Booking not found'})

    import random, string
    txn_id = 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    conn.execute("INSERT INTO payments (booking_id,amount,method,transaction_id,status,paid_at) VALUES (?,?,?,?,?,?)",
                 (booking_id, booking['total_amount'], method, txn_id, 'success', datetime.now()))
    conn.execute("UPDATE bookings SET payment_status='paid', payment_method=? WHERE id=?", (method, booking_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'transaction_id': txn_id, 'amount': booking['total_amount']})

# ─── Owner API ────────────────────────────────────────────────────────────────
@app.route('/api/owner/bookings')
@login_required
@owner_required
def owner_bookings():
    status = request.args.get('status', '')
    conn = get_db()
    query = """
        SELECT b.*, s.name as service_name, u.name as customer_name, u.phone, u.email
        FROM bookings b JOIN services s ON b.service_id=s.id JOIN users u ON b.customer_id=u.id
    """
    if status:
        query += " WHERE b.status=?"
        rows = conn.execute(query + " ORDER BY b.created_at DESC", (status,)).fetchall()
    else:
        rows = conn.execute(query + " ORDER BY b.created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/owner/booking/<int:bid>/status', methods=['PUT'])
@login_required
@owner_required
def update_booking_status(bid):
    data = request.json
    conn = get_db()
    conn.execute("UPDATE bookings SET status=? WHERE id=?", (data['status'], bid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/owner/stats')
@login_required
@owner_required
def owner_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM bookings").fetchone()['c']
    pending = conn.execute("SELECT COUNT(*) as c FROM bookings WHERE status='pending'").fetchone()['c']
    confirmed = conn.execute("SELECT COUNT(*) as c FROM bookings WHERE status='confirmed'").fetchone()['c']
    completed = conn.execute("SELECT COUNT(*) as c FROM bookings WHERE status='completed'").fetchone()['c']
    revenue = conn.execute("SELECT COALESCE(SUM(amount),0) as r FROM payments WHERE status='success'").fetchone()['r']
    customers = conn.execute("SELECT COUNT(*) as c FROM users WHERE role='customer'").fetchone()['c']
    conn.close()
    return jsonify({
        'total': total, 'pending': pending, 'confirmed': confirmed,
        'completed': completed, 'revenue': revenue, 'customers': customers
    })

@app.route('/api/owner/services', methods=['POST'])
@login_required
@owner_required
def add_service():
    data = request.json
    conn = get_db()
    conn.execute("INSERT INTO services (name,category,description,price,duration,icon) VALUES (?,?,?,?,?,?)",
                 (data['name'], data['category'], data['description'], data['price'], data['duration'], data.get('icon','fa-wrench')))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)