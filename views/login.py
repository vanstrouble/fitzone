import customtkinter as ctk
from controllers.crud import authenticate_admin
from views.colors import COLORS, set_palette, get_current_palette, get_palette_names


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=COLORS["primary"][0])
        self.on_login_success = on_login_success

        # Create palette switcher button (top right)
        self.palette_button = ctk.CTkButton(
            self,
            text="🎨",
            width=40,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=18),
            fg_color=COLORS["accent"][0],
            hover_color=COLORS["accent"][1],
            text_color="white",
            command=self._switch_palette,
        )
        self.palette_button.place(relx=0.95, y=30, anchor="ne")

        # Login form container
        self.form_container = ctk.CTkFrame(
            self,
            width=400,
            height=450,
            corner_radius=16,
            fg_color=COLORS["neutral_fg"],
            border_width=2,
            border_color=COLORS["accent"][0],
        )
        self.form_container.pack(pady=(50, 40), padx=20, expand=True)
        self.form_container.pack_propagate(False)

        # App branding
        self.app_logo = ctk.CTkLabel(
            self.form_container,
            text="🦾",
            font=ctk.CTkFont(size=48),
        )
        self.app_logo.pack(pady=(30, 5))

        self.brand_label = ctk.CTkLabel(
            self.form_container,
            text="FitZone",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["primary"][0],
        )
        self.brand_label.pack(pady=(0, 20))

        # Form header
        self.login_title = ctk.CTkLabel(
            self.form_container,
            text="Welcome Back",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        self.login_title.pack(pady=(0, 5))

        self.login_subtitle = ctk.CTkLabel(
            self.form_container,
            text="Please enter your credentials",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        )
        self.login_subtitle.pack(pady=(0, 25))

        # Form fields
        self.username_entry = ctk.CTkEntry(
            self.form_container,
            width=320,
            height=45,
            placeholder_text="Email or Username",
            border_width=2,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            border_color=COLORS["text_secondary"],
            fg_color=COLORS["neutral_bg"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_secondary"],
        )
        self.username_entry.pack(pady=(0, 15))
        self.username_entry.bind("<Return>", self._on_enter_key)

        self.password_entry = ctk.CTkEntry(
            self.form_container,
            width=320,
            height=45,
            placeholder_text="Password",
            show="•",
            border_width=2,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            border_color=COLORS["text_secondary"],
            fg_color=COLORS["neutral_bg"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_secondary"],
        )
        self.password_entry.pack(pady=(0, 10))
        self.password_entry.bind("<Return>", self._on_enter_key)

        # Error label
        self.error_label = ctk.CTkLabel(
            self.form_container,
            text="",
            text_color=COLORS["danger"],
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.error_label.pack(pady=(0, 15))

        # Login button
        self.login_button = ctk.CTkButton(
            self.form_container,
            text="Sign In",
            width=320,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=16, weight="bold"),
            hover_color=COLORS["primary"][1],
            fg_color=COLORS["primary"][0],
            text_color="white",
            command=self.validate_login,
        )
        self.login_button.pack(pady=(0, 30))

        # Footer
        self.footer_text = ctk.CTkLabel(
            self,
            text="Secure gym management system",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        )
        self.footer_text.pack(side="bottom", pady=20)

    def _switch_palette(self):
        """Switch between available color palettes"""
        palettes = get_palette_names()
        current = get_current_palette()

        # Find next palette
        try:
            current_index = palettes.index(current)
            next_index = (current_index + 1) % len(palettes)
            new_palette = palettes[next_index]
        except ValueError:
            new_palette = palettes[0]

        # Set new palette and refresh colors
        set_palette(new_palette)
        self._refresh_colors()

        # Refresh app header
        try:
            app_instance = self.winfo_toplevel()
            if hasattr(app_instance, "refresh_header_colors"):
                app_instance.refresh_header_colors()
        except Exception:
            pass

    def _refresh_colors(self):
        """Refresh all UI components with new color palette"""
        # Update main background
        self.configure(fg_color=COLORS["primary"][0])

        # Update form container
        self.form_container.configure(
            fg_color=COLORS["neutral_fg"], border_color=COLORS["accent"][0]
        )

        # Update labels
        self.brand_label.configure(text_color=COLORS["primary"][0])
        self.login_title.configure(text_color=COLORS["text_primary"])
        self.login_subtitle.configure(text_color=COLORS["text_secondary"])
        self.footer_text.configure(text_color=COLORS["text_secondary"])

        # Update entry fields
        self.username_entry.configure(
            border_color=COLORS["text_secondary"],
            fg_color=COLORS["neutral_bg"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_secondary"],
        )

        self.password_entry.configure(
            border_color=COLORS["text_secondary"],
            fg_color=COLORS["neutral_bg"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_secondary"],
        )

        # Update buttons
        self.login_button.configure(
            hover_color=COLORS["primary"][1], fg_color=COLORS["primary"][0]
        )

        self.palette_button.configure(
            fg_color=COLORS["accent"][0], hover_color=COLORS["accent"][1]
        )

        # Update error label
        self.error_label.configure(text_color=COLORS["danger"])

    def _on_enter_key(self, event=None):
        """Handle Enter key press in either field"""
        if self.username_entry.get() and self.password_entry.get():
            self.validate_login()
        elif not self.username_entry.get():
            self.username_entry.focus_set()
        elif not self.password_entry.get():
            self.password_entry.focus_set()
        return "break"

    def validate_login(self):
        """Validate user credentials"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text="Please enter both username and password")
            return

        admin = authenticate_admin(username, password)
        if admin:
            self.error_label.configure(text="")
            self.on_login_success(admin)
        else:
            self.error_label.configure(text="Invalid credentials. Please try again.")
            # Highlight fields with error
            self.username_entry.configure(border_color=COLORS["danger"][0])
            self.password_entry.configure(border_color=COLORS["danger"][0])
