import customtkinter as ctk
import subprocess
import sys
import os
import mysql.connector
from datetime import datetime
from tkinter import messagebox
from tkcalendar import Calendar
from PIL import Image
import tkinter as tk

# CONFIGURATION 
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Database Configuration
DB_CONFIG = {
    "host": "141.209.241.57",
    "port": 3306,
    "user": "putch1v",
    "password": "mypass",
    "database": "BIS698MSpring26Group_2"
}

PRIMARY_GREEN = "#5C8A3C"
SIDEBAR_GREEN = "#4A7A2E"
LIGHT_GREEN_HEADER = "#A8C68F"

# IMAGE CONFIGURATION 
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")

ROOM_IMAGE_MAPPING = {
    "Single": "single_room.jpg",
    "Double": "double_room.jpg",
    "Suite": "suite.jpg",
    "Deluxe": "deluxe_room.jpg",
    "Executive": "executive_room.jpg",
    "Family": "family_room.jpg",
    "Presidential": "presidential_room.jpg"
}

NAV_ITEMS = ["Rooms", "Banquet Halls", "My Bookings", "Settings"]
NAV_SCREENS = {
    
    "Rooms": "search_room_screen.py",
    "Banquet Halls": "banquet_hall_screen.py",
    "My Bookings": "mybookings.py",
    "Settings": "settings.py"
}

class SearchRoomScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.user_id = self._get_session_id()
        self.user_name = self._get_logged_in_user_name()
        
        self.title("Hotel Reservation - Availability Search")
        self.geometry("1200x950") 
        self.configure(fg_color="white")
        
        self.raw_rooms = [] 
        self.room_images = {} 
        self.active_calendar_frame = None 
        
        self._load_images()
        self._build_ui()
        self._apply_filters()
        self.after(0, lambda: self.state('zoomed'))

    def _get_session_id(self):
        session_path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(session_path):
            with open(session_path, "r") as f:
                return f.read().strip()
        return None

    def _get_logged_in_user_name(self):
        try:
            if not self.user_id: return "Guest"
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT first_name FROM User WHERE user_id = %s", (self.user_id,)) 
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "Guest"
        except: return "User"

    def _load_images(self):
        target_width = 480 
        for room_type, filename in ROOM_IMAGE_MAPPING.items():
            full_path = os.path.join(STATIC_PATH, filename)
            try:
                pil_image = Image.open(full_path).convert('RGB')
                orig_w, orig_h = pil_image.size
                aspect_ratio = orig_h / orig_w
                target_height = int(target_width * aspect_ratio)
                
                if target_height > 260:
                    target_height = 260
                    current_width = int(target_height / aspect_ratio)
                else:
                    current_width = target_width

                self.room_images[room_type] = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(current_width, target_height)
                )
            except Exception:
                self.room_images[room_type] = None

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="white")
        outer.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(outer, fg_color=SIDEBAR_GREEN, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar, text="🏨 Hotel Reservation", font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(pady=30, padx=15, anchor="w")

        for item in NAV_ITEMS:
            is_active = item == "Rooms"
            btn = ctk.CTkButton(sidebar, text=f"  {item}", fg_color="#3D6A22" if is_active else "transparent",
                                hover_color="#3D6A22", text_color="white", anchor="w", height=45, corner_radius=6,
                                command=lambda s=item: self._nav(s))
            btn.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(sidebar, text="🚪 Sign Out", fg_color="transparent", hover_color="#A33333", 
                      text_color="white", anchor="w", height=45, command=self._logout).pack(side="bottom", fill="x", padx=10, pady=20)

        main = ctk.CTkFrame(outer, fg_color="white")
        main.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color=LIGHT_GREEN_HEADER, corner_radius=0, height=160)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text=f"Welcome back, {self.user_name}! 👋", 
                      font=ctk.CTkFont(size=14, weight="bold"), text_color=SIDEBAR_GREEN).pack(side="top", anchor="ne", padx=30, pady=(15, 0))

        ctk.CTkLabel(header, text="Find Your Perfect Room", font=ctk.CTkFont(family="Georgia", size=28, weight="bold"), text_color=SIDEBAR_GREEN).pack(pady=(10, 5))

        # Filter Bar
        filter_frame = ctk.CTkFrame(main, fg_color="white")
        filter_frame.pack(fill="x", padx=20, pady=15)

        self.type_var = ctk.StringVar(value="All Types")
        ctk.CTkOptionMenu(filter_frame, values=["All Types", "Single", "Double", "Suite", "Deluxe", "Executive", "Family", "Presidential"],
                          variable=self.type_var, width=180, height=35, command=self._apply_filters).grid(row=0, column=0, padx=8)

        self.price_var = ctk.StringVar(value="All Prices")
        ctk.CTkOptionMenu(filter_frame, values=["All Prices", "Under $150", "$150-$300", "$300+"],
                          variable=self.price_var, width=180, height=35, command=self._apply_filters).grid(row=0, column=1, padx=8)

        self.avail_status_var = ctk.StringVar(value="Available")
        ctk.CTkOptionMenu(filter_frame, values=["Available", "Booked"],
                          variable=self.avail_status_var, width=180, height=35, command=self._apply_filters).grid(row=0, column=2, padx=8)

        date_pick_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_pick_frame.grid(row=0, column=3, padx=8)
        self.search_date_entry = ctk.CTkEntry(date_pick_frame, width=130, height=35)
        self.search_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.search_date_entry.pack(side="left", padx=2)
        
        cal_btn = ctk.CTkButton(date_pick_frame, text="📅", width=40, height=35)
        cal_btn.configure(command=lambda: self._toggle_dropdown_calendar(self.search_date_entry, cal_btn, refresh=True))
        cal_btn.pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(main, fg_color="white")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def _toggle_dropdown_calendar(self, entry_widget, btn_widget, refresh=False, refresh_callback=None):
        """Floating calendar with logic to refresh UI components after date selection."""
        if self.active_calendar_frame and self.active_calendar_frame.winfo_exists():
            self.active_calendar_frame.destroy()
            self.active_calendar_frame = None
            return

        top_window = btn_widget.winfo_toplevel()
        self.active_calendar_frame = ctk.CTkFrame(top_window, border_width=2, border_color=PRIMARY_GREEN, fg_color="white", corner_radius=10)
        
        x = btn_widget.winfo_rootx() - top_window.winfo_rootx()
        y = btn_widget.winfo_rooty() - top_window.winfo_rooty() + btn_widget.winfo_height()
        x -= 300 
        if x < 10: x = 10

        self.active_calendar_frame.place(x=x, y=y)

        cal = Calendar(self.active_calendar_frame, selectmode='day', date_pattern='y-mm-dd', mindate=datetime.now())
        cal.pack(padx=10, pady=10)

        def select_date():
            entry_widget.delete(0, "end")
            entry_widget.insert(0, cal.get_date())
            self.active_calendar_frame.destroy()
            self.active_calendar_frame = None
            if refresh: self._apply_filters()
            if refresh_callback: refresh_callback()

        ctk.CTkButton(self.active_calendar_frame, text="Confirm Date", fg_color=PRIMARY_GREEN, command=select_date).pack(pady=5)

    def _apply_filters(self, _=None):
        selected_date = self.search_date_entry.get()
        selected_status = self.avail_status_var.get()
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            overlap_query = """SELECT DISTINCT room_id FROM Reservation WHERE %s >= check_in_date AND %s < check_out_date AND status NOT IN ('Cancelled')"""
            cursor.execute(overlap_query, (selected_date, selected_date))
            booked_room_ids = [row['room_id'] for row in cursor.fetchall()]

            if selected_status == "Available":
                if not booked_room_ids:
                    query = "SELECT * FROM Room WHERE is_banquet_hall = 0 AND status != 'Maintenance'"
                else:
                    format_strings = ','.join(['%s'] * len(booked_room_ids))
                    query = f"SELECT * FROM Room WHERE is_banquet_hall = 0 AND status != 'Maintenance' AND room_id NOT IN ({format_strings})"
                cursor.execute(query, tuple(booked_room_ids) if booked_room_ids else ())
            else:
                if not booked_room_ids:
                    self.raw_rooms = []
                    self._render_cards([])
                    conn.close()
                    return
                format_strings = ','.join(['%s'] * len(booked_room_ids))
                query = f"SELECT * FROM Room WHERE is_banquet_hall = 0 AND room_id IN ({format_strings})"
                cursor.execute(query, tuple(booked_room_ids))

            self.raw_rooms = cursor.fetchall()
            conn.close()
            self._filter_and_display()
        except Exception as e: print(f"Filter Error: {e}")

    def _filter_and_display(self):
        t_filter, p_filter = self.type_var.get(), self.price_var.get()
        seen_types = {}
        for r in self.raw_rooms:
            t_match = (t_filter == "All Types" or r['room_type'] == t_filter)
            p_val = float(r['price_per_night'])
            if p_filter == "All Prices": p_match = True
            elif p_filter == "Under $150": p_match = p_val < 150
            elif p_filter == "$150-$300": p_match = 150 <= p_val <= 300
            else: p_match = p_val > 300

            if t_match and p_match:
                t = r['room_type']
                if t not in seen_types:
                    seen_types[t] = {"room_type": t, "price": p_val, "capacity": r['capacity'], "rooms": []}
                seen_types[t]["rooms"].append(r['room_number'])
        self._render_cards(list(seen_types.values()))

    def _render_cards(self, data):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        if not data:
            ctk.CTkLabel(self.scroll_frame, text="No matches found.", font=ctk.CTkFont(size=18)).pack(pady=60)
            return
        cols = 2
        for i, item in enumerate(data):
            card = ctk.CTkFrame(self.scroll_frame, fg_color="white", corner_radius=15, border_width=2, border_color="#D0E8C0")
            card.grid(row=i//cols, column=i%cols, padx=20, pady=20, sticky="nsew")
            
            img_obj = self.room_images.get(item['room_type'])
            if img_obj: ctk.CTkLabel(card, text="", image=img_obj).pack(side="top", pady=(15, 5), padx=15)
            
            ctk.CTkLabel(card, text=f"{item['room_type']}", font=ctk.CTkFont(size=22, weight="bold"), text_color=SIDEBAR_GREEN).pack(pady=5)
            price_badge = ctk.CTkFrame(card, fg_color="#F0F7EB", corner_radius=10)
            price_badge.pack(pady=5)
            ctk.CTkLabel(price_badge, text=f"Starting at ${item['price']}/night", font=ctk.CTkFont(size=16, weight="bold"), text_color=SIDEBAR_GREEN).pack(padx=15, pady=5)
            ctk.CTkLabel(card, text=f"Up to {item['capacity']} Guests • Premium Amenities", font=ctk.CTkFont(size=13), text_color="gray").pack(pady=5)
            
            btn = ctk.CTkButton(card, text="Book Now", fg_color=SIDEBAR_GREEN, height=40, corner_radius=10, 
                                command=lambda cat=item: self._open_booking_popup(cat))
            btn.pack(side="top", fill="x", padx=35, pady=(15, 25))
        for c in range(cols): self.scroll_frame.grid_columnconfigure(c, weight=1)

    def _open_booking_popup(self, category):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Book {category['room_type']}")
        popup.geometry("600x850") 
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text=f"Reserve {category['room_type']}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # 1. Date Inputs
        def date_row(lbl, initial_val=""):
            ctk.CTkLabel(popup, text=lbl, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=60)
            f = ctk.CTkFrame(popup, fg_color="transparent")
            f.pack(pady=(5, 15))
            e = ctk.CTkEntry(f, width=420, height=40)
            e.insert(0, initial_val)
            e.pack(side="left", padx=5)
            b = ctk.CTkButton(f, text="📅", width=50, height=40, fg_color=SIDEBAR_GREEN)
            b.pack(side="left")
            return e, b

        e_in, b_in = date_row("Check-in Date", self.search_date_entry.get())
        e_out, b_out = date_row("Check-out Date")

        # 2. Dynamic Room Dropdown
        ctk.CTkLabel(popup, text="Select Available Room Number", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=60)
        r_var = ctk.StringVar(value="Select Dates First")
        room_dropdown = ctk.CTkOptionMenu(popup, variable=r_var, values=["Select Dates First"], width=480, height=40)
        room_dropdown.pack(pady=(5, 15))

        def update_room_list():
            """Re-calculates availability based on exact dates in the popup."""
            cin, cout = e_in.get(), e_out.get()
            if not cin or not cout: return
            try:
                datetime.strptime(cin, "%Y-%m-%d")
                datetime.strptime(cout, "%Y-%m-%d")
                
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                
                # Check for overlap
                cursor.execute("""
                    SELECT room_id FROM Reservation 
                    WHERE status NOT IN ('Cancelled')
                    AND (%s < check_out_date AND %s > check_in_date)
                """, (cin, cout))
                booked_ids = [row['room_id'] for row in cursor.fetchall()]

                # Filter rooms of this type
                query = f"SELECT room_number FROM Room WHERE room_type = %s AND is_banquet_hall = 0 AND status != 'Maintenance'"
                if booked_ids:
                    query += f" AND room_id NOT IN ({','.join(['%s']*len(booked_ids))})"
                    cursor.execute(query, (category['room_type'], *booked_ids))
                else:
                    cursor.execute(query, (category['room_type'],))

                avail = [r['room_number'] for r in cursor.fetchall()]
                conn.close()

                if avail:
                    room_dropdown.configure(values=avail)
                    r_var.set(avail[0])
                else:
                    room_dropdown.configure(values=["No Rooms Available"])
                    r_var.set("No Rooms Available")
            except Exception: pass

        # Assign callbacks to calendars
        b_in.configure(command=lambda: self._toggle_dropdown_calendar(e_in, b_in, refresh_callback=update_room_list))
        b_out.configure(command=lambda: self._toggle_dropdown_calendar(e_out, b_out, refresh_callback=update_room_list))

        # 3. Rest of Form
        ctk.CTkLabel(popup, text="Number of Guests", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=60)
        g_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(popup, variable=g_var, values=[str(i) for i in range(1, category['capacity'] + 1)], width=480, height=40).pack(pady=(5, 15))
        
        ctk.CTkLabel(popup, text="Special Requests", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=60)
        e_req = ctk.CTkTextbox(popup, width=480, height=100, border_width=1)
        e_req.pack(pady=(5, 20))

        def confirm():
            if r_var.get() in ["Select Dates First", "No Rooms Available"]:
                messagebox.showerror("Error", "Please select valid dates and an available room.")
                return
            try:
                cin_dt, cout_dt = datetime.strptime(e_in.get(), "%Y-%m-%d"), datetime.strptime(e_out.get(), "%Y-%m-%d")
                if cout_dt <= cin_dt:
                    messagebox.showerror("Error", "Check-out must be after check-in.")
                    return

                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT room_id, price_per_night FROM Room WHERE room_number = %s", (r_var.get(),))
                res = cursor.fetchone()
                
                total = (cout_dt - cin_dt).days * float(res['price_per_night'])
                sql = """INSERT INTO Reservation (user_id, room_id, check_in_date, check_out_date, num_guests, 
                         special_requests, total_amount, status, payment_status) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, 'Confirmed', 'Pending')"""
                cursor.execute(sql, (self.user_id, res['room_id'], e_in.get(), e_out.get(), int(g_var.get()), e_req.get("1.0", "end").strip(), total))
                conn.commit()
                conn.close()
                popup.destroy()
                messagebox.showinfo("Success", f"Booking Confirmed!\nTotal: ${total:.2f}")
                self._apply_filters()
            except Exception as e: messagebox.showerror("Error", str(e))

        ctk.CTkButton(popup, text="Request Booking", fg_color=PRIMARY_GREEN, height=50, width=250, command=confirm).pack(pady=20)
        update_room_list() # Initial load

    def _nav(self, item):
        script = NAV_SCREENS.get(item)
        if script:
            self.destroy()
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), script)])

    def _logout(self):
        if os.path.exists("session.txt"): os.remove("session.txt")
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "login_screen.py")])

if __name__ == "__main__":
    app = SearchRoomScreen()
    app.mainloop()