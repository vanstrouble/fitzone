import customtkinter as ctk
from crud import authenticate_admin
from views.colors import COLORS


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
