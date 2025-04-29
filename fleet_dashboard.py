import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from fleet_operations import  add_vehicle, update_vehicle, fetch_all_vehicles, \
    refresh_treeview, get_vehicle_by_id, save_vehicle_to_db


def show_dashboard(parent):
    """Display a modern dashboard with vehicle data from the database in a scrollable Treeview."""
    frame = tk.Frame(parent, bg="#2E2E2E")  # Dark background for dashboard
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ---------- Scrollbars + Treeview Container ----------
    container = tk.Frame(frame)
    container.pack(fill=tk.BOTH, expand=True)

    tree_scroll_y = ttk.Scrollbar(container, orient="vertical")
    tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    tree_scroll_x = ttk.Scrollbar(container, orient="horizontal")
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- Define Columns ----------
    columns = [
        'ID', 'PLATE NR', 'DRIVER', 'SITE', 'MAKE', 'MOT DUE',
        'TAX DUE', 'SHELL', 'ESSO', 'ULEZ', 'CONGEST', 'DART',
        'MILEAGE', 'NO TRACK', 'DUE FOR CAMBELT', 'QUARTIX',
        'DIVIDE BY SITES', 'PRIVATE', 'SIDE NOTES'
    ]

    treeview = ttk.Treeview(container, columns=columns, show="headings",
                            yscrollcommand=tree_scroll_y.set,
                            xscrollcommand=tree_scroll_x.set,
                            selectmode="browse")

    tree_scroll_y.config(command=treeview.yview)
    tree_scroll_x.config(command=treeview.xview)

    # ---------- Treeview Style ----------
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
                    background="#1E1E1E",
                    foreground="#FFFFFF",
                    rowheight=25,
                    fieldbackground="#2E2E2E",
                    font=("Segoe UI", 10))
    style.configure("Treeview.Heading",
                    font=("Segoe UI", 10, "bold"),
                    background="#4A90E2",
                    foreground="white")

    # ---------- Setup Column Headings ----------
    for col in columns:
        treeview.heading(col, text=col)
        treeview.column(col, anchor="center", width=120)

    treeview.pack(fill=tk.BOTH, expand=True)

    # ---------- Populate with Database Data ----------
    fleet_data = fetch_all_vehicles()
    for vehicle in fleet_data:
        treeview.insert("", "end", values=vehicle)

    return treeview

def empty_vehicle_by_id(treeview):
    """Modern UI: Empty a vehicle from the fleet by ID (without deleting the ID) using SQLite."""

    dialog = tk.Toplevel()
    dialog.title("Empty Vehicle Data")
    dialog.geometry("400x250")
    dialog.configure(bg="#F9F9F9")
    dialog.grab_set()  # Modal behavior
    dialog.resizable(False, False)

    # ---------- Header ----------
    header_frame = tk.Frame(dialog, bg="#F9F9F9")
    header_frame.pack(pady=(20, 10))

    tk.Label(header_frame, text="Empty Vehicle Data", font=("Segoe UI", 14, "bold"), bg="#F9F9F9", fg="#333")\
        .pack()

    # ---------- ID Entry ----------
    id_frame = tk.Frame(dialog, bg="#F9F9F9")
    id_frame.pack(pady=(10, 5))

    tk.Label(id_frame, text="Enter Vehicle ID:", font=("Segoe UI", 11), bg="#F9F9F9").pack(pady=5)

    id_entry = tk.Entry(id_frame, font=("Segoe UI", 11), justify="center", width=20)
    id_entry.pack(ipady=5)

    # ---------- Action Buttons ----------
    button_frame = tk.Frame(dialog, bg="#F9F9F9")
    button_frame.pack(pady=25)

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

        with sqlite3.connect('fleet.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fleet WHERE id=?", (vehicle_id,))
            vehicle = cursor.fetchone()

            if not vehicle:
                messagebox.showwarning("Not Found", f"No vehicle found with ID {vehicle_id}.")
                return

            confirm = messagebox.askyesno("Confirm Emptying", f"Are you sure you want to clear vehicle ID {vehicle_id}?")
            if confirm:
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
                messagebox.showinfo("Success", f"Vehicle ID {vehicle_id} has been cleared.")
                refresh_treeview(treeview)
                dialog.destroy()

    # Buttons
    tk.Button(button_frame, text="Empty Vehicle", font=("Segoe UI", 11, "bold"),
              bg="#D9534F", fg="white", relief="flat", width=15, command=confirm_empty).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="Cancel", font=("Segoe UI", 10),
              bg="#E0E0E0", fg="#333", relief="flat", width=10, command=dialog.destroy).pack(side=tk.LEFT, padx=10)

def edit_vehicle_by_id(treeview):
    edit_window = tk.Toplevel()
    edit_window.title("Edit Vehicle Details")
    edit_window.geometry("800x600")
    edit_window.configure(bg="#F5F5F5")

    # ---------- Top Section: ID Input ----------
    id_frame = tk.Frame(edit_window, bg="#F5F5F5")
    id_frame.pack(pady=10)

    tk.Label(id_frame, text="Enter Vehicle ID to Edit:", font=("Segoe UI", 12, "bold"), bg="#F5F5F5")\
        .pack(side=tk.LEFT, padx=5)

    vehicle_id_entry = tk.Entry(id_frame, font=("Segoe UI", 12), width=10)
    vehicle_id_entry.pack(side=tk.LEFT)

    # ---------- Middle Section: Scrollable Fields ----------
    container = tk.Frame(edit_window, bg="#F5F5F5")
    container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    canvas = tk.Canvas(container, bg="#F5F5F5")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=v_scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    fields_frame = tk.Frame(canvas, bg="#F5F5F5")
    canvas.create_window((0, 0), window=fields_frame, anchor="nw")

    entry_widgets = {}
    fields = [
        'ID', 'PLATE NR', 'DRIVER', 'SITE', 'MAKE', 'MOT DUE', 'TAX DUE', 'SHELL', 'ESSO', 'ULEZ', 'CONGEST',
        'DART', 'MILEAGE', 'NO TRACK', 'DUE FOR CAMBELT', 'QUARTIX', 'DIVIDE BY SITES', 'PRIVATE', 'SIDE NOTES'
    ]

    def build_fields(vehicle):
        for widget in fields_frame.winfo_children():
            widget.destroy()
        entry_widgets.clear()

        for idx, field in enumerate(fields):
            row = idx // 2
            col = (idx % 2) * 2

            label = tk.Label(fields_frame, text=field + ":", bg="#F5F5F5", font=("Segoe UI", 10))
            label.grid(row=row, column=col, sticky="e", padx=10, pady=5)

            entry = tk.Entry(fields_frame, font=("Segoe UI", 10), width=30)
            entry.grid(row=row, column=col + 1, padx=5, pady=5)

            value = str(vehicle[idx]) if idx < len(vehicle) and vehicle[idx] is not None else ""
            entry.insert(0, value)
            entry_widgets[field] = entry

    # ---------- Bottom Section: Buttons ----------
    button_frame = tk.Frame(edit_window, bg="#F5F5F5")
    button_frame.pack(pady=15)

    def on_submit():
        vehicle_id = vehicle_id_entry.get().strip()
        if not vehicle_id:
            messagebox.showwarning("Missing ID", "Please enter a vehicle ID.")
            return

        vehicle = get_vehicle_by_id(vehicle_id)
        if not vehicle:
            messagebox.showwarning("Not Found", f"No vehicle found with ID {vehicle_id}.")
            return

        build_fields(vehicle)

    def save_changes():
        vehicle_id = vehicle_id_entry.get().strip()
        if not vehicle_id:
            messagebox.showerror("Error", "No vehicle ID entered.")
            return

        new_data = {k: entry_widgets[k].get() for k in fields if k != 'ID'}
        update_vehicle(vehicle_id, new_data)
        messagebox.showinfo("Success", "Vehicle updated successfully.")
        refresh_treeview(treeview)
        edit_window.destroy()

    tk.Button(button_frame, text="Submit", font=("Segoe UI", 11), bg="#4A90E2", fg="white", width=12,
              command=on_submit).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="Save Changes", font=("Segoe UI", 11, "bold"), bg="#28A745", fg="white", width=15,
              command=save_changes).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="Cancel", font=("Segoe UI", 11), bg="#DC3545", fg="white", width=12,
              command=edit_window.destroy).pack(side=tk.LEFT, padx=10)

def open_fleet_management(parent):
    """Open the fleet management window to manage the fleet."""
    management_window = tk.Toplevel(parent)
    management_window.title("Manage Fleet")
    management_window.geometry("1000x600")
    management_window.configure(bg="#f0f0f0")

    # ---------- Header Buttons ----------
    header_frame = tk.Frame(management_window, bg="#f0f0f0")
    header_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)

    tk.Button(
        header_frame, text="Add Vehicle",
        command=lambda: open_add_edit_vehicle_dialog(management_window, editing=False),
        relief="flat", bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
        padx=15, pady=8
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        header_frame, text="Edit Vehicle",
        command=lambda: edit_vehicle_by_id(management_window.treeview_management),
        relief="flat", bg="#2196F3", fg="white", font=("Segoe UI", 11, "bold"),
        padx=15, pady=8
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        header_frame, text="Delete Vehicle",
        command=lambda: empty_vehicle_by_id(management_window.treeview_management),
        relief="flat", bg="#f44336", fg="white", font=("Segoe UI", 11, "bold"),
        padx=15, pady=8
    ).pack(side=tk.LEFT, padx=10)

    # ---------- Treeview Area ----------
    treeview_frame = tk.Frame(management_window, bg="#f0f0f0")
    treeview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    vertical_scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical")
    vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    horizontal_scrollbar = ttk.Scrollbar(treeview_frame, orient="horizontal")
    horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    columns = [
        'ID', 'PLATE NR', 'DRIVER', 'SITE', 'MAKE', 'MOT DUE', 'TAX DUE', 'SHELL', 'ESSO',
        'ULEZ', 'CONGEST', 'DART', 'MILEAGE', 'NO TRACK', 'DUE FOR CAMBELT',
        'QUARTIX', 'DIVIDE BY SITES', 'PRIVATE', 'SIDE NOTES'
    ]

    treeview_management = ttk.Treeview(
        treeview_frame, columns=columns, show="headings",
        yscrollcommand=vertical_scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )

    for col in columns:
        treeview_management.heading(col, text=col)
        treeview_management.column(col, width=120, anchor="center")

    treeview_management.pack(fill=tk.BOTH, expand=True)

    # Scrollbar binding
    vertical_scrollbar.config(command=treeview_management.yview)
    horizontal_scrollbar.config(command=treeview_management.xview)

    # Treeview styling
    style = ttk.Style()
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    # ---------- Load Data ----------
    fleet_data = fetch_all_vehicles()
    for vehicle in fleet_data:
        treeview_management.insert("", "end", values=vehicle)

    # Attach Treeview for other callbacks
    management_window.treeview_management = treeview_management

def open_add_edit_vehicle_dialog(management_window, editing=False, vehicle=None):

    fields = [
        'PLATE NR', 'DRIVER', 'SITE', 'MAKE', 'MOT DUE', 'TAX DUE', 'SHELL', 'ESSO', 'ULEZ', 'CONGEST', 'DART',
        'MILEAGE', 'NO TRACK', 'DUE FOR CAMBELT', 'QUARTIX', 'DIVIDE BY SITES', 'PRIVATE', 'SIDE NOTES'
    ]
    vehicle_data = dict(zip(fields, vehicle[1:])) if editing and vehicle else {field: "" for field in fields}

    dialog = tk.Toplevel(management_window)
    dialog.title("Edit Vehicle" if editing else "Add Vehicle")
    dialog.geometry("750x600")
    dialog.configure(bg="#f0f0f0")

    # Scrollable canvas setup
    canvas_frame = tk.Frame(dialog, bg="#f0f0f0")
    canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    canvas = tk.Canvas(canvas_frame, bg="#f0f0f0", highlightthickness=0)
    v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=v_scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    form_frame = tk.Frame(canvas, bg="#f0f0f0")
    canvas.create_window((0, 0), window=form_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    form_frame.bind("<Configure>", on_frame_configure)

    input_fields = {}
    for i, field in enumerate(fields):
        row = i // 2
        col = (i % 2) * 2

        label = tk.Label(form_frame, text=f"{field}:", font=("Segoe UI", 10), bg="#f0f0f0")
        label.grid(row=row, column=col, sticky="e", padx=10, pady=5)

        entry = tk.Entry(form_frame, font=("Segoe UI", 10), width=30)
        entry.insert(0, vehicle_data.get(field, ''))
        entry.grid(row=row, column=col + 1, padx=5, pady=5)

        input_fields[field] = entry

    # Bottom action buttons
    button_frame = tk.Frame(dialog, bg="#f0f0f0")
    button_frame.pack(pady=15)

    save_button = tk.Button(
        button_frame, text="Save",
        command=lambda: save_vehicle_to_db(dialog, input_fields, vehicle[0] if editing else None, management_window),
        relief="flat", bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=8
    )
    save_button.pack(side=tk.LEFT, padx=10)

    cancel_button = tk.Button(
        button_frame, text="Cancel",
        command=dialog.destroy,
        relief="flat", bg="#f44336", fg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=8
    )
    cancel_button.pack(side=tk.LEFT, padx=10)

