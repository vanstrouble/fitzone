import customtkinter as ctk
from controllers.crud import authenticate_admin
from views.colors import COLORS


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success

        # Focus state tracking for visual feedback
        self._username_focused = False
        self._password_focused = False

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
        self.username_entry.bind("<Return>", self.on_return_key)
        self.username_entry.bind("<FocusIn>", self._on_username_focus_in)
        self.username_entry.bind("<FocusOut>", self._on_username_focus_out)

        # Advanced keyboard shortcuts for username
        self._bind_username_shortcuts()

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
        self.password_entry.bind("<Return>", self.on_return_key)
        self.password_entry.bind("<FocusIn>", self._on_password_focus_in)
        self.password_entry.bind("<FocusOut>", self._on_password_focus_out)

        # Advanced keyboard shortcuts for password (only Cmd/Ctrl + Backspace)
        self._bind_password_shortcuts()

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

    def _bind_username_shortcuts(self):
        """Bind advanced keyboard shortcuts for username field"""
        import platform

        # Detect operating system for correct modifier keys
        is_mac = platform.system() == "Darwin"

        if is_mac:
            # macOS shortcuts
            self.username_entry.bind("<Command-BackSpace>", self._delete_username_to_beginning)
            self.username_entry.bind("<Option-BackSpace>", self._delete_username_word_backward)
        else:
            # Windows/Linux shortcuts
            self.username_entry.bind("<Control-BackSpace>", self._delete_username_word_backward)
            self.username_entry.bind(
                "<Control-Shift-BackSpace>",
                self._delete_username_to_beginning
            )

        # Universal shortcuts
        self.username_entry.bind("<Escape>", self._unfocus_username)
        self.username_entry.bind("<Control-a>", self._select_all_username)
        if is_mac:
            self.username_entry.bind("<Command-a>", self._select_all_username)

    def _bind_password_shortcuts(self):
        """Bind keyboard shortcuts for password field (only Cmd/Ctrl + Backspace)"""
        import platform

        # Detect operating system for correct modifier keys
        is_mac = platform.system() == "Darwin"

        if is_mac:
            # macOS shortcuts - only Cmd + Backspace for security
            self.password_entry.bind("<Command-BackSpace>", self._delete_password_to_beginning)
        else:
            # Windows/Linux shortcuts - only Ctrl + Shift + Backspace for security
            self.password_entry.bind(
                "<Control-Shift-BackSpace>",
                self._delete_password_to_beginning
            )

        # Universal shortcuts
        self.password_entry.bind("<Escape>", self._unfocus_password)

    # Focus event handlers for visual feedback
    def _on_username_focus_in(self, event):
        """Handle username field focus in - highlight the entry"""
        self._username_focused = True
        self._update_username_style()

    def _on_username_focus_out(self, event):
        """Handle username field focus out - remove highlight"""
        self._username_focused = False
        self._update_username_style()

    def _on_password_focus_in(self, event):
        """Handle password field focus in - highlight the entry"""
        self._password_focused = True
        self._update_password_style()

    def _on_password_focus_out(self, event):
        """Handle password field focus out - remove highlight"""
        self._password_focused = False
        self._update_password_style()

    def _update_username_style(self):
        """Update username field appearance based on focus state"""
        # Check if there's an error state (thick red border)
        current_border_width = self.username_entry.cget("border_width")
        current_border_color = self.username_entry.cget("border_color")

        # Don't override error state styling
        if current_border_width == 2 and current_border_color == COLORS["danger"][0]:
            return

        if self._username_focused:
            # Focused state - primary color border
            self.username_entry.configure(
                border_color=COLORS["primary"][0],
                border_width=1
            )
        else:
            # Normal state - default border
            self.username_entry.configure(
                border_color=("gray60", "gray40"),
                border_width=1
            )

    def _update_password_style(self):
        """Update password field appearance based on focus state"""
        # Check if there's an error state (thick red border)
        current_border_width = self.password_entry.cget("border_width")
        current_border_color = self.password_entry.cget("border_color")

        # Don't override error state styling
        if current_border_width == 2 and current_border_color == COLORS["danger"][0]:
            return

        if self._password_focused:
            # Focused state - primary color border
            self.password_entry.configure(
                border_color=COLORS["primary"][0],
                border_width=1
            )
        else:
            # Normal state - default border
            self.password_entry.configure(
                border_color=("gray60", "gray40"),
                border_width=1
            )

    # Advanced text editing methods for username
    def _delete_username_to_beginning(self, event):
        """Delete from cursor position to the beginning of username field"""
        cursor_pos = self.username_entry.index(ctk.INSERT)
        if cursor_pos > 0:
            self.username_entry.delete(0, cursor_pos)
        return "break"

    def _delete_username_word_backward(self, event):
        """Delete word backward from cursor position in username field"""
        text = self.username_entry.get()
        cursor_pos = self.username_entry.index(ctk.INSERT)

        if cursor_pos == 0:
            return "break"

        # Find the start of the current word
        start_pos = cursor_pos - 1

        # Skip whitespace
        while start_pos >= 0 and text[start_pos].isspace():
            start_pos -= 1

        # Find word boundary
        while start_pos >= 0 and not text[start_pos].isspace():
            start_pos -= 1

        start_pos += 1  # Move to the beginning of the word

        # Delete the word
        if start_pos < cursor_pos:
            self.username_entry.delete(start_pos, cursor_pos)

        return "break"

    def _delete_password_to_beginning(self, event):
        """Delete from cursor position to the beginning of password field"""
        cursor_pos = self.password_entry.index(ctk.INSERT)
        if cursor_pos > 0:
            self.password_entry.delete(0, cursor_pos)
        return "break"

    def _unfocus_username(self, event):
        """Unfocus the username field when Escape is pressed"""
        self.username_entry.master.focus()
        return "break"

    def _unfocus_password(self, event):
        """Unfocus the password field when Escape is pressed"""
        self.password_entry.master.focus()
        return "break"

    def _select_all_username(self, event):
        """Select all text in the username field"""
        self.username_entry.select_range(0, ctk.END)
        return "break"

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
            # Reset to normal style when successful
            self.username_entry.configure(border_width=1)
            self.password_entry.configure(border_width=1)
            self._update_username_style()
            self._update_password_style()
            self.on_login_success(admin)
        else:
            self.error_label.configure(text="Invalid credentials. Please try again.")
            # Make border thicker and red for error state
            self.username_entry.configure(
                border_color=COLORS["danger"][0],
                border_width=2
            )
            self.password_entry.configure(
                border_color=COLORS["danger"][0],
                border_width=2
            )
