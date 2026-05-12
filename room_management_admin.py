import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
import subprocess
import sys
import os
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    "host": "141.209.241.57",
    "port": 3306,
    "user": "putch1v",
    "password": "mypass",
    "database": "BIS698MSpring26Group_2"
}

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# UI Styling Colors
PRIMARY_GREEN = "#5C8A3C"
SIDEBAR_GREEN = "#4A7A2E"
DARK_TEXT = "#2C3E50"
GRAY_TEXT = "#666666"
SECTION_GREEN = "#3D7A1A"

NAV_ITEMS = [
    ("User & Report Management", "👥"), ("Room & Hall Management", "🛏"),
    ("Booking Calendar", "📅"), ("BI Dashboard", "📊"),("Settings", "⚙")
]

class RoomManagementScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.admin_id = self._get_session_id()
        self.admin_name = self._get_admin_name()
        
        self.title("Admin Center - Room & Hall Management")
        self.after(0, lambda: self.state('zoomed')) 
        self.configure(fg_color="white")
        
        self._build_ui()

    def _get_session_id(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return None

    def _get_admin_name(self):
        if not self.admin_id: return "Admin"
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT first_name FROM User WHERE user_id = %s", (self.admin_id,))
            res = cursor.fetchone()
            conn.close()
            return res['first_name'] if res else "Admin"
        except Error: return "Admin"

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="white")
        outer.pack(fill="both", expand=True)
        
        # Sidebar
        sidebar = ctk.CTkFrame(outer, fg_color=SIDEBAR_GREEN, width=215, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        ctk.CTkLabel(sidebar, text="⚙ Admin Center", font=ctk.CTkFont(size=15, weight="bold"), text_color="white").pack(pady=20, padx=15, anchor="w")
        
        for label, icon in NAV_ITEMS:
            is_active = (label == "Room & Hall Management")
            btn = ctk.CTkButton(sidebar, text=f"  {icon}  {label}", 
                                fg_color="#3D6A22" if is_active else "transparent", 
                                hover_color="#3D6A22", text_color="white", anchor="w", height=40,
                                command=lambda l=label: self._navigate(l))
            btn.pack(fill="x", padx=10, pady=2)
            
        ctk.CTkButton(sidebar, text="Sign Out", fg_color="transparent", border_width=1, border_color="#AAAAAA", command=self._sign_out).pack(side="bottom", padx=15, pady=20)

        # Main Area
        main_area = ctk.CTkFrame(outer, fg_color="white")
        main_area.pack(side="left", fill="both", expand=True)
        
        header = ctk.CTkFrame(main_area, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))
        ctk.CTkLabel(header, text="Room & Hall Management", font=ctk.CTkFont(family="Georgia", size=26, weight="bold"), text_color=SIDEBAR_GREEN).pack(anchor="w")
        ctk.CTkLabel(header, text=f"Welcome, {self.admin_name}!", font=ctk.CTkFont(size=14), text_color=GRAY_TEXT).pack(anchor="w")
        
        btn_frame = ctk.CTkFrame(main_area, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkButton(btn_frame, text="➕ Add New Room/Hall", fg_color=PRIMARY_GREEN, font=ctk.CTkFont(weight="bold"), command=self._open_add_room_window).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="🔄 Refresh List", fg_color="gray", width=120, command=self._refresh_data).pack(side="left")

        table_container = ctk.CTkFrame(main_area, fg_color="#F5F5F5", corner_radius=12)
        table_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        h = ctk.CTkFrame(table_container, fg_color="#E8E8E8", height=40, corner_radius=0)
        h.pack(fill="x", padx=10, pady=(10, 0))
        # Change this line in _build_ui:
        cols = [("Number/ID", 0.02), ("Type", 0.12), ("Category", 0.25), ("Capacity", 0.38), ("Price", 0.50), ("Floor/Loc", 0.63), ("Status", 0.75), ("Actions", 0.88)]
        for text, pos in cols:
            ctk.CTkLabel(h, text=text, font=ctk.CTkFont(size=12, weight="bold"), text_color=DARK_TEXT).place(relx=pos, rely=0.5, anchor="w")

        self.scroll_frame = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._refresh_data()

    def _refresh_data(self):
        """Calculates occupancy and provides maintenance controls."""
        for w in self.scroll_frame.winfo_children(): w.destroy()
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            # The SQL remains the same as your current dynamic status logic
            sql = """
            SELECT 
                r.*, 
                CASE 
                    WHEN r.status = 'Maintenance' THEN 'Maintenance'
                    WHEN EXISTS (
                        SELECT 1 FROM Reservation res 
                        WHERE res.room_id = r.room_id 
                        AND CURDATE() >= DATE(res.check_in_date)
                        AND CURDATE() < DATE(res.check_out_date)
                        AND TRIM(res.status) NOT IN ('Cancelled')
                    ) THEN 'Occupied'
                    WHEN EXISTS (
                        SELECT 1 FROM Booking b 
                        WHERE b.room_id = r.room_id 
                        AND b.event_date = CURDATE()
                        AND TRIM(b.status) NOT IN ('Cancelled')
                    ) THEN 'Occupied'
                    ELSE 'Available'
                END AS dynamic_status
            FROM Room r
            ORDER BY r.is_banquet_hall, r.room_number
            """
            
            cursor.execute(sql)
            rooms = cursor.fetchall()
            
            for i, r in enumerate(rooms):
                row = ctk.CTkFrame(self.scroll_frame, fg_color="white" if i%2==0 else "#FDFDFD", height=45, corner_radius=0)
                row.pack(fill="x")
                row.pack_propagate(False)
                
                category = "Banquet Hall" if r['is_banquet_hall'] else "Hotel Room"
                price = f"${r['price_per_hour']}/hr" if r['is_banquet_hall'] else f"${r['price_per_night']}/night"
                loc = r['location'] if r['is_banquet_hall'] else f"Floor {r['floor']}"
                
                status_text = r['dynamic_status']
                
                # Logic for status color and Action Button appearance
                if status_text == "Occupied":
                    status_color = "#E67E22"
                    btn_txt = "In Use"
                    btn_color = "#A6A6A6"
                    btn_state = "disabled"
                elif status_text == "Maintenance":
                    status_color = "#C0392B"
                    btn_txt = "Set Available"
                    btn_color = "#27AE60"
                    btn_state = "normal"
                else:
                    status_color = "#27AE60"
                    btn_txt = "Set Maintenance"
                    btn_color = "#C0392B"
                    btn_state = "normal"
                
                # Columns with updated relx spacing to accommodate the button
                ctk.CTkLabel(row, text=r['room_number']).place(relx=0.02, rely=0.5, anchor="w")
                ctk.CTkLabel(row, text=r['room_type'], font=ctk.CTkFont(weight="bold")).place(relx=0.12, rely=0.5, anchor="w")
                ctk.CTkLabel(row, text=category).place(relx=0.25, rely=0.5, anchor="w")
                ctk.CTkLabel(row, text=r['capacity']).place(relx=0.38, rely=0.5, anchor="w")
                ctk.CTkLabel(row, text=price).place(relx=0.50, rely=0.5, anchor="w")
                ctk.CTkLabel(row, text=loc).place(relx=0.63, rely=0.5, anchor="w")
                ctk.CTkLabel(row, text=status_text, text_color=status_color, font=ctk.CTkFont(weight="bold")).place(relx=0.75, rely=0.5, anchor="w")

                # Action Button
                ctk.CTkButton(row, text=btn_txt, fg_color=btn_color, height=28, width=110,
                              state=btn_state, font=ctk.CTkFont(size=11, weight="bold"),
                              command=lambda rid=r['room_id'], st=status_text: self._toggle_maintenance(rid, st)).place(relx=0.87, rely=0.5, anchor="w")
            
            conn.close()
        except Error as e: 
            messagebox.showerror("Error", f"Precision fetch failed: {e}")

    def _toggle_maintenance(self, room_id, current_status):
        """Database function to switch status."""
        new_status = "Available" if current_status == "Maintenance" else "Maintenance"
        
        if messagebox.askyesno("Confirm Status Change", f"Are you sure you want to set this room to {new_status}?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("UPDATE Room SET status = %s WHERE room_id = %s", (new_status, room_id))
                conn.commit()
                conn.close()
                self._refresh_data() # Refresh UI to reflect change
            except Error as e:
                messagebox.showerror("Database Error", str(e))

    def _open_add_room_window(self):
        self.add_win = ctk.CTkToplevel(self)
        self.add_win.title("Add New Asset")
        self.add_win.geometry("500x700")
        self.add_win.grab_set()
        main_f = ctk.CTkScrollableFrame(self.add_win, fg_color="white")
        main_f.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(main_f, text="Register New Room/Hall", font=ctk.CTkFont(size=20, weight="bold"), text_color=SECTION_GREEN).pack(pady=10)
        self.type_var = ctk.BooleanVar(value=False)
        toggle_frame = ctk.CTkFrame(main_f, fg_color="transparent")
        toggle_frame.pack(fill="x", pady=10)
        ctk.CTkRadioButton(toggle_frame, text="Hotel Room", variable=self.type_var, value=False, command=self._toggle_fields).pack(side="left", padx=10)
        ctk.CTkRadioButton(toggle_frame, text="Banquet Hall", variable=self.type_var, value=True, command=self._toggle_fields).pack(side="left", padx=10)
        self.inputs = {}
        self.field_container = ctk.CTkFrame(main_f, fg_color="transparent")
        self.field_container.pack(fill="both", expand=True)
        self._toggle_fields()

    def _toggle_fields(self):
        for w in self.field_container.winfo_children(): w.destroy()
        self.inputs = {} 
        is_hall = self.type_var.get()
        self._create_input("Room Number/ID", "room_number")
        types = ['Single', 'Double', 'Suite', 'Deluxe', 'Executive', 'Family', 'Presidential'] if not is_hall else ['Hall-50', 'Hall-150', 'Hall-300']
        self._create_dropdown("Type", "room_type", types)
        self._create_input("Capacity", "capacity")
        if is_hall:
            self._create_input("Hall Name", "hall_name")
            self._create_input("Price Per Hour ($)", "price_per_hour")
            self._create_input("Location", "location")
        else:
            self._create_input("Price Per Night ($)", "price_per_night")
            self._create_input("Floor Number", "floor")
        self._create_input("Amenities (Comma separated)", "amenities")
        ctk.CTkButton(self.field_container, text="Save to Database", fg_color=PRIMARY_GREEN, height=40, command=self._save_room).pack(pady=30, fill="x")

    def _create_input(self, label, key):
        ctk.CTkLabel(self.field_container, text=label, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
        ent = ctk.CTkEntry(self.field_container, width=400)
        ent.pack(pady=(0, 5))
        self.inputs[key] = ent

    def _create_dropdown(self, label, key, options):
        ctk.CTkLabel(self.field_container, text=label, font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 2))
        var = ctk.StringVar(value=options[0])
        ctk.CTkOptionMenu(self.field_container, values=options, variable=var, fg_color=PRIMARY_GREEN, width=400).pack(pady=(0, 5))
        self.inputs[key] = var

    def _save_room(self):
        is_hall = self.type_var.get()
        data = {k: (v.get().strip() if hasattr(v, 'get') else v.get()) for k, v in self.inputs.items()}
        try:
            if not data['room_number'] or not data['capacity']:
                messagebox.showerror("Error", "Required fields missing.")
                return
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            if is_hall:
                sql = """INSERT INTO Room (room_number, room_type, capacity, hall_name, is_banquet_hall, price_per_hour, location, amenities, status) 
                         VALUES (%s, %s, %s, %s, TRUE, %s, %s, %s, 'Available')"""
                val = (data['room_number'], data['room_type'], int(data['capacity']), data['hall_name'], float(data['price_per_hour']), data['location'], data['amenities'])
            else:
                sql = """INSERT INTO Room (room_number, room_type, capacity, price_per_night, floor, is_banquet_hall, amenities, status) 
                         VALUES (%s, %s, %s, %s, %s, FALSE, %s, 'Available')"""
                val = (data['room_number'], data['room_type'], int(data['capacity']), float(data['price_per_night']), int(data['floor']), data['amenities'])
            cursor.execute(sql, val)
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Asset added!")
            self.add_win.destroy()
            self._refresh_data()
        except Exception as e: messagebox.showerror("Error", f"Save failed: {e}")

    def _navigate(self, label):
        file_map = {
            "User & Report Management": "user_management_screen.py",
            "Booking Calendar": "booking_calender.py",
            "BI Dashboard": "bi_dashboard.py",
            "Settings": "settings_admin.py"
        }
        if label == "Room & Hall Management": return
        if label in file_map:
            target = os.path.join(os.path.dirname(__file__), file_map[label])
            if os.path.exists(target):
                self.destroy()
                subprocess.Popen([sys.executable, target])
            else:
                messagebox.showerror("Error", f"File {file_map[label]} not found.")
        else:
            messagebox.showinfo("Module", f"{label} coming soon.")

    def _sign_out(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(path): os.remove(path)
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "login_screen.py")])

if __name__ == "__main__":
    app = RoomManagementScreen()
    app.mainloop()