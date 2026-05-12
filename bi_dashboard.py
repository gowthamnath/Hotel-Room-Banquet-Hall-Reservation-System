import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox, filedialog, ttk
import subprocess
import sys
import os
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
from tkcalendar import DateEntry  # Requires: pip install tkcalendar

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
SIDEBAR_GREEN = "#4A7A2E"
BG_WHITE = "#FFFFFF"
SECTION_TITLE_COLOR = "#2C3E50"

NAV_ITEMS = [
    ("User & Report Management", "👥"), ("Room & Hall Management", "🛏"),
    ("Booking Calendar", "📅"), ("BI Dashboard", "📊"), ("Settings", "⚙")
]

class ReportsAnalyticsScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.admin_id = self._get_session_id()
        self.admin_full_name = self._get_admin_full_name()
        
        self.title("Admin Center - Financial Dashboard")
        self.after(0, lambda: self.state('zoomed'))
        self.configure(fg_color=BG_WHITE)
        
        # Track figures and containers for refreshing
        self.fig_pie = self.fig_bar = self.fig_cust = None
        self.charts_row = self.cust_row = self.table_row = None
        
        self._build_ui()

    def _get_session_id(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        return open(path, "r").read().strip() if os.path.exists(path) else None

    def _get_admin_full_name(self):
        if not self.admin_id: return "Administrator"
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT first_name, last_name FROM User WHERE user_id = %s", (self.admin_id,))
            res = cursor.fetchone()
            conn.close()
            return f"{res['first_name']} {res['last_name']}" if res else "Administrator"
        except: return "Administrator"

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color=BG_WHITE, corner_radius=0)
        outer.pack(fill="both", expand=True)

        # SIDEBAR
        sidebar = ctk.CTkFrame(outer, fg_color=SIDEBAR_GREEN, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="⚙ Admin Center", font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(pady=30, padx=20, anchor="w")

        for label, icon in NAV_ITEMS:
            is_active = (label == "BI Dashboard")
            btn = ctk.CTkButton(sidebar, text=f"  {icon}  {label}", 
                                fg_color="#3D6A22" if is_active else "transparent", 
                                hover_color="#3D6A22", text_color="white", anchor="w", height=45,
                                command=lambda l=label: self._navigate(l))
            btn.pack(fill="x", padx=12, pady=4)

        ctk.CTkButton(sidebar, text="Sign Out", fg_color="transparent", border_width=1, border_color="#AAAAAA", command=self._sign_out).pack(side="bottom", padx=20, pady=30)

        # MAIN CONTENT AREA
        self.main_area = ctk.CTkScrollableFrame(outer, fg_color=BG_WHITE, corner_radius=0)
        self.main_area.pack(side="left", fill="both", expand=True)

        # HEADER
        header = ctk.CTkFrame(self.main_area, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 10))
        
        ctk.CTkLabel(header, text="Business Intelligence Dashboard", 
                     font=ctk.CTkFont(family="Georgia", size=32, weight="bold"), 
                     text_color=SIDEBAR_GREEN).pack(side="left")
        
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        ctk.CTkButton(btn_frame, text="📄 Export PDF", fg_color=PRIMARY_GREEN, font=ctk.CTkFont(weight="bold"), 
                      command=self._export_pdf_dashboard).pack()

        # --- FILTER SECTION ---
        filter_bar = ctk.CTkFrame(self.main_area, fg_color="#F2F2F2", corner_radius=10)
        filter_bar.pack(fill="x", padx=40, pady=10)

        ctk.CTkLabel(filter_bar, text="Filter Period:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=10)

        self.filter_var = ctk.StringVar(value="Last one year")
        self.filter_menu = ctk.CTkOptionMenu(filter_bar, 
                                            values=["Today", "Last month", "Last 3 months", "Last 6 months", "Last one year", "Select a range"],
                                            variable=self.filter_var,
                                            command=self._on_filter_change,
                                            fg_color=PRIMARY_GREEN, button_color=SIDEBAR_GREEN)
        self.filter_menu.pack(side="left", padx=10)

        self.custom_range_frame = ctk.CTkFrame(filter_bar, fg_color="transparent")
        ctk.CTkLabel(self.custom_range_frame, text="From:").pack(side="left", padx=5)
        self.start_cal = DateEntry(self.custom_range_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.start_cal.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.custom_range_frame, text="To:").pack(side="left", padx=5)
        self.end_cal = DateEntry(self.custom_range_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.end_cal.pack(side="left", padx=5)

        ctk.CTkButton(self.custom_range_frame, text="Apply Range", width=80, command=self._refresh_data).pack(side="left", padx=10)

        # Dashboard Containers
        self.charts_row = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.charts_row.pack(fill="x", padx=40, pady=10)
        self.cust_row = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.cust_row.pack(fill="x", padx=40, pady=10)
        self.table_row = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.table_row.pack(fill="x", padx=40, pady=10)

        self._refresh_data()

    def _get_filter_sql(self, date_col):
        choice = self.filter_var.get()
        if choice == "Today": return f"DATE({date_col}) = CURDATE()"
        if choice == "Last month": return f"{date_col} >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
        if choice == "Last 3 months": return f"{date_col} >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
        if choice == "Last 6 months": return f"{date_col} >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)"
        if choice == "Last one year": return f"{date_col} >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)"
        if choice == "Select a range":
            return f"DATE({date_col}) BETWEEN '{self.start_cal.get()}' AND '{self.end_cal.get()}'"
        return "1=1"

    def _on_filter_change(self, choice):
        if choice == "Select a range":
            self.custom_range_frame.pack(side="left", padx=10)
        else:
            self.custom_range_frame.pack_forget()
            self._refresh_data()

    def _refresh_data(self):
        for row in [self.charts_row, self.cust_row, self.table_row]:
            for child in row.winfo_children(): child.destroy()

        self._plot_pie_chart(self.charts_row)
        self._plot_bar_chart(self.charts_row)
        
        ctk.CTkLabel(self.cust_row, text="Top Loyal Customers", font=ctk.CTkFont(size=20, weight="bold"), text_color=SECTION_TITLE_COLOR).pack(anchor="w")
        self._plot_customer_chart(self.cust_row)
        
        ctk.CTkLabel(self.table_row, text="Recent Transactions", font=ctk.CTkFont(size=20, weight="bold"), text_color=SECTION_TITLE_COLOR).pack(anchor="w", pady=(20,10))
        self._build_transactions_table(self.table_row)

    def _plot_pie_chart(self, parent):
        self.fig_pie, ax = plt.subplots(figsize=(5, 4), dpi=95)
        sql_filter = self._get_filter_sql("Reservation.payment_date")
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(f"SELECT room_type, COUNT(*) FROM Reservation JOIN Room ON Reservation.room_id = Room.room_id WHERE payment_status = 'Completed' AND {sql_filter} GROUP BY room_type")
            data = cursor.fetchall()
            conn.close()
            if data:
                ax.pie([x[1] for x in data], labels=[x[0] for x in data], autopct='%1.1f%%', startangle=140, colors=['#5C8A3C', '#3498DB', '#E67E22', '#9B59B6', "#4424D2", "#B80E0E", "#D4D11B"])
                ax.set_title("Revenue by Room Type", fontweight='bold')
            else: ax.text(0.5, 0.5, "No Data for Period", ha='center')
        except: ax.text(0.5, 0.5, "Database Error", ha='center')
        FigureCanvasTkAgg(self.fig_pie, master=parent).get_tk_widget().pack(side="left", expand=True, padx=10)

    def _plot_bar_chart(self, parent):
        self.fig_bar, ax = plt.subplots(figsize=(5, 4), dpi=95)
        sql_filter = self._get_filter_sql("Booking.payment_date")
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(f"SELECT room_type, COUNT(*) FROM Booking JOIN Room ON Booking.room_id = Room.room_id WHERE payment_status = 'Completed' AND {sql_filter} GROUP BY room_type")
            data = cursor.fetchall()
            conn.close()
            if data:
                ax.bar([x[0] for x in data], [x[1] for x in data], color='#3498DB')
                ax.set_title("Revenue by Hall Type", fontweight='bold')
            else: ax.text(0.5, 0.5, "No Data for Period", ha='center')
        except: ax.text(0.5, 0.5, "Database Error", ha='center')
        FigureCanvasTkAgg(self.fig_bar, master=parent).get_tk_widget().pack(side="left", expand=True, padx=10)

    def _plot_customer_chart(self, parent):
        self.fig_cust, ax = plt.subplots(figsize=(12, 4), dpi=95)
        sql_filter_res = self._get_filter_sql("Reservation.payment_date")
        sql_filter_bk = self._get_filter_sql("Booking.payment_date")
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = f"""
                SELECT U.first_name, COUNT(*) as total FROM User U
                JOIN (
                    SELECT user_id FROM Reservation WHERE payment_status = 'Completed' AND {sql_filter_res}
                    UNION ALL 
                    SELECT user_id FROM Booking WHERE payment_status = 'Completed' AND {sql_filter_bk}
                ) as Combined ON U.user_id = Combined.user_id GROUP BY U.user_id ORDER BY total DESC LIMIT 8
            """
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()
            if data:
                names = [x[0] for x in data]
                counts = [x[1] for x in data]

                ax.barh(names, counts, color='#2980B9')
                ax.set_title("Top Loyal Customers", fontweight='bold')
                ax.set_xlabel("Total Bookings")
                ax.invert_yaxis()
            else: ax.text(0.5, 0.5, "No Data", ha='center')
        except: ax.text(0.5, 0.5, "Database Error", ha='center')
        plt.tight_layout()
        FigureCanvasTkAgg(self.fig_cust, master=parent).get_tk_widget().pack(fill="x")

    def _build_transactions_table(self, parent):
        cols = ("cat", "email", "amt", "date")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=8)
        for c, t in zip(cols, ["Category", "Email", "Amount", "Date"]): 
            tree.heading(c, text=t)
            tree.column(c, anchor="center")
        
        sql_filter_res = self._get_filter_sql("R.payment_date")
        sql_filter_bk = self._get_filter_sql("B.payment_date")
        
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"""
                SELECT 'Room' as Cat, U.email, R.total_amount as Amt, R.payment_date as Dt
                FROM Reservation R JOIN User U ON R.user_id = U.user_id WHERE R.payment_status='Completed' AND {sql_filter_res}
                UNION ALL
                SELECT 'Hall', U.email, B.total_amount, B.payment_date
                FROM Booking B JOIN User U ON B.user_id = U.user_id WHERE B.payment_status='Completed' AND {sql_filter_bk}
                ORDER BY Dt DESC LIMIT 15
            """)
            for row in cursor.fetchall():
                tree.insert("", "end", values=(row['Cat'], row['email'], f"${row['Amt']:.2f}", row['Dt']))
            conn.close()
        except: pass
        tree.pack(fill="x")

    def _export_pdf_dashboard(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            initialfile=f"BI_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        if not file_path: return
        
        try:
            # 1. Save charts
            self.fig_pie.savefig("t1.png")
            self.fig_bar.savefig("t2.png")
            self.fig_cust.savefig("t3.png")

            # 2. PDF Gen
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 22)
            pdf.set_text_color(74, 122, 46) 
            pdf.cell(0, 20, "Revenue & Customer Loyalty Report", ln=True, align='C')
            
            pdf.set_font("Arial",  size=10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 8, f"Report Generated by: {self.admin_full_name} | Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='R')
            filter_text = self.filter_var.get()
            if filter_text == "Select a range":
                 filter_text = f"Custom Range: {self.start_cal.get()} to {self.end_cal.get()}"
            pdf.set_font("Arial",  size = 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 8, f"Report Filter: {filter_text}", ln=True, align='R')
            
            pdf.ln(5)
            pdf.image("t1.png", x=10, y=50, w=90)
            pdf.image("t2.png", x=110, y=50, w=90)
            pdf.ln(75)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Customer Loyalty Analysis", ln=True)
            pdf.image("t3.png", x=10, w=190)
            
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 15, "Transaction Audit Log", ln=True)
            
            # Header
            pdf.set_font("Arial", 'B', 11)
            pdf.set_fill_color(92, 138, 60) 
            pdf.set_text_color(255, 255, 255)
            pdf.cell(30, 10, "Category", 1, 0, 'C', True)
            pdf.cell(75, 10, "Email", 1, 0, 'C', True)
            pdf.cell(35, 10, "Amount", 1, 0, 'C', True)
            pdf.cell(50, 10, "Date", 1, 1, 'C', True)

            # Data
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0, 0, 0)
            
            # Reuse logic for data
            sql_res = self._get_filter_sql("R.payment_date")
            sql_bk = self._get_filter_sql("B.payment_date")
            
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"""
                SELECT 'Room' as Cat, U.email, R.total_amount as Amt, R.payment_date as Dt
                FROM Reservation R JOIN User U ON R.user_id = U.user_id WHERE R.payment_status='Completed' AND {sql_res}
                UNION ALL
                SELECT 'Hall', U.email, B.total_amount, B.payment_date
                FROM Booking B JOIN User U ON B.user_id = U.user_id WHERE B.payment_status='Completed' AND {sql_bk}
                ORDER BY Dt DESC
            """)
            
            fill = False
            for row in cursor.fetchall():
                pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
                pdf.cell(30, 9, str(row['Cat']), 1, 0, 'C', True)
                pdf.cell(75, 9, str(row['email']), 1, 0, 'C', True)
                pdf.cell(35, 9, f"${row['Amt']:.2f}", 1, 0, 'C', True)
                pdf.cell(50, 9, str(row['Dt']), 1, 1, 'C', True)
                fill = not fill

            pdf.output(name=file_path, dest='F')
            conn.close()
            # Automatically open PDF in Chrome
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                  r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]

            chrome = next((path for path in chrome_paths if os.path.exists(path)), None)

            if chrome:
                subprocess.Popen([chrome, file_path])
            else:
    # fallback: open with system default PDF viewer
              os.startfile(file_path)
            time.sleep(0.5)
            for f in ["t1.png", "t2.png", "t3.png"]: 
                if os.path.exists(f): os.remove(f)

            messagebox.showinfo("Success", f"Report saved to: {file_path}")
        except Exception as e: 
            messagebox.showerror("Error", f"PDF Export Error: {e}")

    def _navigate(self, label):
        if label == "BI Dashboard": return
        file_map = {
            "User & Report Management": "user_management_screen.py", 
            "Room & Hall Management": "room_management_admin.py", 
            "Booking Calendar": "booking_calender.py", 
            "Settings": "settings_admin.py"
        }
        if label in file_map:
            target_path = os.path.join(os.path.dirname(__file__), file_map[label])
            if os.path.exists(target_path):
                subprocess.Popen([sys.executable, target_path])
                self.withdraw()
                self.after(200, self.destroy)
            else:
                messagebox.showerror("Error", f"File {file_map[label]} not found.")

    def _sign_out(self):
        path = os.path.join(os.path.dirname(__file__), "session.txt")
        if os.path.exists(path): os.remove(path)
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "login_screen.py")])

if __name__ == "__main__":
    app = ReportsAnalyticsScreen()
    app.mainloop()