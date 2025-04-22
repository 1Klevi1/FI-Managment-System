import sqlite3

DB_FILE = "fleet.db"

# Initialize DB (if it doesn't exist)
def initialize_database():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fleet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year TEXT NOT NULL,
                license_plate TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        conn.commit()


# Read all vehicles
def read_fleet_data():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fleet")
        return cursor.fetchall()


# Add new vehicle
def add_vehicle(vehicle_data):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fleet (make, model, year, license_plate, status)
            VALUES (?, ?, ?, ?, ?)
        ''', vehicle_data)
        conn.commit()


# Update existing vehicle
def update_vehicle(vehicle_id, new_data):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE fleet
            SET make=?, model=?, year=?, license_plate=?, status=?
            WHERE id=?
        ''', (
            new_data['Make'], new_data['Model'], new_data['Year'],
            new_data['LicensePlate'], new_data['Status'], vehicle_id
        ))
        conn.commit()


# Delete vehicle by ID
def delete_vehicle(vehicle_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fleet WHERE id=?", (vehicle_id,))
        conn.commit()
