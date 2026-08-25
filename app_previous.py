# from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime, timedelta
# import sqlite3
# import os
# import json
# from functools import wraps
# import random
# import secrets

# app = Flask(__name__)
# # Generate a secure secret key
# app.secret_key = secrets.token_hex(32)

# # Database initialization
# def init_db():
#     conn = sqlite3.connect('service_portal.db')
#     cursor = conn.cursor()
    
#     # Users table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             email TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL,
#             name TEXT NOT NULL,
#             phone TEXT,
#             address TEXT,
#             city TEXT,
#             user_type TEXT NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
    
#     # Workers table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS workers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER,
#             skills TEXT NOT NULL,
#             experience INTEGER,
#             hourly_rate REAL,
#             description TEXT,
#             rating REAL DEFAULT 0.0,
#             total_jobs INTEGER DEFAULT 0,
#             availability TEXT DEFAULT 'available',
#             certifications TEXT,
#             FOREIGN KEY (user_id) REFERENCES users (id)
#         )
#     ''')
    
#     # Service requests table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS service_requests (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER,
#             worker_id INTEGER,
#             service_type TEXT NOT NULL,
#             description TEXT,
#             location TEXT,
#             preferred_date TEXT,
#             preferred_time TEXT,
#             budget REAL,
#             status TEXT DEFAULT 'pending',
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (user_id) REFERENCES users (id),
#             FOREIGN KEY (worker_id) REFERENCES workers (id)
#         )
#     ''')
    
#     # Reviews table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS reviews (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             request_id INTEGER,
#             user_id INTEGER,
#             worker_id INTEGER,
#             rating INTEGER,
#             review TEXT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (request_id) REFERENCES service_requests (id),
#             FOREIGN KEY (user_id) REFERENCES users (id),
#             FOREIGN KEY (worker_id) REFERENCES workers (id)
#         )
#     ''')
    
#     # Subscription plans table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS subscriptions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER,
#             plan_type TEXT,
#             start_date TEXT,
#             end_date TEXT,
#             status TEXT DEFAULT 'active',
#             FOREIGN KEY (user_id) REFERENCES users (id)
#         )
#     ''')
    
#     conn.commit()
#     conn.close()

# # Helper functions
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect(url_for('login'))
#         return f(*args, **kwargs)
#     return decorated_function

# def get_db_connection():
#     conn = sqlite3.connect('service_portal.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# def get_seasonal_recommendations():
#     """AI-based seasonal service recommendations"""
#     current_month = datetime.now().month
#     recommendations = {
#         'summer': ['AC Repair', 'Pool Cleaning', 'Lawn Care', 'Pest Control'],
#         'winter': ['Heating Repair', 'Home Insulation', 'Carpet Cleaning', 'Interior Painting'],
#         'monsoon': ['Waterproofing', 'Drainage Cleaning', 'Electrical Safety Check', 'Mold Treatment'],
#         'spring': ['Deep Cleaning', 'Garden Setup', 'Home Organization', 'Appliance Maintenance']
#     }
    
#     if current_month in [6, 7, 8]:
#         return recommendations['summer']
#     elif current_month in [12, 1, 2]:
#         return recommendations['winter']
#     elif current_month in [7, 8, 9]:
#         return recommendations['monsoon']
#     else:
#         return recommendations['spring']

# def calculate_dynamic_pricing(base_price, demand_factor=1.0):
#     """Dynamic pricing based on demand"""
#     surge_multiplier = max(1.0, min(2.0, demand_factor))
#     return round(base_price * surge_multiplier, 2)

# # Routes
# @app.route('/')
# def index():
#     if 'user_id' in session:
#         if session['user_type'] == 'worker':
#             return redirect(url_for('worker_dashboard'))
#         else:
#             return redirect(url_for('user_dashboard'))
#     return render_template('index.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         name = request.form['name']
#         phone = request.form['phone']
#         address = request.form['address']
#         city = request.form['city']
#         user_type = request.form['user_type']
        
#         hashed_password = generate_password_hash(password)
        
#         conn = get_db_connection()
#         try:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 INSERT INTO users (email, password, name, phone, address, city, user_type)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             ''', (email, hashed_password, name, phone, address, city, user_type))
            
#             user_id = cursor.lastrowid
            
#             if user_type == 'worker':
#                 skills = request.form.get('skills', '')
#                 experience = int(request.form.get('experience', 0))
#                 hourly_rate = float(request.form.get('hourly_rate', 0))
#                 description = request.form.get('description', '')
                
#                 cursor.execute('''
#                     INSERT INTO workers (user_id, skills, experience, hourly_rate, description)
#                     VALUES (?, ?, ?, ?, ?)
#                 ''', (user_id, skills, experience, hourly_rate, description))
            
#             conn.commit()
#             flash('Registration successful! Please login.')
#             return redirect(url_for('login'))
            
#         except sqlite3.IntegrityError:
#             flash('Email already exists!')
#         finally:
#             conn.close()
    
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
        
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
#         conn.close()
        
#         if user and check_password_hash(user['password'], password):
#             session['user_id'] = user['id']
#             session['user_type'] = user['user_type']
#             session['user_name'] = user['name']
#             session['user_city'] = user['city']
            
#             if user['user_type'] == 'worker':
#                 return redirect(url_for('worker_dashboard'))
#             else:
#                 return redirect(url_for('user_dashboard'))
#         else:
#             flash('Invalid email or password!')
    
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))

# @app.route('/user_dashboard')
# @login_required
# def user_dashboard():
#     if session['user_type'] != 'user':
#         return redirect(url_for('worker_dashboard'))
    
#     conn = get_db_connection()
    
#     recent_requests = conn.execute('''
#         SELECT sr.*, w.skills, u.name as worker_name
#         FROM service_requests sr
#         LEFT JOIN workers w ON sr.worker_id = w.id
#         LEFT JOIN users u ON w.user_id = u.id
#         WHERE sr.user_id = ?
#         ORDER BY sr.created_at DESC
#         LIMIT 5
#     ''', (session['user_id'],)).fetchall()
    
#     seasonal_services = get_seasonal_recommendations()
    
#     local_workers = conn.execute('''
#         SELECT w.*, u.name, u.city
#         FROM workers w
#         JOIN users u ON w.user_id = u.id
#         WHERE u.city = ? AND w.availability = 'available'
#         ORDER BY w.rating DESC
#         LIMIT 8
#     ''', (session['user_city'],)).fetchall()
    
#     conn.close()
    
#     return render_template('user_dashboard.html', 
#                          recent_requests=recent_requests,
#                          seasonal_services=seasonal_services,
#                          local_workers=local_workers)

# @app.route('/worker_dashboard')
# @login_required
# def worker_dashboard():
#     if session['user_type'] != 'worker':
#         return redirect(url_for('user_dashboard'))
    
#     conn = get_db_connection()
    
#     worker = conn.execute('''
#         SELECT w.*, u.name, u.email, u.phone
#         FROM workers w
#         JOIN users u ON w.user_id = u.id
#         WHERE w.user_id = ?
#     ''', (session['user_id'],)).fetchone()
    
#     pending_requests = conn.execute('''
#         SELECT sr.*, u.name as customer_name, u.phone as customer_phone
#         FROM service_requests sr
#         JOIN users u ON sr.user_id = u.id
#         WHERE sr.worker_id = ? AND sr.status = 'pending'
#         ORDER BY sr.created_at DESC
#     ''', (worker['id'],)).fetchall()
    
#     earnings = conn.execute('''
#         SELECT SUM(budget) as total_earnings, COUNT(*) as completed_jobs
#         FROM service_requests
#         WHERE worker_id = ? AND status = 'completed'
#     ''', (worker['id'],)).fetchone()
    
#     conn.close()
    
#     return render_template('worker_dashboard.html',
#                          worker=worker,
#                          pending_requests=pending_requests,
#                          earnings=earnings)

# @app.route('/search_workers')
# @login_required
# def search_workers():
#     service_type = request.args.get('service', '')
#     city = request.args.get('city', session.get('user_city', ''))
    
#     conn = get_db_connection()
    
#     if service_type:
#         workers = conn.execute('''
#             SELECT w.*, u.name, u.city, u.phone
#             FROM workers w
#             JOIN users u ON w.user_id = u.id
#             WHERE (w.skills LIKE ? OR ? = '') 
#             AND (u.city = ? OR ? = '')
#             AND w.availability = 'available'
#             ORDER BY w.rating DESC, w.total_jobs DESC
#         ''', (f'%{service_type}%', service_type, city, city)).fetchall()
#     else:
#         workers = conn.execute('''
#             SELECT w.*, u.name, u.city, u.phone
#             FROM workers w
#             JOIN users u ON w.user_id = u.id
#             WHERE u.city = ? AND w.availability = 'available'
#             ORDER BY w.rating DESC, w.total_jobs DESC
#         ''', (city,)).fetchall()
    
#     conn.close()
    
#     return render_template('search_workers.html', workers=workers, service_type=service_type)

# @app.route('/book_service/<int:worker_id>', methods=['GET', 'POST'])
# @login_required
# def book_service(worker_id):
#     if session['user_type'] != 'user':
#         return redirect(url_for('worker_dashboard'))
    
#     conn = get_db_connection()
    
#     if request.method == 'POST':
#         service_type = request.form['service_type']
#         description = request.form['description']
#         location = request.form['location']
#         preferred_date = request.form['preferred_date']
#         preferred_time = request.form['preferred_time']
#         budget = float(request.form['budget'])
        
#         demand_factor = random.uniform(1.0, 1.5)
#         final_budget = calculate_dynamic_pricing(budget, demand_factor)
        
#         conn.execute('''
#             INSERT INTO service_requests 
#             (user_id, worker_id, service_type, description, location, preferred_date, preferred_time, budget)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (session['user_id'], worker_id, service_type, description, location, 
#               preferred_date, preferred_time, final_budget))
        
#         conn.commit()
#         conn.close()
        
#         flash('Service request sent successfully!')
#         return redirect(url_for('user_dashboard'))
    
#     worker = conn.execute('''
#         SELECT w.*, u.name, u.city
#         FROM workers w
#         JOIN users u ON w.user_id = u.id
#         WHERE w.id = ?
#     ''', (worker_id,)).fetchone()
    
#     conn.close()
    
#     if not worker:
#         flash('Worker not found!')
#         return redirect(url_for('search_workers'))
    
#     # Pass datetime to template
#     return render_template('book_service.html', worker=worker, datetime=datetime)

# @app.route('/manage_request/<int:request_id>/<action>')
# @login_required
# def manage_request(request_id, action):
#     if session['user_type'] != 'worker':
#         return redirect(url_for('user_dashboard'))
    
#     conn = get_db_connection()
    
#     if action in ['accept', 'decline', 'complete']:
#         status_map = {
#             'accept': 'accepted',
#             'decline': 'declined',
#             'complete': 'completed'
#         }
        
#         conn.execute('''
#             UPDATE service_requests 
#             SET status = ? 
#             WHERE id = ?
#         ''', (status_map[action], request_id))
        
#         if action == 'complete':
#             conn.execute('''
#                 UPDATE workers 
#                 SET total_jobs = total_jobs + 1
#                 WHERE user_id = ?
#             ''', (session['user_id'],))
        
#         conn.commit()
#         flash(f'Request {action}ed successfully!')
    
#     conn.close()
#     return redirect(url_for('worker_dashboard'))

# @app.route('/subscription_plans')
# @login_required
# def subscription_plans():
#     if session['user_type'] != 'user':
#         return redirect(url_for('worker_dashboard'))
    
#     plans = [
#         {
#             'name': 'Basic',
#             'price': 99,
#             'duration': 'monthly',
#             'benefits': ['10% discount on all services', 'Priority booking', '24/7 support']
#         },
#         {
#             'name': 'Premium',
#             'price': 299,
#             'duration': 'monthly',
#             'benefits': ['20% discount on all services', 'Priority booking', 'Free service once a month', 'Emergency SOS feature']
#         },
#         {
#             'name': 'Annual',
#             'price': 2999,
#             'duration': 'yearly',
#             'benefits': ['25% discount on all services', 'Priority booking', '2 free services per month', 'Emergency SOS feature', 'AR/VR preview access']
#         }
#     ]
    
#     return render_template('subscription_plans.html', plans=plans)

# @app.route('/worker_training')
# @login_required
# def worker_training():
#     if session['user_type'] != 'worker':
#         return redirect(url_for('user_dashboard'))
    
#     courses = [
#         {
#             'title': 'Customer Service Excellence',
#             'duration': '2 hours',
#             'description': 'Learn how to provide outstanding customer service and build long-term relationships.',
#             'certification': True
#         },
#         {
#             'title': 'Safety Protocols and Best Practices',
#             'duration': '3 hours',
#             'description': 'Essential safety measures for different types of service work.',
#             'certification': True
#         },
#         {
#             'title': 'Digital Marketing for Service Professionals',
#             'duration': '4 hours',
#             'description': 'How to market your services online and build your personal brand.',
#             'certification': False
#         },
#         {
#             'title': 'Time Management and Scheduling',
#             'duration': '1.5 hours',
#             'description': 'Optimize your work schedule and increase productivity.',
#             'certification': False
#         }
#     ]
    
#     return render_template('worker_training.html', courses=courses)

# @app.route('/api/recommendations')
# @login_required
# def api_recommendations():
#     user_city = session.get('user_city', '')
    
#     conn = get_db_connection()
    
#     user_history = conn.execute('''
#         SELECT service_type, COUNT(*) as frequency
#         FROM service_requests
#         WHERE user_id = ?
#         GROUP BY service_type
#         ORDER BY frequency DESC
#         LIMIT 5
#     ''', (session['user_id'],)).fetchall()
    
#     trending = conn.execute('''
#         SELECT service_type, COUNT(*) as requests
#         FROM service_requests sr
#         JOIN users u ON sr.user_id = u.id
#         WHERE u.city = ?
#         AND sr.created_at >= date('now', '-30 days')
#         GROUP BY service_type
#         ORDER BY requests DESC
#         LIMIT 5
#     ''', (user_city,)).fetchall()
    
#     conn.close()
    
#     seasonal = get_seasonal_recommendations()
    
#     recommendations = {
#         'personal': [dict(row) for row in user_history],
#         'trending': [dict(row) for row in trending],
#         'seasonal': seasonal
#     }
    
#     return jsonify(recommendations)

# # Run the application
# if __name__ == '__main__':
#     # Create templates directory first
#     os.makedirs('templates', exist_ok=True)
    
#     # Initialize database
#     init_db()
    
#     print("=" * 50)
#     print("Flask Service Portal Starting...")
#     print("=" * 50)
#     print("Database initialized: service_portal.db")
#     print("Templates directory created")
#     print("\nAccess the application at: http://127.0.0.1:5000")
#     print("\nPress CTRL+C to stop the server")
#     print("=" * 50)
    
#     app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import json
from functools import wraps
import random
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Enhanced Database initialization
def init_db():
    conn = sqlite3.connect('service_portal.db')
    cursor = conn.cursor()
    
    # Add migration for location columns if they don't exist
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN current_latitude REAL")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN current_longitude REAL")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN last_location_update TIMESTAMP")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN preferred_radius INTEGER DEFAULT 10")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    
    # Users table
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
            is_premium BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Workers table with enhanced fields
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
            police_verified BOOLEAN DEFAULT 0,
            vaccination_status TEXT,
            eco_friendly BOOLEAN DEFAULT 0,
            profile_image TEXT,
            current_latitude REAL,
            current_longitude REAL,
            last_location_update TIMESTAMP,
            preferred_radius INTEGER DEFAULT 10,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Service requests with tracking
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
            is_group_booking BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (worker_id) REFERENCES workers (id)
        )
    ''')
    
    # Reviews table
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
    
    # Subscription plans
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
    
    # Service categories with seasonal data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT,
            seasonal_peak TEXT,
            eco_friendly_available BOOLEAN DEFAULT 0,
            base_price REAL
        )
    ''')
    
    # Insert default service categories
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
    
    cursor.execute('SELECT COUNT(*) FROM service_categories')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO service_categories (name, icon, seasonal_peak, eco_friendly_available, base_price)
            VALUES (?, ?, ?, ?, ?)
        ''', categories)
    
    conn.commit()
    conn.close()

# Helper functions
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
    conn.execute('PRAGMA journal_mode=WAL')  # Enable WAL mode for better concurrency
    return conn

def get_seasonal_recommendations():
    """AI-based seasonal service recommendations"""
    current_month = datetime.now().month
    conn = get_db_connection()
    
    season = 'all'
    if current_month in [3, 4, 5, 6]:
        season = 'summer'
    elif current_month in [12, 1, 2]:
        season = 'winter'
    elif current_month in [7, 8, 9]:
        season = 'monsoon'
    else:
        season = 'spring'
    
    # Get services that peak in this season
    seasonal_services = conn.execute('''
        SELECT name, icon FROM service_categories 
        WHERE seasonal_peak = ? OR seasonal_peak = 'all'
        LIMIT 6
    ''', (season,)).fetchall()
    
    conn.close()
    return [dict(s) for s in seasonal_services]

def calculate_dynamic_pricing(base_price, service_type, date, time):
    """Dynamic pricing with detailed breakdown"""
    # Check demand based on time and date
    hour = int(time.split(':')[0])
    is_peak_hour = 9 <= hour <= 18
    is_weekend = datetime.strptime(date, '%Y-%m-%d').weekday() >= 5
    
    # Base surge calculation
    surge_multiplier = 1.0
    if is_peak_hour:
        surge_multiplier += 0.2
    if is_weekend:
        surge_multiplier += 0.15
    
    # Random demand factor (simulating real-time demand)
    surge_multiplier += random.uniform(0, 0.3)
    surge_multiplier = min(surge_multiplier, 2.0)
    
    # Calculate costs
    labor_cost = round(base_price * surge_multiplier, 2)
    material_cost = round(base_price * 0.3, 2)  # 30% of base for materials
    subtotal = labor_cost + material_cost
    tax = round(subtotal * 0.18, 2)  # 18% GST
    final_price = round(subtotal + tax, 2)
    
    return {
        'base_price': base_price,
        'labor_cost': labor_cost,
        'material_cost': material_cost,
        'tax': tax,
        'surge_multiplier': round(surge_multiplier, 2),
        'final_price': final_price
    }

def get_ai_recommendations(user_id):
    """AI-based personalized recommendations"""
    conn = get_db_connection()
    
    # User's booking history
    history = conn.execute('''
        SELECT service_type, COUNT(*) as frequency
        FROM service_requests
        WHERE user_id = ?
        GROUP BY service_type
        ORDER BY frequency DESC
        LIMIT 3
    ''', (user_id,)).fetchall()
    
    # Trending in user's locality
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
    
    # Seasonal recommendations
    seasonal = get_seasonal_recommendations()
    
    conn.close()
    
    return {
        'personal': [dict(h) for h in history],
        'trending': [dict(t) for t in trending],
        'seasonal': seasonal
    }

def get_chatbot_response(message, user_id=None):
    """AI chatbot for handling user queries"""
    message_lower = message.lower()
    
    # Greetings
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return {
            'response': "Hello! 👋 I'm your service assistant. I can help you with:\n• Finding workers\n• Booking services\n• Pricing information\n• Tracking your orders\n• Account queries\n\nWhat would you like to know?",
            'suggestions': ['Find a plumber', 'Check pricing', 'Track my order', 'View services']
        }
    
    # Service inquiries
    elif 'service' in message_lower or 'worker' in message_lower or 'find' in message_lower:
        conn = get_db_connection()
        categories = conn.execute('SELECT name FROM service_categories LIMIT 6').fetchall()
        conn.close()
        
        services = ', '.join([c['name'] for c in categories])
        return {
            'response': f"We offer various services including: {services} and more!\n\nWould you like to:\n• Browse workers by category\n• Search in your area\n• Get price estimates",
            'suggestions': ['Browse plumbers', 'Search nearby', 'Get pricing']
        }
    
    # Pricing queries
    elif 'price' in message_lower or 'cost' in message_lower or 'rate' in message_lower:
        return {
            'response': "Our pricing is dynamic and transparent:\n• Base service cost\n• Labor charges (varies by demand)\n• Material costs\n• 18% GST\n\n💰 Premium members get 10% off!\n🎉 Group bookings get 15% discount!\n\nWant to get an estimate for a specific service?",
            'suggestions': ['Plumbing cost', 'Electrician rates', 'Cleaning prices']
        }
    
    # Booking queries
    elif 'book' in message_lower or 'appointment' in message_lower or 'schedule' in message_lower:
        return {
            'response': "Booking is easy! Here's how:\n1. Browse or search for workers\n2. Select a worker you like\n3. Choose date & time\n4. Get instant price estimate\n5. Confirm booking\n\n✅ Real-time tracking included!\n🎁 Earn loyalty points on every booking!",
            'suggestions': ['Browse services', 'My bookings', 'Track order']
        }
    
    # Tracking queries
    elif 'track' in message_lower or 'status' in message_lower or 'order' in message_lower:
        if user_id:
            conn = get_db_connection()
            active = conn.execute('''
                SELECT COUNT(*) as count FROM service_requests 
                WHERE user_id = ? AND status IN ('pending', 'accepted')
            ''', (user_id,)).fetchone()
            conn.close()
            
            if active['count'] > 0:
                return {
                    'response': f"You have {active['count']} active booking(s).\n\n📍 Track in real-time:\n• Worker location\n• ETA updates\n• Live status\n\nGo to 'My Dashboard' to track your orders!",
                    'suggestions': ['View dashboard', 'Contact worker']
                }
        
        return {
            'response': "Track your service in real-time!\n• Worker assigned notification\n• Live location tracking\n• ETA updates\n• Arrival alerts\n\nLogin to view your active bookings.",
            'suggestions': ['Login', 'View services']
        }
    
    # Loyalty program
    elif 'loyalty' in message_lower or 'points' in message_lower or 'reward' in message_lower:
        return {
            'response': "🎁 Loyalty Rewards Program:\n\n• Earn 1 point per ₹10 spent\n• Redeem for discounts & free services\n• Level up: Bronze → Silver → Gold → Platinum\n\nRewards available:\n• ₹100 off (500 points)\n• Free cleaning (1500 points)\n• Premium upgrade (3000 points)",
            'suggestions': ['My points', 'View rewards', 'Premium plans']
        }
    
    # Premium/Subscription
    elif 'premium' in message_lower or 'subscription' in message_lower or 'plan' in message_lower:
        return {
            'response': "⭐ Premium Benefits:\n\n📦 Basic (₹99/month):\n• 10% discount • Priority booking\n\n👑 Premium (₹299/month):\n• 20% discount • 1 free service/month\n\n💎 Annual (₹2999/year):\n• 25% discount • 2 free services/month • AR preview\n\nAll plans include 24/7 support!",
            'suggestions': ['View plans', 'Subscribe now', 'Compare benefits']
        }
    
    # Worker-specific queries
    elif 'become worker' in message_lower or 'join as worker' in message_lower:
        return {
            'response': "Join as a Service Professional! 🛠️\n\nBenefits:\n• Flexible schedule\n• Competitive earnings\n• Free training & certifications\n• Insurance coverage\n• Weekly payouts\n\nRequirements:\n• Skill proficiency\n• Police verification\n• Vaccination certificate",
            'suggestions': ['Register as worker', 'View training', 'Earnings info']
        }
    
    # Safety & verification
    elif 'safe' in message_lower or 'verify' in message_lower or 'trust' in message_lower:
        return {
            'response': "Your safety is our priority! 🔒\n\n✅ All workers are:\n• Police verified\n• Background checked\n• Skill certified\n• Rated by customers\n• Insured\n\n🛡️ Filter by 'Verified Only' when booking!",
            'suggestions': ['Verified workers', 'Safety guidelines']
        }
    
    # Help/Support
    elif 'help' in message_lower or 'support' in message_lower or 'contact' in message_lower:
        return {
            'response': "We're here to help! 📞\n\n• Chat: Available 24/7 (you're chatting now!)\n• Email: support@findmyworker.com\n• Phone: 1800-123-4567\n• Emergency: SOS button in app\n\nPremium members get priority support!",
            'suggestions': ['Report issue', 'FAQs', 'Contact support']
        }
    
    # Default response
    else:
        return {
            'response': "I'm here to help! I can assist with:\n\n🔍 Finding & booking services\n💰 Pricing & estimates\n📍 Tracking orders\n🎁 Loyalty rewards\n⭐ Premium plans\n🛡️ Safety & verification\n\nWhat would you like to know?",
            'suggestions': ['Browse services', 'Get pricing', 'My account', 'Help']
        }

@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    """Chatbot API endpoint"""
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        # Get response from chatbot
        response = get_chatbot_response(message, session.get('user_id'))
        
        # Store chat history (optional - you can add a chat_history table)
        return jsonify({
            'success': True,
            'response': response['response'],
            'suggestions': response.get('suggestions', []),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chatbot_widget')
@login_required
def chatbot_widget():
    """Render chatbot interface"""
    return render_template('chatbot.html')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers using Haversine formula"""
    import math
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def get_nearby_workers(customer_lat, customer_lon, service_type, radius_km=10):
    """Get workers near customer location for specific service"""
    conn = get_db_connection()
    
    # Get all available workers for the service type
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
    
    nearby_workers = []
    for worker in workers:
        if worker['current_latitude'] and worker['current_longitude']:
            distance = calculate_distance(
                customer_lat, customer_lon,
                worker['current_latitude'], worker['current_longitude']
            )
            
            if distance <= radius_km:
                worker_dict = dict(worker)
                worker_dict['distance_km'] = round(distance, 2)
                worker_dict['distance_m'] = round(distance * 1000, 0)
                nearby_workers.append(worker_dict)
    
    # Sort by distance (closest first)
    nearby_workers.sort(key=lambda x: x['distance_km'])
    
    conn.close()
    return nearby_workers

def update_worker_location(worker_id, latitude, longitude):
    """Update worker's current location"""
    conn = get_db_connection()
    
    conn.execute('''
        UPDATE workers 
        SET current_latitude = ?, current_longitude = ?, last_location_update = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (latitude, longitude, worker_id))
    
    conn.commit()
    conn.close()

def award_loyalty_points(user_id, points, conn=None):
    """Award loyalty points to user"""
    if conn is None:
        conn = get_db_connection()
        conn.execute('''
            UPDATE users 
            SET loyalty_points = loyalty_points + ? 
            WHERE id = ?
        ''', (points, user_id))
        conn.commit()
        conn.close()
    else:
        conn.execute('''
            UPDATE users 
            SET loyalty_points = loyalty_points + ? 
            WHERE id = ?
        ''', (points, user_id))

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        if session['user_type'] == 'worker':
            return redirect(url_for('worker_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
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
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (email, password, name, phone, address, city, locality, user_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, hashed_password, name, phone, address, city, locality, user_type))
            
            user_id = cursor.lastrowid
            
            if user_type == 'worker':
                skills = request.form.get('skills', '')
                experience = int(request.form.get('experience', 0))
                hourly_rate = float(request.form.get('hourly_rate', 0))
                description = request.form.get('description', '')
                police_verified = request.form.get('police_verified', 'off') == 'on'
                eco_friendly = request.form.get('eco_friendly', 'off') == 'on'
                vaccination_status = request.form.get('vaccination_status', 'not_disclosed')
                
                cursor.execute('''
                    INSERT INTO workers (user_id, skills, experience, hourly_rate, description, 
                                       police_verified, eco_friendly, vaccination_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, skills, experience, hourly_rate, description, 
                     police_verified, eco_friendly, vaccination_status))
            
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError:
            flash('Email already exists!')
        finally:
            conn.close()
    
    # Get service categories for worker registration
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
            elif user['user_type'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password!')
    
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
    
    # Get AI recommendations
    recommendations = get_ai_recommendations(session['user_id'])
    
    # Get all service categories
    service_categories = conn.execute('''
        SELECT * FROM service_categories ORDER BY name
    ''').fetchall()
    
    # Recent requests with tracking
    recent_requests = conn.execute('''
        SELECT sr.*, w.skills, u.name as worker_name, u.phone as worker_phone
        FROM service_requests sr
        LEFT JOIN workers w ON sr.worker_id = w.id
        LEFT JOIN users u ON w.user_id = u.id
        WHERE sr.user_id = ?
        ORDER BY sr.created_at DESC
        LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    # Top rated workers in locality
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
    
    return render_template('user_dashboard.html', 
                         recommendations=recommendations,
                         service_categories=service_categories,
                         recent_requests=recent_requests,
                         local_workers=local_workers)

    # --- SOS Alert Route ---
    @app.route('/sos_alert', methods=['POST'])
    @login_required
    def sos_alert():
        """Handle SOS alert from user dashboard"""
        user_id = session.get('user_id')
        user_name = session.get('user_name')
        user_city = session.get('user_city')
        user_locality = session.get('user_locality')
        data = request.get_json(force=True)
        user_latitude = data.get('latitude')
        user_longitude = data.get('longitude')
        try:
            conn = get_db_connection()
            # Get latest accepted service request for this user
            service_request = conn.execute('''
                SELECT sr.*, w.*, u.name as worker_name, u.email as worker_email, u.phone as worker_phone
                FROM service_requests sr
                JOIN workers w ON sr.worker_id = w.id
                JOIN users u ON w.user_id = u.id
                WHERE sr.user_id = ? AND sr.status = 'accepted'
                ORDER BY sr.created_at DESC LIMIT 1
            ''', (user_id,)).fetchone()

            # Prepare worker info if available
            worker_info = {}
            if service_request:
                worker_info = {
                    'worker_id': service_request['worker_id'],
                    'worker_name': service_request['worker_name'],
                    'worker_email': service_request['worker_email'],
                    'worker_phone': service_request['worker_phone'],
                    'worker_skills': service_request['skills'],
                    'worker_experience': service_request['experience'],
                    'worker_rating': service_request['rating'],
                    'worker_locality': service_request['locality'],
                    'worker_city': service_request['city']
                }

            # Log the SOS event with user, worker info, and location
            conn.execute('''
                INSERT INTO sos_alerts (user_id, user_name, city, locality, timestamp, worker_info, latitude, longitude)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
            ''', (user_id, user_name, user_city, user_locality, str(worker_info), user_latitude, user_longitude))
            conn.commit()
            conn.close()

            # Notify admin (example: print to console, replace with email logic)
            admin_message = f"SOS ALERT!\nUser: {user_name} (ID: {user_id})\nLocation: {user_city}, {user_locality}, Lat: {user_latitude}, Long: {user_longitude}\nWorker: {worker_info}\n"
            print(admin_message)  # Replace with email logic if needed

            return jsonify({'success': True, 'message': 'SOS alert sent and admin notified.'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/browse_services/<category>')
@login_required
def browse_services(category):
    """Browse workers by service category"""
    conn = get_db_connection()
    
    filters = request.args
    locality = filters.get('locality', session.get('user_locality', ''))
    eco_friendly = filters.get('eco_friendly') == 'true'
    verified_only = filters.get('verified_only') == 'true'
    min_rating = float(filters.get('min_rating', 0))
    
    query = '''
        SELECT w.*, u.name, u.city, u.locality, u.phone
        FROM workers w
        JOIN users u ON w.user_id = u.id
        WHERE w.skills LIKE ? 
        AND w.availability = 'available'
    '''
    params = [f'%{category}%']
    
    if locality:
        query += ' AND u.locality = ?'
        params.append(locality)
    
    if eco_friendly:
        query += ' AND w.eco_friendly = 1'
    
    if verified_only:
        query += ' AND w.police_verified = 1'
    
    if min_rating > 0:
        query += ' AND w.rating >= ?'
        params.append(min_rating)
    
    query += ' ORDER BY w.rating DESC, w.total_jobs DESC'
    
    workers = conn.execute(query, params).fetchall()
    
    # Get category info
    category_info = conn.execute('''
        SELECT * FROM service_categories WHERE name = ?
    ''', (category,)).fetchone()
    
    conn.close()
    
    return render_template('browse_services.html', 
                         workers=workers, 
                         category=category,
                         category_info=category_info,
                         filters=filters)

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
            
            # Get base price for service
            category = conn.execute('''
                SELECT base_price FROM service_categories WHERE name = ?
            ''', (service_type,)).fetchone()
            
            base_price = category['base_price'] if category else 500
            
            # Calculate dynamic pricing
            pricing = calculate_dynamic_pricing(base_price, service_type, preferred_date, preferred_time)
            
            # Apply discount for group booking
            if is_group_booking:
                pricing['final_price'] = round(pricing['final_price'] * 0.85, 2)  # 15% discount
            
            # Apply premium member discount
            if session.get('is_premium'):
                pricing['final_price'] = round(pricing['final_price'] * 0.9, 2)  # 10% discount
            
            conn.execute('''
                INSERT INTO service_requests 
                (user_id, worker_id, service_type, description, location, locality,
                 preferred_date, preferred_time, base_price, labor_cost, material_cost, 
                 tax, surge_multiplier, final_price, is_group_booking)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], worker_id, service_type, description, location, locality,
                  preferred_date, preferred_time, pricing['base_price'], pricing['labor_cost'],
                  pricing['material_cost'], pricing['tax'], pricing['surge_multiplier'],
                  pricing['final_price'], is_group_booking))
            
            # Award loyalty points
            points = int(pricing['final_price'] / 10)  # 1 point per ₹10
            award_loyalty_points(session['user_id'], points, conn)
            
            conn.commit()
            flash(f'Service request sent! You earned {points} loyalty points!')
            return redirect(url_for('user_dashboard'))
            
        except Exception as e:
            flash(f'Error booking service: {str(e)}', 'error')
            return redirect(url_for('user_dashboard'))
        finally:
            if conn:
                conn.close()
    
    # GET request - show booking form
    conn = None
    try:
        conn = get_db_connection()
        worker = conn.execute('''
            SELECT w.*, u.name, u.city, u.locality
            FROM workers w
            JOIN users u ON w.user_id = u.id
            WHERE w.id = ?
        ''', (worker_id,)).fetchone()
        
        if not worker:
            flash('Worker not found!')
            return redirect(url_for('user_dashboard'))
        
        return render_template('book_service.html', worker=worker, datetime=datetime)
        
    except Exception as e:
        flash(f'Error loading worker details: {str(e)}', 'error')
        return redirect(url_for('user_dashboard'))
    finally:
        if conn:
            conn.close()

@app.route('/track_service/<int:request_id>')
@login_required
def track_service(request_id):
    """Real-time service tracking simulation"""
    conn = get_db_connection()
    
    service_request = conn.execute('''
        SELECT sr.*, w.skills, u.name as worker_name, u.phone as worker_phone
        FROM service_requests sr
        JOIN workers w ON sr.worker_id = w.id
        JOIN users u ON w.user_id = u.id
        WHERE sr.id = ? AND sr.user_id = ?
    ''', (request_id, session['user_id'])).fetchone()
    
    conn.close()
    
    if not service_request:
        flash('Service request not found!')
        return redirect(url_for('user_dashboard'))
    
    # Simulate tracking statuses
    tracking_stages = [
        {'status': 'confirmed', 'message': 'Booking confirmed', 'icon': 'check-circle'},
        {'status': 'worker_assigned', 'message': 'Worker assigned', 'icon': 'user-check'},
        {'status': 'worker_started', 'message': 'Worker started journey', 'icon': 'route'},
        {'status': 'nearby', 'message': 'Worker nearby (5 min)', 'icon': 'map-marker-alt'},
        {'status': 'arrived', 'message': 'Worker arrived', 'icon': 'home'},
        {'status': 'in_progress', 'message': 'Service in progress', 'icon': 'tools'},
        {'status': 'completed', 'message': 'Service completed', 'icon': 'check-double'}
    ]
    
    return render_template('track_service.html', 
                         service_request=service_request,
                         tracking_stages=tracking_stages)

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
    """Loyalty and gamification page"""
    conn = get_db_connection()
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    # Calculate user level
    points = user['loyalty_points']
    level = 'Bronze'
    if points >= 5000:
        level = 'Platinum'
    elif points >= 2000:
        level = 'Gold'
    elif points >= 500:
        level = 'Silver'
    
    # Available rewards
    rewards = [
        {'name': '₹100 Off Coupon', 'points': 500, 'icon': 'ticket-alt'},
        {'name': '₹250 Off Coupon', 'points': 1000, 'icon': 'gift'},
        {'name': 'Free Cleaning Service', 'points': 1500, 'icon': 'broom'},
        {'name': '₹500 Off Coupon', 'points': 2000, 'icon': 'star'},
        {'name': 'Premium Upgrade (1 month)', 'points': 3000, 'icon': 'crown'}
    ]
    
    conn.close()
    
    return render_template('loyalty_rewards.html', 
                         user=user, 
                         level=level, 
                         rewards=rewards)

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
    
    # Enhanced earnings data
    earnings = conn.execute('''
        SELECT 
            SUM(final_price) as total_earnings,
            COUNT(*) as completed_jobs,
            AVG(final_price) as avg_job_value
        FROM service_requests
        WHERE worker_id = ? AND status = 'completed'
    ''', (worker['id'],)).fetchone()
    
    # Weekly earnings
    weekly_earnings = conn.execute('''
        SELECT 
            strftime('%Y-%W', created_at) as week,
            SUM(final_price) as earnings
        FROM service_requests
        WHERE worker_id = ? AND status = 'completed'
        AND created_at >= date('now', '-8 weeks')
        GROUP BY week
        ORDER BY week
    ''', (worker['id'],)).fetchall()
    
    conn.close()
    
    return render_template('worker_dashboard.html',
                         worker=worker,
                         pending_requests=pending_requests,
                         earnings=earnings,
                         weekly_earnings=weekly_earnings)

@app.route('/worker_training')
@login_required
def worker_training():
    if session['user_type'] != 'worker':
        return redirect(url_for('user_dashboard'))
    
    courses = [
        {
            'title': 'Customer Service Excellence',
            'duration': '2 hours',
            'description': 'Learn to provide outstanding customer service and build long-term relationships.',
            'certification': True,
            'level': 'Beginner'
        },
        {
            'title': 'Safety Protocols and Best Practices',
            'duration': '3 hours',
            'description': 'Essential safety measures for different types of service work.',
            'certification': True,
            'level': 'Beginner'
        },
        {
            'title': 'Digital Marketing for Service Professionals',
            'duration': '4 hours',
            'description': 'Market your services online and build your personal brand.',
            'certification': False,
            'level': 'Intermediate'
        },
        {
            'title': 'Time Management and Route Optimization',
            'duration': '1.5 hours',
            'description': 'Optimize your work schedule and increase productivity.',
            'certification': False,
            'level': 'Intermediate'
        },
        {
            'title': 'Eco-Friendly Service Practices',
            'duration': '2 hours',
            'description': 'Learn sustainable and eco-friendly methods for your services.',
            'certification': True,
            'level': 'Advanced'
        },
        {
            'title': 'Financial Management for Freelancers',
            'duration': '3 hours',
            'description': 'Manage your earnings, taxes, and financial planning.',
            'certification': True,
            'level': 'Advanced'
        }
    ]
    
    return render_template('worker_training.html', courses=courses)

@app.route('/manage_request/<int:request_id>/<action>')
@login_required
def manage_request(request_id, action):
    if session['user_type'] != 'worker':
        return redirect(url_for('user_dashboard'))
    
    conn = get_db_connection()
    
    if action in ['accept', 'decline', 'complete']:
        status_map = {
            'accept': 'accepted',
            'decline': 'declined',
            'complete': 'completed'
        }
        
        conn.execute('''
            UPDATE service_requests 
            SET status = ?, tracking_status = ?
            WHERE id = ?
        ''', (status_map[action], 'worker_assigned' if action == 'accept' else 'not_started', request_id))
        
        if action == 'complete':
            conn.execute('''
                UPDATE workers 
                SET total_jobs = total_jobs + 1
                WHERE user_id = ?
            ''', (session['user_id'],))
        
        conn.commit()
        flash(f'Request {action}ed successfully!')
    
    conn.close()
    return redirect(url_for('worker_dashboard'))

@app.route('/api/recommendations')
@login_required
def api_recommendations():
    """API endpoint for AI recommendations"""
    recommendations = get_ai_recommendations(session['user_id'])
    return jsonify(recommendations)

@app.route('/api/pricing_estimate', methods=['POST'])
@login_required
def api_pricing_estimate():
    """API endpoint for dynamic pricing estimate"""
    data = request.json
    service_type = data.get('service_type')
    date = data.get('date')
    time = data.get('time')
    
    conn = get_db_connection()
    category = conn.execute('''
        SELECT base_price FROM service_categories WHERE name = ?
    ''', (service_type,)).fetchone()
    conn.close()
    
    base_price = category['base_price'] if category else 500
    pricing = calculate_dynamic_pricing(base_price, service_type, date, time)
    
    return jsonify(pricing)

@app.route('/add_worker', methods=['GET', 'POST'])
@login_required
def add_worker():
    """Manual worker registration form"""
    if request.method == 'POST':
        try:
            # Get form data
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
            
            # Checkboxes
            police_verified = 'police_verified' in request.form
            eco_friendly = 'eco_friendly' in request.form
            is_premium = 'is_premium' in request.form
            give_loyalty_points = 'loyalty_points' in request.form
            
            # Optional fields
            rating = float(request.form.get('rating', 0))
            total_jobs = int(request.form.get('total_jobs', 0))
            loyalty_points_amount = int(request.form.get('loyalty_points_amount', 0))
            
            # Hash password
            password_hash = generate_password_hash(password)
            
            conn = None
            try:
                conn = get_db_connection()
                
                # Check if email already exists
                existing_user = conn.execute(
                    'SELECT id FROM users WHERE email = ?', (email,)
                ).fetchone()
                
                if existing_user:
                    flash('Email already exists!', 'error')
                    return render_template('add_worker.html')
                
                # Insert into users table
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (name, email, password, phone, address, city, locality, 
                                     user_type, loyalty_points, is_premium)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, email, password_hash, phone, address, city, locality, 
                      'worker', loyalty_points_amount if give_loyalty_points else 0, 
                      1 if is_premium else 0))
                
                user_id = cursor.lastrowid
                
                # Insert into workers table
                cursor.execute('''
                    INSERT INTO workers (user_id, skills, experience, hourly_rate, description,
                                       rating, total_jobs, availability, certifications,
                                       police_verified, vaccination_status, eco_friendly, profile_image,
                                       current_latitude, current_longitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, skills, experience, hourly_rate, description, rating, total_jobs,
                      availability, certifications, police_verified, vaccination_status, 
                      eco_friendly, profile_image, initial_latitude, initial_longitude))
                
                conn.commit()
                flash(f'Worker "{name}" has been successfully added!', 'success')
                return redirect(url_for('worker_dashboard'))
                
            except Exception as e:
                if conn:
                    conn.rollback()
                flash(f'Error adding worker: {str(e)}', 'error')
                return render_template('add_worker.html')
            finally:
                if conn:
                    conn.close()
        except Exception as e:
            flash(f'Error processing form: {str(e)}', 'error')
            return render_template('add_worker.html')
    
    return render_template('add_worker.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard for managing workers"""
    # Check if user is admin (you can modify this logic based on your admin system)
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get all workers with user details
    workers = conn.execute('''
        SELECT u.id, u.name, u.email, u.phone, u.city, u.locality, u.created_at,
               w.skills, w.experience, w.hourly_rate, w.rating, w.total_jobs, 
               w.availability, w.police_verified, w.eco_friendly, w.vaccination_status
        FROM users u
        JOIN workers w ON u.id = w.user_id
        ORDER BY u.created_at DESC
    ''').fetchall()
    
    # Get statistics
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

@app.route('/nearby_workers_page')
@login_required
def nearby_workers_page():
    """Display nearby workers page with map"""
    return render_template('nearby_workers.html')

@app.route('/update_location', methods=['POST'])
@login_required
def update_location():
    """Update worker's current location"""
    if session.get('user_type') != 'worker':
        return jsonify({'error': 'Only workers can update location'}), 403
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # Get worker ID from session
        conn = get_db_connection()
        worker = conn.execute(
            'SELECT id FROM workers WHERE user_id = ?', (session['user_id'],)
        ).fetchone()
        conn.close()
        
        if not worker:
            return jsonify({'error': 'Worker not found'}), 404
        
        update_worker_location(worker['id'], latitude, longitude)
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully',
            'location': {'lat': latitude, 'lon': longitude}
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid latitude or longitude values'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
 # --- SOS Alert Route ---
@app.route('/sos_alert', methods=['POST'])
@login_required
def sos_alert():
    """Handle SOS alert from user dashboard"""
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_city = session.get('user_city')
        user_id = session.get('user_id')
        user_name = session.get('user_name')
        user_city = session.get('user_city')
        user_locality = session.get('user_locality')
        data = request.get_json(force=True)
        user_latitude = data.get('latitude')
        user_longitude = data.get('longitude')
        try:
            conn = get_db_connection()
            # Get latest accepted service request for this user
            service_request = conn.execute('''
                SELECT sr.*, w.*, u.name as worker_name, u.email as worker_email, u.phone as worker_phone
                FROM service_requests sr
                JOIN workers w ON sr.worker_id = w.id
                JOIN users u ON w.user_id = u.id
                WHERE sr.user_id = ? AND sr.status = 'accepted'
                ORDER BY sr.created_at DESC LIMIT 1
            ''', (user_id,)).fetchone()

            # Prepare worker info if available
            worker_info = {}
            if service_request:
                worker_info = {
                    'worker_id': service_request['worker_id'],
                    'worker_name': service_request['worker_name'],
                    'worker_email': service_request['worker_email'],
                    'worker_phone': service_request['worker_phone'],
                    'worker_skills': service_request['skills'],
                    'worker_experience': service_request['experience'],
                    'worker_rating': service_request['rating'],
                    'worker_locality': service_request['locality'],
                    'worker_city': service_request['city']
                }

            # Log the SOS event with user, worker info, and location
            conn.execute('''
                INSERT INTO sos_alerts (user_id, user_name, city, locality, timestamp, worker_info, latitude, longitude)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
            ''', (user_id, user_name, user_city, user_locality, str(worker_info), user_latitude, user_longitude))
            conn.commit()
            conn.close()

            # Notify admin (example: print to console, replace with email logic)
            admin_message = f"SOS ALERT!\nUser: {user_name} (ID: {user_id})\nLocation: {user_city}, {user_locality}, Lat: {user_latitude}, Long: {user_longitude}\nWorker: {worker_info}\n"
            print(admin_message)  # Replace with email logic if needed

            return jsonify({'success': True, 'message': 'SOS alert sent and admin notified.'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
                'latitude': latitude,
                'longitude': longitude,
                'radius_km': radius
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/worker_location_status')
@login_required
def worker_location_status():
    """Get worker's current location status"""
    if session.get('user_type') != 'worker':
        return jsonify({'error': 'Only workers can access this'}), 403
    
    conn = get_db_connection()
    worker = conn.execute('''
        SELECT current_latitude, current_longitude, last_location_update, availability
        FROM workers WHERE user_id = ?
    ''', (session['user_id'],)).fetchone()
    conn.close()
    
    if not worker:
        return jsonify({'error': 'Worker not found'}), 404
    
    return jsonify({
        'success': True,
        'location': {
            'latitude': worker['current_latitude'],
            'longitude': worker['current_longitude'],
            'last_update': worker['last_location_update'],
            'has_location': worker['current_latitude'] is not None
        },
        'availability': worker['availability']
    })

@app.route('/create_admin')
def create_admin():
    """Create admin user for testing (remove in production)"""
    conn = get_db_connection()
    
    # Check if admin already exists
    existing_admin = conn.execute(
        'SELECT id FROM users WHERE email = ?', ('admin@findmyworker.com',)
    ).fetchone()
    
    if existing_admin:
        flash('Admin user already exists!', 'info')
        conn.close()
        return redirect(url_for('login'))
    
    # Create admin user
    password_hash = generate_password_hash('admin123')
    conn.execute('''
        INSERT INTO users (name, email, password, phone, address, city, locality, user_type, is_premium)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('Admin User', 'admin@findmyworker.com', password_hash, '9999999999', 
          'Admin Address', 'Admin City', 'Admin Locality', 'admin', 1))
    
    conn.commit()
    conn.close()
    
    flash('Admin user created! Email: admin@findmyworker.com, Password: admin123', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    init_db()
    
    print("=" * 60)
    print("ENHANCED FLASK SERVICE PORTAL")
    print("=" * 60)
    print("Features Activated:")
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