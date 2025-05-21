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


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, current_admin, on_section_change, on_logout):
        super().__init__(master, width=200, corner_radius=0)
        self.on_section_change = on_section_change
        self.current_admin = current_admin

        # Track the active section and buttons
        self.active_section = None
        self.nav_buttons = {}

        # Configure grid
        self.grid_columnconfigure(0, weight=1)  # Make column expand to fill width
        self.grid_rowconfigure(4, weight=1)

        # User Profile Section
        self._create_user_profile()

        # Navigation Buttons
        self._create_navigation_buttons(current_admin)

        # Logout Button
        self._create_logout_button(on_logout)

    def _create_user_profile(self):
        # Profile container
        profile_frame = ctk.CTkFrame(self, fg_color="transparent")
        profile_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 20))
        profile_frame.grid_columnconfigure(0, weight=1)

        # User avatar or icon (using an emoji as placeholder)
        avatar_label = ctk.CTkLabel(
            profile_frame,
            text="👤",  # User icon emoji
            font=ctk.CTkFont(size=32),
        )
        avatar_label.grid(row=0, column=0, pady=(5, 0))

        # Username (in uppercase)
        username_label = ctk.CTkLabel(
            profile_frame,
            text=self.current_admin.username.upper(),
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        username_label.grid(row=1, column=0, pady=(5, 0))

        # Role as a subtle subtitle (not a button)
        role_label = ctk.CTkLabel(
            profile_frame,
            text=self.current_admin.role.capitalize(),
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color=("gray40", "gray60"),
        )
        role_label.grid(row=2, column=0, pady=(3, 8))

        # Separator line
        separator = ctk.CTkFrame(
            profile_frame,
            height=1,
            fg_color=("gray75", "gray45")
        )
        separator.grid(row=3, column=0, sticky="ew", pady=(10, 0))

    def _create_navigation_buttons(self, current_admin):
        next_button_row = 1

        # Admin button (conditional)
        if current_admin and is_admin(current_admin.username):
            self._create_button("Admins", next_button_row)
            next_button_row += 1

        # Other buttons
        self._create_button("Trainers", next_button_row)
        next_button_row += 1

        self._create_button("Users", next_button_row)
        return next_button_row

    def _create_button(self, text, row):
        button = ctk.CTkButton(
            self,
            text=text.upper(),
            command=lambda section=text: self._on_button_click(section),
            corner_radius=6,             # Rounded corners for elegant look
            height=38,                   # Slightly shorter buttons
            anchor="w",                  # Left-aligned text
            fg_color=("gray85", "gray25"),  # Default background
            text_color=("gray10", "gray90"),  # Default text color
            hover_color=("#3a7ebf", "#1f538d"),  # Blue hover effect
            border_width=0,              # No border
            font=ctk.CTkFont(size=13),   # Slightly larger font
        )
        button.grid(row=row, column=0, padx=15, pady=(7, 0), sticky="ew")

        # Store the button reference for later use
        self.nav_buttons[text] = button

        return button

    def _on_button_click(self, section):
        # Update active section and button appearances
        self.set_active_section(section)
        # Call the original callback
        self.on_section_change(section)

    def set_active_section(self, section):
        """Set the active section and update button appearances"""
        # Reset all buttons to default style
        for name, button in self.nav_buttons.items():
            if name == section:
                # Selected button - highlight it
                button.configure(
                    fg_color=("#3a7ebf", "#1f538d"),  # Blue background
                    text_color=("white", "white"),    # White text
                )
            else:
                # Unselected buttons - default style
                button.configure(
                    fg_color=("gray85", "gray25"),    # Default background
                    text_color=("gray10", "gray90"),  # Default text color
                )

        # Update the active section
        self.active_section = section

    def _create_logout_button(self, on_logout):
        sign_out_button = ctk.CTkButton(
            self,
            text="Sign Out",
            command=on_logout,
            fg_color="red",              # Keep distinctive red color
            hover_color="#c00000",       # Darker red on hover
            corner_radius=6,             # Match navigation buttons
            height=38,                   # Match navigation buttons
            anchor="center",             # Center-aligned text as requested
            font=ctk.CTkFont(size=13, weight="bold"),  # Bold for emphasis
        )
        sign_out_button.grid(row=5, column=0, padx=15, pady=(20, 15), sticky="ews")


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, on_logout_callback, current_admin):
        super().__init__(master)
        self.current_admin = current_admin

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create Sidebar
        self.sidebar = Sidebar(
            self,
            current_admin=current_admin,
            on_section_change=self.show_content,
            on_logout=on_logout_callback,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # Create Content Frame
        self._create_content_frame()

        # Show default content
        self._show_default_content()

    def _create_content_frame(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.content_label = ctk.CTkLabel(
            self.content_frame, text="", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.content_label.grid(row=0, column=0, padx=20, pady=20)

    def _show_default_content(self):
        default_section = (
            "Admins" if is_admin(self.current_admin.username) else "Trainers"
        )
        self.show_content(default_section)

    def show_content(self, section_name):
        self.content_label.configure(text=f"{section_name} Content")

        # Update sidebar active section
        self.sidebar.set_active_section(section_name)


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
