import sqlite3

# Create DB and table
def init_db():
    conn = sqlite3.connect('fleet.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id TEXT PRIMARY KEY,
            make TEXT,
            model TEXT,
            year TEXT,
            license_plate TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()


def read_fleet_data():
    conn = sqlite3.connect('fleet.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles")
    data = cursor.fetchall()
    conn.close()
    return data


def add_vehicle(data):  # data = tuple (id, make, model, year, license, status)
    conn = sqlite3.connect('fleet.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vehicles (id, make, model, year, license_plate, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()


def update_vehicle(vehicle_id, new_data):
    conn = sqlite3.connect('fleet.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE vehicles
        SET make=?, model=?, year=?, license_plate=?, status=?
        WHERE id=?
    ''', (
        new_data['Make'],
        new_data['Model'],
        new_data['Year'],
        new_data['LicensePlate'],
        new_data['Status'],
        vehicle_id
    ))
    conn.commit()
    conn.close()


def delete_vehicle(vehicle_id):
    conn = sqlite3.connect('fleet.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE id=?", (vehicle_id,))
    conn.commit()
    conn.close()


def migrate_txt_to_db(txt_file='db.txt'):
    init_db()
    with open(txt_file, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 6:
                add_vehicle(tuple(parts))
    print("Migration complete.")
