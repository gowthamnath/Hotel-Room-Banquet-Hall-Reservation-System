import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
import subprocess
import sys
import os
import re  # Required for password validation

# Use the same DB_CONFIG from your other screens
DB_CONFIG = {
    "host": "141.209.241.57",
    "port": 3306,
    "user": "putch1v",
    "password": "mypass",
    "database": "BIS698MSpring26Group_2"
}

class ForgotPasswordScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Reset Password - Security Verification")
        self.geometry("1000x700")
        self.configure(fg_color="white")
        self.after(0, lambda: self.state('zoomed'))
        
        # Data storage for the session
        self.user_data = None 
        
        self._build_ui()

    def _build_ui(self):
        # Navbar (Simplified)
        nav = ctk.CTkFrame(self, fg_color="white", height=70, corner_radius=0)
        nav.pack(fill="x")
        ctk.CTkLabel(nav, text="🏨 Hotel System - Recovery", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=20)
        ctk.CTkButton(nav, text="← Back to Login", fg_color="#5C8A3C", command=self._go_login).pack(side="right", padx=20, pady=15)

        # Main Container
        self.container = ctk.CTkFrame(self, fg_color="white")
        self.container.pack(fill="both", expand=True)
        
        # Show the first step
        self._show_step_1_find_email()
    
    def _toggle_password_visibility(self):
        show_value = "" if self.show_password_var.get() else "*"
        self.new_pass.configure(show=show_value)
        self.confirm_pass.configure(show=show_value)

    def _show_step_1_find_email(self):
        self._clear_container()
        card = self._create_card()
        
        ctk.CTkLabel(card, text="Find Your Account", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(card, text="Enter your registered email to begin.", text_color="gray").pack()

        self.email_input = ctk.CTkEntry(card, placeholder_text="Email Address", width=350, height=45)
        self.email_input.pack(pady=30)

        ctk.CTkButton(card, text="Verify Email", fg_color="#5C8A3C", height=45, width=350, 
                      command=self._verify_email_exists).pack(pady=10)

    def _verify_email_exists(self):
        email = self.email_input.get().strip()
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
            self.user_data = cursor.fetchone()
            conn.close()

            if self.user_data:
                self._show_step_2_security_questions()
            else:
                messagebox.showerror("Error", "No account found with that email.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _show_step_2_security_questions(self):
        self._clear_container()
        card = self._create_card()
        
        ctk.CTkLabel(card, text="Security Verification", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        # Question 1
        ctk.CTkLabel(card, text=f"Q1: {self.user_data['security_question_1']}", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=40)
        self.ans1 = ctk.CTkEntry(card, placeholder_text="Your Answer", width=350, height=40)
        self.ans1.pack(pady=(5, 15))

        # Question 2
        ctk.CTkLabel(card, text=f"Q2: {self.user_data['security_question_2']}", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=40)
        self.ans2 = ctk.CTkEntry(card, placeholder_text="Your Answer", width=350, height=40)
        self.ans2.pack(pady=(5, 20))

        ctk.CTkButton(card, text="Check Answers", fg_color="#5C8A3C", height=45, width=350, 
                      command=self._verify_answers).pack()

    def _verify_answers(self):
        # Direct string comparison
        match1 = self.ans1.get().strip().lower() == str(self.user_data['security_answer_1_hash']).lower()
        match2 = self.ans2.get().strip().lower() == str(self.user_data['security_answer_2_hash']).lower()

        if match1 and match2:
            self._show_step_3_new_password()
        else:
            messagebox.showerror("Security Failed", "Answers do not match our records.")

    def _show_step_3_new_password(self):
        self._clear_container()
        card = self._create_card()

        ctk.CTkLabel(card, text="Create New Password", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        self.new_pass = ctk.CTkEntry(card, placeholder_text="New Password", show="*", width=350, height=45)
        self.new_pass.pack(pady=10)

        self.confirm_pass = ctk.CTkEntry(card, placeholder_text="Confirm New Password", show="*", width=350, height=45)
        self.confirm_pass.pack(pady=10)

        # Show Password Checkbox
        self.show_password_var = ctk.BooleanVar()
        ctk.CTkCheckBox(card, text="Show Password", variable=self.show_password_var, command=self._toggle_password_visibility).pack(pady=(5, 10))

        ctk.CTkButton(card, text="Reset Password", fg_color="#5C8A3C", height=45, width=350, command=self._update_password_in_db).pack(pady=20)

    def _update_password_in_db(self):
        p1 = self.new_pass.get()
        p2 = self.confirm_pass.get()

        # 1. Basic matching and empty check
        if p1 != p2 or not p1:
            messagebox.showerror("Error", "Passwords do not match or are empty.")
            return

        # 2. Complexity Rules (Same as Signup)
        has_upper = re.search(r"[A-Z]", p1)
        has_num_or_spec = re.search(r"[0-9!@#$%^&*(),.?\":{}|<>]", p1)

        if len(p1) < 8 or not has_upper or not has_num_or_spec:
            messagebox.showerror("Weak Password", 
                                 "The password must contain minimum 8 characters, "
                                 "one capital letter, and one numeric value or special character.")
            return

        # 3. Database Update
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET password_hash = %s WHERE user_id = %s", (p1, self.user_data['user_id']))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Password updated successfully! Please login.")
            self._go_login()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    # Helper Utilities
    def _create_card(self):
        card = ctk.CTkFrame(self.container, fg_color="white", border_width=1, border_color="#C8E6C9", width=450, height=500)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)
        return card

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _go_login(self):
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "login_screen.py")])

if __name__ == "__main__":
    app = ForgotPasswordScreen()
    app.mainloop()