import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os
import sys

from fleet_dashboard import open_fleet_management


# Resource path function to handle path differences in development and packaged apps
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and PyInstaller. """
    try:
        if hasattr(sys, '_MEIPASS'):
            # If running in PyInstaller
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # Running in development mode
            return os.path.join(os.path.abspath("."), relative_path)
    except Exception as e:
        print(f"Error loading resource: {e}")
        return None


class MainDashboard:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("F & I Management Dashboard")
        self.parent.geometry("900x650")
        self.parent.configure(bg="#2E2E2E")

        # Create the frame for the dashboard
        self.frame = tk.Frame(self.parent, bg="#2E2E2E")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # Header with company logo and title
        self.header_frame = tk.Frame(self.frame, bg="#2E2E2E")
        self.header_frame.pack(fill=tk.X, pady=30, anchor="n")

        # Load logo
        logo_path = resource_path("logo1.png")  # Get the logo path using resource_path
        if logo_path:
            try:
                img = Image.open(logo_path)  # Open the logo image
                img = img.resize((120, 120))  # Resize logo if necessary

                # Crop the logo into a circle (round corners)
                mask = Image.new('L', (120, 120), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 120, 120), fill=255)
                img.putalpha(mask)

                # Convert the image to PhotoImage format
                self.logo = ImageTk.PhotoImage(img)

                # Create label for logo and place it in the header, centered
                self.logo_label = tk.Label(self.header_frame, image=self.logo, bg="#2E2E2E")
                self.logo_label.pack(pady=10, anchor="center")

            except Exception as e:
                print(f"Error loading logo image: {e}")
                error_label = tk.Label(self.header_frame, text="Logo failed to load", bg="#2E2E2E", fg="red")
                error_label.pack(pady=20, anchor="center")
        else:
            print("Logo path is incorrect or logo file not found")
            error_label = tk.Label(self.header_frame, text="Logo file not found", bg="#2E2E2E", fg="red")
            error_label.pack(pady=20, anchor="center")

        # Dashboard title
        self.title_label = tk.Label(self.header_frame, text="F & I Management System",
                                    font=("Segoe UI", 18, "bold"), bg="#2E2E2E", fg="#FFFFFF", anchor="center")
        self.title_label.pack(pady=10)

        # Main dashboard buttons
        self.main_button_frame = tk.Frame(self.frame, bg="#2E2E2E")
        self.main_button_frame.pack(pady=30, expand=True)

        # Manage Fleet Button (centered)
        self.manage_button = tk.Button(self.main_button_frame, text="Manage Fleet", font=("Segoe UI", 14, "bold"),
                                       bg="#4A90E2", fg="white", padx=30, pady=10, relief="flat", width=20,
                                       command=self.open_fleet_management)
        self.manage_button.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # Example additional button (Vehicle Reports, centered)
        self.report_button = tk.Button(self.main_button_frame, text="Vehicle Reports", font=("Segoe UI", 14, "bold"),
                                       bg="#50E3C2", fg="white", padx=30, pady=10, relief="flat", width=20,
                                       command=self.open_reports_window)
        self.report_button.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        # Optional description below the buttons
        self.description_label = tk.Label(self.frame, text="Manage your fleet, generate reports, and much more.",
                                          font=("Segoe UI", 12), bg="#2E2E2E", fg="#FFFFFF")
        self.description_label.pack(pady=10, anchor="center")

        # Footer with copyright information
        self.footer_label = tk.Label(self.frame, text="© 2025 F & I Ltd | All Rights Reserved",
                                     font=("Helvetica Neue", 10), bg="#2E2E2E", fg="#777777")
        self.footer_label.pack(side=tk.BOTTOM, pady=20)

    def open_fleet_management(self):
        open_fleet_management(self.parent)

    def open_reports_window(self):
        # Placeholder for the vehicle reports window
        report_window = tk.Toplevel()
        report_window.title("Vehicle Reports")
        report_window.geometry("600x400")
        report_window.configure(bg="#2E2E2E")

        header = tk.Label(report_window, text="Vehicle Reports Dashboard", font=("Segoe UI", 16, "bold"),
                          bg="#4A90E2", fg="white", pady=15)
        header.pack(fill=tk.X)

        # Sample content
        report_label = tk.Label(report_window, text="Generate your vehicle reports here.",
                                font=("Segoe UI", 14), bg="#2E2E2E", fg="#666")
        report_label.pack(pady=20)
# pyinstaller --onefile --windowed --add-data "logo1.png;." --add-data "fleet.db;." main.py