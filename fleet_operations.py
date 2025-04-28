import sqlite3
from tkinter import messagebox
import pandas as pd

DB_FILE = "fleet.db"

def initialize_database():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS fleet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_nr TEXT NOT NULL,
            driver TEXT,
            site TEXT,
            make TEXT,
            mot_due DATE,
            tax_due DATE,
            shell_account TEXT,
            esso_account TEXT,
            ulez_compliant TEXT,
            congestion_charge TEXT,
            dart_charge TEXT,
            mileage INTEGER,
            no_track TEXT,
            due_for_cambelt TEXT,
            quartix TEXT,
            divide_by_sites TEXT,
            private TEXT,
            side_notes TEXT
        )''')
        conn.commit()

def import_dataset_to_db(csv_file):
    try:
        df = pd.read_csv(csv_file, delimiter=';', encoding='latin1')
        df.columns = df.columns.str.strip()

        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns

        if 'CONGEST.' in df.columns:
            df.rename(columns={'CONGEST.': 'CONGEST'}, inplace=True)

        df = df.where(pd.notnull(df), None)  # Replace NaNs with None

        if 'MILEAGE' in df.columns:
            df['MILEAGE'] = pd.to_numeric(df['MILEAGE'], errors='coerce').fillna(0).astype(int)

        if 'Side Notes' in df.columns:
            df['Side Notes'] = df['Side Notes'].apply(lambda x: str(x).strip() if isinstance(x, str) else x)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for index, row in df.iterrows():
            cursor.execute('''INSERT INTO fleet (
                plate_nr, driver, site, make, mot_due, tax_due,
                shell_account, esso_account, ulez_compliant,
                congestion_charge, dart_charge, mileage,
                no_track, due_for_cambelt, quartix, divide_by_sites, private, side_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                row.get('PLATE NR') or None,
                row.get('DRIVER') or None,
                row.get('SITE') or None,
                row.get('MAKE') or None,
                row.get('MOT DUE') or None,
                row.get('TAX DUE') or None,
                row.get('SHELL') or None,
                row.get('ESSO') or None,
                row.get('ULEZ') or None,
                row.get('CONGEST') or None,
                row.get('DART') or None,
                int(row.get('MILEAGE') or 0),
                row.get('NO TRACK') or None,
                row.get('DUE FOR CAMBELT') or None,
                row.get('QUARTIX') or None,
                row.get('DIVIDE BY SITES') or None,
                row.get('PRIVATE') or None,
                row.get('SIDE NOTES') or None
            ))

        conn.commit()
        conn.close()
        print(f"Data from {csv_file} imported successfully into the database.")
    except Exception as e:
        print(f"Error occurred while importing dataset: {e}")

def read_fleet_data():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fleet")
        return cursor.fetchall()

def add_vehicle(vehicle_data):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO fleet (
            plate_nr, driver, site, make, mot_due, tax_due,
            shell_account, esso_account, ulez_compliant,
            congestion_charge, dart_charge, mileage,
            no_track, due_for_cambelt, quartix, divide_by_sites, private, side_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', vehicle_data)
        conn.commit()

def reset_autoincrement():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(ID) FROM fleet")
        max_id = cursor.fetchone()[0]
        if max_id is not None:
            cursor.execute(f"UPDATE sqlite_sequence SET seq = {max_id} WHERE name='fleet'")
            conn.commit()

def update_vehicle(vehicle_id, new_data):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Prepare dynamic SET clause based on provided fields in new_data
        set_clause = []
        values = []

        # Check if any fields are provided in new_data
        if not new_data:
            print("No fields provided to update.")
            return

        for key, value in new_data.items():
            set_clause.append(f"{key}=?")
            values.append(value)

        set_clause_str = ", ".join(set_clause)
        values.append(vehicle_id)  # Add vehicle_id for the WHERE clause

        # Build the final query
        query = f"UPDATE fleet SET {set_clause_str} WHERE id=?"

        # Debugging: Print the query and values to check the correctness
        print(f"Query: {query}")
        print(f"Values: {tuple(values)}")

        try:
            # Execute the query with dynamic values
            cursor.execute(query, tuple(values))
            conn.commit()

            # Check if any rows were affected
            if cursor.rowcount == 0:
                print(f"No rows were updated for vehicle ID {vehicle_id}.")
            else:
                print(f"Vehicle ID {vehicle_id} updated successfully.")
        except Exception as e:
            print(f"Error occurred while updating vehicle: {e}")

def get_vehicle_by_id(vehicle_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fleet WHERE id = ?", (vehicle_id,))
    vehicle = cursor.fetchone()
    conn.close()
    return vehicle

def empty_vehicle(vehicle_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE fleet
            SET plate_nr='', driver=NULL, site=NULL, make='', mot_due=NULL, tax_due=NULL,
                shell_account=NULL, esso_account=NULL, ulez_compliant=NULL,
                congestion_charge=NULL, dart_charge=NULL, mileage=NULL,
                no_track=NULL, due_for_cambelt=NULL, quartix=NULL, divide_by_sites=NULL,
                private=NULL, side_notes=NULL
            WHERE id=?''', (vehicle_id,))
        conn.commit()

def find_empty_vehicle_id():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM fleet WHERE plate_nr IS ''")
        result = cursor.fetchone()
        return result[0] if result else None

def parse_mileage(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def save_vehicle_to_db(dialog, input_fields, vehicle_id, management_window):
    data = {field: input_fields[field].get().strip() for field in input_fields}

    required_fields = ['PLATE NR', 'MAKE']
    if not all(data[field] for field in required_fields):
        messagebox.showwarning("Missing Fields", "Please fill out required fields: Plate Nr and Make.")
        return

    field_mapping = {
        'PLATE NR': 'plate_nr',
        'DRIVER': 'driver',
        'SITE': 'site',
        'MAKE': 'make',
        'MOT DUE': 'mot_due',
        'TAX DUE': 'tax_due',
        'SHELL': 'shell_account',
        'ESSO': 'esso_account',
        'ULEZ': 'ulez_compliant',
        'CONGEST': 'congestion_charge',
        'DART': 'dart_charge',
        'MILEAGE': 'mileage',
        'NO TRACK': 'no_track',
        'DUE FOR CAMBELT': 'due_for_cambelt',
        'QUARTIX': 'quartix',
        'DIVIDE BY SITES': 'divide_by_sites',
        'PRIVATE': 'private',
        'SIDE NOTES': 'side_notes'
    }

    if vehicle_id:  # Editing existing
        translated_data = {field_mapping.get(k, k): (parse_mileage(v) if k == 'MILEAGE' else v) for k, v in data.items()}
        print(f"Updating vehicle ID {vehicle_id} with data: {translated_data}")
        update_vehicle(vehicle_id, translated_data)
        messagebox.showinfo("Success", "Vehicle updated successfully.")
    else:  # Adding new vehicle
        mileage = parse_mileage(data.get('MILEAGE'))

        vehicle = [
            data.get('PLATE NR') or None,
            data.get('DRIVER') or None,
            data.get('SITE') or None,
            data.get('MAKE') or None,
            data.get('MOT DUE') or None,
            data.get('TAX DUE') or None,
            data.get('SHELL') or None,
            data.get('ESSO') or None,
            data.get('ULEZ') or None,
            data.get('CONGEST') or None,
            data.get('DART') or None,
            mileage,
            data.get('NO TRACK') or None,
            data.get('DUE FOR CAMBELT') or None,
            data.get('QUARTIX') or None,
            data.get('DIVIDE BY SITES') or None,
            data.get('PRIVATE') or None,
            data.get('SIDE NOTES') or None
        ]

        print(f"Adding new vehicle: {vehicle}")

        empty_id = find_empty_vehicle_id()
        if empty_id:
            translated_data = {field_mapping.get(k, k): (parse_mileage(v) if k == 'MILEAGE' else v) for k, v in data.items()}
            print(f"translated data: {translated_data}")

            update_vehicle(empty_id, translated_data)
            messagebox.showinfo("Success", "Vehicle added successfully (reused empty slot).")
        else:
            add_vehicle(vehicle)
            messagebox.showinfo("Success", "Vehicle added successfully.")

    dialog.destroy()  # Close the dialog after the action
    refresh_treeview(management_window.treeview_management)

def fetch_all_vehicles():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fleet")
    rows = cursor.fetchall()
    conn.close()
    return rows

def refresh_treeview(treeview):
    for item in treeview.get_children():
        treeview.delete(item)

    fleet_data = fetch_all_vehicles()

    for vehicle in fleet_data:
        treeview.insert("", "end", values=vehicle)
