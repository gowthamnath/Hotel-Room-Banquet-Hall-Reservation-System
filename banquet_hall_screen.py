import customtkinter as ctk
import subprocess
import sys
import os
import mysql.connector
from datetime import datetime
from tkinter import messagebox
from tkcalendar import Calendar
from PIL import Image

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

HALL_IMAGE_MAPPING = {
    "Grand Ballroom": "grand_ball_room.jpg",
    "Crystal Hall": "crystall_hall.jpg",
    "Garden Pavilion": "garden_pavilion.jpg",
    "Executive Conference Center": "executive_conference_center.jpg",
    "Royal Banquet Hall": "royal_banquet_hall.jpg",
    "Emerald Room": "emerald_room.jpg",
    "Sapphire Lounge": "sapphire_lounge.jpg",
    "Diamond Ballroom": "diamond_ballroom.jpg",
    "Pearl Hall": "pearl_hall.jpg",
    "Ruby Meeting Room": "ruby_meeting_hall.jpg"
}

NAV_ITEMS = [ "Rooms", "Banquet Halls", "My Bookings", "Settings"]
NAV_SCREENS = { 
    "Rooms": "search_room_screen.py",
    "Banquet Halls": "banquet_hall_screen.py",
    "My Bookings": "mybookings.py",
    "Settings": "settings.py"
}

class BanquetHallScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.user_id = self._get_session_id()
        self.user_name = self._get_logged_in_user_name()
        
        self.title("Hotel Reservation - Banquet Halls")
        self.geometry("1300x950")
        self.configure(fg_color="white")
        
        self.raw_halls = []
        self.hall_images = {}
        self.active_calendar_frame = None 
        
        self._load_hall_images()
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

    def _load_hall_images(self):
        target_width = 320 
        for hall_name, filename in HALL_IMAGE_MAPPING.items():
            full_path = os.path.join(STATIC_PATH, filename)
            try:
                pil_image = Image.open(full_path).convert('RGB')
                orig_w, orig_h = pil_image.size
                aspect_ratio = orig_h / orig_w
                target_height = int(target_width * aspect_ratio)
                if target_height > 180:
                    target_height = 180
                    current_width = int(target_height / aspect_ratio)
                else:
                    current_width = target_width
                self.hall_images[hall_name] = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(current_width, target_height))
            except:
                self.hall_images[hall_name] = None

    def _fetch_all_hall_names(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG); cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT hall_name FROM Room WHERE is_banquet_hall = 1 AND hall_name IS NOT NULL")
            names = [row[0] for row in cursor.fetchall()]
            conn.close()
            return ["All Types"] + sorted(names)
        except: return ["All Types", "Grand Ballroom", "Crystal Hall", "Garden Pavilion"]

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="white")
        outer.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(outer, fg_color=SIDEBAR_GREEN, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar, text="🏨 Hotel Reservation", font=ctk.CTkFont(size=14, weight="bold"), text_color="white").pack(pady=30, padx=15)

        for item in NAV_ITEMS:
            is_active = item == "Banquet Halls"
            btn = ctk.CTkButton(sidebar, text=f"  {item}", fg_color="#3D6A22" if is_active else "transparent",
                                hover_color="#3D6A22", text_color="white", anchor="w", height=40,
                                command=lambda s=item: self._nav(s))
            btn.pack(fill="x", padx=10, pady=3)

        ctk.CTkButton(sidebar, text="🚪 Sign Out", fg_color="transparent", hover_color="#A33333", 
                      text_color="white", anchor="w", height=40, command=self._sign_out).pack(side="bottom", fill="x", padx=10, pady=20)

        main = ctk.CTkFrame(outer, fg_color="white")
        main.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color=LIGHT_GREEN_HEADER, corner_radius=0, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text=f"Welcome, {self.user_name}! 👋", 
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=SIDEBAR_GREEN).pack(side="top", anchor="ne", padx=25, pady=(10, 0))
        ctk.CTkLabel(header, text="Events & Celebrations", font=ctk.CTkFont(family="Georgia", size=24, weight="bold"), text_color=SIDEBAR_GREEN).pack(pady=(10, 5))

        filter_frame = ctk.CTkFrame(main, fg_color="white")
        filter_frame.pack(fill="x", padx=20, pady=10)

        self.type_var = ctk.StringVar(value="All Types")
        ctk.CTkOptionMenu(filter_frame, values=self._fetch_all_hall_names(), variable=self.type_var, width=160, command=self._apply_filters).grid(row=0, column=0, padx=5)

        self.price_var = ctk.StringVar(value="All Prices")
        ctk.CTkOptionMenu(filter_frame, values=["All Prices", "Under $200/hr", "$200-$500/hr", "$500+/hr"], 
                          variable=self.price_var, width=160, command=self._apply_filters).grid(row=0, column=1, padx=5)

        self.avail_status_var = ctk.StringVar(value="Available")
        ctk.CTkOptionMenu(filter_frame, values=["Available", "Booked"], variable=self.avail_status_var, width=140, command=self._apply_filters).grid(row=0, column=2, padx=5)

        date_pick_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_pick_frame.grid(row=0, column=3, padx=5)
        self.search_date_entry = ctk.CTkEntry(date_pick_frame, width=110)
        self.search_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.search_date_entry.pack(side="left", padx=2)
        
        cal_btn = ctk.CTkButton(date_pick_frame, text="📅", width=35)
        cal_btn.configure(command=lambda: self._toggle_dropdown_calendar(self.search_date_entry, cal_btn, refresh=True))
        cal_btn.pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(main, fg_color="white")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _toggle_dropdown_calendar(self, entry_widget, btn_widget, refresh=False):
        if self.active_calendar_frame and self.active_calendar_frame.winfo_exists():
            self.active_calendar_frame.destroy()
            self.active_calendar_frame = None
            return

        top_window = btn_widget.winfo_toplevel()
        self.active_calendar_frame = ctk.CTkFrame(top_window, border_width=2, border_color=PRIMARY_GREEN, fg_color="white", corner_radius=10)
        
        x = btn_widget.winfo_rootx() - top_window.winfo_rootx()
        y = btn_widget.winfo_rooty() - top_window.winfo_rooty() + btn_widget.winfo_height()

        # Shift left for filter bar or center for popup
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

        ctk.CTkButton(self.active_calendar_frame, text="Confirm Date", fg_color=PRIMARY_GREEN, command=select_date).pack(pady=5)

    def _apply_filters(self, _=None):
        s_date = self.search_date_entry.get()
        s_status = self.avail_status_var.get()
        try:
            conn = mysql.connector.connect(**DB_CONFIG); cursor = conn.cursor(dictionary=True)
            overlap_sql = "SELECT DISTINCT room_id FROM Booking WHERE event_date = %s AND status != 'Cancelled'"
            cursor.execute(overlap_sql, (s_date,))
            booked_ids = [r['room_id'] for r in cursor.fetchall()]

            if s_status == "Available":
                if not booked_ids: sql = "SELECT * FROM Room WHERE is_banquet_hall = 1"
                else: sql = f"SELECT * FROM Room WHERE is_banquet_hall = 1 AND room_id NOT IN ({','.join(['%s']*len(booked_ids))})"
                cursor.execute(sql, tuple(booked_ids) if booked_ids else ())
            else:
                if not booked_ids: self.raw_halls = []; self._render_cards([]); return
                sql = f"SELECT * FROM Room WHERE is_banquet_hall = 1 AND room_id IN ({','.join(['%s']*len(booked_ids))})"
                cursor.execute(sql, tuple(booked_ids))

            self.raw_halls = cursor.fetchall()
            conn.close(); self._process_display_logic()
        except Exception as e: print(f"DB Error: {e}")

    def _process_display_logic(self):
        t_filter = self.type_var.get()
        p_filter = self.price_var.get()
        seen = {}
        for r in self.raw_halls:
            if t_filter != "All Types" and r['hall_name'] != t_filter: continue
            p_val = float(r['price_per_hour'])
            if p_filter == "All Prices": p_match = True
            elif p_filter == "Under $200/hr": p_match = p_val < 200
            elif p_filter == "$200-$500/hr": p_match = 200 <= p_val <= 500
            else: p_match = p_val > 500
            
            if not p_match: continue
            name = r['hall_name']
            if name not in seen:
                seen[name] = {"name": name, "price": p_val, "cap": r['capacity'], "nums": []}
            seen[name]["nums"].append(r['room_number'])
        self._render_cards(list(seen.values()))

    def _render_cards(self, data):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        if not data:
            ctk.CTkLabel(self.scroll_frame, text="No matches found.").pack(pady=40); return

        is_avail = self.avail_status_var.get() == "Available"
        cols = 3 
        for i, item in enumerate(data):
            hall_name = item['name']
            card = ctk.CTkFrame(self.scroll_frame, fg_color="white", corner_radius=12, border_width=1, border_color="#E0E0E0")
            card.grid(row=i//cols, column=i%cols, padx=10, pady=10, sticky="nsew")
            
            img_obj = self.hall_images.get(hall_name)
            if img_obj: ctk.CTkLabel(card, text="", image=img_obj).pack(side="top", pady=(10, 5))
            
            ctk.CTkLabel(card, text=hall_name, font=ctk.CTkFont(size=18, weight="bold"), text_color=SIDEBAR_GREEN).pack()
            price_box = ctk.CTkFrame(card, fg_color="#F0F7EB", corner_radius=8); price_box.pack(pady=5)
            ctk.CTkLabel(price_box, text=f"${item['price']}/hour", font=ctk.CTkFont(size=14, weight="bold"), text_color=SIDEBAR_GREEN).pack(padx=10, pady=2)
            ctk.CTkLabel(card, text=f"Max Guests: {item['cap']}", font=ctk.CTkFont(size=12), text_color="gray").pack()
            
            btn_text, btn_state, btn_color = ("Book Now", "normal", SIDEBAR_GREEN) if is_avail else ("Full", "disabled", "#A6A6A6")
            cmd = (lambda h=item: self._open_booking_popup(h)) if is_avail else None
            ctk.CTkButton(card, text=btn_text, fg_color=btn_color, state=btn_state, font=ctk.CTkFont(size=13, weight="bold"), height=32, corner_radius=8, command=cmd).pack(fill="x", padx=20, pady=(10, 15))

        for c in range(cols): self.scroll_frame.grid_columnconfigure(c, weight=1)

    def _open_booking_popup(self, hall):
        pop = ctk.CTkToplevel(self); pop.title(f"Book {hall['name']}"); pop.geometry("600x850"); pop.attributes("-topmost", True)
        ctk.CTkLabel(pop, text=f"Reserve {hall['name']}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        ctk.CTkLabel(pop, text="Select Hall Unit", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=60)
        r_var = ctk.StringVar(value=hall['nums'][0]); ctk.CTkOptionMenu(pop, variable=r_var, values=hall['nums'], width=480, height=40).pack(pady=(5, 15))

        def dr(lbl):
            ctk.CTkLabel(pop, text=lbl, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=60)
            f = ctk.CTkFrame(pop, fg_color="transparent"); f.pack(pady=(5, 15))
            e = ctk.CTkEntry(f, width=420, height=40); e.pack(side="left", padx=5)
            btn = ctk.CTkButton(f, text="📅", width=50, height=40, fg_color=SIDEBAR_GREEN)
            btn.configure(command=lambda: self._toggle_dropdown_calendar(e, btn))
            btn.pack(side="left"); return e

        e_date = dr("Event Date"); e_date.insert(0, self.search_date_entry.get())
        
        time_options = [f"{hour:02d}:{minute}" for hour in range(8, 24) for minute in ["00", "30"]]

        t_frame = ctk.CTkFrame(pop, fg_color="transparent"); t_frame.pack(pady=10)
        ctk.CTkLabel(t_frame, text="Start (HH:MM)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10)
        ctk.CTkLabel(t_frame, text="End (HH:MM)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10)

        s_t_var = ctk.StringVar(value="09:00"); e_t_var = ctk.StringVar(value="10:00")
        ctk.CTkOptionMenu(t_frame, width=220, height=40, values=time_options, variable=s_t_var).grid(row=1, column=0, padx=5)
        ctk.CTkOptionMenu(t_frame, width=220, height=40, values=time_options, variable=e_t_var).grid(row=1, column=1, padx=5)

        ctk.CTkLabel(pop, text="Event Type", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=60)
        e_type = ctk.CTkEntry(pop, width=480, height=40); e_type.pack(pady=(5, 15))
        
        ctk.CTkLabel(pop, text="Expected Guests", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=60)
        e_g = ctk.CTkEntry(pop, width=480, height=40, placeholder_text="Minimum 50 guests"); e_g.pack(pady=(5, 20))

        def do_book():
            try:
                guest_val = int(e_g.get())
                if guest_val < 50 or guest_val > hall['cap']:
                    raise ValueError(f"Guests must be between 50 and {hall['cap']}.")

                s_time, e_time = s_t_var.get(), e_t_var.get()
                fmt = '%H:%M'
                tdelta = datetime.strptime(e_time, fmt) - datetime.strptime(s_time, fmt)
                hours = tdelta.seconds / 3600
                if hours <= 0: raise ValueError("End time must be after start time.")

                conn = mysql.connector.connect(**DB_CONFIG); cur = conn.cursor(dictionary=True)
                cur.execute("SELECT room_id, price_per_hour FROM Room WHERE room_number = %s", (r_var.get(),))
                h_data = cur.fetchone()
                
                total = hours * float(h_data['price_per_hour'])
                cur.execute("""
                    INSERT INTO Booking (user_id, room_id, event_date, start_time, end_time, event_type, guest_count, total_amount, status, payment_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Confirmed', 'Pending')
                """, (self.user_id, h_data['room_id'], e_date.get(), s_time, e_time, e_type.get(), guest_val, total))
                
                conn.commit(); conn.close()
                pop.destroy()
                messagebox.showinfo("Success", f"Hall Booked! Total: ${total:.2f}")
                self._apply_filters()
            except Exception as e: messagebox.showerror("Error", str(e))

        ctk.CTkButton(pop, text="Confirm Booking", fg_color=PRIMARY_GREEN, height=50, width=250, font=ctk.CTkFont(size=16, weight="bold"), command=do_book).pack(pady=20)

    def _nav(self, item):
        script = NAV_SCREENS.get(item)
        if script: self.destroy(); subprocess.Popen([sys.executable, script])

    def _sign_out(self):
        if os.path.exists("session.txt"): os.remove("session.txt")
        self.destroy(); subprocess.Popen([sys.executable, "login_screen.py"])

if __name__ == "__main__":
    BanquetHallScreen().mainloop()