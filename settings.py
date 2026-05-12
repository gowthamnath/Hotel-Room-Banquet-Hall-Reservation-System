import customtkinter as ctk
import subprocess
import sys
import os
import mysql.connector
from tkinter import messagebox

# Database Configuration
DB_CONFIG = {
    "host": "141.209.241.57",
    "port": 3306,
    "user": "putch1v",
    "password": "mypass",
    "database": "BIS698MSpring26Group_2"
}

# UI Styling (Aligned with Admin Center)
PRIMARY_GREEN = "#5C8A3C"
SIDEBAR_GREEN = "#4A7A2E"
DARK_TEXT = "#2C3E50"
GRAY_TEXT = "#666666"
SECTION_GREEN = "#3D7A1A"

NAV_ITEMS = ["Rooms", "Banquet Halls", "My Bookings", "Settings"
     
]

NAV_SCREENS = {
    "Rooms": "search_room_screen.py",
    "Banquet Halls": "banquet_hall_screen.py",
    "My Bookings": "mybookings.py"
}

class SettingsScreen(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.user_id = self._get_logged_in_user_id()
        self.user_name = self._get_logged_in_user_name()

        self.title("Hotel Reservation - Settings")
        self.configure(fg_color="white")
        
        # UI Build
        self._build_ui()
        self.after(0, lambda: self.state('zoomed'))
        
        if self.user_id:
            self._load_current_data()

    # SESSION

    def _get_logged_in_user_id(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return None

    def _get_logged_in_user_name(self):
        if not self.user_id: return "Guest"
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT first_name FROM User WHERE user_id = %s", (self.user_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "Guest"
        except:
            return "User"

    #  UI BUILD 

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="white")
        outer.pack(fill="both", expand=True)

        # Sidebar
        sidebar = ctk.CTkFrame(outer, fg_color=SIDEBAR_GREEN, width=215, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="🏨 Hotel Center", font=ctk.CTkFont(size=15, weight="bold"), text_color="white").pack(pady=20, padx=15, anchor="w")

        for label in NAV_ITEMS:
            is_active = (label == "Settings")
            btn = ctk.CTkButton(sidebar, 
                                text=f"  {label}", 
                                fg_color="#3D6A22" if is_active else "transparent", 
                                hover_color="#3D6A22", 
                                text_color="white", 
                                anchor="w", 
                                height=40,
                                command=lambda l=label: self._nav(l))
            btn.pack(fill="x", padx=10, pady=2)

        ctk.CTkButton(sidebar, text="Sign Out", fg_color="transparent", border_width=1, border_color="#AAAAAA", command=self._sign_out).pack(side="bottom", padx=15, pady=20)

        # Main Content Area
        main_scroll = ctk.CTkScrollableFrame(outer, fg_color="white")
        main_scroll.pack(side="left", fill="both", expand=True)

        # Header Section
        ctk.CTkLabel(main_scroll, text="Account Settings", font=ctk.CTkFont(family="Georgia", size=26, weight="bold"), text_color=SIDEBAR_GREEN).pack(anchor="w", padx=30, pady=(25, 5))
        ctk.CTkLabel(main_scroll, text=f"Welcome back, {self.user_name}! Manage your personal info and security preferences.", font=ctk.CTkFont(size=12), text_color=GRAY_TEXT).pack(anchor="w", padx=30, pady=(0, 20))

        # SECTION 1: PROFILE SETTINGS 
        prof_frame = self._create_section(main_scroll, "Profile Settings")
        
        ctk.CTkLabel(prof_frame, text="Email Address", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
        self.email_entry = ctk.CTkEntry(prof_frame, width=400, placeholder_text="example@domain.com")
        self.email_entry.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(prof_frame, text="Phone Number", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
        self.phone_entry = ctk.CTkEntry(prof_frame, width=400, placeholder_text="+1 000 000 0000")
        self.phone_entry.pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(prof_frame, text="Update Profile", fg_color=PRIMARY_GREEN, width=160, height=35, command=self._update_profile).pack(anchor="w", pady=15)

        # SECTION 2: SECURITY SETTINGS 
        sec_frame = self._create_section(main_scroll, "Security Settings")
        
        ctk.CTkLabel(sec_frame, text="Old Password", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
        self.old_password = ctk.CTkEntry(sec_frame, width=400, show="*")
        self.old_password.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(sec_frame, text="New Password", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
        self.new_password = ctk.CTkEntry(sec_frame, width=400, show="*")
        self.new_password.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(sec_frame, text="Confirm New Password", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
        self.confirm_password = ctk.CTkEntry(sec_frame, width=400, show="*")
        self.confirm_password.pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(sec_frame, text="Change Password", fg_color="#E67E22", hover_color="#D35400", width=160, height=35, command=self._change_password).pack(anchor="w", pady=15)

    def _create_section(self, parent, title):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=30, pady=15)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=SECTION_GREEN).pack(anchor="w")
        ctk.CTkFrame(frame, fg_color="#C8DDB4", height=2).pack(fill="x", pady=(5, 15))
        return frame

    # DB FUNCTIONS 

    def _load_current_data(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT email, phone FROM User WHERE user_id = %s", (self.user_id,))
            user = cursor.fetchone()
            if user:
                self.email_entry.insert(0, user['email'] or "")
                self.phone_entry.insert(0, user['phone'] or "")
            conn.close()
        except:
            pass

    def _update_profile(self):
        if not self.user_id:
            messagebox.showerror("Error", "No active session found.")
            return

        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET email = %s, phone = %s WHERE user_id = %s", (email, phone, self.user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Profile updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update: {e}")

    def _change_password(self):
        if not self.user_id:
            messagebox.showerror("Error", "No active session found.")
            return

        old_pw = self.old_password.get()
        new_pw = self.new_password.get()
        confirm_pw = self.confirm_password.get()

        if new_pw != confirm_pw:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM User WHERE user_id = %s", (self.user_id,))
            result = cursor.fetchone()

            if result and result[0] == old_pw:
                cursor.execute("UPDATE User SET password_hash = %s WHERE user_id = %s", (new_pw, self.user_id))
                conn.commit()
                messagebox.showinfo("Success", "Password changed successfully!")
                self.old_password.delete(0, 'end'); self.new_password.delete(0, 'end'); self.confirm_password.delete(0, 'end')
            else:
                messagebox.showerror("Error", "Incorrect old password.")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # NAV

    def _nav(self, label):
        if label == "Settings": return
        script = NAV_SCREENS.get(label)
        if script:
            target_path = os.path.join(os.path.dirname(__file__), script)
            if os.path.exists(target_path):
                self.destroy()
                subprocess.Popen([sys.executable, target_path])

    def _sign_out(self):
        session_path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(session_path):
            os.remove(session_path)
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "login_screen.py")])

if __name__ == "__main__":
    app = SettingsScreen()
    app.mainloop()