import tkinter as tk
from dashboard import MainDashboard
from fleet_operations import initialize_database


def main():
    root = tk.Tk()
    dashboard = MainDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    initialize_database()
    main()

