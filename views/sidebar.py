import customtkinter as ctk
from crud import is_admin
from views.colors import COLORS


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
