import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
import calendar
import subprocess
import sys
import os
from datetime import datetime, timedelta

# DATABASE CONFIGURATION
DB_CONFIG = {
    "host": "141.209.241.57",
    "port": 3306,
    "user": "putch1v",
    "password": "mypass",
    "database": "BIS698MSpring26Group_2"
}

# THEME COLORS
PRIMARY_GREEN = "#5C8A3C"
SIDEBAR_GREEN = "#4A7A2E"
CAL_BG = "#F8F9FA"
ROOM_COLOR = "#3498DB" 
HALL_COLOR = "#9B59B6"
TODAY_HIGHLIGHT = "#E8F5E9"

NAV_ITEMS = [
    ("User & Report Management", "👥"), ("Room & Hall Management", "🛏"),
    ("Booking Calendar", "📅"), ("BI Dashboard", "📊"), ("Settings", "⚙")
]

class BookingCalendar(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.admin_id = self._get_session_id()
        self.admin_name = self._get_admin_name()
        
        self.title("Admin Center - Booking Calendar")
        self.after(0, lambda: self.state('zoomed'))
        self.configure(fg_color="white")
        
        # Date State
        self.now = datetime.now()
        self.curr_month = self.now.month
        self.curr_year = self.now.year

        self._build_ui()
        self._load_month()

    def _get_session_id(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        return open(path, "r").read().strip() if os.path.exists(path) else None

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

    def _get_bookings(self):
        """Fetches both Room and Hall bookings, handling multi-day stays for rooms."""
        bookings_by_day = {}
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            # 1. ROOM RESERVATIONS (Logic: Show until check-out date)
            cursor.execute("""
                SELECT R.*, Rm.room_number, Rm.room_type, U.first_name, U.last_name, U.email, U.phone 
                FROM Reservation R 
                JOIN Room Rm ON R.room_id = Rm.room_id 
                JOIN User U ON R.user_id = U.user_id
                WHERE (MONTH(check_in_date) = %s OR MONTH(check_out_date) = %s)
                AND R.status NOT IN ('Cancelled')
            """, (self.curr_month, self.curr_month))
            
            for row in cursor.fetchall():
                curr_date = row['check_in_date']
                end_date = row['check_out_date']
                # Room stays visible every day between in and out
                while curr_date < end_date:
                    if curr_date.month == self.curr_month and curr_date.year == self.curr_year:
                        d = curr_date.day
                        if d not in bookings_by_day: bookings_by_day[d] = []
                        bookings_by_day[d].append({
                            "text": f"Rm {row['room_number']}: {row['last_name']}",
                            "color": ROOM_COLOR,
                            "type": "Room",
                            "details": row
                        })
                    curr_date += timedelta(days=1)

            # 2. BANQUET HALL BOOKINGS
            cursor.execute("""
                SELECT B.*, Rm.room_number, Rm.hall_name, U.first_name, U.last_name, U.email, U.phone 
                FROM Booking B 
                JOIN Room Rm ON B.room_id = Rm.room_id
                JOIN User U ON B.user_id = U.user_id
                WHERE MONTH(event_date) = %s AND YEAR(event_date) = %s 
                AND B.status NOT IN ('Cancelled')
            """, (self.curr_month, self.curr_year))
            
            for row in cursor.fetchall():
                d = row['event_date'].day
                if d not in bookings_by_day: bookings_by_day[d] = []
                bookings_by_day[d].append({
                    "text": f"Hall {row['room_number']}: {row['event_type']}",
                    "color": HALL_COLOR,
                    "type": "Hall",
                    "details": row
                })
            conn.close()
        except Error as e:
            print(f"Calendar DB Error: {e}")
        return bookings_by_day

    def _show_details(self, data):
        """Displays a robust popup with info based on booking type."""
        pop = ctk.CTkToplevel(self)
        pop.title("Reservation Details")
        pop.geometry("500x620")
        pop.attributes("-topmost", True)
        
        d = data['details']
        color = data['color']
        
        ctk.CTkLabel(pop, text=f"{data['type']} Details", font=ctk.CTkFont(size=22, weight="bold"), text_color=color).pack(pady=20)
        
        container = ctk.CTkFrame(pop, fg_color="#F9F9F9", corner_radius=15)
        container.pack(fill="both", expand=True, padx=30, pady=10)

        # Base info common to both
        info = [
            ("Customer Name", f"{d['first_name']} {d['last_name']}"),
            ("Email Address", d['email']),
            ("Phone Number", d['phone']),
            ("Unit Number", d['room_number']),
            ("Total Amount", f"${d['total_amount']}"),
            ("Booking Status", d['status']),
            ("Payment Status", d['payment_status'])
        ]
        
        if data['type'] == "Room":
            info.insert(4, ("Room Type", d['room_type']))
            info.append(("Check-In", d['check_in_date']))
            info.append(("Check-Out", d['check_out_date']))
            info.append(("Num Guests", d['num_guests']))
            if d.get('special_requests'):
                info.append(("Requests", d['special_requests']))
        else:
            info.insert(4, ("Hall Name", d['hall_name']))
            info.append(("Event Date", d['event_date']))
            info.append(("Event Type", d['event_type']))
            info.append(("Timing", f"{d['start_time']} - {d['end_time']}"))
            info.append(("Guest Count", d['guest_count']))

        for key, val in info:
            row = ctk.CTkFrame(container, fg_color="transparent")
            row.pack(fill="x", pady=6, padx=20)
            ctk.CTkLabel(row, text=f"{key}:", font=ctk.CTkFont(size=13, weight="bold"), width=140, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(val), font=ctk.CTkFont(size=13), anchor="w", wraplength=250).pack(side="left")

        ctk.CTkButton(pop, text="Close Details", fg_color=SIDEBAR_GREEN, command=pop.destroy).pack(pady=25)

    def _load_month(self):
        """Renders the calendar grid for the current month."""
        for widget in self.calendar_frame.winfo_children(): widget.destroy()
        self.month_label.configure(text=f"{calendar.month_name[self.curr_month]} {self.curr_year}")
        
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            self.calendar_frame.columnconfigure(i, weight=1, uniform="cal")
            ctk.CTkLabel(self.calendar_frame, text=day, font=ctk.CTkFont(weight="bold"), text_color="#777777").grid(row=0, column=i, pady=5)

        cal_matrix = calendar.monthcalendar(self.curr_year, self.curr_month)
        db_data = self._get_bookings()
        today = datetime.now().date()

        for r, week in enumerate(cal_matrix):
            self.calendar_frame.rowconfigure(r+1, weight=1)
            for c, day in enumerate(week):
                if day == 0: continue
                
                is_today = (day == today.day and self.curr_month == today.month and self.curr_year == today.year)
                
                day_box = ctk.CTkFrame(self.calendar_frame, fg_color=TODAY_HIGHLIGHT if is_today else "white", 
                                       border_width=1, border_color="#E0E0E0", corner_radius=8)
                day_box.grid(row=r+1, column=c, sticky="nsew", padx=2, pady=2)
                
                ctk.CTkLabel(day_box, text=str(day), font=ctk.CTkFont(size=11, weight="bold"), 
                             text_color=SIDEBAR_GREEN if is_today else "#333333").pack(anchor="nw", padx=5, pady=2)
                
                if day in db_data:
                    for b in db_data[day]:
                        lbl = ctk.CTkLabel(day_box, text=b['text'], fg_color=b['color'], text_color="white", 
                                           font=ctk.CTkFont(size=9, weight="bold"), corner_radius=4, height=18, cursor="hand2")
                        lbl.pack(fill="x", padx=3, pady=1)
                        lbl.bind("<Button-1>", lambda e, data=b: self._show_details(data))

    def _build_ui(self):
        self.outer = ctk.CTkFrame(self, fg_color="white")
        self.outer.pack(fill="both", expand=True)

        # SIDEBAR
        sidebar = ctk.CTkFrame(self.outer, fg_color=SIDEBAR_GREEN, width=215, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar, text="⚙ Admin Center", font=ctk.CTkFont(size=15, weight="bold"), text_color="white").pack(pady=20, padx=15, anchor="w")

        for label, icon in NAV_ITEMS:
            is_active = (label == "Booking Calendar")
            btn = ctk.CTkButton(sidebar, text=f"  {icon}  {label}", 
                                fg_color="#3D6A22" if is_active else "transparent", 
                                hover_color="#3D6A22", text_color="white", anchor="w", height=40,
                                command=lambda l=label: self._navigate(l))
            btn.pack(fill="x", padx=10, pady=2)

        ctk.CTkButton(sidebar, text="Sign Out", fg_color="transparent", border_width=1, border_color="#AAAAAA", command=self._sign_out).pack(side="bottom", padx=15, pady=20)

        # MAIN CONTENT
        main_content = ctk.CTkFrame(self.outer, fg_color="white")
        main_content.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main_content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))
        ctk.CTkLabel(header, text="Booking Calendar Dashboard", font=ctk.CTkFont(family="Georgia", size=26, weight="bold"), text_color=SIDEBAR_GREEN).pack(anchor="w")
        
        control_bar = ctk.CTkFrame(main_content, fg_color="#F1F1F1", height=60, corner_radius=10)
        control_bar.pack(fill="x", padx=30, pady=10)
        ctk.CTkButton(control_bar, text="<", width=40, fg_color=PRIMARY_GREEN, command=self._prev_month).pack(side="left", padx=20, pady=10)
        self.month_label = ctk.CTkLabel(control_bar, text="", font=ctk.CTkFont(size=20, weight="bold"), text_color=SIDEBAR_GREEN)
        self.month_label.pack(side="left", expand=True)
        ctk.CTkButton(control_bar, text=">", width=40, fg_color=PRIMARY_GREEN, command=self._next_month).pack(side="right", padx=20, pady=10)

        legend = ctk.CTkFrame(main_content, fg_color="transparent")
        legend.pack(fill="x", padx=30)
        self._create_legend_item(legend, "Hotel Room", ROOM_COLOR)
        self._create_legend_item(legend, "Banquet Hall", HALL_COLOR)

        self.calendar_frame = ctk.CTkFrame(main_content, fg_color=CAL_BG, corner_radius=12)
        self.calendar_frame.pack(fill="both", expand=True, padx=30, pady=20)

    def _create_legend_item(self, parent, text, color):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", padx=10)
        ctk.CTkLabel(f, text="■", text_color=color, font=("Arial", 16)).pack(side="left")
        ctk.CTkLabel(f, text=text, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)

    def _prev_month(self):
        if self.curr_month == 1: self.curr_month = 12; self.curr_year -= 1
        else: self.curr_month -= 1
        self._load_month()

    def _next_month(self):
        if self.curr_month == 12: self.curr_month = 1; self.curr_year += 1
        else: self.curr_month += 1
        self._load_month()

    def _navigate(self, label):
        if label == "Booking Calendar": return
        self.destroy()
        file_map = {"User & Report Management": "user_management_screen.py", "Room & Hall Management": "room_management_admin.py", "BI Dashboard": "bi_dashboard.py", "Settings": "settings_admin.py"}
        if label in file_map: subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), file_map[label])])

    def _sign_out(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(path): os.remove(path)
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "login_screen.py")])

if __name__ == "__main__":
    app = BookingCalendar()
    app.mainloop()