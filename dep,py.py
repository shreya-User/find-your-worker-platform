def init_db():
    """Initialize database with all required tables and migrations"""
    conn = sqlite3.connect('service_portal.db')
    cursor = conn.cursor()
    
    # Enable WAL mode
    cursor.execute('PRAGMA journal_mode=WAL')
    
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
    
    # Workers table
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
    
    # Service requests table
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
            budget REAL,
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
    
    # Subscriptions table with Razorpay fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_type TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'active',
            stripe_subscription_id TEXT,
            stripe_customer_id TEXT,
            razorpay_order_id TEXT,
            razorpay_payment_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stripe_payment_intent_id TEXT UNIQUE,
            stripe_checkout_session_id TEXT,
            amount REAL,
            currency TEXT DEFAULT 'inr',
            status TEXT,
            payment_type TEXT,
            service_request_id INTEGER,
            subscription_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (service_request_id) REFERENCES service_requests (id),
            FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
        )
    ''')
    
    # Service categories
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
    
    # Insert default service categories if not exists
    cursor.execute('SELECT COUNT(*) FROM service_categories')
    if cursor.fetchone()[0] == 0:
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
        cursor.executemany('''
            INSERT INTO service_categories (name, icon, seasonal_peak, eco_friendly_available, base_price)
            VALUES (?, ?, ?, ?, ?)
        ''', categories)
    
    # Run migrations for existing tables
    print("Running database migrations...")
    
    migrations = [
        # Users table migrations
        ("ALTER TABLE users ADD COLUMN locality TEXT", "locality to users"),
        ("ALTER TABLE users ADD COLUMN loyalty_points INTEGER DEFAULT 0", "loyalty_points to users"),
        ("ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT 0", "is_premium to users"),
        
        # Workers table migrations
        ("ALTER TABLE workers ADD COLUMN police_verified BOOLEAN DEFAULT 0", "police_verified to workers"),
        ("ALTER TABLE workers ADD COLUMN vaccination_status TEXT", "vaccination_status to workers"),
        ("ALTER TABLE workers ADD COLUMN eco_friendly BOOLEAN DEFAULT 0", "eco_friendly to workers"),
        ("ALTER TABLE workers ADD COLUMN profile_image TEXT", "profile_image to workers"),
        ("ALTER TABLE workers ADD COLUMN current_latitude REAL", "current_latitude to workers"),
        ("ALTER TABLE workers ADD COLUMN current_longitude REAL", "current_longitude to workers"),
        ("ALTER TABLE workers ADD COLUMN last_location_update TIMESTAMP", "last_location_update to workers"),
        ("ALTER TABLE workers ADD COLUMN preferred_radius INTEGER DEFAULT 10", "preferred_radius to workers"),
        
        # Service requests migrations
        ("ALTER TABLE service_requests ADD COLUMN locality TEXT", "locality to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN base_price REAL", "base_price to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN labor_cost REAL", "labor_cost to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN material_cost REAL", "material_cost to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN tax REAL", "tax to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN surge_multiplier REAL DEFAULT 1.0", "surge_multiplier to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN final_price REAL", "final_price to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN tracking_status TEXT DEFAULT 'not_started'", "tracking_status to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN eta_minutes INTEGER", "eta_minutes to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN is_group_booking BOOLEAN DEFAULT 0", "is_group_booking to service_requests"),
        
        # Subscriptions migrations
        ("ALTER TABLE subscriptions ADD COLUMN razorpay_order_id TEXT", "razorpay_order_id to subscriptions"),
        ("ALTER TABLE subscriptions ADD COLUMN razorpay_payment_id TEXT", "razorpay_payment_id to subscriptions"),
        ("ALTER TABLE subscriptions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "created_at to subscriptions"),
    ]
    
    for migration_sql, description in migrations:
        try:
            cursor.execute(migration_sql)
            print(f"✓ Added {description}")
        except sqlite3.OperationalError:
            pass  # Column already exists
    
    conn.commit()
    conn.close()
    print("Database initialization complete!")