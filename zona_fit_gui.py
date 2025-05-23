import customtkinter as ctk
from crud import (
    ensure_default_admin_exists,
    authenticate_admin,
    is_admin,
    get_all_admins,
)

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
            text="🦾",
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

        # Bind key events for username field
        self.username_entry.bind("<Command-BackSpace>", self.clear_username)
        self.username_entry.bind("<Return>", self.on_return_key)

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

        # Bind key events for password field
        self.password_entry.bind("<Command-BackSpace>", self.clear_password)
        self.password_entry.bind("<Return>", self.on_return_key)

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

    def clear_username(self, event=None):
        """Clear the username entry field"""
        self.username_entry.delete(0, "end")
        return "break"  # Prevent default behavior

    def clear_password(self, event=None):
        """Clear the password entry field"""
        self.password_entry.delete(0, "end")
        return "break"  # Prevent default behavior

    def on_return_key(self, event=None):
        """Handle Return/Enter key press in either field"""
        # Check if both fields have content
        if self.username_entry.get() and self.password_entry.get():
            self.validate_login()
        elif not self.username_entry.get():
            # If username is empty, focus on it
            self.username_entry.focus_set()
        elif not self.password_entry.get():
            # If password is empty, focus on it
            self.password_entry.focus_set()
        return "break"  # Prevent default behavior

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
        self.content_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=8,  # Slightly rounded corners
            fg_color=("white", "gray17"),  # Light/dark background for the content
        )
        self.content_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

    def _show_default_content(self):
        default_section = (
            "Admins" if is_admin(self.current_admin.username) else "Trainers"
        )
        self.show_content(default_section)

    def show_content(self, section_name):
        # Check if this is a configuration section
        if section_name.startswith("Configuration "):
            username = section_name.split(" ", 1)[1]
            self._show_user_configuration(username)
        else:
            # Clear previous content
            for widget in self.content_container.winfo_children():
                widget.destroy()

            # Update sidebar active section
            self.sidebar.set_active_section(section_name)

            # Show the appropriate content based on section_name
            if section_name == "Admins":
                self._show_admins_table()
            elif section_name == "Trainers":
                self._show_trainers_table()
            elif section_name == "Users":
                self._show_users_table()
            else:
                # Fallback for unknown sections
                self.content_label = ctk.CTkLabel(
                    self.content_container,
                    text=f"{section_name} Content",
                    font=ctk.CTkFont(size=24, weight="bold"),
                )
                self.content_label.grid(row=0, column=0, padx=20, pady=20)

    def _show_admins_table(self):
        self._create_table_view(
            section_name="Admins",
            title="Admin Users",
            description="View and manage system administrators",
            headers=["ID", "Username", "Role", "Created At"],
            data_func=get_all_admins,
        )

    def _show_trainers_table(self):
        # Note: Using None instead of get_all_trainers since it's not imported
        self._create_table_view(
            section_name="Trainers",
            title="Trainers",
            description="View and manage gym trainers",
            headers=["ID", "Name", "Specialty", "Schedule", "Created At"],
            data_func=None,
            empty_data=[],
        )

    def _show_users_table(self):
        # Note: Using None instead of get_all_users since it's not imported
        self._create_table_view(
            section_name="Users",
            title="Gym Users",
            description="View and manage gym members",
            headers=["ID", "Name", "Membership", "Renovation Date", "Created At"],
            data_func=None,
            empty_data=[],
        )

    def _create_table_view(
        self, section_name, title, description, headers, data_func, empty_data=None
    ):
        """
        Create a standard table view for different sections (Admins, Trainers, Users)

        Parameters:
        - section_name: The name of the section (e.g., "Admins", "Trainers", "Users")
        - title: The title to display
        - description: Description text to show below the title
        - headers: List of column headers for the table
        - data_func: Function to get data or None to use empty_data
        - empty_data: Default empty data if data_func is None
        """
        # Clear previous content
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Configure row weights to make the table expand vertically
        self.content_container.grid_rowconfigure(0, weight=0)  # Title - fixed height
        self.content_container.grid_rowconfigure(
            1, weight=0
        )  # Description - fixed height
        self.content_container.grid_rowconfigure(
            2, weight=1
        )  # Table - takes remaining space
        self.content_container.grid_rowconfigure(3, weight=0)  # Buttons - fixed height

        # Create a title
        title_label = ctk.CTkLabel(
            self.content_container,
            text=title,
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.grid(
            row=0, column=0, padx=20, pady=(20, 5), sticky="w"
        )  # Reduced bottom padding

        # Create description
        description_label = ctk.CTkLabel(
            self.content_container,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        )
        description_label.grid(
            row=1, column=0, padx=20, pady=(0, 10), sticky="w"
        )  # Reduced bottom padding

        # Get data
        items = data_func() if data_func else empty_data or []

        # Format data for the table based on section_name
        table_data = self._format_table_data(section_name, items)

        # Create reusable table with headers and data
        table = TableFrame(self.content_container, headers=headers, data=table_data)
        table.grid(
            row=2, column=0, padx=20, pady=(0, 10), sticky="nsew"
        )  # Make table fill available space

        # Add action buttons below the table
        buttons_frame = ctk.CTkFrame(
            self.content_container,
            fg_color="transparent",
        )
        buttons_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="e")

        # Add button
        add_button = ctk.CTkButton(
            buttons_frame,
            text=(
                f"Add {section_name[:-1]}"
                if section_name.endswith("s")
                else f"Add {section_name}"
            ),
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["primary"][0],
            hover_color=COLORS["primary"][1],
            corner_radius=6,
            height=32,
            width=120,
            command=getattr(self, f"_show_add_{section_name.lower()[:-1]}_form"),
        )
        add_button.grid(row=0, column=0, padx=(0, 10))

        # Refresh button
        refresh_button = ctk.CTkButton(
            buttons_frame,
            text="Refresh",
            font=ctk.CTkFont(size=13),
            fg_color=("gray80", "gray30"),
            hover_color=("gray70", "gray40"),
            corner_radius=6,
            height=32,
            width=100,
            command=lambda: self.show_content(section_name),
        )
        refresh_button.grid(row=0, column=1)

    def _format_table_data(self, section_name, items):
        """Format data for the table based on section name"""
        table_data = []

        if not items:
            return table_data

        if section_name == "Admins":
            for admin in items:
                # Format created_at date
                created_at_text = self._format_date(admin.created_at)

                # Create role badge data
                role_badge = {
                    "type": "badge",
                    "text": admin.role,
                    "color": (
                        COLORS["primary"] if admin.role == "admin" else COLORS["accent"]
                    ),
                }

                table_data.append(
                    [str(admin.unique_id), admin.username, role_badge, created_at_text]
                )

        elif section_name == "Trainers":
            for trainer in items:
                created_at_text = self._format_date(trainer.created_at)

                table_data.append(
                    [
                        str(trainer.unique_id),
                        f"{trainer.name} {trainer.lastname}",
                        trainer.specialty,
                        f"{trainer.start_time} - {trainer.end_time}",
                        created_at_text,
                    ]
                )

        elif section_name == "Users":
            for user in items:
                table_data.append(
                    [
                        str(user.unique_id),
                        f"{user.name} {user.lastname}",
                        user.membership_type,
                        user.renovation_date,
                        self._format_date(user.created_at),
                    ]
                )

        return table_data

    def _format_date(self, date_value):
        """Format date consistently across all tables"""
        if not date_value:
            return "N/A"

        if isinstance(date_value, str):
            return date_value
        else:
            # If it's a datetime object
            return date_value.strftime("%Y-%m-%d %H:%M")

    def _show_add_admin_form(self):
        # Create a dialog or replace the table view with a form
        # For now, we'll just print a message
        print("Add admin functionality to be implemented")

    def _show_user_configuration(self, username):
        # Clear previous content
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Create a title
        title_label = ctk.CTkLabel(
            self.content_container,
            text=f"User Configuration: {username}",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=20, pady=20)

        # Configuration content would go here

    def _show_add_trainer_form(self):
        # To be implemented
        print("Add trainer functionality to be implemented")

    def _show_add_user_form(self):
        # To be implemented
        print("Add user functionality to be implemented")


class TableFrame(ctk.CTkFrame):
    """A reusable table component that can display data in rows and columns"""

    def __init__(
        self,
        master,
        headers,
        data=None,
        row_height=30,
        header_color=None,
        row_color=None,
        min_height=300,  # Added minimum height parameter
    ):
        super().__init__(
            master,
            fg_color=("gray95", "gray20"),
            corner_radius=6,
        )

        self.headers = headers
        self.data = data or []
        self.row_height = row_height
        self.header_color = header_color or ("gray90", "gray25")
        self.row_color = row_color or ("white", "gray20")
        self.min_height = min_height

        # Set minimum height
        self.configure(height=min_height)

        # Prevent resizing smaller than minimum height
        self.grid_propagate(False)

        # Configure column weights
        for i in range(len(headers)):
            self.grid_columnconfigure(i, weight=1)

        # Configure row weights to fill vertical space
        self.grid_rowconfigure(
            2, weight=1
        )  # Make the "no data" or table content row expandable

        # Create the table
        self._create_table()

    def _create_table(self):
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Create headers
        for i, header in enumerate(self.headers):
            header_label = ctk.CTkLabel(
                self,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            header_label.grid(row=0, column=i, padx=10, pady=(10, 5), sticky="w")

        # Add a separator line
        separator = ctk.CTkFrame(self, height=1, fg_color=("gray75", "gray45"))
        separator.grid(
            row=1, column=0, columnspan=len(self.headers), sticky="ew", padx=10
        )

        if not self.data:
            no_data_label = ctk.CTkLabel(
                self,
                text="No data found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"],
            )
            no_data_label.grid(
                row=2,
                column=0,
                columnspan=len(self.headers),
                padx=20,
                pady=20,
                sticky="n",
            )

            # Add an empty frame to fill the space
            spacer = ctk.CTkFrame(self, fg_color="transparent")
            spacer.grid(row=3, column=0, columnspan=len(self.headers), sticky="nsew")
            self.grid_rowconfigure(3, weight=1)
            return

        # Add data rows
        for row_idx, row_data in enumerate(self.data, start=2):
            self._add_row(row_idx, row_data)

        # If there are few rows, add a spacer to fill the remaining space
        if len(self.data) < 5:  # Arbitrary threshold for "few rows"
            spacer = ctk.CTkFrame(self, fg_color="transparent")
            spacer.grid(
                row=len(self.data) + 2,
                column=0,
                columnspan=len(self.headers),
                sticky="nsew",
            )
            self.grid_rowconfigure(len(self.data) + 2, weight=1)

    def _add_row(self, row_idx, row_data):
        """Add a row of data to the table"""
        for col_idx, cell_data in enumerate(row_data):
            # Skip None values
            if cell_data is None:
                continue

            # Check if the cell data is a dictionary with special rendering
            if isinstance(cell_data, dict) and "type" in cell_data:
                if cell_data["type"] == "badge":
                    # Create a badge (label with background color)
                    badge_frame = ctk.CTkFrame(
                        self,
                        fg_color=cell_data.get("color", COLORS["primary"]),
                        corner_radius=4,
                        height=22,
                    )
                    badge_frame.grid(
                        row=row_idx, column=col_idx, padx=10, pady=5, sticky="w"
                    )

                    badge_label = ctk.CTkLabel(
                        badge_frame,
                        text=str(cell_data.get("text", "")).upper(),
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color="white",
                    )
                    badge_label.grid(row=0, column=0, padx=8, pady=0)
                elif cell_data["type"] == "button":
                    # Create a button
                    button = ctk.CTkButton(
                        self,
                        text=cell_data.get("text", "Button"),
                        font=ctk.CTkFont(size=12),
                        command=cell_data.get("command"),
                        fg_color=cell_data.get("color", COLORS["primary"][0]),
                        hover_color=cell_data.get("hover_color", COLORS["primary"][1]),
                        corner_radius=4,
                        height=24,
                        width=60,
                    )
                    button.grid(
                        row=row_idx, column=col_idx, padx=10, pady=5, sticky="w"
                    )
            else:
                # Regular text cell
                cell_label = ctk.CTkLabel(
                    self,
                    text=str(cell_data),
                    font=ctk.CTkFont(size=13),
                )
                cell_label.grid(
                    row=row_idx, column=col_idx, padx=10, pady=5, sticky="w"
                )

    def update_data(self, data):
        """Update the table with new data"""
        self.data = data
        self._create_table()


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
