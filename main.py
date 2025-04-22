import tkinter as tk
from dashboard import MainDashboard  # Import the MainDashboard class from dashboard.py
from fleet_database import init_db, read_fleet_data, add_vehicle, update_vehicle, delete_vehicle


def main():
    root = tk.Tk()
    dashboard = MainDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    init_db()  # Initialize DB and table if not already existing
    main()

