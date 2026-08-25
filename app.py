from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os
import json
from functools import wraps
import random
import secrets
import math
import requests


# -------------------------
LOCALITY_CHOICES = [
    "Ambernath", "Shahad", "Titwala", "Kalyan", "Thakurli",
    "Dombivli", "Kopar", "Diva", "Mumbra", "Kalwa", "Thane"
]


app = Flask(__name__)
from voice_routes import voice_bp
app.register_blueprint(voice_bp, url_prefix='/voice')
app.secret_key = secrets.token_hex(32)

# -------------------------
# Database initialization
# -------------------------
def init_db():
    conn = sqlite3.connect('service_portal.db', timeout=30.0)
    cursor = conn.cursor()

    # Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            city TEXT,
            locality TEXT,
            user_type TEXT NOT NULL,
            loyalty_points INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Workers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skills TEXT NOT NULL,
            experience INTEGER,
            hourly_rate REAL,
            description TEXT,
            rating REAL DEFAULT 0.0,
            total_jobs INTEGER DEFAULT 0,
            availability TEXT DEFAULT 'available',
            certifications TEXT,
            police_verified INTEGER DEFAULT 0,
            vaccination_status TEXT,
            eco_friendly INTEGER DEFAULT 0,
            profile_image TEXT,
            current_latitude REAL,
            current_longitude REAL,
            last_location_update TIMESTAMP,
            preferred_radius INTEGER DEFAULT 10,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Service requests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            worker_id INTEGER,
            service_type TEXT NOT NULL,
            description TEXT,
            location TEXT,
            locality TEXT,
            preferred_date TEXT,
            preferred_time TEXT,
            base_price REAL,
            labor_cost REAL,
            material_cost REAL,
            tax REAL,
            surge_multiplier REAL DEFAULT 1.0,
            final_price REAL,
            status TEXT DEFAULT 'pending',
            tracking_status TEXT DEFAULT 'not_started',
            eta_minutes INTEGER,
            is_group_booking INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (worker_id) REFERENCES workers (id)
        )
    ''')

    # Reviews
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            user_id INTEGER,
            worker_id INTEGER,
            rating INTEGER,
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES service_requests (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (worker_id) REFERENCES workers (id)
        )
    ''')

    # Subscriptions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_type TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Service categories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT,
            seasonal_peak TEXT,
            eco_friendly_available INTEGER DEFAULT 0,
            base_price REAL
        )
    ''')

    # SOS alerts (for sos_alert route)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sos_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            city TEXT,
            locality TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            worker_info TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')

    # Seed categories if empty
    cursor.execute('SELECT COUNT(*) FROM service_categories')
    count = cursor.fetchone()[0]
    if count == 0:
        categories = [
            ('Plumbing', 'fa-wrench', 'monsoon', 1, 500),
            ('Electrician', 'fa-bolt', 'all', 0, 600),
            ('Cleaning', 'fa-broom', 'spring', 1, 400),
            ('Painting', 'fa-paint-roller', 'spring', 1, 800),
            ('AC Repair', 'fa-snowflake', 'summer', 0, 700),
            ('Carpentry', 'fa-hammer', 'all', 1, 650),
            ('Pest Control', 'fa-bug', 'monsoon', 1, 550),
            ('Cook', 'fa-utensils', 'all', 0, 300),
            ('Gardening', 'fa-leaf', 'spring', 1, 350),
            ('Home Appliance Repair', 'fa-tv', 'all', 0, 500),
            ('Masonry', 'fa-hard-hat', 'all', 0, 700),
            ('Car Wash', 'fa-car', 'all', 1, 250),
            ('Beauty & Salon', 'fa-cut', 'all', 0, 400),
            ('Tutor', 'fa-book', 'all', 0, 500)
        ]
        cursor.executemany(
            '''INSERT INTO service_categories (name, icon, seasonal_peak, eco_friendly_available, base_price)
               VALUES (?, ?, ?, ?, ?)''',
            categories
        )

    conn.commit()
    conn.close()

# -------------------------
# Helpers
# -------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    conn = sqlite3.connect('service_portal.db', timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def get_seasonal_recommendations():
    current_month = datetime.now().month
    if current_month in [3, 4, 5, 6]:
        season = 'summer'
    elif current_month in [12, 1, 2]:
        season = 'winter'
    elif current_month in [7, 8, 9]:
        season = 'monsoon'
    else:
        season = 'spring'
    conn = get_db_connection()
    rows = conn.execute(
        '''SELECT name, icon FROM service_categories
           WHERE seasonal_peak = ? OR seasonal_peak = 'all'
           LIMIT 6''',
        (season,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def calculate_dynamic_pricing(base_price, service_type, date, time):
    hour = int(time.split(':')[0])
    is_peak_hour = 9 <= hour <= 18
    is_weekend = datetime.strptime(date, '%Y-%m-%d').weekday() >= 5

    surge = 1.0
    if is_peak_hour:
        surge += 0.2
    if is_weekend:
        surge += 0.15
    surge += random.uniform(0, 0.3)
    surge = min(surge, 2.0)

    labor_cost = round(base_price*surge, 2)
    material_cost = round(base_price * 0.30, 2)
    subtotal = labor_cost + material_cost
    tax = round(subtotal * 0.18, 2)
    final_price = round(subtotal + tax, 2)

    return {
        'base_price': base_price,
        'labor_cost': labor_cost,
        'material_cost': material_cost,
        'tax': tax,
        'surge_multiplier': round(surge, 2),
        'final_price': final_price
    }

def get_ai_recommendations(user_id):
    conn = get_db_connection()
    history = conn.execute('''
        SELECT service_type, COUNT(*) as frequency
        FROM service_requests
        WHERE user_id = ?
        GROUP BY service_type
        ORDER BY frequency DESC
        LIMIT 3
    ''', (user_id,)).fetchall()

    user = conn.execute('SELECT locality FROM users WHERE id = ?', (user_id,)).fetchone()
    if user and user['locality']:
        trending = conn.execute('''
            SELECT sr.service_type, COUNT(*) as bookings
            FROM service_requests sr
            JOIN users u ON sr.user_id = u.id
            WHERE u.locality = ?
              AND sr.created_at >= date('now', '-30 days')
            GROUP BY sr.service_type
            ORDER BY bookings DESC
            LIMIT 3
        ''', (user['locality'],)).fetchall()
    else:
        trending = []

    seasonal = get_seasonal_recommendations()
    conn.close()
    return {
        'personal': [dict(h) for h in history],
        'trending': [dict(t) for t in trending],
        'seasonal': seasonal
    }

def get_chatbot_response(message, user_id=None):
    m = message.lower()

    if any(w in m for w in ['hello', 'hi', 'hey', 'greetings']):
        return {
            'response': (
                "Hello! 👋 I'm your service assistant. I can help with:\n"
                "• Finding workers\n• Booking services\n• Pricing\n• Tracking\n• Account\n\nWhat is needed?"
            ),
            'suggestions': ['Find a plumber', 'Check pricing', 'Track my order', 'View services']
        }

    if any(w in m for w in ['service', 'worker', 'find']):
        conn = get_db_connection()
        cats = conn.execute('SELECT name FROM service_categories LIMIT 6').fetchall()
        conn.close()
        services = ', '.join([c['name'] for c in cats])
        return {
            'response': (
                f"We offer: {services} and more!\n\nWould you like to:\n"
                f"• Browse workers\n• Search nearby\n• Get price estimates"
            ),
            'suggestions': ['Browse plumbers', 'Search nearby', 'Get pricing']
        }

    if any(w in m for w in ['price', 'cost', 'rate']):
        return {
            'response': (
                "Pricing breakdown:\n• Base cost\n• Labor (demand-based)\n• Materials\n• 18% GST\n\n"
                "Premium members get 10% off; group bookings get 15% off. Need an estimate?"
            ),
            'suggestions': ['Plumbing cost', 'Electrician rates', 'Cleaning prices']
        }

    if any(w in m for w in ['book', 'appointment', 'schedule']):
        return {
            'response': (
                "Booking steps:\n1) Pick worker\n2) Choose date/time\n3) Get instant estimate\n"
                "4) Confirm\n\nTracking included; loyalty points awarded."
            ),
            'suggestions': ['Browse services', 'My bookings', 'Track order']
        }

    if any(w in m for w in ['track', 'status', 'order']):
        if user_id:
            conn = get_db_connection()
            active = conn.execute('''
                SELECT COUNT(*) as c FROM service_requests
                WHERE user_id = ? AND status IN ('pending','accepted')
            ''', (user_id,)).fetchone()
            conn.close()
            if active['c'] > 0:
                return {
                    'response': (
                        f"You have {active['c']} active booking(s).\nTrack via dashboard for live location and ETA."
                    ),
                    'suggestions': ['View dashboard', 'Contact worker']
                }
        return {
            'response': (
                "Track in real-time after login: live location, ETA, and status updates."
            ),
            'suggestions': ['Login', 'View services']
        }

    if any(w in m for w in ['loyalty', 'points', 'reward']):
        return {
            'response': (
                "Loyalty program:\n• 1 point per ₹10\n• Redeem for discounts/free services\n"
                "Levels: Bronze→Silver→Gold→Platinum"
            ),
            'suggestions': ['My points', 'View rewards', 'Premium plans']
        }

    if any(w in m for w in ['premium', 'subscription', 'plan']):
        return {
            'response': (
                "Plans:\nBasic ₹99/m: 10% off, priority\n"
                "Premium ₹299/m: 20% off, 1 free service\n"
                "Annual ₹2999/y: 25% off, 2 free services"
            ),
            'suggestions': ['View plans', 'Subscribe now', 'Compare benefits']
        }

    if 'become worker' in m or 'join as worker' in m:
        return {
            'response': (
                "Join as a professional: flexible schedule, earnings, training, insurance.\n"
                "Requirements: skills, police verification, vaccination."
            ),
            'suggestions': ['Register as worker', 'View training', 'Earnings info']
        }

    if any(w in m for w in ['safe', 'verify', 'trust']):
        return {
            'response': (
                "Safety: police verification, background checks, certifications, ratings, insurance."
            ),
            'suggestions': ['Verified workers', 'Safety guidelines']
        }

    if any(w in m for w in ['help', 'support', 'contact']):
        return {
            'response': (
                "Support 24/7 (this chat), email support@findmyworker.com, phone 1800-123-4567."
            ),
            'suggestions': ['Report issue', 'FAQs', 'Contact support']
        }

    return {
        'response': (
            "I can help with finding/booking, pricing, tracking, loyalty, premium, and safety.\n"
            "What would be helpful?"
        ),
        'suggestions': ['Browse services', 'Get pricing', 'My account', 'Help']
    }

# def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine
    # rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # dlat = rlat2 - rlat1
    # dlon = rlon2 - rlon1
    # a = math.sin(dlat/2)**2 + math.cos(rlat1)*math.cos(rlat2)*math.sin(dlon/2)**2
    # c = 2 * math.asin(math.sqrt(a))
    # return 6371 * c

def get_osrm_distance(lat1, lon1, lat2, lon2):
    """
    FREE road distance using OpenStreetMap OSRM
    Returns (distance_km, duration_minutes)
    """
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}?overview=false"
    )
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("code") != "Ok":
            return None, None

        route = data["routes"][0]
        return round(route["distance"] / 1000, 2), round(route["duration"] / 60)
    except Exception:
        return None, None


# def get_nearby_workers(customer_lat, customer_lon, service_type, radius_km=10):
#     conn = get_db_connection()
#     workers = conn.execute('''
#         SELECT w.*, u.name, u.phone, u.locality, u.city,
#                w.current_latitude, w.current_longitude, w.last_location_update
#         FROM workers w
#         JOIN users u ON w.user_id = u.id
#         WHERE w.availability = 'available'
#           AND w.skills LIKE ?
#           AND w.current_latitude IS NOT NULL
#           AND w.current_longitude IS NOT NULL
#     ''', (f'%{service_type}%',)).fetchall()
#     conn.close()

#     nearby = []
#     for w in workers:
#         d = calculate_distance(customer_lat, customer_lon, w['current_latitude'], w['current_longitude'])
#         if d <= radius_km:
#             row = dict(w)
#             row['distance_km'] = round(d, 2)
#             row['distance_m'] = round(d * 1000, 0)
#             nearby.append(row)
#     nearby.sort(key=lambda x: x['distance_km'])
#     return nearby

def get_nearby_workers(customer_lat, customer_lon, service_type, radius_km=10):
    conn = get_db_connection()
    workers = conn.execute('''
        SELECT w.*, u.name, u.phone, u.locality, u.city,
               w.current_latitude, w.current_longitude, w.last_location_update
        FROM workers w
        JOIN users u ON w.user_id = u.id
        WHERE w.availability = 'available'
          AND w.skills LIKE ?
          AND w.current_latitude IS NOT NULL
          AND w.current_longitude IS NOT NULL
    ''', (f'%{service_type}%',)).fetchall()
    conn.close()

    # ---------- STEP 1: fast pre-filter (cheap & free) ----------
    candidates = []
    for w in workers:
        approx_km = (
            ((customer_lat - w['current_latitude']) ** 2 +
             (customer_lon - w['current_longitude']) ** 2) ** 0.5
        ) * 111  # rough km estimate

        if approx_km <= radius_km * 1.5:
            candidates.append(w)

    # Limit OSRM calls (VERY IMPORTANT)
    candidates = candidates[:15]

    # ---------- STEP 2: accurate OSRM distance ----------
    nearby = []
    for w in candidates:
        dist_km, eta_min = get_osrm_distance(
            customer_lat,
            customer_lon,
            w['current_latitude'],
            w['current_longitude']
        )
        # print("OSRM CHECK → worker:", w['id'], "distance:", dist_km, "eta:", eta_min)


        if dist_km is None:
            continue

        if dist_km <= radius_km:
            row = dict(w)
            row['distance_km'] = dist_km
            row['distance_m'] = round(dist_km * 1000)
            row['eta_minutes'] = eta_min
            nearby.append(row)

    # Sort by ETA (better UX than straight distance)
    nearby.sort(key=lambda x: x['eta_minutes'])
    return nearby

def update_worker_location(worker_id, latitude, longitude):
    conn = get_db_connection()
    conn.execute('''
        UPDATE workers
        SET current_latitude = ?, current_longitude = ?, last_location_update = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (latitude, longitude, worker_id))
    conn.commit()
    conn.close()

def award_loyalty_points(user_id, points, conn=None):
    own = False
    if conn is None:
        conn = get_db_connection()
        own = True
    conn.execute('UPDATE users SET loyalty_points = loyalty_points + ? WHERE id = ?', (points, user_id))
    if own:
        conn.commit()
        conn.close()

# -------------------------
# Routes
# -------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('worker_dashboard' if session.get('user_type') == 'worker' else 'user_dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        locality = request.form.get('locality', '')
        user_type = request.form['user_type']
        hashed = generate_password_hash(password)

        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO users (email, password, name, phone, address, city, locality, user_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, hashed, name, phone, address, city, locality, user_type))
            user_id = cur.lastrowid

            if user_type == 'worker':
                skills = request.form.get('skills', '')
                experience = int(request.form.get('experience', 0))
                hourly_rate = float(request.form.get('hourly_rate', 0))
                description = request.form.get('description', '')
                police_verified = 1 if request.form.get('police_verified') == 'on' else 0
                eco_friendly = 1 if request.form.get('eco_friendly') == 'on' else 0
                vaccination_status = request.form.get('vaccination_status', 'not_disclosed')
                cur.execute('''
                    INSERT INTO workers (
                        user_id, skills, experience, hourly_rate, description,
                        police_verified, eco_friendly, vaccination_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, skills, experience, hourly_rate, description, police_verified, eco_friendly, vaccination_status))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
        finally:
            conn.close()

    conn = get_db_connection()
    categories = conn.execute('SELECT name FROM service_categories ORDER BY name').fetchall()
    conn.close()
    return render_template('register.html', categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_type'] = user['user_type']
            session['user_name'] = user['name']
            session['user_city'] = user['city']
            session['user_locality'] = user['locality']
            session['loyalty_points'] = user['loyalty_points']
            session['is_premium'] = user['is_premium']
            if user['user_type'] == 'worker':
                return redirect(url_for('worker_dashboard'))
            if user['user_type'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        flash('Invalid email or password!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if session['user_type'] != 'user':
        return redirect(url_for('worker_dashboard'))
    conn = get_db_connection()

    recommendations = get_ai_recommendations(session['user_id'])
    service_categories = conn.execute('SELECT * FROM service_categories ORDER BY name').fetchall()
    recent_requests = conn.execute('''
        SELECT sr.*, w.skills, u.name as worker_name, u.phone as worker_phone
        FROM service_requests sr
        LEFT JOIN workers w ON sr.worker_id = w.id
        LEFT JOIN users u ON w.user_id = u.id
        WHERE sr.user_id = ?
        ORDER BY sr.created_at DESC
        LIMIT 5
    ''', (session['user_id'],)).fetchall()
    local_workers = conn.execute('''
        SELECT w.*, u.name, u.city, u.locality
        FROM workers w
        JOIN users u ON w.user_id = u.id
        WHERE (u.locality = ? OR u.city = ?)
          AND w.availability = 'available'
        ORDER BY w.rating DESC, w.total_jobs DESC
        LIMIT 8
    ''', (session.get('user_locality', ''), session['user_city'])).fetchall()

    conn.close()
    return render_template(
        'user_dashboard.html',
        recommendations=recommendations,
        service_categories=service_categories,
        recent_requests=recent_requests,
        local_workers=local_workers
    )

@app.route('/worker_dashboard')
@login_required
def worker_dashboard():
    if session['user_type'] != 'worker':
        return redirect(url_for('user_dashboard'))
    conn = get_db_connection()
    worker = conn.execute('''
        SELECT w.*, u.name, u.email, u.phone, u.locality
        FROM workers w
        JOIN users u ON w.user_id = u.id
        WHERE w.user_id = ?
    ''', (session['user_id'],)).fetchone()

    pending_requests = conn.execute('''
        SELECT sr.*, u.name as customer_name, u.phone as customer_phone, u.locality
        FROM service_requests sr
        JOIN users u ON sr.user_id = u.id
        WHERE sr.worker_id = ? AND sr.status = 'pending'
        ORDER BY sr.created_at DESC
    ''', (worker['id'],)).fetchall()

    earnings = conn.execute('''
        SELECT
            SUM(final_price) as total_earnings,
            COUNT(*) as completed_jobs,
            AVG(final_price) as avg_job_value
        FROM service_requests
        WHERE worker_id = ? AND status = 'completed'
    ''', (worker['id'],)).fetchone()

    weekly_earnings = conn.execute('''
        SELECT strftime('%Y-%W', created_at) as week, SUM(final_price) as earnings
        FROM service_requests
        WHERE worker_id = ? AND status = 'completed'
          AND created_at >= date('now', '-8 weeks')
        GROUP BY week
        ORDER BY week
    ''', (worker['id'],)).fetchall()

    review_count = conn.execute('''
    SELECT COUNT(*) as count
    FROM reviews
    WHERE worker_id = ?
    ''', (worker['id'],)).fetchone()['count']

    completed_jobs = conn.execute('''
    SELECT COUNT(*) as count
    FROM service_requests
    WHERE worker_id = ? AND status = 'accepted'
    ''', (worker['id'],)).fetchone()['count']

    # ⭐ Calculate average rating from reviews
    avg_rating = conn.execute('''
        SELECT AVG(rating) as avg_rating
        FROM reviews
        WHERE worker_id = ?
    ''', (worker['id'],)).fetchone()['avg_rating']

    if avg_rating is None:
        avg_rating = 0.0

    worker = dict(worker)
    worker['rating'] = round(avg_rating, 1)
    # ⭐ FIX ENDS HERE

    return render_template(
    'worker_dashboard.html',
    worker=worker,
    pending_requests=pending_requests,
    earnings=earnings,
    weekly_earnings=weekly_earnings,
    review_count=review_count,
    completed_jobs=completed_jobs   # 👈 ADD THIS
    )


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    conn = get_db_connection()
    workers = conn.execute('''
        SELECT u.id, u.name, u.email, u.phone, u.city, u.locality, u.created_at,
               w.skills, w.experience, w.hourly_rate, w.rating, w.total_jobs,
               w.availability, w.police_verified, w.eco_friendly, w.vaccination_status
        FROM users u
        JOIN workers w ON u.id = w.user_id
        ORDER BY u.created_at DESC
    ''').fetchall()
    stats = conn.execute('''
        SELECT
            COUNT(*) as total_workers,
            COUNT(CASE WHEN availability = 'available' THEN 1 END) as available_workers,
            COUNT(CASE WHEN police_verified = 1 THEN 1 END) as verified_workers,
            COUNT(CASE WHEN eco_friendly = 1 THEN 1 END) as eco_workers,
            AVG(rating) as avg_rating
        FROM workers
    ''').fetchone()
    conn.close()
    return render_template('admin_dashboard.html', workers=workers, stats=stats)

# @app.route('/browse_services/<category>')
# @login_required
# def browse_services(category):
#     conn = get_db_connection()
#     filters = request.args
#     locality = filters.get('locality', session.get('user_locality', ''))
#     eco_friendly = filters.get('eco_friendly') == 'true'
#     verified_only = filters.get('verified_only') == 'true'
#     min_rating = float(filters.get('min_rating', 0))

#     query = '''
#         SELECT w.*, u.name, u.city, u.locality, u.phone
#         FROM workers w
#         JOIN users u ON w.user_id = u.id
#         WHERE w.skills LIKE ?
#           AND w.availability = 'available'
#     '''
#     params = [f'%{category}%']
#     if locality:
#         query += ' AND u.locality = ?'
#         params.append(locality)
#     if eco_friendly:
#         query += ' AND w.eco_friendly = 1'
#     if verified_only:
#         query += ' AND w.police_verified = 1'
#     if min_rating > 0:
#         query += ' AND w.rating >= ?'
#         params.append(min_rating)
#     query += ' ORDER BY w.rating DESC, w.total_jobs DESC'

#     workers = conn.execute(query, params).fetchall()
#     category_info = conn.execute('SELECT * FROM service_categories WHERE name = ?', (category,)).fetchone()
#     conn.close()
#     return render_template(
#         'browse_services.html',
#         workers=workers,
#         category=category,
#         category_info=category_info,
#         filters=filters
#     )

@app.route('/browse_services/<category>')
@login_required
def browse_services(category):
    conn = get_db_connection()

    query = '''
        SELECT w.*, u.name, u.city, u.locality, u.phone
        FROM workers w
        JOIN users u ON w.user_id = u.id
        WHERE w.skills LIKE ?
          AND w.availability = 'available'
        ORDER BY w.rating DESC, w.total_jobs DESC
    '''
    
    workers = conn.execute(query, (f'%{category}%',)).fetchall()

    category_info = conn.execute(
        'SELECT * FROM service_categories WHERE name = ?',
        (category,)
    ).fetchone()

    conn.close()

    return render_template(
        'browse_services.html',
        workers=workers,
        category=category,
        category_info=category_info
    )

@app.route('/book_service/<int:worker_id>', methods=['GET', 'POST'])
@login_required
def book_service(worker_id):
    if session['user_type'] != 'user':
        return redirect(url_for('worker_dashboard'))

    if request.method == 'POST':
        conn = None
        try:
            conn = get_db_connection()
            service_type = request.form['service_type']
            description = request.form['description']
            location = request.form['location']
            locality = request.form['locality']
            preferred_date = request.form['preferred_date']
            preferred_time = request.form['preferred_time']
            is_group_booking = request.form.get('group_booking') == 'on'

            cat = conn.execute('SELECT base_price FROM service_categories WHERE name = ?', (service_type,)).fetchone()
            base_price = cat['base_price'] if cat else 500
            pricing = calculate_dynamic_pricing(base_price, service_type, preferred_date, preferred_time)

            # if is_group_booking:
            #     pricing['final_price'] = round(pricing['final_price'] * 0.85, 2)
            # if session.get('is_premium'):
            #     pricing['final_price'] = round(pricing['final_price'] * 0.90, 2)

            # conn.execute('''
            #     INSERT INTO service_requests
            #     (user_id, worker_id, service_type, description, location, locality,
            #      preferred_date, preferred_time, base_price, labor_cost, material_cost,
            #      tax, surge_multiplier, final_price, is_group_booking)
            #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            # ''', (
            #     session['user_id'], worker_id, service_type, description, location, locality,
            #     preferred_date, preferred_time, pricing['base_price'], pricing['labor_cost'],
            #     pricing['material_cost'], pricing['tax'], pricing['surge_multiplier'],
            #     pricing['final_price'], 1 if is_group_booking else 0
            # ))

            # points = int(pricing['final_price'] / 10)

            conn.execute('''
                INSERT INTO service_requests
                (user_id, worker_id, service_type, description, location, locality,
                preferred_date, preferred_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'], worker_id, service_type, description, location, locality,
                preferred_date, preferred_time
            ))

            award_loyalty_points(session['user_id'],10, conn)
            conn.commit()
            flash('Service request sent! Earned 10 loyalty points!')
            return redirect(url_for('user_dashboard'))
        except Exception as e:
            if conn:
                conn.rollback()
            flash(f'Error booking service: {str(e)}', 'error')
            return redirect(url_for('user_dashboard'))
        finally:
            if conn:
                conn.close()

    conn = get_db_connection()
    worker = conn.execute('''
        SELECT w.*, u.name, u.city, u.locality
        FROM workers w
        JOIN users u ON w.user_id = u.id
        WHERE w.id = ?
    ''', (worker_id,)).fetchone()
    conn.close()
    if not worker:
        flash('Worker not found!', 'error')
        return redirect(url_for('user_dashboard'))
    return render_template('book_service.html', worker=worker, datetime=datetime, category=request.args.get('category'))

@app.route('/track_service/<int:request_id>')
@login_required
def track_service(request_id):
    conn = get_db_connection()
    sr = conn.execute('''
        SELECT sr.*, w.skills, u.name as worker_name, u.phone as worker_phone
        FROM service_requests sr
        JOIN workers w ON sr.worker_id = w.id
        JOIN users u ON w.user_id = u.id
        WHERE sr.id = ? AND sr.user_id = ?
    ''', (request_id, session['user_id'])).fetchone()
    conn.close()
    if not sr:
        flash('Service request not found!', 'error')
        return redirect(url_for('user_dashboard'))

    tracking_stages = [
        {'status': 'confirmed', 'message': 'Booking Status', 'icon': 'check-circle'},
        {'status': 'worker_assigned', 'message': 'Worker assigned', 'icon': 'user-check'},
        # {'status': 'worker_started', 'message': 'Worker started journey', 'icon': 'route'},
        # {'status': 'nearby', 'message': 'Worker nearby (5 min)', 'icon': 'map-marker-alt'},
        # {'status': 'arrived', 'message': 'Worker arrived', 'icon': 'home'},
        # {'status': 'in_progress', 'message': 'Service in progress', 'icon': 'tools'},
        # {'status': 'completed', 'message': 'Service completed', 'icon': 'check-double'}
    ]
    return render_template('track_service.html', service_request=sr, tracking_stages=tracking_stages)

@app.route('/subscription_plans')
@login_required
def subscription_plans():
    if session['user_type'] != 'user':
        return redirect(url_for('worker_dashboard'))
    plans = [
        {
            'name': 'Basic',
            'price': 99,
            'duration': 'monthly',
            'badge': 'Bronze',
            'benefits': [
                '10% discount on all services',
                'Priority booking',
                '24/7 support',
                '100 bonus loyalty points'
            ]
        },
        {
            'name': 'Premium',
            'price': 299,
            'duration': 'monthly',
            'badge': 'Gold',
            'benefits': [
                '20% discount on all services',
                'Priority booking',
                '1 free service per month',
                'Emergency SOS feature',
                '500 bonus loyalty points',
                'Free rescheduling'
            ]
        },
        {
            'name': 'Annual',
            'price': 2999,
            'duration': 'yearly',
            'badge': 'Platinum',
            'benefits': [
                '25% discount on all services',
                'Top priority booking',
                '2 free services per month',
                'Emergency SOS feature',
                'AR/VR preview access',
                '5000 bonus loyalty points',
                'Dedicated support manager'
            ]
        }
    ]
    return render_template('subscription_plans.html', plans=plans)

@app.route('/loyalty_rewards')
@login_required
def loyalty_rewards():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    points = user['loyalty_points']
    level = 'Bronze'
    if points >= 5000:
        level = 'Platinum'
    elif points >= 2000:
        level = 'Gold'
    elif points >= 500:
        level = 'Silver'
    rewards = [
        {'name': '₹100 Off Coupon', 'points': 500, 'icon': 'ticket-alt'},
        {'name': '₹250 Off Coupon', 'points': 1000, 'icon': 'gift'},
        {'name': 'Free Cleaning Service', 'points': 1500, 'icon': 'broom'},
        {'name': '₹500 Off Coupon', 'points': 2000, 'icon': 'star'},
        {'name': 'Premium Upgrade (1 month)', 'points': 3000, 'icon': 'crown'}
    ]
    return render_template('loyalty_rewards.html', user=user, level=level, rewards=rewards)

#not used
@app.route('/add_worker', methods=['GET', 'POST'])
@login_required
def add_worker():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            address = request.form['address']
            city = request.form['city']
            locality = request.form['locality']
            skills = request.form['skills']
            experience = int(request.form['experience'])
            hourly_rate = float(request.form['hourly_rate'])
            availability = request.form['availability']
            description = request.form.get('description', '')
            certifications = request.form.get('certifications', '')
            vaccination_status = request.form['vaccination_status']
            profile_image = request.form.get('profile_image', '')
            initial_latitude = request.form.get('initial_latitude')
            initial_longitude = request.form.get('initial_longitude')
            police_verified = 1 if 'police_verified' in request.form else 0
            eco_friendly = 1 if 'eco_friendly' in request.form else 0
            is_premium = 1 if 'is_premium' in request.form else 0
            give_loyalty_points = 'loyalty_points' in request.form
            # rating = float(request.form.get('rating', 0))
            total_jobs = int(request.form.get('total_jobs', 0))
            loyalty_points_amount = int(request.form.get('loyalty_points_amount', 0))

            password_hash = generate_password_hash(password)

            conn = get_db_connection()
            try:
                existing = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
                if existing:
                    flash('Email already exists!', 'error')
                    return render_template('add_worker.html')

                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO users (name, email, password, phone, address, city, locality,
                                       user_type, loyalty_points, is_premium)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, email, password_hash, phone, address, city, locality,
                      'worker', loyalty_points_amount if give_loyalty_points else 0, is_premium))
                user_id = cur.lastrowid

                cur.execute('''
                    INSERT INTO workers (user_id, skills, experience, hourly_rate, description,
                                         total_jobs, availability, certifications,
                                         police_verified, vaccination_status, eco_friendly, profile_image,
                                         current_latitude, current_longitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, skills, experience, hourly_rate, description, total_jobs,
                      availability, certifications, police_verified, vaccination_status, eco_friendly,
                      profile_image, initial_latitude, initial_longitude))
                conn.commit()
                flash(f'Worker "{name}" has been successfully added!', 'success')
                return redirect(url_for('worker_dashboard'))
            except Exception as e:
                conn.rollback()
                flash(f'Error adding worker: {str(e)}', 'error')
                return render_template('add_worker.html')
            finally:
                conn.close()
        except Exception as e:
            flash(f'Error processing form: {str(e)}', 'error')
            return render_template('add_worker.html')
    return render_template('add_worker.html')

@app.route('/nearby_workers_page')
@login_required
def nearby_workers_page():
    return render_template('nearby_workers.html')

@app.route('/update_location', methods=['POST'])
@login_required
def update_location():
    if session.get('user_type') != 'worker':
        return jsonify({'error': 'Only workers can update location'}), 403
    try:
        data = request.get_json(force=True)
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        conn = get_db_connection()
        worker = conn.execute('SELECT id FROM workers WHERE user_id = ?', (session['user_id'],)).fetchone()
        conn.close()
        if not worker:
            return jsonify({'error': 'Worker not found'}), 404
        update_worker_location(worker['id'], latitude, longitude)
        return jsonify({
            'success': True,
            'message': 'Location updated successfully',
            'location': {'lat': latitude, 'lon': longitude}
        })
    except ValueError:
        return jsonify({'error': 'Invalid latitude or longitude values'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/worker_location_status')
@login_required
def worker_location_status():
    if session.get('user_type') != 'worker':
        return jsonify({'error': 'Only workers can access this'}), 403
    conn = get_db_connection()
    w = conn.execute('''
        SELECT current_latitude, current_longitude, last_location_update, availability
        FROM workers WHERE user_id = ?
    ''', (session['user_id'],)).fetchone()
    conn.close()
    if not w:
        return jsonify({'error': 'Worker not found'}), 404

    # ✅ FIX STARTS HERE
    last_update = w['last_location_update']

    if last_update:
        from datetime import timezone

        # If already datetime → use directly
        if hasattr(last_update, 'isoformat'):
            dt = last_update
        else:
            # If string → convert
            from datetime import datetime
            dt = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")

        dt = dt.replace(tzinfo=timezone.utc)
        last_update_iso = dt.isoformat()
    else:
        last_update_iso = None
    # ✅ FIX ENDS HERE

    return jsonify({
        'success': True,
        'location': {
            'latitude': w['current_latitude'],
            'longitude': w['current_longitude'],
            # 'last_update': w['last_location_update'],
            'last_update': last_update_iso,
            'has_location': w['current_latitude'] is not None
        },
        'availability': w['availability']
    })

@app.route('/manage_request/<int:request_id>/<action>')
@login_required
def manage_request(request_id, action):
    if session['user_type'] != 'worker':
        return redirect(url_for('user_dashboard'))
    if action not in ['accept', 'decline', 'complete']:
        flash('Invalid action', 'error')
        return redirect(url_for('worker_dashboard'))

    status_map = {'accept': 'accepted', 'decline': 'declined', 'complete': 'completed'}
    tracking = 'worker_assigned' if action == 'accept' else ('completed' if action == 'complete' else 'not_started')

    conn = get_db_connection()
    conn.execute('UPDATE service_requests SET status = ?, tracking_status = ? WHERE id = ?',
                 (status_map[action], tracking, request_id))
    if action == 'complete':
        conn.execute('UPDATE workers SET total_jobs = total_jobs + 1 WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    flash(f'Request {action}ed successfully!')
    return redirect(url_for('worker_dashboard'))

@app.route('/api/recommendations')
@login_required
def api_recommendations():
    return jsonify(get_ai_recommendations(session['user_id']))

@app.route('/api/nearby_workers')
@login_required
def api_nearby_workers():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({'error': 'lat and lon are required'}), 400
    service_type = request.args.get('service_type', '')
    radius_km = float(request.args.get('radius_km', '8'))
    results = get_nearby_workers(lat, lon, service_type, radius_km)
    workers = [{
        'id': w['id'],
        'name': w['name'],
        'skills': w['skills'],
        'rating': w['rating'],
        'total_jobs': w['total_jobs'],
        'city': w['city'],
        'locality': w['locality'],
        'distance_km': w['distance_km'],
        'latitude': w['current_latitude'],
        'longitude': w['current_longitude'],
        'eta_minutes': w.get('eta_minutes')
    } for w in results]
    return jsonify({'workers': workers})


@app.route('/api/pricing_estimate', methods=['POST'])
@login_required
def api_pricing_estimate():
    data = request.get_json(force=True)
    service_type = data.get('service_type')
    date = data.get('date')
    time = data.get('time')
    conn = get_db_connection()
    cat = conn.execute('SELECT base_price FROM service_categories WHERE name = ?', (service_type,)).fetchone()
    conn.close()
    base_price = cat['base_price'] if cat else 500
    return jsonify(calculate_dynamic_pricing(base_price, service_type, date, time))

@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    try:
        data = request.get_json(force=True)
        message = data.get('message', '')
        if not message:
            return jsonify({'error': 'Message required'}), 400
        resp = get_chatbot_response(message, session.get('user_id'))
        return jsonify({
            'success': True,
            'response': resp['response'],
            'suggestions': resp.get('suggestions', []),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chatbot_widget')
@login_required
def chatbot_widget():
    return render_template('chatbot.html')

@app.route('/sos_alert', methods=['POST'])
@login_required
def sos_alert():
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_city = session.get('user_city')
    user_locality = session.get('user_locality')
    data = request.get_json(force=True)
    user_latitude = data.get('latitude')
    user_longitude = data.get('longitude')
    try:
        conn = get_db_connection()
        sr = conn.execute('''
            SELECT sr.*, w.*, u.name as worker_name, u.email as worker_email, u.phone as worker_phone
            FROM service_requests sr
            JOIN workers w ON sr.worker_id = w.id
            JOIN users u ON w.user_id = u.id
            WHERE sr.user_id = ?
            AND sr.status = 'accepted'
            AND sr.created_at >= datetime('now', '-1 day')
            ORDER BY sr.created_at DESC
            LIMIT 1
        ''', (user_id,)).fetchone()

        # ❗ Block SOS if no recent booking
        if not sr:
            return jsonify({
                "success": False,
                "message": "SOS can only be used when a recent service is active."
            }), 403

        worker_info = {}
        if sr:
            worker_info = {
                'worker_id': sr['worker_id'],
                'worker_name': sr['worker_name'],
                'worker_email': sr['worker_email'],
                # 'worker_phone': sr['worker_phone'],
                # 'worker_skills': sr['skills'],
                # 'worker_experience': sr['experience'],
                # 'worker_rating': sr['rating'],
                # 'worker_locality': sr['locality'],
                # 'worker_city': sr['city']
            }

        conn.execute('''
            INSERT INTO sos_alerts (user_id, user_name, city, locality, worker_info, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_name, user_city, user_locality, json.dumps(worker_info), user_latitude, user_longitude))
        conn.commit()
        conn.close()

        print(f"SOS ALERT!\nUser: {user_name} (ID: {user_id})\nLocation: {user_city}, {user_locality}, "
              f"Lat: {user_latitude}, Long: {user_longitude}\nWorker: {worker_info}\n")
        return jsonify({'success': True, 'message': 'SOS alert sent and admin notified.'})
    except Exception as e:
        print("SOS ERROR:", e)
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
    

# Add to app.py
# @app.route('/api/sos_alerts')
# @login_required
# def api_sos_alerts():
#     if session.get('user_type') != 'admin':
#         return jsonify({'error': 'Forbidden'}), 403

#     conn = get_db_connection()
#     rows = conn.execute('''
#         SELECT id,
#                user_name,
#                city,
#                locality,
#                datetime(timestamp) AS timestamp,
#                worker_info,
#                latitude,
#                longitude
#         FROM sos_alerts
#         ORDER BY timestamp DESC
#         LIMIT 50
#     ''').fetchall()
#     conn.close()

#     alerts = []
#     for r in rows:
#         try:
#             wi = json.loads(r['worker_info']) if r['worker_info'] else {}
#         except Exception:
#             wi = {}
#         alerts.append({
#             'id': r['id'],
#             'user_name': r['user_name'],
#             'city': r['city'],
#             'locality': r['locality'],
#             'timestamp': r['timestamp'],
#             'latitude': r['latitude'],
#             'longitude': r['longitude'],
#             'worker': wi
#         })
#     return jsonify({'alerts': alerts})

@app.route('/api/sos_alerts')
@login_required
def api_sos_alerts():
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    conn = get_db_connection()
    rows = conn.execute('''
        SELECT id,
               user_name,
               user_id,
               city,
               locality,
               timestamp,         -- stored as UTC (SQLite CURRENT_TIMESTAMP)
               worker_info,
               latitude,
               longitude
        FROM sos_alerts
        ORDER BY timestamp DESC
        LIMIT 50
    ''').fetchall()
    conn.close()

    # Convert UTC -> Asia/Kolkata for display
    from datetime import datetime, timezone, timedelta
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo('Asia/Kolkata')
        use_zoneinfo = True
    except Exception:
        tz = timedelta(hours=5, minutes=30)  # fallback fixed offset
        use_zoneinfo = False

    alerts = []
    for r in rows:
        raw_ts = r['timestamp']  # format: 'YYYY-MM-DD HH:MM:SS'
        ts_local = raw_ts
        if raw_ts:
            try:
                dt_utc = datetime.strptime(raw_ts, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                if use_zoneinfo:
                    dt_local = dt_utc.astimezone(tz)
                else:
                    dt_local = dt_utc + tz
                ts_local = dt_local.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                ts_local = raw_ts  # fallback without conversion

        try:
            wi = json.loads(r['worker_info']) if r['worker_info'] else {}
        except Exception:
            wi = {}

        alerts.append({
            'id': r['id'],
            'user_id': r['user_id'],
            'user_name': r['user_name'],
            'city': r['city'],
            'locality': r['locality'],
            'timestamp': ts_local,         # now in IST for UI
            'timestamp_utc': raw_ts,       # optional: keep original for debugging
            'latitude': r['latitude'],
            'longitude': r['longitude'],
            'worker': wi
        })

    return jsonify({'alerts': alerts})

@app.route('/admin/clear_sos')
@login_required
def admin_clear_sos():
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    conn = get_db_connection()
    conn.execute('DELETE FROM sos_alerts')
    conn.commit()
    conn.close()
    flash('All SOS alerts cleared.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/create_admin')
def create_admin():
    conn = get_db_connection()
    exist = conn.execute('SELECT id FROM users WHERE email = ?', ('admin@findmyworker.com',)).fetchone()
    if exist:
        conn.close()
        flash('Admin user already exists!', 'info')
        return redirect(url_for('login'))
    pw = generate_password_hash('admin123')
    conn.execute('''
        INSERT INTO users (name, email, password, phone, address, city, locality, user_type, is_premium)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('Admin User', 'admin@findmyworker.com', pw, '9999999999', 'Admin Address', 'Admin City', 'Admin Locality', 'admin', 1))
    conn.commit()
    conn.close()
    flash('Admin user created! Email: admin@findmyworker.com, Password: admin123', 'success')
    return redirect(url_for('login'))

# Add near other imports (top of app.py)
# from faker import Faker  # uncomment if you prefer a global import

@app.route('/admin/seed_workers')
@login_required
def admin_seed_workers():
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    try:
        from faker import Faker
    except Exception as e:
        return jsonify({'error': f'Faker not installed: {e}'}), 500

    fake = Faker('en_IN')  # Indian names/addresses
    count = int(request.args.get('count', 50))

    conn = get_db_connection()
    cur = conn.cursor()

    # Available service categories to sample as skills
    cats = [r['name'] for r in conn.execute('SELECT name FROM service_categories').fetchall()]

    inserted = 0
    for _ in range(count):
        try:
            name = fake.name()
            email = fake.unique.email()
            phone = fake.msisdn()[-10:]  # 10-digit
            address = fake.street_address()
            city = session.get('user_city') or 'Kalyan'
            locality = session.get('user_locality') or 'KDMC'

            # Create user row
            pwd_hash = generate_password_hash('worker123')
            cur.execute('''
                INSERT INTO users (email, password, name, phone, address, city, locality, user_type, loyalty_points, is_premium)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, pwd_hash, name, phone, address, city, locality, 'worker', 0, 0))
            user_id = cur.lastrowid

            # Create worker row
            if cats:
                skills = ', '.join(fake.random_elements(elements=cats, unique=False, length=min(2, len(cats))))
            else:
                skills = 'General'

            experience = fake.random_int(min=1, max=15)
            hourly_rate = fake.random_element(elements=[250, 300, 350, 400, 450, 500, 600, 700])
            description = fake.sentence(nb_words=12)
            # rating = round(fake.random_number(digits=1, fix_len=False) / 2 + 3.5, 1)
            # rating = min(5.0, max(3.0, rating))
            # total_jobs = fake.random_int(min=0, max=500)
            availability = 'available'
            # certifications = 'verified' if fake.random_int(0, 100) < 40 else ''
            # police_verified = 1 if fake.random_int(0, 100) < 60 else 0
            # eco_friendly = 1 if fake.random_int(0, 100) < 30 else 0
            # vaccination_status = fake.random_element(elements=['fully_vaccinated', 'partially_vaccinated', 'not_disclosed'])

            cur.execute('''
                INSERT INTO workers (
                    user_id, skills, experience, hourly_rate, description,
                    total_jobs, availability,
                    current_latitude, current_longitude
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, skills, experience, float(hourly_rate), description,
                total_jobs, availability,
                None, None  # set to real coords later if needed
            ))
            inserted += 1
        except Exception:
            # Continue on duplicate email or transient errors
            conn.rollback()
            continue

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'inserted': inserted, 'default_password': 'worker123'})

# Add to app.py (admin-only): seed coordinates near a center
@app.route('/admin/seed_worker_locations')
@login_required
def admin_seed_worker_locations():
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    import math, random
    try:
        lat0 = float(request.args.get('lat', '19.2183'))   # Kalyan default
        lon0 = float(request.args.get('lon', '73.1645'))
        radius_km = float(request.args.get('radius_km', '8'))
    except ValueError:
        return jsonify({'error': 'Invalid lat/lon/radius'}), 400

    def sample_point(latc, lonc, rkm):
        # uniform in circle of radius rkm
        ang = random.uniform(0, 2*math.pi)
        dist_m = rkm * 1000 * math.sqrt(random.random())
        dlat = (dist_m * math.cos(ang)) / 111000.0
        dlon = (dist_m * math.sin(ang)) / (111000.0 * math.cos(math.radians(latc)))
        return latc + dlat, lonc + dlon

    conn = get_db_connection()
    cur = conn.cursor()
    rows = conn.execute('''
        SELECT id, current_latitude, current_longitude
        FROM workers
        WHERE current_latitude IS NULL OR current_longitude IS NULL
    ''').fetchall()

    updated = 0
    for r in rows:
        lat, lon = sample_point(lat0, lon0, radius_km)
        cur.execute('''
            UPDATE workers
            SET current_latitude = ?, current_longitude = ?, last_location_update = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (lat, lon, r['id']))
        updated += 1

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'updated': updated, 'center': {'lat': lat0, 'lon': lon0}, 'radius_km': radius_km})

from collections import defaultdict

@app.route('/admin/assign_random_localities', methods=['POST'])
@login_required
def admin_assign_random_localities():
    # Admin guard
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    # Optional query params: limit (default 50), offset (default 0), update_coords (default true)
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        update_coords = request.args.get('update_coords', 'true').lower() != 'false'
    except ValueError:
        return jsonify({'error': 'Invalid limit/offset'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # See if a 'localities' table with coordinates exists (added in previous step)
    has_localities = False
    try:
        exists = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='localities'"
        ).fetchone()
        if exists:
            has_localities = True
    except Exception:
        has_localities = False

    # Pick target workers: join users for city/locality update
    rows = cur.execute('''
        SELECT w.id AS worker_id, u.id AS user_id
        FROM workers w
        JOIN users u ON w.user_id = u.id
        ORDER BY u.id
        LIMIT ? OFFSET ?
    ''', (limit, offset)).fetchall()

    assigned = defaultdict(int)
    updated = 0

    for r in rows:
        loc = random.choice(LOCALITY_CHOICES)
        # Update user's city/locality; keep city as 'Thane' umbrella district
        cur.execute(
            "UPDATE users SET city = ?, locality = ? WHERE id = ?",
            ('Thane', loc, r['user_id'])
        )

        if update_coords and has_localities:
            locrow = cur.execute(
                "SELECT latitude, longitude FROM localities WHERE name = ?",
                (loc,)
            ).fetchone()
            if locrow and locrow['latitude'] is not None and locrow['longitude'] is not None:
                cur.execute(
                    '''UPDATE workers
                       SET current_latitude = ?, current_longitude = ?, last_location_update = CURRENT_TIMESTAMP
                       WHERE id = ?''',
                    (locrow['latitude'], locrow['longitude'], r['worker_id'])
                )

        assigned[loc] += 1
        updated += 1

    conn.commit()
    conn.close()

    # Return a small distribution summary
    distribution = [{'locality': k, 'count': v} for k, v in sorted(assigned.items())]
    return jsonify({
        'success': True,
        'updated_workers': updated,
        'limit': limit,
        'offset': offset,
        'used_localities': LOCALITY_CHOICES,
        'distribution': distribution
    })

@app.route('/worker_rating/<int:worker_id>')
def worker_rating(worker_id):
    conn = get_db_connection()

    result = conn.execute('''
        SELECT AVG(rating) as avg_rating, COUNT(*) as total
        FROM reviews
        WHERE worker_id = ?
    ''', (worker_id,)).fetchone()

    avg_rating = result['avg_rating'] if result['avg_rating'] else 0.0
    total_reviews = result['total']

    conn.close()

    return jsonify({
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews
    })

@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    data = request.get_json()

    request_id = data.get('request_id')
    worker_id = data.get('worker_id')
    rating = data.get('rating')
    review = data.get('review')
    user_id = session['user_id']

    conn = get_db_connection()

    # prevent duplicate review (important)
    existing = conn.execute('''
        SELECT id FROM reviews WHERE request_id = ?
    ''', (request_id,)).fetchone()

    if existing:
        return jsonify({'error': 'Review already submitted'}), 400

    conn.execute('''
        INSERT INTO reviews (request_id, user_id, worker_id, rating, review)
        VALUES (?, ?, ?, ?, ?)
    ''', (request_id, user_id, worker_id, rating, review))

    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/get_reviews/<int:worker_id>')
def get_reviews(worker_id):
    conn = get_db_connection()

    reviews = conn.execute('''
        SELECT r.rating, r.review, r.created_at, u.name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.worker_id = ?
        ORDER BY r.created_at DESC
    ''', (worker_id,)).fetchall()

    conn.close()

    return jsonify({
        'success': True,
        'reviews': [dict(r) for r in reviews]
    })




# -------------------------
# Entrypoint
# -------------------------
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    init_db()
    print("=" * 60)
    print("ENHANCED FLASK SERVICE PORTAL")
    print("=" * 60)
    print("- AI-based recommendations")
    print("- Dynamic pricing with breakdown")
    print("- Real-time service tracking")
    print("- Loyalty rewards & gamification")
    print("- Eco-friendly & verified worker filters")
    print("- Group booking discounts")
    print("- Worker training portal")
    print("- Earnings dashboard")
    print("- 🤖 AI Chatbot Support")
    print("=" * 60)
    print("\nAccess at: http://127.0.0.1:5000")
    print("Press CTRL+C to stop")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
