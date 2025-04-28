import tkinter as tk
from dashboard import MainDashboard
from fleet_operations import initialize_database, import_dataset_to_db


def main():
    root = tk.Tk()
    dashboard = MainDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    initialize_database()
    # Specify the path to your CSV file here
    import_dataset_to_db('Excel/importData.csv')
    main()

