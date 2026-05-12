import customtkinter as ctk
import subprocess
import sys
import os
import tkinter as tk
import mysql.connector
from mysql.connector import Error

# CONFIGURATION
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

PRIMARY_GREEN = "#5C8A3C"
LIGHT_GREEN_BG = "#A8C68F"
YELLOW_BG = "#FAFAD2"
DARK_TEXT = "#2C3E50"
GRAY_TEXT = "#888888"

class LoginScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hotel Reservation System - Unified Login")
        self.geometry("1100x750")
        self.configure(fg_color="white")
        self.resizable(True, True)
        self.after(0, lambda: self.state('zoomed'))
        self.bind("<Return>", lambda event: self._do_login())
        
        # --- Capture email passed from Signup Screen ---
        self.passed_email = sys.argv[1] if len(sys.argv) > 1 else ""
        
        # Database connection details
        self.db_config = {
            'host': '141.209.241.57',
            'port': 3306,
            'user': 'putch1v',
            'password': 'mypass',
            'database': 'BIS698MSpring26Group_2'
        }
        
        self._build_ui()
        
        # --- Auto-populate the email field if an email was caught ---
        if self.passed_email:
            self.email_entry.insert(0, self.passed_email)
    
    def _toggle_password(self):
        if self.show_password_var.get():
            self.password_entry.configure(show="")   
        else:
            self.password_entry.configure(show="•")  

    def _build_ui(self):
        # Top navbar
        navbar = ctk.CTkFrame(self, fg_color="white", height=70, corner_radius=0)
        navbar.pack(fill="x", side="top")
        navbar.pack_propagate(False)

        logo_frame = ctk.CTkFrame(navbar, fg_color=PRIMARY_GREEN, width=48, height=48, corner_radius=10)
        logo_frame.pack(side="left", padx=20, pady=10)
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="🏨", font=ctk.CTkFont(size=22)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(navbar, text="Hotel Reservation System",
                     font=ctk.CTkFont(size=17, weight="bold"), text_color=DARK_TEXT).pack(side="left", padx=8)

        back_btn = ctk.CTkButton(navbar, text="← Back to Home",
                                 fg_color=PRIMARY_GREEN, hover_color="#4a7230",
                                 text_color="white", width=150, height=38,
                                 corner_radius=8, command=self._go_home)
        back_btn.pack(side="right", padx=20, pady=15)

        ctk.CTkFrame(self, fg_color="#E0E0E0", height=1, corner_radius=0).pack(fill="x")

        # Content area
        content = ctk.CTkFrame(self, fg_color="white")
        content.pack(fill="both", expand=True)

        # Left panel - form
        left = ctk.CTkFrame(content, fg_color="white")
        left.pack(side="left", fill="both", expand=True, padx=60, pady=40)

        ctk.CTkLabel(left, text="Log In",
                     font=ctk.CTkFont(family="Georgia", size=36, weight="bold"),
                     text_color=DARK_TEXT).pack(anchor="w", pady=(20, 30))

        # Email field
        ctk.CTkLabel(left, text="Email", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=PRIMARY_GREEN).pack(anchor="w")
        self.email_entry = ctk.CTkEntry(left, placeholder_text="email@example.com",
                                        width=460, height=48, corner_radius=8,
                                        border_color=PRIMARY_GREEN, border_width=1,
                                        font=ctk.CTkFont(size=14))
        self.email_entry.pack(anchor="w", pady=(4, 18))

        # Password field
        ctk.CTkLabel(left, text="Password", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=PRIMARY_GREEN).pack(anchor="w")
        self.password_entry = ctk.CTkEntry(left, placeholder_text="password",
                                           width=460, height=48, corner_radius=8,
                                           border_color=PRIMARY_GREEN, border_width=1,
                                           font=ctk.CTkFont(size=14), show="•")
        self.password_entry.pack(anchor="w", pady=(4, 10))

        # Password options row
        row = ctk.CTkFrame(left, fg_color="white", width=460)
        row.pack(anchor="w", pady=(0, 24))

        self.show_password_var = ctk.BooleanVar()
        ctk.CTkCheckBox(row, text="Show Password",
                variable=self.show_password_var,
                text_color=DARK_TEXT,
                font=ctk.CTkFont(size=13),
                fg_color=PRIMARY_GREEN,
                command=self._toggle_password).pack(side="left")

        forgot_btn = ctk.CTkButton(row, text="Forgot Password?",
                                   fg_color="transparent", hover_color="#F0F0F0",
                                   text_color=PRIMARY_GREEN, font=ctk.CTkFont(size=13),
                                   width=130, command=self._go_forgot)
        forgot_btn.pack(side="right", padx=(165, 0)) 

        # Action Buttons
        login_btn = ctk.CTkButton(left, text="Log In  →",
                                  fg_color=PRIMARY_GREEN, hover_color="#4a7230",
                                  text_color="white", width=460, height=52,
                                  corner_radius=8, font=ctk.CTkFont(size=16, weight="bold"),
                                  command=self._do_login)
        login_btn.pack(anchor="w", pady=6)

        clear_btn = ctk.CTkButton(left, text="Clear Form  ✕",
                                  fg_color=YELLOW_BG, hover_color="#e8e8b0",
                                  text_color=PRIMARY_GREEN, width=460, height=52,
                                  corner_radius=8, font=ctk.CTkFont(size=16, weight="bold"),
                                  border_width=0, command=self._clear_form)
        clear_btn.pack(anchor="w", pady=6)

        # Registration Link
        link_frame = ctk.CTkFrame(left, fg_color="white")
        link_frame.pack(anchor="w", pady=16)
        ctk.CTkLabel(link_frame, text="Don't have an Account?",
                     text_color=GRAY_TEXT, font=ctk.CTkFont(size=13)).pack(side="left")
        ctk.CTkButton(link_frame, text="Sign Up",
                      fg_color="transparent", hover_color="#F0F0F0",
                      text_color=PRIMARY_GREEN, font=ctk.CTkFont(size=13, weight="bold"),
                      width=70, command=self._go_signup).pack(side="left")

        # Right panel
        right = ctk.CTkFrame(content, fg_color=LIGHT_GREEN_BG, corner_radius=0, width=440)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        card = ctk.CTkFrame(right, fg_color="white", corner_radius=16, width=340, height=460)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        self._draw_hotel_illustration(card)

    def _draw_hotel_illustration(self, parent):
        canvas = tk.Canvas(parent, width=300, height=420, bg="white", highlightthickness=0)
        canvas.place(relx=0.5, rely=0.5, anchor="center")
        
        # Ground line
        canvas.create_line(30, 360, 270, 360, fill="#CCCCCC", width=2)
        
        # Main Building Body
        canvas.create_rectangle(85, 160, 215, 360, fill="#F0F0F0", outline="#CCCCCC", width=2)
        
        # Roof Sections
        canvas.create_rectangle(105, 115, 195, 165, fill="#E0E0E0", outline="#CCCCCC", width=1)
        canvas.create_rectangle(138, 88, 162, 118, fill="#DDDDDD", outline="#BBBBBB", width=1)
        
        # Windows
        for y in [180, 220, 260]:
            for x in [93, 127, 161]:
                canvas.create_rectangle(x, y, x+25, y+20, fill="#7B86E8", outline="#5A66D6", width=1)
        
        # Entrance Door
        canvas.create_rectangle(133, 310, 167, 360, fill="#2C2C2C", outline="#111111", width=1)
        
        # Decorative Trees/Lamps
        canvas.create_oval(30, 220, 80, 280, fill="white", outline="#AAAAAA", width=1)
        canvas.create_line(55, 280, 55, 360, fill="#AAAAAA", width=2)
        
        canvas.create_oval(220, 220, 270, 280, fill="white", outline="#AAAAAA", width=1)
        canvas.create_line(245, 280, 245, 360, fill="#AAAAAA", width=2)
        
        # Accent circle
        canvas.create_oval(225, 235, 265, 275, fill="#FF6B8A", outline="")

    def _do_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            self._show_message("Please enter both email and password.")
            return

        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)

            # --- Using RAW password comparison to match Signup Screen ---
            query = """
                SELECT user_id, username, role 
                FROM User 
                WHERE email = %s AND BINARY password_hash = %s AND is_active = TRUE
            """
            cursor.execute(query, (email, password))
            user = cursor.fetchone()

            if user:
                with open("session.txt", "w") as f:
                    f.write(str(user['user_id']))

                role = user['role']
                script_dir = os.path.dirname(__file__)
                
                if role == 'Admin':
                    target_script = "user_management_screen.py"
                elif role == 'Staff':
                    target_script = "staff_dashboard.py"
                else:  # Guest
                    target_script = "search_room_screen.py"

                self.destroy()
                subprocess.Popen([sys.executable, os.path.join(script_dir, target_script)])
            
            else:
                self._show_message("Invalid user credentials or account inactive.")

        except Error as e:
            self._show_message(f"Database Error: {e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def _clear_form(self):
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")

    def _show_message(self, msg):
        win = ctk.CTkToplevel(self)
        win.title("Notification")
        win.geometry("400x150")
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text=msg, wraplength=350).pack(pady=20)
        ctk.CTkButton(win, text="OK", width=100, command=win.destroy, fg_color=PRIMARY_GREEN).pack(pady=10)

    def _go_home(self):
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "landing_screen.py")])

    def _go_signup(self):
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "signup_screen.py")])

    def _go_forgot(self):
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "forgot_password_screen.py")])

if __name__ == "__main__":
    app = LoginScreen()
    app.mainloop()