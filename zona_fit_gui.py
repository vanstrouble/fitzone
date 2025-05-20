import customtkinter as ctk
from crud import ensure_default_admin_exists, authenticate_admin, is_admin


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success

        # App icon/logo
        app_logo = ctk.CTkLabel(
            self,
            text="💪",
            font=ctk.CTkFont(size=48),
        )
        app_logo.pack(pady=(30, 10))

        login_title = ctk.CTkLabel(
            self,
            text="Welcome Back",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        login_title.pack(pady=(0, 5))

        login_subtitle = ctk.CTkLabel(
            self,
            text="Please enter your credentials",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60"),
        )
        login_subtitle.pack(pady=(0, 25))

        self.username_entry = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            placeholder_text="Username",
            border_width=1,
            corner_radius=8,
        )
        self.username_entry.pack(pady=(0, 15), padx=40)

        self.password_entry = ctk.CTkEntry(
            self,
            width=300,
            height=40,
            placeholder_text="Password",
            show="•",
            border_width=1,
            corner_radius=8,
        )
        self.password_entry.pack(pady=(0, 25))

        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.error_label.pack(pady=(0, 5))

        login_button = ctk.CTkButton(
            self,
            text="Sign In",
            width=300,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=15, weight="bold"),
            hover_color=("#2b5f8f", "#144870"),
            fg_color=("#3a7ebf", "#1f538d"),
            command=self.validate_login,
        )
        login_button.pack(pady=(0, 30))

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        admin = authenticate_admin(username, password)
        if admin:
            self.error_label.configure(text="")
            self.username_entry.configure(border_color="gray")
            self.password_entry.configure(border_color="gray")
            self.on_login_success(admin)
        else:
            self.error_label.configure(text="Invalid credentials. Please try again.")
            self.username_entry.configure(border_color="red")
            self.password_entry.configure(border_color="red")


class DashboardFrame(ctk.CTkFrame):
    def __init__(
        self, master, on_logout_callback, current_admin
    ):  # Added current_admin
        super().__init__(master)
        self.on_logout_callback = on_logout_callback
        self.current_admin = current_admin  # Store the logged-in admin

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(
            4, weight=1
        )  # Push sign out button to bottom

        sidebar_title = ctk.CTkLabel(
            self.sidebar_frame, text="Menu", font=ctk.CTkFont(size=20, weight="bold")
        )
        sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        next_button_row = 1

        # Conditionally show Admins button using is_admin check
        if self.current_admin and is_admin(self.current_admin.username):
            admins_button = ctk.CTkButton(
                self.sidebar_frame,
                text="Admins",
                command=lambda: self.show_content("Admins"),
            )
            admins_button.grid(
                row=next_button_row, column=0, padx=20, pady=10, sticky="ew"
            )
            next_button_row += 1

        trainers_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Trainers",
            command=lambda: self.show_content("Trainers"),
        )
        trainers_button.grid(
            row=next_button_row, column=0, padx=20, pady=10, sticky="ew"
        )
        next_button_row += 1

        users_button = ctk.CTkButton(
            self.sidebar_frame, text="Users", command=lambda: self.show_content("Users")
        )
        users_button.grid(row=next_button_row, column=0, padx=20, pady=10, sticky="ew")
        # next_button_row += 1 # Not needed before sign_out_button at fixed row 5

        sign_out_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Sign Out",
            command=self.on_logout_callback,
            fg_color="red",
            hover_color="#c00000",
        )
        sign_out_button.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="ews")

        # Content Frame
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.content_label = ctk.CTkLabel(
            self.content_frame, text="", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.content_label.grid(row=0, column=0, padx=20, pady=20)

        # Show default content
        if self.current_admin and is_admin(self.current_admin.username):
            self.show_content("Admins")
        else:
            # If Admins section is not available, default to Trainers or another appropriate section
            self.show_content("Trainers")

    def show_content(self, section_name):
        self.content_label.configure(text=f"{section_name} Content")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ensure_default_admin_exists()
        self.current_admin = None
        self.window_config()
        self.show_login()

    def window_config(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.title("FitZone - Management System")
        self.geometry("1200x720")
        self.resizable(True, True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=("#3a7ebf", "#1f538d"),
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self.header_frame,
            text="FITZONE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#ffffff",
        )
        title_label.pack(pady=(10, 5))

        subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Gym Management System",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff",
        )
        subtitle_label.pack(pady=(0, 10))

        self.main_frame = ctk.CTkFrame(
            self, corner_radius=10, fg_color=("gray90", "gray16")
        )
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_main_frame()
        self.current_admin = None  # Clear current admin on logout
        login_frame = LoginFrame(self.main_frame, self.on_login_success)
        login_frame.pack(expand=True, fill="both")

    def on_login_success(self, admin):
        self.current_admin = admin
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_main_frame()
        # Pass the current_admin to DashboardFrame
        dashboard_frame = DashboardFrame(
            self.main_frame, self.logout, self.current_admin
        )
        dashboard_frame.pack(expand=True, fill="both")

    def logout(self):
        self.show_login()


if __name__ == "__main__":
    app = App()
    app.mainloop()
