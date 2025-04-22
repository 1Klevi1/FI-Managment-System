import tkinter as tk
from dashboard import MainDashboard  # Import the MainDashboard class from dashboard.py


def main():
    root = tk.Tk()
    dashboard = MainDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
