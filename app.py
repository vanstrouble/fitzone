"""
FitZone - Gym Management System
Main application entry point
"""

import customtkinter as ctk
from controllers.crud import ensure_default_admin_exists
from views.login import LoginFrame
from views.dashboard import DashboardFrame
from views.colors import COLORS


class App(ctk.CTk):
    """Main application class for FitZone gym management system"""

    def __init__(self):
        super().__init__()
        ensure_default_admin_exists()
        self.current_admin = None
        self._setup_window()
        self._create_header()
        self._create_main_frame()
        self.show_login()

    def _setup_window(self):
        """Configure main window properties"""
        # Appearance and theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Window properties
        self.title("FitZone - Management System")
        self.configure(fg_color=COLORS["neutral_bg"])

        # Size and position
        window_width, window_height = 1200, 720
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(window_width, window_height)
        self.resizable(True, True)

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _create_header(self):
        """Create the application header"""
        self.header_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["primary"][0],
            height=60,
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.header_frame,
            text="FITZONE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white",
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            self.header_frame,
            text="Gym Management System",
            font=ctk.CTkFont(size=14),
            text_color="white",
        ).pack(pady=(0, 10))

    def refresh_header_colors(self):
        """Refresh header colors when palette changes"""
        if hasattr(self, "header_frame"):
            self.header_frame.configure(fg_color=COLORS["primary"][0])

    def _create_main_frame(self):
        """Create the main content frame"""
        self.main_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color=COLORS["neutral_bg"]
        )
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def show_login(self):
        """Display the login screen"""
        self._clear_main_frame()
        LoginFrame(self.main_frame, self.on_login_success).pack(
            expand=True, fill="both"
        )

    def show_dashboard(self):
        """Display the main dashboard"""
        self._clear_main_frame()
        DashboardFrame(self.main_frame, self.on_logout, self.current_admin).pack(
            expand=True, fill="both"
        )

    def on_login_success(self, admin):
        """Handle successful login"""
        self.current_admin = admin
        self.show_dashboard()

    def on_logout(self):
        """Handle user logout"""
        self.current_admin = None
        self.show_login()

    def _clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()


def main():
    """Main entry point of the application"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
