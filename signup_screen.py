import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
import subprocess
import sys
import os
import re

# Theme Configuration
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

PRIMARY_GREEN = "#5C8A3C"
YELLOW_BG = "#FAFAD2"
DARK_TEXT = "#2C3E50"

class GuestSignupScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hotel Reservation System - Guest Sign Up")
        self.geometry("960x950")
        self.configure(fg_color="white")
        self.after(0, lambda: self.state('zoomed'))
        
        self.questions = [
            "What was the name of your first pet?",
            "In what city were you born?",
            "What was the name of your elementary school?",
            "What is your mother's maiden name?",
            "What was the make of your first car?",
            "What is your favorite book?"
        ]
        
        self.db_config = {
            'host': '141.209.241.57',
            'port': 3306,
            'user': 'putch1v',
            'password': 'mypass',
            'database': 'BIS698MSpring26Group_2'
        }
        
        self._build_ui()

    def _build_ui(self):
        navbar = ctk.CTkFrame(self, fg_color="white", height=70, corner_radius=0)
        navbar.pack(fill="x", side="top")
        navbar.pack_propagate(False)

        logo_frame = ctk.CTkFrame(navbar, fg_color=PRIMARY_GREEN, width=48, height=48, corner_radius=10)
        logo_frame.pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(logo_frame, text="🏨", font=ctk.CTkFont(size=22)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(navbar, text="Hotel Reservation System",
                     font=ctk.CTkFont(size=17, weight="bold"), text_color=DARK_TEXT).pack(side="left", padx=8)

        back_btn = ctk.CTkButton(navbar, text="← Back to Home",
                                 fg_color=PRIMARY_GREEN, hover_color="#4a7230",
                                 text_color="white", width=150, height=38,
                                 corner_radius=8, command=self._go_home)
        back_btn.pack(side="right", padx=20, pady=15)

        ctk.CTkFrame(self, fg_color="#E0E0E0", height=1, corner_radius=0).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(self, fg_color="white")
        scroll.pack(fill="both", expand=True)

        card = ctk.CTkFrame(scroll, fg_color=YELLOW_BG, corner_radius=16)
        card.pack(padx=80, pady=40, fill="x")

        ctk.CTkLabel(card, text="Guest Sign Up",
                     font=ctk.CTkFont(family="Georgia", size=32, weight="bold"),
                     text_color=DARK_TEXT).pack(pady=(30, 25))

        form = ctk.CTkFrame(card, fg_color=YELLOW_BG)
        form.pack(padx=40, pady=(0, 20), fill="x")

        def make_row(parent, labels_placeholders):
            row = ctk.CTkFrame(parent, fg_color=YELLOW_BG)
            row.pack(fill="x", pady=10)
            entries = []
            for i, (label, placeholder) in enumerate(labels_placeholders):
                col = ctk.CTkFrame(row, fg_color=YELLOW_BG)
                col.pack(side="left", fill="x", expand=True, padx=(0, 10 if i < len(labels_placeholders)-1 else 0))
                ctk.CTkLabel(col, text=label, font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=PRIMARY_GREEN).pack(anchor="w")
                
                is_password = "password" in label.lower()
                entry = ctk.CTkEntry(col, placeholder_text=placeholder,
                                     height=44, corner_radius=8,
                                     border_color="#CCCCCC", border_width=1,
                                     fg_color="white", font=ctk.CTkFont(size=13),
                                     show="•" if is_password else "")
                entry.pack(fill="x", pady=(4, 0))
                entries.append(entry)
            return entries

        r1 = make_row(form, [("First Name", "Enter first name"), ("Last Name", "Enter last name")])
        self.first_name, self.last_name = r1

        r2 = make_row(form, [("Username", "Choose a unique username"), ("Email Address", "email@example.com")])
        self.username, self.email = r2

        r3_frame = ctk.CTkFrame(form, fg_color=YELLOW_BG)
        r3_frame.pack(fill="x", pady=10)
        
        phone_col = ctk.CTkFrame(r3_frame, fg_color=YELLOW_BG)
        phone_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(phone_col, text="Phone Number", font=ctk.CTkFont(size=13, weight="bold"), text_color=PRIMARY_GREEN).pack(anchor="w")
        self.phone = ctk.CTkEntry(phone_col, placeholder_text="10-13 digits", height=44, corner_radius=8, fg_color="white")
        self.phone.pack(fill="x", pady=(4, 0))

        id_type_col = ctk.CTkFrame(r3_frame, fg_color=YELLOW_BG)
        id_type_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(id_type_col, text="ID Proof Type", font=ctk.CTkFont(size=13, weight="bold"), text_color=PRIMARY_GREEN).pack(anchor="w")
        self.id_type = ctk.CTkOptionMenu(id_type_col, values=["Passport", "Driver's License", "State ID"], 
                                       height=44, corner_radius=8, fg_color=PRIMARY_GREEN, button_color="#4a7230")
        self.id_type.pack(fill="x", pady=(4, 0))
        self.id_type.set("Passport")

        r4 = make_row(form, [("Password", "Create password"), ("Confirm Password", "Repeat password")])
        self.password, self.confirm_password = r4

        # Show Password Toggle Checkbox
        self.show_pwd_var = ctk.StringVar(value="off")
        self.show_pwd_check = ctk.CTkCheckBox(
            form, text="Show Password", variable=self.show_pwd_var,
            onvalue="on", offvalue="off", command=self._toggle_password,
            font=ctk.CTkFont(size=12), text_color=DARK_TEXT,
            fg_color=PRIMARY_GREEN, hover_color="#4a7230",
            checkbox_width=18, checkbox_height=18
        )
        self.show_pwd_check.pack(anchor="w", pady=(5, 10))

        addr_frame = ctk.CTkFrame(form, fg_color=YELLOW_BG)
        addr_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(addr_frame, text="Full Address", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=PRIMARY_GREEN).pack(anchor="w")
        self.address = ctk.CTkEntry(addr_frame, placeholder_text="Street address, Apartment, Suite",
                                    height=44, corner_radius=8, border_color="#CCCCCC", border_width=1,
                                    fg_color="white", font=ctk.CTkFont(size=13))
        self.address.pack(fill="x", pady=(4, 0))

        r5 = make_row(form, [("City", "Enter city"), ("Country", "Enter country"), ("ID Number", "Enter ID number")])
        self.city, self.country, self.id_number = r5

        sec_label = ctk.CTkLabel(form, text="Security Recovery Setup", 
                                 font=ctk.CTkFont(size=16, weight="bold"), text_color=DARK_TEXT)
        sec_label.pack(anchor="w", pady=(20, 10))

        q1_row = ctk.CTkFrame(form, fg_color=YELLOW_BG)
        q1_row.pack(fill="x", pady=5)
        q1_col = ctk.CTkFrame(q1_row, fg_color=YELLOW_BG)
        q1_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(q1_col, text="Security Question 1", font=ctk.CTkFont(size=13, weight="bold"), text_color=PRIMARY_GREEN).pack(anchor="w")
        self.q1_dropdown = ctk.CTkOptionMenu(q1_col, values=self.questions, height=44, fg_color=PRIMARY_GREEN)
        self.q1_dropdown.pack(fill="x", pady=(4, 0))
        self.q1_dropdown.set(self.questions[0])

        ans1_col = ctk.CTkFrame(q1_row, fg_color=YELLOW_BG)
        ans1_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(ans1_col, text="Answer 1", font=ctk.CTkFont(size=13, weight="bold"), text_color=PRIMARY_GREEN).pack(anchor="w")
        self.a1_entry = ctk.CTkEntry(ans1_col, placeholder_text="Your answer", height=44, fg_color="white")
        self.a1_entry.pack(fill="x", pady=(4, 0))

        q2_row = ctk.CTkFrame(form, fg_color=YELLOW_BG)
        q2_row.pack(fill="x", pady=5)
        q2_col = ctk.CTkFrame(q2_row, fg_color=YELLOW_BG)
        q2_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(q2_col, text="Security Question 2", font=ctk.CTkFont(size=13, weight="bold"), text_color=PRIMARY_GREEN).pack(anchor="w")
        self.q2_dropdown = ctk.CTkOptionMenu(q2_col, values=self.questions, height=44, fg_color=PRIMARY_GREEN)
        self.q2_dropdown.pack(fill="x", pady=(4, 0))
        self.q2_dropdown.set(self.questions[1])

        ans2_col = ctk.CTkFrame(q2_row, fg_color=YELLOW_BG)
        ans2_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(ans2_col, text="Answer 2", font=ctk.CTkFont(size=13, weight="bold"), text_color=PRIMARY_GREEN).pack(anchor="w")
        self.a2_entry = ctk.CTkEntry(ans2_col, placeholder_text="Your answer", height=44, fg_color="white")
        self.a2_entry.pack(fill="x", pady=(4, 0))

        btn_row = ctk.CTkFrame(card, fg_color=YELLOW_BG)
        btn_row.pack(padx=40, pady=(20, 40), fill="x")

        signup_btn = ctk.CTkButton(btn_row, text="Create Account 🧑",
                                   fg_color=PRIMARY_GREEN, hover_color="#4a7230",
                                   text_color="white", width=260, height=52,
                                   command=self._do_signup)
        signup_btn.pack(side="left", pady=5)

        clear_btn = ctk.CTkButton(btn_row, text="Clear Form ✕",
                                  fg_color="transparent", hover_color="#e8e8b0",
                                  text_color=PRIMARY_GREEN, width=120, height=52,
                                  command=self._clear_form)
        clear_btn.pack(side="left", padx=20, pady=5)

    def _toggle_password(self):
        if self.show_pwd_var.get() == "on":
            self.password.configure(show="")
            self.confirm_password.configure(show="")
        else:
            self.password.configure(show="•")
            self.confirm_password.configure(show="•")

    def _do_signup(self):
        data = {
            "uname": self.username.get().strip(),
            "email": self.email.get().strip(),
            "fname": self.first_name.get().strip(),
            "lname": self.last_name.get().strip(),
            "phone": self.phone.get().strip(),
            "pwd": self.password.get().strip(),
            "cpwd": self.confirm_password.get().strip(),
            "id_t": self.id_type.get(),
            "id_n": self.id_number.get().strip(),
            "addr": self.address.get().strip(),
            "city": self.city.get().strip(),
            "country": self.country.get().strip(),
            "a1": self.a1_entry.get().strip(),
            "a2": self.a2_entry.get().strip()
        }

        if not all(data.values()):
            self._show_message("Error", "Please fill all the details to create an account.")
            return

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data["email"]):
            self._show_message("Invalid Format", "Please enter a valid email address. Example: John@gmail.com")
            return

        phone_digits = re.sub(r'\D', '', data["phone"])
        if not (10 <= len(phone_digits) <= 13):
            self._show_message("Invalid Phone", "Phone number must be between 10 and 13 digits.")
            return

        has_upper = re.search(r"[A-Z]", data["pwd"])
        has_num_or_spec = re.search(r"[0-9!@#$%^&*(),.?\":{}|<>]", data["pwd"])
        if len(data["pwd"]) < 8 or not has_upper or not has_num_or_spec:
            self._show_message("Weak Password", "Password must be minimum 8 characters with atleast one capital and a number/special character.")
            return

        if data["pwd"] != data["cpwd"]:
            self._show_message("Error", "Passwords do not match!")
            return

        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            sql = """INSERT INTO User (username, password_hash, email, first_name, last_name, phone, role, 
                     id_proof_type, id_proof_number, address, city, country, security_question_1, 
                     security_answer_1_hash, security_question_2, security_answer_2_hash, is_active, created_at) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"""
            
            val = (data["uname"], data["pwd"], data["email"], data["fname"], data["lname"], 
                   data["phone"], 'Guest', data["id_t"], data["id_n"], data["addr"], 
                   data["city"], data["country"], self.q1_dropdown.get(), data["a1"], 
                   self.q2_dropdown.get(), data["a2"], True)
            
            cursor.execute(sql, val)
            connection.commit()
            
            self._show_message("Success", "Account created! Redirecting...")
            self.after(2000, lambda: self._go_login(data["email"]))
        except Error as e:
            self._show_message("Error", f"Database Error: {e}")
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def _clear_form(self):
        entries = [self.username, self.email, self.first_name, self.last_name, self.phone, 
                   self.password, self.confirm_password, self.id_number, self.address, 
                   self.city, self.country, self.a1_entry, self.a2_entry]
        for entry in entries: entry.delete(0, "end")
        self.id_type.set("Passport")
        self.show_pwd_var.set("off")
        self.password.configure(show="•")
        self.confirm_password.configure(show="•")

    def _show_message(self, title, msg):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("400x200")
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text=msg, wraplength=350).pack(pady=20, padx=20)
        ctk.CTkButton(win, text="OK", command=win.destroy, fg_color=PRIMARY_GREEN).pack(pady=10)

    def _go_home(self):
        self.destroy()
        subprocess.Popen([sys.executable, "landing_screen.py"])

    def _go_login(self, email=""):
        self.destroy()
        subprocess.Popen([sys.executable, "login_screen.py", email])

if __name__ == "__main__":
    app = GuestSignupScreen()
    app.mainloop()