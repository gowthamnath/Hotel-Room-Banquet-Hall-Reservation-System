import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
import os
import sys
import subprocess
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    "host": "141.209.241.57",
    "port": 3306,
    "user": "putch1v",
    "password": "mypass",
    "database": "BIS698MSpring26Group_2"
}

# UI Styling Colors
PRIMARY_GREEN = "#5C8A3C"
SIDEBAR_GREEN = "#4A7A2E"
DARK_TEXT = "#2C3E50"
GRAY_TEXT = "#666666"
SECTION_GREEN = "#3D7A1A"

NAV_ITEMS = [
    ("User & Report Management", "👥"), ("Room & Hall Management", "🛏"),
    ("Booking Calendar", "📅"), ("BI Dashboard", "📊"), ("Settings", "⚙")
]

class SettingsAdminScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Session Handling (Non-blocking)
        self.admin_id = self._get_session_id()
        self.admin_name = self._get_admin_name()
        
        self.title("Admin Center - Settings")
        
        # Set to Full Screen (Maximized)
        self.after(0, lambda: self.state('zoomed'))
        
        self.configure(fg_color="white")
        self._build_ui()
        
        # Load existing data if session exists
        if self.admin_id:
            self._load_current_data()

    def _get_session_id(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read().strip()
        except:
            pass
        return None

    def _get_admin_name(self):
        if not self.admin_id: 
            return "Admin"
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT first_name FROM User WHERE user_id = %s", (self.admin_id,))
            res = cursor.fetchone()
            conn.close()
            return res['first_name'] if res else "Admin"
        except Error: 
            return "Admin"

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="white")
        outer.pack(fill="both", expand=True)
        
        # Sidebar Navigation
        sidebar = ctk.CTkFrame(outer, fg_color=SIDEBAR_GREEN, width=215, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        ctk.CTkLabel(sidebar, text="⚙ Admin Center", font=ctk.CTkFont(size=15, weight="bold"), text_color="white").pack(pady=20, padx=15, anchor="w")
        
        for label, icon in NAV_ITEMS:
            is_active = (label == "Settings")
            btn = ctk.CTkButton(sidebar, 
                                text=f"  {icon}  {label}", 
                                fg_color="#3D6A22" if is_active else "transparent", 
                                hover_color="#3D6A22", 
                                text_color="white", 
                                anchor="w", 
                                height=40,
                                command=lambda l=label: self._navigate(l))
            btn.pack(fill="x", padx=10, pady=2)
            
        ctk.CTkButton(sidebar, text="Sign Out", fg_color="transparent", border_width=1, border_color="#AAAAAA", command=self._sign_out).pack(side="bottom", padx=15, pady=20)

        # Main Content Area
        main_scroll = ctk.CTkScrollableFrame(outer, fg_color="white")
        main_scroll.pack(side="left", fill="both", expand=True)
        
        # Header
        ctk.CTkLabel(main_scroll, text="Account Settings", font=ctk.CTkFont(family="Georgia", size=26, weight="bold"), text_color=SIDEBAR_GREEN).pack(anchor="w", padx=30, pady=(25, 5))
        ctk.CTkLabel(main_scroll, text=f"Welcome, {self.admin_name}! Manage your profile and security credentials below.", font=ctk.CTkFont(size=12), text_color=GRAY_TEXT).pack(anchor="w", padx=30, pady=(0, 20))

        # SECTION 1: PROFILE SETTINGS 
        prof_frame = self._create_section(main_scroll, "Profile Settings")
        
        ctk.CTkLabel(prof_frame, text="Update Email and Phone", font=ctk.CTkFont(size=13, weight="bold"), text_color=DARK_TEXT).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(prof_frame, text="Email Address", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        self.email_entry = ctk.CTkEntry(prof_frame, width=400, placeholder_text="Enter new email")
        self.email_entry.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(prof_frame, text="Phone Number", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        self.phone_entry = ctk.CTkEntry(prof_frame, width=400, placeholder_text="Enter new phone number")
        self.phone_entry.pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(prof_frame, text="Save Profile Changes", fg_color=PRIMARY_GREEN, command=self._update_profile, width=180, height=35).pack(anchor="w", pady=15)

        # SECTION 2: SECURITY SETTINGS 
        sec_frame = self._create_section(main_scroll, "Security Settings")
        
        ctk.CTkLabel(sec_frame, text="Update Password", font=ctk.CTkFont(size=13, weight="bold"), text_color=DARK_TEXT).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(sec_frame, text="Old Password", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        self.old_pass = ctk.CTkEntry(sec_frame, width=400, show="*", placeholder_text="Enter old password")
        self.old_pass.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(sec_frame, text="New Password", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        self.new_pass = ctk.CTkEntry(sec_frame, width=400, show="*", placeholder_text="Enter new password")
        self.new_pass.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(sec_frame, text="Confirm New Password", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        self.confirm_pass = ctk.CTkEntry(sec_frame, width=400, show="*", placeholder_text="Confirm new password")
        self.confirm_pass.pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(sec_frame, text="Update Password", fg_color="#E67E22", hover_color="#D35400", command=self._update_password, width=180, height=35).pack(anchor="w", pady=15)

    def _create_section(self, parent, title):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=30, pady=15)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=SECTION_GREEN).pack(anchor="w")
        ctk.CTkFrame(frame, fg_color="#C8DDB4", height=2).pack(fill="x", pady=(5, 15))
        return frame

    def _load_current_data(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT email, phone FROM User WHERE user_id = %s", (self.admin_id,))
            user = cursor.fetchone()
            if user:
                self.email_entry.delete(0, 'end')
                self.email_entry.insert(0, user['email'] or "")
                self.phone_entry.delete(0, 'end')
                self.phone_entry.insert(0, user['phone'] or "")
            conn.close()
        except Error:
            pass

    def _update_profile(self):
        if not self.admin_id:
            messagebox.showerror("Error", "No active session. Please log in.")
            return

        new_email = self.email_entry.get().strip()
        new_phone = self.phone_entry.get().strip()

        if not new_email:
            messagebox.showwarning("Input Error", "Email is required.")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET email = %s, phone = %s WHERE user_id = %s", 
                           (new_email, new_phone, self.admin_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Profile information updated successfully.")
        except Error as e:
            messagebox.showerror("Database Error", str(e))

    def _update_password(self):
        if not self.admin_id:
            messagebox.showerror("Error", "No active session. Please log in.")
            return

        old = self.old_pass.get()
        new = self.new_pass.get()
        confirm = self.confirm_pass.get()

        if not old or not new or not confirm:
            messagebox.showwarning("Input Error", "All password fields must be filled.")
            return
        
        if new != confirm:
            messagebox.showerror("Validation Error", "The new passwords do not match.")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            # Verify the old password matches what's in the DB
            cursor.execute("SELECT password_hash FROM User WHERE user_id = %s", (self.admin_id,))
            res = cursor.fetchone()
            
            if res and res['password_hash'] == old:
                cursor.execute("UPDATE User SET password_hash = %s WHERE user_id = %s", (new, self.admin_id))
                conn.commit()
                messagebox.showinfo("Success", "Password changed successfully.")
                self.old_pass.delete(0, 'end')
                self.new_pass.delete(0, 'end')
                self.confirm_pass.delete(0, 'end')
            else:
                messagebox.showerror("Security Error", "Current password provided is incorrect.")
            
            conn.close()
        except Error as e:
            messagebox.showerror("Database Error", str(e))

    def _navigate(self, label):
        file_map = {
            "User & Report Management": "user_management_screen.py",
            "Room & Hall Management": "room_management_admin.py",
            "Booking Calendar": "booking_calender.py",
            "BI Dashboard": "bi_dashboard.py",
            "Settings": "settings_admin.py"
        }
        
        if label == "Settings": return
        
        target_file = file_map.get(label)
        if target_file:
            target_path = os.path.join(os.path.dirname(__file__), target_file)
            if os.path.exists(target_path):
                self.destroy()
                subprocess.Popen([sys.executable, target_path])

    def _sign_out(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(path): os.remove(path)
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "login_screen.py")])

if __name__ == "__main__":
    app = SettingsAdminScreen()
    app.mainloop()