import sqlite3
from tkinter import messagebox

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

def reset_autoincrement():
    conn = sqlite3.connect("fleet.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='fleet'")
    conn.commit()
    conn.close()

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

def get_vehicle_by_id(vehicle_id):
    conn = sqlite3.connect("fleet.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fleet WHERE id = ?", (vehicle_id,))
    vehicle = cursor.fetchone()
    conn.close()
    return vehicle

# Delete vehicle by ID
def delete_vehicle(vehicle_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fleet WHERE id=?", (vehicle_id,))
        conn.commit()


def save_vehicle_to_db(dialog, input_fields, vehicle_id, management_window):

    data = {field: input_fields[field].get().strip() for field in input_fields}

    # Basic validation
    if not all(data.values()):
        messagebox.showwarning("Missing Fields", "Please fill out all fields.")
        return

    if vehicle_id:  # Editing existing
        update_vehicle(vehicle_id, data)
        messagebox.showinfo("Success", "Vehicle updated successfully.")

    else:  # Adding new
        vehicle = [data['Make'], data['Model'], data['Year'], data['LicensePlate'], data['Status']]
        print("Adding vehicle:", vehicle)  # Debugging line to see the vehicle data
        add_vehicle(vehicle)
        messagebox.showinfo("Success", "Vehicle added successfully.")

    dialog.destroy()
    refresh_treeview(management_window.treeview_management)

def fetch_all_vehicles():
    conn = sqlite3.connect("fleet.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM fleet")
    rows = cursor.fetchall()

    conn.close()
    return rows

def refresh_treeview(treeview):
    """Refresh the Treeview by fetching all vehicles and updating the display."""
    # Clear current items
    for item in treeview.get_children():
        treeview.delete(item)

    # Fetch the latest fleet data from the database
    fleet_data = fetch_all_vehicles()

    # Insert the updated data into the Treeview
    for vehicle in fleet_data:
        treeview.insert("", "end", values=vehicle)