import customtkinter as tk
from tkinter import messagebox


class App(tk.CTk):
    def __init__(self):
        super().__init__()
        self.window_config()

    def window_config(self):
        # Configure theme
        tk.set_appearance_mode("light")
        tk.set_default_color_theme("blue")  # Puedes usar: "blue", "green", "dark-blue"

        # Configure main window
        self.title("FitZone - Management System")
        self.geometry("1200x720")
        self.resizable(True, True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create a header that spans the entire top section
        self.header_frame = tk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=("#3a7ebf", "#1f538d"),  # Azul para destacarlo
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        # Ensure the header spans the entire width
        self.header_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.CTkLabel(
            self.header_frame,
            text="FITZONE",
            font=tk.CTkFont(size=28, weight="bold"),
            text_color="#ffffff",
        )
        title_label.pack(pady=(10, 5))

        subtitle_label = tk.CTkLabel(
            self.header_frame,
            text="Gym Management System",
            font=tk.CTkFont(size=14),
            text_color="#ffffff",
        )
        subtitle_label.pack(pady=(0, 10))

        self.main_frame = tk.CTkFrame(
            self, corner_radius=10, fg_color=("gray90", "gray16")
        )
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Login frame with shadow effect
        self.login_frame = tk.CTkFrame(
            self.main_frame,
            corner_radius=15,
            fg_color=("white", "gray17"),
            border_width=1,
            border_color=("gray75", "gray30"),
        )
        self.login_frame.pack(expand=True, padx=20, pady=20)

        # App icon/logo
        app_logo = tk.CTkLabel(
            self.login_frame,
            text="💪",  # You can replace this with an actual image
            font=tk.CTkFont(size=48),
        )
        app_logo.pack(pady=(30, 10))

        # Login title with modern font
        login_title = tk.CTkLabel(
            self.login_frame,
            text="Welcome Back",
            font=tk.CTkFont(size=24, weight="bold"),
        )
        login_title.pack(pady=(0, 5))

        login_subtitle = tk.CTkLabel(
            self.login_frame,
            text="Please enter your credentials",
            font=tk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        )
        login_subtitle.pack(pady=(0, 25))

        # Username with modern styling
        self.username_entry = tk.CTkEntry(
            self.login_frame,
            width=300,
            height=40,
            placeholder_text="Username",
            border_width=1,
            corner_radius=8,
        )
        self.username_entry.pack(pady=(0, 15), padx=40)

        # Password with modern styling
        self.password_entry = tk.CTkEntry(
            self.login_frame,
            width=300,
            height=40,
            placeholder_text="Password",
            show="•",
            border_width=1,
            corner_radius=8,
        )
        self.password_entry.pack(pady=(0, 25))

        # Login button with enhanced styling
        login_button = tk.CTkButton(
            self.login_frame,
            text="Sign In",
            width=300,
            height=40,
            corner_radius=8,
            font=tk.CTkFont(size=15, weight="bold"),
            hover_color=("#2b5f8f", "#144870"),
            fg_color=("#3a7ebf", "#1f538d"),
        )
        login_button.pack(pady=(0, 30))

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin":  # Temporary credentials
            messagebox.showinfo("Success", "Login successful!")
        else:
            messagebox.showerror("Error", "Invalid credentials")


if __name__ == "__main__":
    app = App()
    app.mainloop()
