import sqlite3
from datetime import datetime

def migrate_database():
    """Migrate existing database to add missing columns"""
    conn = sqlite3.connect('service_portal.db')
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # List of all migrations
    migrations = [
        # Subscriptions table migrations
        ("ALTER TABLE subscriptions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP", 
         "created_at column to subscriptions"),
        ("ALTER TABLE subscriptions ADD COLUMN razorpay_order_id TEXT", 
         "razorpay_order_id column to subscriptions"),
        ("ALTER TABLE subscriptions ADD COLUMN razorpay_payment_id TEXT", 
         "razorpay_payment_id column to subscriptions"),
        
        # Users table migrations
        ("ALTER TABLE users ADD COLUMN locality TEXT", 
         "locality column to users"),
        ("ALTER TABLE users ADD COLUMN loyalty_points INTEGER DEFAULT 0", 
         "loyalty_points column to users"),
        ("ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT 0", 
         "is_premium column to users"),
        
        # Workers table migrations
        ("ALTER TABLE workers ADD COLUMN police_verified BOOLEAN DEFAULT 0", 
         "police_verified column to workers"),
        ("ALTER TABLE workers ADD COLUMN vaccination_status TEXT", 
         "vaccination_status column to workers"),
        ("ALTER TABLE workers ADD COLUMN eco_friendly BOOLEAN DEFAULT 0", 
         "eco_friendly column to workers"),
        ("ALTER TABLE workers ADD COLUMN profile_image TEXT", 
         "profile_image column to workers"),
        ("ALTER TABLE workers ADD COLUMN current_latitude REAL", 
         "current_latitude column to workers"),
        ("ALTER TABLE workers ADD COLUMN current_longitude REAL", 
         "current_longitude column to workers"),
        ("ALTER TABLE workers ADD COLUMN last_location_update TIMESTAMP", 
         "last_location_update column to workers"),
        ("ALTER TABLE workers ADD COLUMN preferred_radius INTEGER DEFAULT 10", 
         "preferred_radius column to workers"),
        
        # Service requests table migrations
        ("ALTER TABLE service_requests ADD COLUMN locality TEXT", 
         "locality column to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN base_price REAL", 
         "base_price column to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN labor_cost REAL", 
         "labor_cost column to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN material_cost REAL", 
         "material_cost column to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN tax REAL", 
         "tax column to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN surge_multiplier REAL DEFAULT 1.0", 
         "surge_multiplier column to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN final_price REAL", 
         "final_price column to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN tracking_status TEXT DEFAULT 'not_started'", 
         "tracking_status column to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN eta_minutes INTEGER", 
         "eta_minutes column to service_requests"),
        ("ALTER TABLE service_requests ADD COLUMN is_group_booking BOOLEAN DEFAULT 0", 
         "is_group_booking column to service_requests"),
    ]
    
    successful = 0
    skipped = 0
    
    for migration_sql, description in migrations:
        try:
            cursor.execute(migration_sql)
            print(f"✓ Added {description}")
            successful += 1
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"⊘ Skipped {description} (already exists)")
                skipped += 1
            else:
                print(f"✗ Failed to add {description}: {e}")
    
    # Migrate old budget column to final_price if needed
    try:
        cursor.execute("SELECT budget FROM service_requests LIMIT 1")
        # If budget column exists, copy data to final_price
        cursor.execute("""
            UPDATE service_requests 
            SET final_price = budget 
            WHERE final_price IS NULL AND budget IS NOT NULL
        """)
        print("✓ Migrated budget data to final_price")
    except sqlite3.OperationalError:
        print("⊘ No budget column to migrate")
    
    conn.commit()
    conn.close()
    
    print(f"\nMigration complete!")
    print(f"Successful: {successful}, Skipped: {skipped}")
    print("Database is now up to date.")

if __name__ == '__main__':
    migrate_database()
    
    
    