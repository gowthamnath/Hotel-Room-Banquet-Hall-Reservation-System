import customtkinter as ctk
import subprocess
import sys
import os
import mysql.connector
from datetime import datetime
from tkinter import messagebox

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
DARK_TEXT = "#2C3E50"

NAV_ITEMS = ["Rooms", "Banquet Halls", "My Bookings", "Settings"]

NAV_SCREENS = {
    "Rooms": "search_room_screen.py", 
    "Banquet Halls": "banquet_hall_screen.py",
    "My Bookings": "my_bookings_screen.py",
    "Settings": "settings.py"
}

class MyBookingsScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Get Session Data
        self.user_id = self._get_user_id()
        self.user_name = self._get_logged_in_user_name()
        
        self.title("Hotel Reservation - My Bookings History")
        self.geometry("1200x850")
        self.configure(fg_color="#F5F5F5")
        self._build_ui()
        self.after(0, lambda: self.state('zoomed'))

    def _get_user_id(self):
        session_path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(session_path):
            with open(session_path, "r") as f:
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
        except: return "User"

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="#F5F5F5")
        outer.pack(fill="both", expand=True)

        # Sidebar
        sidebar = ctk.CTkFrame(outer, fg_color=SIDEBAR_GREEN, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="🏨 Hotel Reservation", font=ctk.CTkFont(size=14, weight="bold"), text_color="white").pack(pady=20, padx=15, anchor="w")

        for item in NAV_ITEMS:
            is_active = item == "My Bookings"
            btn = ctk.CTkButton(sidebar, text=f"  {item}", fg_color="#3D6A22" if is_active else "transparent",
                                hover_color="#3D6A22", text_color="white", anchor="w", height=40, corner_radius=6,
                                command=lambda s=item: self._nav(s))
            btn.pack(fill="x", padx=10, pady=3)

        ctk.CTkButton(sidebar, text="🚪 Sign Out", fg_color="transparent", hover_color="#A33333", 
                      text_color="white", anchor="w", height=40, command=self._sign_out).pack(side="bottom", fill="x", padx=10, pady=20)

        # Main content
        main = ctk.CTkFrame(outer, fg_color="#F5F5F5")
        main.pack(side="left", fill="both", expand=True)

        # Header Section
        header = ctk.CTkFrame(main, fg_color=LIGHT_GREEN_HEADER, corner_radius=0, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text=f"Welcome back, {self.user_name}! 👋", font=ctk.CTkFont(size=14, weight="bold"), text_color=SIDEBAR_GREEN).pack(side="top", anchor="ne", padx=30, pady=(15, 0))
        ctk.CTkLabel(header, text="My Reservation History", font=ctk.CTkFont(family="Georgia", size=26, weight="bold"), text_color=SIDEBAR_GREEN).pack(pady=(5, 8))

        # Scrollable Area
        self.scroll_frame = ctk.CTkScrollableFrame(main, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._load_data()

    def _load_data(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.user_id:
            ctk.CTkLabel(self.scroll_frame, text="Please log in to view bookings.").pack(pady=20)
            return

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)

            # Room Reservations
            cursor.execute("""
                SELECT r.reservation_id, rm.room_number, rm.room_type, r.check_in_date, 
                       r.status, r.payment_status, r.total_amount, r.room_id
                FROM Reservation r 
                JOIN Room rm ON r.room_id = rm.room_id 
                WHERE r.user_id = %s ORDER BY r.check_in_date DESC
            """, (self.user_id,))
            res_data = cursor.fetchall()

            # Banquet Bookings
            cursor.execute("""
                SELECT b.booking_id, rm.hall_name, b.event_date, b.event_type, 
                       b.status, b.payment_status, b.total_amount, b.room_id
                FROM Booking b 
                JOIN Room rm ON b.room_id = rm.room_id 
                WHERE b.user_id = %s ORDER BY b.event_date DESC
            """, (self.user_id,))
            hall_data = cursor.fetchall()

            conn.close()

            self._create_section("🏨 Hotel Room Reservations", res_data, is_hall=False)
            self._create_section("🎊 Banquet Hall Bookings", hall_data, is_hall=True)

        except Exception as e:
            print(f"Database Error: {e}")

    def _create_section(self, title, data, is_hall):
        ctk.CTkLabel(self.scroll_frame, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=SIDEBAR_GREEN).pack(anchor="w", pady=(20, 5))
        
        header_row = ctk.CTkFrame(self.scroll_frame, fg_color="#E8E8E8", height=35, corner_radius=5)
        header_row.pack(fill="x", pady=(0, 5))
        
        # Headers adjusted: Removed "Action"
        headers = [("Details", 0.05), ("Total", 0.35), ("Booking Status", 0.52), ("Payment Status", 0.75)]
        for text, relx in headers:
            lbl = ctk.CTkLabel(header_row, text=text, font=ctk.CTkFont(size=12, weight="bold"), text_color="#555555")
            lbl.place(relx=relx, rely=0.5, anchor="w")

        if not data:
            ctk.CTkLabel(self.scroll_frame, text="No records found.", text_color="gray").pack(anchor="w", padx=20, pady=10)
            return

        for item in data:
            card = ctk.CTkFrame(self.scroll_frame, fg_color="white", corner_radius=8, border_width=1, border_color="#DDDDDD", height=85)
            card.pack(fill="x", pady=4)
            card.pack_propagate(False)
            
            name = item['room_number'] if not is_hall else item['hall_name']
            date_val = item['check_in_date'] if not is_hall else item['event_date']
            sub_text = item['room_type'] if not is_hall else item['event_type']
            detail_str = f"{name} ({sub_text})\n{date_val.strftime('%b %d, %Y')}"
            
            ctk.CTkLabel(card, text=detail_str, justify="left", font=ctk.CTkFont(size=12)).place(relx=0.05, rely=0.5, anchor="w")
            ctk.CTkLabel(card, text=f"${item['total_amount']}", font=ctk.CTkFont(size=13, weight="bold")).place(relx=0.35, rely=0.5, anchor="w")
            
            b_status = str(item['status']).strip()
            p_status = str(item['payment_status']).strip()
            
            # Booking Status Color Logic
            b_color = "#4A7A2E" if b_status.lower() in ['confirmed', 'completed', 'checked-in'] else "#A33333"
            ctk.CTkLabel(card, text=b_status, text_color=b_color, font=ctk.CTkFont(weight="bold")).place(relx=0.52, rely=0.5, anchor="w")
            
            # Payment Status Color Logic
            p_color = "#D68910" if p_status.lower() in ["pending", "refund requested"] else "#229954" if p_status.lower() == "completed" else "#A33333"
            ctk.CTkLabel(card, text=p_status, text_color=p_color, font=ctk.CTkFont(size=12, weight="bold")).place(relx=0.75, rely=0.5, anchor="w")

            # Cancel Button Logic: Placed at the far right without a specific header column
            if b_status.lower() not in ['cancelled', 'checked-out']:
                table = "Booking" if is_hall else "Reservation"
                id_val = item['booking_id'] if is_hall else item['reservation_id']
                id_col = "booking_id" if is_hall else "reservation_id"

                cancel_btn = ctk.CTkButton(card, text="Cancel Booking", width=120, height=32, fg_color="#A33333", 
                                           hover_color="#822929", font=ctk.CTkFont(size=11, weight="bold"),
                                           command=lambda t=table, c=id_col, v=id_val, ps=p_status, rid=item['room_id']: 
                                           self._cancel_booking(t, c, v, ps, rid))
                cancel_btn.place(relx=0.88, rely=0.5, anchor="w")

    def _cancel_booking(self, table, id_col, id_val, current_p_status, room_id):
        if not messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this booking?"):
            return

        if current_p_status.lower() == "completed":
            new_pay_status = "Refund Requested"
        else:
            new_pay_status = "Failed"

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            sql = f"UPDATE {table} SET status = 'Cancelled', payment_status = %s WHERE {id_col} = %s"
            cursor.execute(sql, (new_pay_status, id_val))

            cursor.execute("UPDATE Room SET status = 'Available' WHERE room_id = %s", (room_id,))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Booking successfully cancelled. Payment status: {new_pay_status}")
            self._load_data() 

        except Exception as e:
            messagebox.showerror("Error", f"Could not process cancellation: {e}")

    def _nav(self, item):
        script = NAV_SCREENS.get(item)
        if script:
            self.destroy()
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), script)])

    def _sign_out(self):
        session_path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(session_path): os.remove(session_path)
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "login_screen.py")])

if __name__ == "__main__":
    app = MyBookingsScreen()
    app.mainloop()