import sqlite3
from tkinter import messagebox
import pandas as pd

DB_FILE = "fleet.db"

def initialize_database():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fleet (
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
                side_notes TEXT
            )
        ''')
        conn.commit()


def import_dataset_to_db(csv_file):
    try:
        # Read the CSV file with tab delimiter
        df = pd.read_csv(csv_file, delimiter='\t', encoding='latin1')  # Use tab (\t) as delimiter

        # Print column names for debugging
        print("Columns in the dataset:", df.columns)

        # Strip any extra spaces from column names
        df.columns = df.columns.str.strip()

        # Remove unnecessary columns (those with 'Unnamed' in the name)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Rename 'CONGEST.' to 'CONGEST' (remove trailing period)
        if 'CONGEST.' in df.columns:
            df.rename(columns={'CONGEST.': 'CONGEST'}, inplace=True)

        # Preprocess the dataset:
        # 1. Replace blank or NaN values with None (NULL in DB)
        df = df.where(pd.notnull(df), None)

        # 2. Convert "Yes"/"No" columns (Shell, Esso, Dart) to booleans
        if 'SHELL' in df.columns:
            df['SHELL'] = df['SHELL'].apply(lambda x: True if x == 'Yes' else False if x == 'No' else None)

        if 'ESSO' in df.columns:
            df['ESSO'] = df['ESSO'].apply(lambda x: True if x == 'Yes' else False if x == 'No' else None)

        if 'DART' in df.columns:
            df['DART'] = df['DART'].apply(lambda x: True if x == 'Yes' else False if x == 'No' else None)

        # 3. Keep ULEZ and CONGEST as text (string) in the database
        # No transformation needed for ULEZ and CONGEST, just keep them as text in the database

        # 4. Handle mileage as an integer
        if 'MILEAGE' in df.columns:
            df['MILEAGE'] = pd.to_numeric(df['MILEAGE'], errors='coerce')  # Convert invalid entries to NaN
            df['MILEAGE'] = df['MILEAGE'].fillna(0).astype(int)  # Replace NaN with 0 and convert to int

        # Connect to the database
        conn = sqlite3.connect('fleet.db')
        cursor = conn.cursor()

        # Insert the cleaned data into the database
        for index, row in df.iterrows():
            cursor.execute('''
                INSERT INTO fleet (
                    plate_nr, driver, site, make, mot_due, tax_due,
                    shell_account, esso_account, ulez_compliant,
                    congestion_charge, dart_charge, mileage, side_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['PLATE NR'], row['DRIVER'], row['SITE'], row['MAKE'],
                row['MOT DUE'], row['TAX DUE'], row['SHELL'], row['ESSO'],
                row['ULEZ'], row['CONGEST'], row['DART'], row['MILEAGE'],
                row['SIDE NOTES'] if 'SIDE NOTES' in row else None  # Handle missing side notes
            ))

        # Commit and close connection
        conn.commit()
        conn.close()
        print(f"Data from {csv_file} imported successfully into the database.")

    except Exception as e:
        print(f"Error occurred while importing dataset: {e}")

# Read all vehicles
def read_fleet_data():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fleet")
        return cursor.fetchall()


def add_vehicle(vehicle_data):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fleet (
                plate_nr, driver, site, make, mot_due, tax_due,
                shell_account, esso_account, ulez_compliant,
                congestion_charge, dart_charge, mileage, side_notes,
                "NO TRACK", "DUE FOR CAMBELT", "QUARTIX", "DIVIDE BY SITES", "PRIVATE"
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', vehicle_data)
        conn.commit()


def reset_autoincrement():
    with sqlite3.connect("fleet.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fleet")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='fleet'")
            conn.commit()
# Update existing vehicle with partial fields (can set fields to None/NULL as well)
def update_vehicle(vehicle_id, new_data):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Prepare dynamic SET clause based on provided fields in new_data
        set_clause = []
        values = []

        # Check each field in new_data to see if it has a value to update
        for key, value in new_data.items():
            set_clause.append(f"{key}=?")  # Add the field to the SET clause
            values.append(value)  # Add the value (even if it is None) to the list of values to update

        # Always add the vehicle_id at the end for the WHERE clause
        set_clause_str = ", ".join(set_clause)  # Combine all SET conditions
        values.append(vehicle_id)  # Append vehicle_id to the end for the WHERE condition

        # Build the final SQL query string
        query = f"UPDATE fleet SET {set_clause_str} WHERE id=?"

        # Execute the query with the dynamic values
        cursor.execute(query, tuple(values))
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
    # Collecting data from the input fields
    data = {field: input_fields[field].get().strip() for field in input_fields}

    # Basic validation
    if not all(data.values()):
        messagebox.showwarning("Missing Fields", "Please fill out all fields.")
        return

    # Update existing vehicle
    if vehicle_id:  # Editing existing
        update_vehicle(vehicle_id, data)
        messagebox.showinfo("Success", "Vehicle updated successfully.")

    else:  # Adding new vehicle
        # We include all required fields including the new columns
        vehicle = [
            data['PLATE NR'] if data['PLATE NR'] else None,  # If 'PLATE NR' is empty, set as None
            data['DRIVER'] if data['DRIVER'] else None,  # If 'DRIVER' is empty, set as None
            data['SITE'] if data['SITE'] else None,  # If 'SITE' is empty, set as None
            data['MAKE'] if data['MAKE'] else None,  # If 'MAKE' is empty, set as None
            data['MOT DUE'] if data['MOT DUE'] else None,  # If 'MOT DUE' is empty, set as None
            data['TAX DUE'] if data['TAX DUE'] else None,  # If 'TAX DUE' is empty, set as None
            data['SHELL'] if data['SHELL'] else None,  # If 'SHELL' is empty, set as None
            data['ESSO'] if data['ESSO'] else None,  # If 'ESSO' is empty, set as None
            data['ULEZ'] if data['ULEZ'] else None,  # If 'ULEZ' is empty, set as None
            data['CONGEST'] if data['CONGEST'] else None,  # If 'CONGEST' is empty, set as None
            data['DART'] if data['DART'] else None,  # If 'DART' is empty, set as None
            int(data['MILEAGE']) if data['MILEAGE'] else None,  # If 'MILEAGE' is empty or invalid, set as None
            data['SIDE NOTES'] if data.get('SIDE NOTES', '') else None,  # If 'SIDE NOTES' is empty, set as None
            data.get('NO TRACK', None),  # If 'NO TRACK' is empty, set as None
            data.get('DUE FOR CAMBELT', None),  # If 'DUE FOR CAMBELT' is empty, set as None
            data.get('QUARTIX', None),  # If 'QUARTIX' is empty, set as None
            data.get('DIVIDE BY SITES', None),  # If 'DIVIDE BY SITES' is empty, set as None
            data.get('PRIVATE', None)  # If 'PRIVATE' is empty, set as None
        ]
        print("Adding vehicle:", vehicle)  # Debugging line to see the vehicle data
        add_vehicle(vehicle)
        messagebox.showinfo("Success", "Vehicle added successfully.")

    dialog.destroy()  # Close the dialog after the action
    refresh_treeview(management_window.treeview_management)  # Refresh the UI

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