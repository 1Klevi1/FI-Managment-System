import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from fleet_operations import read_fleet_data, write_fleet_data, update_vehicle, add_vehicle, refresh_treeview


def show_dashboard(parent):
    """Function to display the dashboard with vehicle data."""
    frame = tk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Table to display fleet data
    columns = ['ID', 'Make', 'Model', 'Year', 'LicensePlate', 'Status']
    treeview = ttk.Treeview(frame, columns=columns, show="headings", height=10)

    for col in columns:
        treeview.heading(col, text=col)
        treeview.column(col, width=100, anchor="center")

    # Insert vehicle data into the table
    fleet_data = read_fleet_data()
    for vehicle in fleet_data:
        treeview.insert("", "end", values=vehicle)

    # Modernize Treeview appearance
    style = ttk.Style()
    style.configure("Treeview", rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    treeview.pack(fill=tk.BOTH, expand=True)

    # Return treeview for further use (for operations like add/edit/delete)
    return treeview


def delete_vehicle_by_id(treeview):
    """Delete a vehicle from the fleet by ID."""
    vehicle_id = simpledialog.askstring("Delete Vehicle", "Enter the ID of the vehicle to delete:")
    if not vehicle_id:
        messagebox.showwarning("Invalid ID", "Please enter a valid vehicle ID.")
        return

    fleet_data = read_fleet_data()
    vehicle_to_delete = [v for v in fleet_data if v[0] == vehicle_id]
    if not vehicle_to_delete:
        messagebox.showwarning("Vehicle Not Found", f"No vehicle found with ID {vehicle_id}.")
        return

    fleet_data = [v for v in fleet_data if v[0] != vehicle_id]
    write_fleet_data(fleet_data)
    messagebox.showinfo("Success", "Vehicle deleted successfully.")

    refresh_treeview(treeview)


def edit_vehicle_by_id(treeview):
    """Edit a vehicle's details by its ID with a modern UI dialog."""

    # Create a top-level window for the editing dialog
    edit_window = tk.Toplevel()
    edit_window.title("Edit Vehicle Details")
    edit_window.geometry("400x500")
    edit_window.configure(bg="#F5F5F5")  # Light background for the dialog

    # Label and input fields setup
    tk.Label(edit_window, text="Enter Vehicle ID to Edit", font=("Segoe UI", 12, "bold"),
             bg="#F5F5F5", fg="#333").pack(pady=10)

    vehicle_id_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
    vehicle_id_entry.pack(pady=10)

    def on_submit():
        vehicle_id = vehicle_id_entry.get()
        if not vehicle_id:
            messagebox.showwarning("Invalid ID", "Please enter a valid vehicle ID.")
            return

        fleet_data = read_fleet_data()
        vehicle_to_edit = None
        for vehicle in fleet_data:
            if vehicle[0] == vehicle_id:
                vehicle_to_edit = vehicle
                break

        if not vehicle_to_edit:
            messagebox.showwarning("Vehicle Not Found", f"No vehicle found with ID {vehicle_id}.")
            return

        # Create a frame to display the fields for editing
        fields_frame = tk.Frame(edit_window, bg="#F5F5F5")
        fields_frame.pack(pady=10)

        fields = ['Make', 'Model', 'Year', 'LicensePlate', 'Status']
        entry_widgets = {}

        for field in fields:
            tk.Label(fields_frame, text=f"{field}:", font=("Segoe UI", 10), bg="#F5F5F5").grid(row=fields.index(field),
                                                                                               column=0, padx=10,
                                                                                               pady=5)
            entry_widget = tk.Entry(fields_frame, font=("Segoe UI", 12))
            entry_widget.grid(row=fields.index(field), column=1, padx=10, pady=5)
            entry_widget.insert(0, vehicle_to_edit[fields.index(field) + 1])  # Fill with current data
            entry_widgets[field] = entry_widget

        def save_changes():
            # Get the new data from entry widgets
            new_vehicle_data = {field: entry_widgets[field].get() for field in fields}

            # Update the vehicle data in the system
            update_vehicle(vehicle_id, new_vehicle_data)
            messagebox.showinfo("Success", "Vehicle updated successfully.")

            # Refresh the treeview
            refresh_treeview(treeview)
            edit_window.destroy()  # Close the edit window

        # Add a Save button
        save_button = tk.Button(edit_window, text="Save Changes", font=("Segoe UI", 12, "bold"),
                                bg="#4A90E2", fg="white", relief="flat", width=20, command=save_changes)
        save_button.pack(pady=20)

    # Submit button to start the edit process
    submit_button = tk.Button(edit_window, text="Submit", font=("Segoe UI", 12, "bold"), bg="#50E3C2",
                              fg="white", relief="flat", width=20, command=on_submit)
    submit_button.pack(pady=20)

def open_fleet_management(parent):
    """Open the fleet management window to manage the fleet."""
    management_window = tk.Toplevel(parent)
    management_window.title("Manage Fleet")
    management_window.geometry("600x400")  # Set a modern window size
    management_window.configure(bg="#f0f0f0")

    # Create a header frame
    header_frame = tk.Frame(management_window, bg="#f0f0f0")
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    # Add buttons for managing the fleet with modernized appearance
    add_button = tk.Button(header_frame, text="Add Vehicle", command=lambda: open_add_edit_vehicle_dialog(management_window, editing=False),
                           relief="flat", bg="#4CAF50", fg="white", font=("Arial", 12), padx=20, pady=10)
    add_button.pack(side=tk.LEFT, padx=10)

    edit_button = tk.Button(header_frame, text="Edit Vehicle", command=lambda: edit_vehicle_by_id(management_window),
                            relief="flat", bg="#2196F3", fg="white", font=("Arial", 12), padx=20, pady=10)
    edit_button.pack(side=tk.LEFT, padx=10)

    delete_button = tk.Button(header_frame, text="Delete Vehicle", command=lambda: delete_vehicle_by_id(management_window),
                              relief="flat", bg="#f44336", fg="white", font=("Arial", 12), padx=20, pady=10)
    delete_button.pack(side=tk.LEFT, padx=10)

    # Create a frame for the Treeview
    treeview_frame = tk.Frame(management_window, bg="#f0f0f0")
    treeview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create the treeview to display vehicle data
    columns = ['ID', 'Make', 'Model', 'Year', 'LicensePlate', 'Status']
    treeview_management = ttk.Treeview(treeview_frame, columns=columns, show="headings", height=10)

    for col in columns:
        treeview_management.heading(col, text=col)
        treeview_management.column(col, width=100, anchor="center")

    # Insert vehicle data into the treeview
    fleet_data = read_fleet_data()
    for vehicle in fleet_data:
        treeview_management.insert("", "end", values=vehicle)

    # Modernize Treeview appearance
    style = ttk.Style()
    style.configure("Treeview", rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    treeview_management.pack(fill=tk.BOTH, expand=True)

    # Store treeview as an attribute of the management_window
    management_window.treeview_management = treeview_management


def open_add_edit_vehicle_dialog(management_window, editing=False, vehicle=None):
    """Dialog for adding or editing vehicle information."""
    fields = ['Make', 'Model', 'Year', 'LicensePlate', 'Status']
    vehicle_data = {field: "" for field in fields}  # Default empty fields

    if editing and vehicle:
        # Prefill fields with current vehicle data
        vehicle_data = dict(zip(fields, vehicle[1:]))

    # Create a dialog box for input
    dialog = tk.Toplevel(management_window)
    dialog.title("Add/Edit Vehicle")
    dialog.geometry("300x250")
    dialog.configure(bg="#f0f0f0")

    # Create and arrange input fields in a more modern way
    input_frame = tk.Frame(dialog, bg="#f0f0f0")
    input_frame.pack(padx=10, pady=10)

    input_fields = {}
    for field in fields:
        label = tk.Label(input_frame, text=f"{field}:", font=("Arial", 10), bg="#f0f0f0")
        label.grid(row=fields.index(field), column=0, sticky="w", padx=5, pady=5)
        entry = tk.Entry(input_frame, font=("Arial", 10))
        entry.insert(0, vehicle_data.get(field, ''))
        entry.grid(row=fields.index(field), column=1, padx=5, pady=5)
        input_fields[field] = entry

    # Add save and cancel buttons
    save_button = tk.Button(dialog, text="Save", command=lambda: save_vehicle(dialog, input_fields, vehicle, management_window),
                            relief="flat", bg="#4CAF50", fg="white", font=("Arial", 12), padx=20, pady=10)
    save_button.pack(side=tk.LEFT, padx=20, pady=10)

    cancel_button = tk.Button(dialog, text="Cancel", command=dialog.destroy,
                              relief="flat", bg="#f44336", fg="white", font=("Arial", 12), padx=20, pady=10)
    cancel_button.pack(side=tk.RIGHT, padx=20, pady=10)


def save_vehicle(dialog, input_fields, vehicle, management_window):
    """Save the vehicle data (add or edit) and refresh the treeview."""
    new_vehicle_data = {key: entry.get() for key, entry in input_fields.items()}

    if vehicle:  # Editing
        update_vehicle(vehicle[0], new_vehicle_data)
        messagebox.showinfo("Success", "Vehicle updated successfully.")
    else:  # Adding
        add_vehicle([new_vehicle_data['Make'], new_vehicle_data['Model'], new_vehicle_data['Year'],
                     new_vehicle_data['LicensePlate'], new_vehicle_data['Status']])
        messagebox.showinfo("Success", "Vehicle added successfully.")

    # Refresh the treeview of the management window
    refresh_treeview(management_window)
    dialog.destroy()
