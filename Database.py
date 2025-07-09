import sqlite3
import os

def create_database(db_path='cosmic_garage.db'):
    """Create and initialize the SQLite database with required tables if not present."""
    db_exists = os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users table (admins and mechanics)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'mechanic')),
            full_name TEXT
        )
    ''')

    # Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            car_model TEXT NOT NULL,
            vin TEXT UNIQUE NOT NULL,
            issue TEXT,
            date_added TEXT
        )
    ''')

    # Repairs table (vin is NOT unique)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            car_model TEXT NOT NULL,
            vin TEXT NOT NULL,
            issue TEXT,
            status TEXT NOT NULL,
            start_date TEXT,
            assigned_mechanic TEXT,
            priority TEXT,
            estimated_hours REAL,
            estimated_cost REAL,
            end_date TEXT
        )
    ''')

    # Inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_name TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            supplier TEXT,
            last_ordered TEXT
        )
    ''')

    # Schedules table (with status)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mechanic TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            task TEXT,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    ''')
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS login_logs (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT,
               role TEXT,
               login_time TEXT
           )
       ''')

    # Insert default admin if not exists
    cursor.execute('SELECT * FROM users WHERE role="admin"')
    if not cursor.fetchone():
        cursor.execute(
            'INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)',
            ('admin', 'admin', 'admin', 'Administrator')
        )

    conn.commit()
    conn.close()
