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
    columns = ['ID', 'Make', 'Model', 'Year', 'LicensePlate', 'Status']
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


def delete_vehicle_by_id(treeview):
    """Modern UI: Delete a vehicle from the fleet by ID using SQLite."""

    # Create a sleek modal for ID entry
    dialog = tk.Toplevel()
    dialog.title("Delete Vehicle")
    dialog.geometry("350x200")
    dialog.configure(bg="#F9F9F9")
    dialog.grab_set()  # Modal behavior

    tk.Label(dialog, text="Enter Vehicle ID to Delete", font=("Segoe UI", 12, "bold"),
             bg="#F9F9F9", fg="#333").pack(pady=(20, 10))

    id_entry = tk.Entry(dialog, font=("Segoe UI", 11), justify="center")
    id_entry.pack(pady=5, ipadx=10, ipady=5)

    def confirm_delete():
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
        vehicle_to_delete = cursor.fetchone()

        if not vehicle_to_delete:
            messagebox.showwarning("Not Found", f"No vehicle found with ID {vehicle_id}.")
            conn.close()
            return

        # Confirmation popup
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete vehicle ID {vehicle_id}?")
        if confirm:
            cursor.execute("DELETE FROM fleet WHERE id=?", (vehicle_id,))

            # After deletion
            cursor.execute("SELECT COUNT(*) FROM fleet")
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='fleet'")
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Vehicle deleted successfully.")
            refresh_treeview(treeview)
        dialog.destroy()

    # Delete Button
    tk.Button(dialog, text="Delete Vehicle", font=("Segoe UI", 11, "bold"),
              bg="#D9534F", fg="white", relief="flat", padx=10, pady=5,
              command=confirm_delete).pack(pady=20)

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

        fields_frame = tk.Frame(edit_window, bg="#F5F5F5")
        fields_frame.pack(pady=10)

        fields = ['Make', 'Model', 'Year', 'LicensePlate', 'Status']
        entry_widgets = {}

        for idx, field in enumerate(fields):
            tk.Label(fields_frame, text=f"{field}:", font=("Segoe UI", 10), bg="#F5F5F5").grid(row=idx, column=0, padx=10, pady=5)
            entry_widget = tk.Entry(fields_frame, font=("Segoe UI", 12))
            entry_widget.grid(row=idx, column=1, padx=10, pady=5)
            entry_widget.insert(0, vehicle[idx + 1])  # Skip ID at index 0
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
    management_window.geometry("600x400")
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
        command=lambda: delete_vehicle_by_id(management_window.treeview_management),
        relief="flat", bg="#f44336", fg="white", font=("Arial", 12), padx=20, pady=10)
    delete_button.pack(side=tk.LEFT, padx=10)

    # Treeview
    treeview_frame = tk.Frame(management_window, bg="#f0f0f0")
    treeview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    columns = ['ID', 'Make', 'Model', 'Year', 'LicensePlate', 'Status']
    treeview_management = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=10)

    for col in columns:
        treeview_management.heading(col, text=col)
        treeview_management.column(col, width=100, anchor="center")

    # Fetch data from SQLite instead of text file
    fleet_data = fetch_all_vehicles()
    for vehicle in fleet_data:
        treeview_management.insert("", "end", values=vehicle)

    # Treeview styling
    style = ttk.Style()
    style.configure("Treeview", rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    treeview_management.pack(fill=tk.BOTH, expand=True)

    management_window.treeview_management = treeview_management


def open_add_edit_vehicle_dialog(management_window, editing=False, vehicle=None):
    """Dialog for adding or editing vehicle information."""
    fields = ['Make', 'Model', 'Year', 'LicensePlate', 'Status']
    vehicle_data = {field: "" for field in fields}

    if editing and vehicle:
        vehicle_data = dict(zip(fields, vehicle[1:]))

    dialog = tk.Toplevel(management_window)
    dialog.title("Add/Edit Vehicle")
    dialog.geometry("300x280")
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
        update_vehicle(vehicle[0], new_vehicle_data)
        messagebox.showinfo("Success", "Vehicle updated successfully.")
    else:  # Adding new vehicle
        add_vehicle([
            new_vehicle_data['Make'],
            new_vehicle_data['Model'],
            new_vehicle_data['Year'],
            new_vehicle_data['LicensePlate'],
            new_vehicle_data['Status']
        ])
        messagebox.showinfo("Success", "Vehicle added successfully.")

    refresh_treeview(management_window)
    dialog.destroy()