
import sqlite3

def add_columns_if_missing(db_path='cosmic_garage.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- Inventory Table Migration ---
    cursor.execute("PRAGMA table_info(inventory)")
    inventory_columns = [row[1] for row in cursor.fetchall()]

    if 'supplier' not in inventory_columns:
        cursor.execute("ALTER TABLE inventory ADD COLUMN supplier TEXT")
        print("Added 'supplier' column to inventory table.")
    else:
        print("'supplier' column already exists.")

    if 'last_ordered' not in inventory_columns:
        cursor.execute("ALTER TABLE inventory ADD COLUMN last_ordered TEXT")
        print("Added 'last_ordered' column to inventory table.")
    else:
        print("'last_ordered' column already exists.")

    # --- Schedules Table Migration ---
    cursor.execute("PRAGMA table_info(schedules)")
    schedules_columns = [row[1] for row in cursor.fetchall()]

    if 'status' not in schedules_columns:
        cursor.execute("ALTER TABLE schedules ADD COLUMN status TEXT DEFAULT 'pending'")
        print("Added 'status' column to schedules table.")
    else:
        print("'status' column already exists.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_columns_if_missing()
