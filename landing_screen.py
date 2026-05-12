import customtkinter as ctk
import subprocess
import sys
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Colors
PRIMARY_GREEN = "#5C8A3C"
LIGHT_GREEN_BG = "#F0F7EC"
YELLOW_BG = "#FAFAD2"
DARK_TEXT = "#2C3E50"
GRAY_TEXT = "#666666"


class LandingScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hotel Room and Banquet Hall Reservation System")
        self.geometry("960x860")
        self.configure(fg_color="white")
        self.resizable(True, True)
        self._build_ui()
        self.after(0, lambda: self.state('zoomed'))

    def _build_ui(self):
        # Main container
        main = ctk.CTkFrame(self, fg_color="white")
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # Top spacer
        ctk.CTkLabel(main, text="", fg_color="white", height=60).pack()

        # Title
        title = ctk.CTkLabel(
            main,
            text="Hotel Room and Banquet Hall\nReservation System",
            font=ctk.CTkFont(family="Georgia", size=38, weight="bold"),
            text_color=PRIMARY_GREEN,
            justify="center",
        )
        title.pack(pady=(0, 20))

        # Subtitle
        subtitle = ctk.CTkLabel(
            main,
            text="A comprehensive and user-friendly platform designed to simplify the management of\nhotel room reservations, banquet hall bookings, and administrative tasks.",
            font=ctk.CTkFont(size=15),
            text_color=GRAY_TEXT,
            justify="center",
        )
        subtitle.pack(pady=(0, 50))

        # Buttons container
        btn_frame = ctk.CTkFrame(main, fg_color="white")
        btn_frame.pack(pady=10)

        login_btn = ctk.CTkButton(
            btn_frame,
            text="Login  →",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=PRIMARY_GREEN,
            hover_color="#4a7230",
            text_color="white",
            width=420,
            height=55,
            corner_radius=8,
            command=self._go_login,
        )
        login_btn.pack(pady=8)

        signup_btn = ctk.CTkButton(
            btn_frame,
            text="Sign Up  👤",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=YELLOW_BG,
            hover_color="#e8e8b0",
            text_color=PRIMARY_GREEN,
            width=420,
            height=55,
            corner_radius=8,
            border_width=0,
            command=self._go_signup,
        )
        signup_btn.pack(pady=8)

        # Hotel illustration (SVG-style using canvas)
        self._draw_hotel(main)

    def _draw_hotel(self, parent):
        import tkinter as tk

        canvas = tk.Canvas(parent, width=420, height=320, bg="white", highlightthickness=0)
        canvas.pack(pady=20)

        # Ground line
        canvas.create_line(40, 290, 380, 290, fill="#CCCCCC", width=2)

        # Building body
        canvas.create_rectangle(130, 130, 290, 290, fill="#F0F0F0", outline="#CCCCCC", width=2)

        # Roof / top section
        canvas.create_rectangle(155, 90, 265, 135, fill="#E0E0E0", outline="#CCCCCC", width=1)

        # Chimney
        canvas.create_rectangle(200, 65, 220, 95, fill="#DDDDDD", outline="#BBBBBB", width=1)

        # Windows - row 1
        for x in [148, 192, 236]:
            canvas.create_rectangle(x, 150, x + 30, 175, fill="#7B86E8", outline="#5A66D6", width=1)

        # Windows - row 2
        for x in [148, 192, 236]:
            canvas.create_rectangle(x, 190, x + 30, 215, fill="#7B86E8", outline="#5A66D6", width=1)

        # Windows - row 3
        for x in [148, 192, 236]:
            canvas.create_rectangle(x, 230, x + 30, 255, fill="#7B86E8", outline="#5A66D6", width=1)

        # Door
        canvas.create_rectangle(193, 255, 227, 290, fill="#2C2C2C", outline="#111111", width=1)

        # Left tree (circle)
        canvas.create_oval(65, 170, 115, 230, fill="white", outline="#AAAAAA", width=1)
        canvas.create_line(90, 230, 90, 290, fill="#AAAAAA", width=2)
        # Arrow decorations on tree
        canvas.create_line(80, 270, 90, 258, fill="#AAAAAA", width=1)
        canvas.create_line(100, 270, 90, 258, fill="#AAAAAA", width=1)

        # Right tree
        canvas.create_oval(305, 170, 355, 230, fill="white", outline="#AAAAAA", width=1)
        canvas.create_line(330, 230, 330, 290, fill="#AAAAAA", width=2)
        canvas.create_line(320, 270, 330, 258, fill="#AAAAAA", width=1)
        canvas.create_line(340, 270, 330, 258, fill="#AAAAAA", width=1)

        # Pink circle decoration
        canvas.create_oval(60, 195, 105, 240, fill="#FF6B8A", outline="")

    def _go_login(self):
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "login_screen.py")])

    def _go_signup(self):
        self.destroy()
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "signup_screen.py")])


if __name__ == "__main__":
    app = LandingScreen()
    app.mainloop()