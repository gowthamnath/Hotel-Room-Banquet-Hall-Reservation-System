import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
import tkinter as tk
from datetime import datetime
from tkcalendar import DateEntry
import subprocess
import sys
import os

# Database Configuration
DB_CONFIG = {
    "host": "141.209.241.57",
    "port": 3306,
    "user": "putch1v",
    "password": "mypass",
    "database": "BIS698MSpring26Group_2"
}

# UI Styling
PRIMARY_GREEN = "#5C8A3C"
SIDEBAR_GREEN = "#2E4A1E"
LIGHT_GREEN_BG = "#A8C68F"
DARK_TEXT = "#2C3E50"

class StaffDashboard(ctk.CTk):
    def __init__(self, staff_id=None):
        super().__init__()
        self.staff_id = staff_id or self._get_session_id()
        self.staff_name = self._get_staff_name()

        self.title("Staff Dashboard - Management Console")
        self.after(0, lambda: self.state('zoomed'))
        self.configure(fg_color="white")

        self._build_ui()
        self._refresh_dashboard()

    def _get_session_id(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(path):
            with open(path, "r") as f: return f.read().strip()
        return None

    def _get_staff_name(self):
        if not self.staff_id: return "Staff"
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT first_name FROM User WHERE user_id=%s", (self.staff_id,))
            user = cursor.fetchone()
            conn.close()
            return user["first_name"] if user else "Staff"
        except: return "Staff"

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="white")
        outer.pack(fill="both", expand=True)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(outer, width=220, corner_radius=0, fg_color=SIDEBAR_GREEN)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(self.sidebar, text="🏨 STAFF PANEL", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(pady=(30, 10))
        ctk.CTkLabel(self.sidebar, text=f"Welcome,\n{self.staff_name}! 👋", font=ctk.CTkFont(size=15, weight="bold"), text_color=LIGHT_GREEN_BG, justify="center").pack(pady=(0, 20))
        
        ctk.CTkButton(self.sidebar, text="🔄 Refresh Data", fg_color="transparent", border_width=1, border_color=LIGHT_GREEN_BG, command=self._refresh_dashboard).pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(self.sidebar, text="🚪 Logout", fg_color="#A33333", hover_color="#802626", command=self._logout).pack(side="bottom", pady=20, padx=20, fill="x")

        # MAIN CONTENT
        main_content = ctk.CTkFrame(outer, fg_color="white")
        main_content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_content, text="Operational Overview", font=ctk.CTkFont(family="Georgia", size=26, weight="bold"), text_color=SIDEBAR_GREEN).pack(anchor="w", pady=(10, 20))

        self.tabview = ctk.CTkTabview(main_content, segmented_button_selected_color=PRIMARY_GREEN, segmented_button_unselected_hover_color=LIGHT_GREEN_BG)
        self.tabview.pack(fill="both", expand=True)
        
        self.room_tab = self.tabview.add("Hotel Room Management")
        self.hall_tab = self.tabview.add("Banquet Hall Management")

    def _refresh_dashboard(self):
        for tab in [self.room_tab, self.hall_tab]:
            for child in tab.winfo_children(): child.destroy()
        self._build_section(self.room_tab, "Reservation")
        self._build_section(self.hall_tab, "Booking")

    def _build_section(self, parent_tab, table):
        sub_tabs = ctk.CTkTabview(parent_tab, segmented_button_selected_color=SIDEBAR_GREEN)
        sub_tabs.pack(fill="both", expand=True)
        self._populate_list(sub_tabs.add("Booking Requests"), table, mode="pending")
        self._populate_list(sub_tabs.add("Cancellation Requests"), table, mode="refund")
        self._populate_list(sub_tabs.add("Verified History"), table, mode="history")

    def _populate_list(self, frame, table, mode):
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        header = ctk.CTkFrame(scroll, fg_color="#E8E8E8", height=40)
        header.pack(fill="x", pady=(0, 10))
        
        cols = [("Guest", 0.02), ("Room/Hall", 0.16), ("Check-in Date/time", 0.30), ("Check-out Date/time", 0.44), ("Amount", 0.58), ("Payment", 0.70)]
        if mode == "history":
            cols.append(("Transaction ID", 0.82))
        elif mode != "history":
            cols.append(("Action", 0.84))

        for t, p in cols: 
            ctk.CTkLabel(header, text=t, font=ctk.CTkFont(size=12, weight="bold"), text_color=DARK_TEXT).place(relx=p, rely=0.5, anchor="w")

        data = self._fetch_db_data(table, mode)
        for item in data:
            row = ctk.CTkFrame(scroll, fg_color="white", height=75, border_width=1, border_color="#EEEEEE")
            row.pack(fill="x", pady=2); row.pack_propagate(False)
            
            id_val = item['reservation_id'] if table == "Reservation" else item['booking_id']
            id_col = "reservation_id" if table == "Reservation" else "booking_id"

            ctk.CTkLabel(row, text=f"{item['first_name']} {item['last_name']}", font=ctk.CTkFont(size=12, weight="bold")).place(relx=0.02, rely=0.5, anchor="w")
            
            disp_name = item.get('room_number') if table == "Reservation" else item.get('hall_name')
            ctk.CTkLabel(row, text=str(disp_name)).place(relx=0.16, rely=0.5, anchor="w")
            
            start = item.get('check_in_date') or item.get('start_time')
            end = item.get('check_out_date') or item.get('end_time')
            ctk.CTkLabel(row, text=str(start)).place(relx=0.30, rely=0.5, anchor="w")
            ctk.CTkLabel(row, text=str(end)).place(relx=0.44, rely=0.5, anchor="w")
            
            ctk.CTkLabel(row, text=f"${item['total_amount']}", font=ctk.CTkFont(size=13, weight="bold"), text_color=PRIMARY_GREEN).place(relx=0.58, rely=0.5, anchor="w")
            
            p_stat = item['payment_status']
            p_color = "#D68910" if "requested" in p_stat.lower() else ("#229954" if p_stat.lower() == "completed" else "#A33333")
            ctk.CTkLabel(row, text=p_stat, text_color=p_color, font=ctk.CTkFont(weight="bold")).place(relx=0.70, rely=0.5, anchor="w")

            if mode == "pending":
                btn_f = ctk.CTkFrame(row, fg_color="transparent")
                btn_f.place(relx=0.84, rely=0.5, anchor="w")
                ctk.CTkButton(btn_f, text="Settle", width=65, height=28, fg_color=PRIMARY_GREEN, command=lambda i=item, t=table, c=id_col, iv=id_val: self._process_payment(i, t, c, iv)).pack(side="left", padx=2)
                ctk.CTkButton(btn_f, text="Reject", width=65, height=28, fg_color="#A33333", command=lambda t=table, c=id_col, iv=id_val: self._reject_booking(t, c, iv)).pack(side="left", padx=2)
            if mode == "history":
                txn_id = item.get('transaction_id', 'N/A')
                ctk.CTkLabel(row, text=str(txn_id), font=ctk.CTkFont(size=11)).place(relx=0.82, rely=0.5, anchor="w")
            elif mode == "refund":
                ctk.CTkButton(row, text="Issue Refund", width=120, height=28, fg_color="#D68910", command=lambda t=table, c=id_col, iv=id_val: self._complete_refund(t, c, iv)).place(relx=0.84, rely=0.5, anchor="w")

    def _fetch_db_data(self, table, mode):
        try:
            conn = mysql.connector.connect(**DB_CONFIG); cursor = conn.cursor(dictionary=True)
            if mode == "pending": cond = "LOWER(t.payment_status) = 'pending'"
            elif mode == "refund": cond = "LOWER(t.payment_status) = 'refund requested'"
            else: cond = "LOWER(t.payment_status) IN ('completed', 'refunded', 'failed')"
            
            query = f"""SELECT t.*, u.first_name, u.last_name, r.room_number, r.hall_name, r.price_per_night, r.price_per_hour, r.room_id
                        FROM {table} t 
                        JOIN User u ON t.user_id=u.user_id 
                        LEFT JOIN Room r ON t.room_id=r.room_id 
                        WHERE {cond} ORDER BY t.created_at DESC LIMIT 500"""
            cursor.execute(query); data = cursor.fetchall(); conn.close()
            return data
        except Exception as e: return []

    def _process_payment(self, item, table, id_col, id_val):
        pay_win = ctk.CTkToplevel(self); pay_win.title("Settle Payment"); pay_win.geometry("500x500"); pay_win.grab_set(); pay_win.configure(fg_color="white")
        is_hall = (table == "Booking")
        updated_amount = tk.DoubleVar(value=float(item['total_amount']))
        
        ctk.CTkLabel(pay_win, text="Payment Finalization", font=ctk.CTkFont(size=20, weight="bold"), text_color=SIDEBAR_GREEN).pack(pady=20)
        
        container = ctk.CTkFrame(pay_win, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40)

        if not is_hall:
            ctk.CTkLabel(container, text="Check-in Date", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            checkin = DateEntry(container, width=35, background=SIDEBAR_GREEN, foreground='white', borderwidth=2)
            checkin.set_date(item.get('check_in_date') or datetime.now().date()); checkin.pack(pady=(0, 15))
            ctk.CTkLabel(container, text="Check-out Date", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            checkout = DateEntry(container, width=35, background=SIDEBAR_GREEN, foreground='white', borderwidth=2)
            checkout.set_date(item.get('check_out_date') or datetime.now().date()); checkout.pack(pady=(0, 15))
        else:
            ctk.CTkLabel(container, text="Start Time (HH:MM:SS)", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            st_e = ctk.CTkEntry(container, width=350); st_e.insert(0, str(item.get('start_time', '12:00:00'))); st_e.pack(pady=(0, 15))
            ctk.CTkLabel(container, text="End Time (HH:MM:SS)", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            en_e = ctk.CTkEntry(container, width=350); en_e.insert(0, str(item.get('end_time', '14:00:00'))); en_e.pack(pady=(0, 15))

        def calc():
            try:
                if not is_hall:
                    days = (checkout.get_date() - checkin.get_date()).days
                    val = float(item.get('price_per_night') or 0) * (max(days, 1))
                else:
                    t1 = datetime.strptime(st_e.get(), "%H:%M:%S")
                    t2 = datetime.strptime(en_e.get(), "%H:%M:%S")
                    hours = (t2 - t1).total_seconds() / 3600
                    if hours <= 0: raise ValueError("End time must be after start time")
                    val = float(item.get('price_per_hour') or 0) * hours
                updated_amount.set(round(val, 2))
                amt_display.configure(text=f"Total Amount: ${updated_amount.get():.2f}")
            except Exception as e: messagebox.showerror("Error", f"Calculation failed: {e}")

        ctk.CTkButton(container, text="Recalculate Price", command=calc, fg_color="gray").pack(pady=5)
        amt_display = ctk.CTkLabel(container, text=f"Total Amount: ${updated_amount.get():.2f}", font=ctk.CTkFont(size=22, weight="bold"), text_color=PRIMARY_GREEN)
        amt_display.pack(pady=15)

        ctk.CTkLabel(container, text="Payment Method", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        method_cb = ctk.CTkComboBox(container, values=["Credit Card", "Debit Card", "Cash", "Zelle", "Net Banking"], width=350); method_cb.pack(pady=(0, 15))
        
        ctk.CTkLabel(container, text="Transaction ID: Auto-Generated ", font=ctk.CTkFont(slant="italic"), text_color="gray").pack(pady=5)

        def finalize():
            try:
                conn = mysql.connector.connect(**DB_CONFIG); cursor = conn.cursor()
                p_date = datetime.now()
                
                # --- AUTO-GENERATE TXN ID ---
                # Format: TXN + FName(3) + AssetID/No + DDMMYY
                prefix = "TXN"
                fname_part = (item['first_name'][:3]).upper()
                asset_id = str(item.get('room_number') or item.get('room_id'))
                date_part = p_date.strftime("%d%m%y")
                generated_txn_id = f"{prefix}{fname_part}{asset_id}{date_part}"
                
                if not is_hall:
                    sql = f"""UPDATE Reservation SET status='Completed', payment_status='Completed', total_amount=%s, 
                              payment_method=%s, transaction_id=%s, payment_date=%s, 
                              actual_checkin=%s, actual_checkout=%s, staff_id=%s WHERE {id_col}=%s"""
                    params = (updated_amount.get(), method_cb.get(), generated_txn_id, p_date, checkin.get_date(), checkout.get_date(), self.staff_id, id_val)
                else:
                    sql = f"""UPDATE Booking SET status='Completed', payment_status='Completed', total_amount=%s, 
                              payment_method=%s, transaction_id=%s, payment_date=%s, 
                              start_time=%s, end_time=%s, staff_id=%s WHERE {id_col}=%s"""
                    params = (updated_amount.get(), method_cb.get(), generated_txn_id, p_date, st_e.get(), en_e.get(), self.staff_id, id_val)
                
                cursor.execute(sql, params)
                cursor.execute(f"UPDATE Room SET status='Available' WHERE room_id=%s", (item['room_id'],))
                conn.commit(); conn.close()
                pay_win.destroy(); self._refresh_dashboard()
                messagebox.showinfo("Success", f"Settlement complete!\nTXN ID: {generated_txn_id}")
            except Error as e: messagebox.showerror("DB Error", str(e))

        ctk.CTkButton(pay_win, text="Confirm & Complete Settlement", fg_color=PRIMARY_GREEN, height=45, width=350, command=finalize).pack(pady=20)

    def _complete_refund(self, table, id_col, id_val):
        if messagebox.askyesno("Confirm Refund", "Confirm that refund has been processed offline?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG); cursor = conn.cursor()
                cursor.execute(f"UPDATE {table} SET payment_status='Refunded' WHERE {id_col}=%s", (id_val,))
                conn.commit(); conn.close(); self._refresh_dashboard()
                messagebox.showinfo("Success", "Record updated to Refunded.")
            except Error as e: messagebox.showerror("Error", str(e))

    def _reject_booking(self, table, id_col, id_val):
        if messagebox.askyesno("Reject", "Reject this booking request?"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG); cursor = conn.cursor()
                cursor.execute(f"UPDATE {table} SET status='Cancelled', payment_status='Failed' WHERE {id_col}=%s", (id_val,))
                conn.commit(); conn.close(); self._refresh_dashboard()
            except Error as e: messagebox.showerror("Error", str(e))

    def _logout(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(path): os.remove(path)
        self.destroy(); subprocess.Popen([sys.executable, "login_screen.py"])

if __name__ == "__main__":
    app = StaffDashboard(); app.mainloop()