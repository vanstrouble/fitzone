import customtkinter as ctk
from crud import ensure_default_admin_exists, authenticate_admin, is_admin

# Global color palette
COLORS = {
    "primary": ("#944388", "#7a3671"),  # Main color / darker variant
    "accent": ("#ECA66C", "#d99558"),  # Accent color for highlights / darker variant
    "danger": ("#D45276", "#b83d60"),  # Danger color for sign out / darker variant
    "neutral_bg": ("#f0f0f0", "#2a2a2a"),  # Background colors (light/dark mode)
    "neutral_fg": ("#e0e0e0", "#3a3a3a"),  # Foreground for frames
    "text_primary": ("#303030", "#e0e0e0"),  # Primary text color
    "text_secondary": ("#707070", "#a0a0a0"),  # Secondary text color
}


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
            text_color=COLORS["text_secondary"],
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
            text_color=COLORS["danger"],
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
            hover_color=COLORS["primary"][1],
            fg_color=COLORS["primary"][0],
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
            self.username_entry.configure(border_color=COLORS["danger"][0])
            self.password_entry.configure(border_color=COLORS["danger"][0])


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, current_admin, on_section_change, on_logout):
        super().__init__(
            master,
            width=200,  # Fixed width
            corner_radius=0,  # No rounded corners
            fg_color=("gray90", "gray20"),  # Sidebar background color
        )
        # Prevent the sidebar from resizing
        self.grid_propagate(False)
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

        # User avatar or icon as a clickable button
        avatar_button = ctk.CTkButton(
            profile_frame,
            text="👤",  # User icon emoji
            font=ctk.CTkFont(size=32),
            fg_color="transparent",  # Transparent background
            hover_color=COLORS["accent"],  # Accent color for hover
            text_color=COLORS["text_primary"],  # Match text color
            width=70,
            height=70,
            corner_radius=35,  # Make it circular
            command=self._on_profile_click,  # Add command to handle click
        )
        avatar_button.grid(row=0, column=0, pady=(5, 0))

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
            text_color=COLORS["text_secondary"],
        )
        role_label.grid(row=2, column=0, pady=(3, 8))

        # Separator line
        separator = ctk.CTkFrame(profile_frame, height=1, fg_color=("gray75", "gray45"))
        separator.grid(row=3, column=0, sticky="ew", pady=(10, 0))

    def _on_profile_click(self):
        """Handle when the user clicks on their profile avatar"""
        # Call the parent's content change method with the specific configuration section
        self.on_section_change(f"Configuration {self.current_admin.username}")

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
            corner_radius=6,  # Rounded corners for elegant look
            height=38,  # Slightly shorter buttons
            anchor="w",  # Left-aligned text
            fg_color=("gray85", "gray25"),  # Default background
            text_color=COLORS["text_primary"],  # Default text color
            hover_color=COLORS["accent"],  # Accent color for hover
            border_width=0,  # No border
            font=ctk.CTkFont(size=13),  # Slightly larger font
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
                    fg_color=COLORS["primary"],  # Primary background
                    text_color=("white", "white"),  # White text
                )
            else:
                # Unselected buttons - default style
                button.configure(
                    fg_color=("gray85", "gray25"),  # Default background
                    text_color=COLORS["text_primary"],  # Default text color
                )

        # Update the active section
        self.active_section = section

    def _create_logout_button(self, on_logout):
        sign_out_button = ctk.CTkButton(
            self,
            text="Sign Out",
            command=on_logout,
            fg_color=COLORS["danger"][0],  # Danger color
            hover_color=COLORS["danger"][1],  # Darker danger color on hover
            corner_radius=6,  # Match navigation buttons
            height=38,  # Match navigation buttons
            anchor="center",  # Center-aligned text as requested
            font=ctk.CTkFont(size=13, weight="bold"),  # Bold for emphasis
        )
        sign_out_button.grid(row=5, column=0, padx=15, pady=(20, 15), sticky="ews")


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, on_logout_callback, current_admin):
        # Use the main background color of the application instead of transparent
        super().__init__(master, fg_color=COLORS["neutral_bg"], corner_radius=0)
        self.current_admin = current_admin

        # Configure grid
        self.grid_columnconfigure(1, weight=1)  # Content takes remaining space
        self.grid_rowconfigure(0, weight=1)  # Single row with full height

        # Create Sidebar with the appropriate color
        self.sidebar = Sidebar(
            self,
            current_admin=current_admin,
            on_section_change=self.show_content,
            on_logout=on_logout_callback,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)  # No padding

        # Create Content Frame
        self._create_content_frame()

        # Show default content
        self._show_default_content()

    def _create_content_frame(self):
        # Change the background color of content_frame to match the general style
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,  # No rounded borders
            fg_color=COLORS["neutral_bg"],  # Use the same neutral background color
        )
        # Remove right padding to avoid gray space
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Main content with a lighter background to differentiate it
        content_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=8,  # Slightly rounded corners
            fg_color=("white", "gray17"),  # Light/dark background for the content
        )
        content_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_rowconfigure(0, weight=1)

        self.content_label = ctk.CTkLabel(
            content_container,  # Change the parent to the new container
            text="",
            font=ctk.CTkFont(size=24, weight="bold"),
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
        # Set the background color of the main application
        self.configure(fg_color=COLORS["neutral_bg"])

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.title("FitZone - Management System")

        # Set initial window size
        window_width = 1200
        window_height = 720
        self.geometry(f"{window_width}x{window_height}")

        # Set minimum window size to match the initial size
        self.minsize(window_width, window_height)

        # Allow resizing (maximize)
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["primary"][0],  # Use index 0 for light mode
            height=60,  # Fixed height for the header
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Force the header height
        self.header_frame.grid_propagate(False)

        title_label = ctk.CTkLabel(
            self.header_frame,
            text="FITZONE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white",  # Use direct value to ensure it's white
        )
        title_label.pack(pady=(10, 5))

        subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Gym Management System",
            font=ctk.CTkFont(size=14),
            text_color="white",  # Use direct value to ensure it's white
        )
        subtitle_label.pack(pady=(0, 10))

        # Remove rounded border and use the same background color for main_frame
        self.main_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color=COLORS["neutral_bg"]
        )
        self.main_frame.grid(
            row=1, column=0, sticky="nsew", padx=0, pady=0
        )  # No padding
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
