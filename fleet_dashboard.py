import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from fleet_operations import  add_vehicle, update_vehicle, fetch_all_vehicles, \
    refresh_treeview, get_vehicle_by_id, save_vehicle_to_db


def show_dashboard(parent):
    """Function to display the dashboard with vehicle data from the database."""
    frame = tk.Frame(parent, bg="#2E2E2E")  # Match the modern theme
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Table to display fleet data
    columns = [
        'ID', 'PLATE NR', 'DRIVER',
        'SITE', 'MAKE', 'MOT DUE',
        'TAX DUE', 'SHELL', 'ESSO',
        'ULEZ', 'CONGEST', 'DART',
        'MILEAGE', 'NO TRACK',
        'DUE FOR CAMBELT',
        'QUARTIX', 'DIVIDE BY SITES',
        'PRIVATE', 'SIDE NOTES'
    ]
    treeview = ttk.Treeview(frame, columns=columns, show="headings", height=10)

    for col in columns:
        treeview.heading(col, text=col)
        treeview.column(col, width=100, anchor="center")

    # Get data from SQLite DB
    fleet_data = fetch_all_vehicles()
    for vehicle in fleet_data:
        treeview.insert("", "end", values=vehicle)

    # Modernize Treeview appearance
    style = ttk.Style()
    style.configure("Treeview", rowheight=25, background="#1E1E1E", foreground="#FFFFFF", fieldbackground="#2E2E2E")
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#4A90E2", foreground="white")

    treeview.pack(fill=tk.BOTH, expand=True)

    return treeview

def empty_vehicle_by_id(treeview):
    """Modern UI: Empty a vehicle from the fleet by ID (without deleting the ID) using SQLite."""

    # Create a sleek modal for ID entry
    dialog = tk.Toplevel()
    dialog.title("Empty Vehicle Data")
    dialog.geometry("350x200")
    dialog.configure(bg="#F9F9F9")
    dialog.grab_set()  # Modal behavior

    tk.Label(dialog, text="Enter Vehicle ID to Empty", font=("Segoe UI", 12, "bold"),
             bg="#F9F9F9", fg="#333").pack(pady=(20, 10))

    id_entry = tk.Entry(dialog, font=("Segoe UI", 11), justify="center")
    id_entry.pack(pady=5, ipadx=10, ipady=5)

    def confirm_empty():
        vehicle_id = id_entry.get().strip()

        if not vehicle_id:
            messagebox.showwarning("Missing Input", "Please enter a vehicle ID.")
            return

        try:
            vehicle_id = int(vehicle_id)
        except ValueError:
            messagebox.showwarning("Invalid ID", "Vehicle ID must be a number.")
            return

        # Connect and check for vehicle
        conn = sqlite3.connect('fleet.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fleet WHERE id=?", (vehicle_id,))
        vehicle = cursor.fetchone()

        if not vehicle:
            messagebox.showwarning("Not Found", f"No vehicle found with ID {vehicle_id}.")
            conn.close()
            return

        # Confirmation popup
        confirm = messagebox.askyesno("Confirm Emptying", f"Are you sure you want to empty vehicle ID {vehicle_id}?")
        if confirm:
            # Empty the vehicle fields instead of deleting
            cursor.execute('''
                UPDATE fleet
                SET plate_nr="", driver=NULL, site=NULL, make="", mot_due=NULL, tax_due=NULL,
                    shell_account=NULL, esso_account=NULL, ulez_compliant=NULL,
                    congestion_charge=NULL, dart_charge=NULL, mileage=NULL,
                    no_track=NULL, due_for_cambelt=NULL, quartix=NULL, divide_by_sites=NULL,
                    private=NULL, side_notes=NULL
                WHERE id=?
            ''', (vehicle_id,))

            conn.commit()
            conn.close()
            messagebox.showinfo("Emptied", "Vehicle data cleared successfully.")
            refresh_treeview(treeview)
        dialog.destroy()

    # Empty Button
    tk.Button(dialog, text="Empty Vehicle", font=("Segoe UI", 11, "bold"),
              bg="#D9534F", fg="white", relief="flat", padx=10, pady=5,
              command=confirm_empty).pack(pady=20)

    # Cancel Button
    tk.Button(dialog, text="Cancel", font=("Segoe UI", 10),
              bg="#ECECEC", fg="#555", relief="flat", padx=8, pady=3,
              command=dialog.destroy).pack()

def edit_vehicle_by_id(treeview):
    """Edit a vehicle's details by its ID with a modern UI dialog using SQLite."""

    edit_window = tk.Toplevel()
    edit_window.title("Edit Vehicle Details")
    edit_window.geometry("400x500")
    edit_window.configure(bg="#F5F5F5")

    tk.Label(edit_window, text="Enter Vehicle ID to Edit", font=("Segoe UI", 12, "bold"),
             bg="#F5F5F5", fg="#333").pack(pady=10)

    vehicle_id_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
    vehicle_id_entry.pack(pady=10)

    def on_submit():
        vehicle_id = vehicle_id_entry.get()
        if not vehicle_id:
            messagebox.showwarning("Invalid ID", "Please enter a valid vehicle ID.")
            return

        vehicle = get_vehicle_by_id(vehicle_id)
        if not vehicle:
            messagebox.showwarning("Vehicle Not Found", f"No vehicle found with ID {vehicle_id}.")
            return

        # Print the fetched vehicle data for debugging
        print(f"Vehicle data: {vehicle}")

        # Check the length of the vehicle data to ensure it's as expected
        if len(vehicle) < 19:
            messagebox.showwarning("Data Incomplete", "The vehicle data is incomplete. Please check the database.")
            return

        fields_frame = tk.Frame(edit_window, bg="#F5F5F5")
        fields_frame.pack(pady=10)

        fields = [
            'ID', 'PLATE NR', 'DRIVER', 'SITE', 'MAKE', 'MOT DUE', 'TAX DUE', 'SHELL', 'ESSO', 'ULEZ', 'CONGEST',
            'DART',
            'MILEAGE', 'NO TRACK', 'DUE FOR CAMBELT', 'QUARTIX', 'DIVIDE BY SITES', 'PRIVATE', 'SIDE NOTES'
        ]
        entry_widgets = {}

        # Create entry widgets for all fields
        for idx, field in enumerate(fields):
            tk.Label(fields_frame, text=f"{field}:", font=("Segoe UI", 10), bg="#F5F5F5").grid(row=idx, column=0,
                                                                                               sticky="w", padx=10,
                                                                                               pady=5)
            entry_widget = tk.Entry(fields_frame, font=("Segoe UI", 12))
            entry_widget.grid(row=idx, column=1, padx=10, pady=5)

            # Ensure you are accessing valid indices and that the vehicle data is not missing
            if idx < len(vehicle):
                value = vehicle[idx] if vehicle[idx] is not None else ""  # Handle None values gracefully
                entry_widget.insert(0, str(value))  # Ensure the value is a string
            else:
                entry_widget.insert(0, "")  # If data is missing, insert empty string

            entry_widgets[field] = entry_widget

        def save_changes():
            new_vehicle_data = {field: entry_widgets[field].get() for field in fields}
            update_vehicle(vehicle_id, new_vehicle_data)
            messagebox.showinfo("Success", "Vehicle updated successfully.")
            refresh_treeview(treeview)
            edit_window.destroy()

        tk.Button(edit_window, text="Save Changes", font=("Segoe UI", 12, "bold"),
                  bg="#4A90E2", fg="white", relief="flat", width=20, command=save_changes).pack(pady=20)

    tk.Button(edit_window, text="Submit", font=("Segoe UI", 12, "bold"), bg="#50E3C2",
              fg="white", relief="flat", width=20, command=on_submit).pack(pady=20)

def open_fleet_management(parent):
    """Open the fleet management window to manage the fleet."""
    management_window = tk.Toplevel(parent)
    management_window.title("Manage Fleet")
    management_window.geometry("800x600")  # Adjusted window size for better fit
    management_window.configure(bg="#f0f0f0")

    # Header buttons
    header_frame = tk.Frame(management_window, bg="#f0f0f0")
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    add_button = tk.Button(
        header_frame, text="Add Vehicle",
        command=lambda: open_add_edit_vehicle_dialog(management_window, editing=False),
        relief="flat", bg="#4CAF50", fg="white", font=("Arial", 12), padx=20, pady=10)

    add_button.pack(side=tk.LEFT, padx=10)

    edit_button = tk.Button(
        header_frame, text="Edit Vehicle",
        command=lambda: edit_vehicle_by_id(management_window.treeview_management),
        relief="flat", bg="#2196F3", fg="white", font=("Arial", 12), padx=20, pady=10)

    edit_button.pack(side=tk.LEFT, padx=10)

    delete_button = tk.Button(
        header_frame, text="Delete Vehicle",
        command=lambda: empty_vehicle_by_id(management_window.treeview_management),
        relief="flat", bg="#f44336", fg="white", font=("Arial", 12), padx=20, pady=10)

    delete_button.pack(side=tk.LEFT, padx=10)

    # Treeview with scrollbars
    treeview_frame = tk.Frame(management_window, bg="#f0f0f0")
    treeview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Add vertical scrollbar
    vertical_scrollbar = tk.Scrollbar(treeview_frame, orient="vertical")
    vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Add horizontal scrollbar
    horizontal_scrollbar = tk.Scrollbar(treeview_frame, orient="horizontal")
    horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Define columns for the Treeview
    columns = [
        'ID','PLATE NR', 'DRIVER', 'SITE', 'MAKE', 'MOT DUE', 'TAX DUE', 'SHELL', 'ESSO', 'ULEZ', 'CONGEST', 'DART',
        'MILEAGE', 'NO TRACK', 'DUE FOR CAMBELT', 'QUARTIX', 'DIVIDE BY SITES', 'PRIVATE', 'SIDE NOTES'
    ]

    treeview_management = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=10,
                                       yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)

    for col in columns:
        treeview_management.heading(col, text=col)
        treeview_management.column(col, width=100, anchor="center")

    # Fetch data from SQLite
    fleet_data = fetch_all_vehicles()
    for vehicle in fleet_data:
        treeview_management.insert("", "end", values=vehicle)

    # Treeview styling
    style = ttk.Style()
    style.configure("Treeview", rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    # Packing the Treeview
    treeview_management.pack(fill=tk.BOTH, expand=True)

    # Configuring the scrollbars to work with Treeview
    vertical_scrollbar.config(command=treeview_management.yview)
    horizontal_scrollbar.config(command=treeview_management.xview)

    # Store treeview for future use
    management_window.treeview_management = treeview_management

def open_add_edit_vehicle_dialog(management_window, editing=False, vehicle=None):
    """Dialog for adding or editing vehicle information."""
    fields = ['PLATE NR', 'DRIVER', 'SITE', 'MAKE', 'MOT DUE', 'TAX DUE', 'SHELL', 'ESSO', 'ULEZ', 'CONGEST', 'DART',
              'MILEAGE', 'NO TRACK', 'DUE FOR CAMBELT', 'QUARTIX', 'DIVIDE BY SITES', 'PRIVATE', 'SIDE NOTES']
    vehicle_data = {field: "" for field in fields}

    if editing and vehicle:
        vehicle_data = dict(zip(fields, vehicle[1:]))

    dialog = tk.Toplevel(management_window)
    dialog.title("Add/Edit Vehicle")
    dialog.geometry("300x380")
    dialog.configure(bg="#f0f0f0")

    input_frame = tk.Frame(dialog, bg="#f0f0f0")
    input_frame.pack(padx=10, pady=10)

    input_fields = {}
    for i, field in enumerate(fields):
        label = tk.Label(input_frame, text=f"{field}:", font=("Arial", 10), bg="#f0f0f0")
        label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
        entry = tk.Entry(input_frame, font=("Arial", 10))
        entry.insert(0, vehicle_data.get(field, ''))
        entry.grid(row=i, column=1, padx=5, pady=5)
        input_fields[field] = entry

    button_frame = tk.Frame(dialog, bg="#f0f0f0")
    button_frame.pack(pady=10)

    save_button = tk.Button(button_frame, text="Save",
                            command=lambda: save_vehicle_to_db(dialog, input_fields, vehicle[0] if editing else None, management_window),
                            relief="flat", bg="#4CAF50", fg="white", font=("Arial", 12), padx=20, pady=8)
    save_button.grid(row=0, column=0, padx=10)

    cancel_button = tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                              relief="flat", bg="#f44336", fg="white", font=("Arial", 12), padx=20, pady=8)
    cancel_button.grid(row=0, column=1, padx=10)


def save_vehicle(dialog, input_fields, vehicle, management_window):
    """Save the vehicle data (add or edit) to the database and refresh the treeview."""
    new_vehicle_data = {key: entry.get() for key, entry in input_fields.items()}
    if vehicle:  # Editing existing vehicle
        # Update vehicle with new data
        update_vehicle(vehicle[0], new_vehicle_data)  # vehicle[0] is the vehicle ID
        messagebox.showinfo("Success", "Vehicle updated successfully.")
    else:  # Adding new vehicle
        # Add a new vehicle to the database
        add_vehicle([
            new_vehicle_data['plate_nr'],
            new_vehicle_data['driver'],
            new_vehicle_data['site'],
            new_vehicle_data['make'],
            new_vehicle_data['mot_due'],
            new_vehicle_data['tax_due'],
            new_vehicle_data['shell_account'],
            new_vehicle_data['esso_account'],
            new_vehicle_data['ulez_compliant'],
            new_vehicle_data['congestion_charge'],
            new_vehicle_data['dart_charge'],
            new_vehicle_data['mileage'],
            new_vehicle_data['no_track'],
            new_vehicle_data['due_for_cambelt'],
            new_vehicle_data['quartix'],
            new_vehicle_data['divide_by_sites'],
            new_vehicle_data['private'],
            new_vehicle_data['side_notes']
        ])
        messagebox.showinfo("Success", "Vehicle added successfully.")

    # Refresh the treeview to reflect the updated data
    refresh_treeview(management_window)

    # Close the dialog
    dialog.destroy()
