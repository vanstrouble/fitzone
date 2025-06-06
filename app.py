"""
FitZone - Gym Management System
Main application entry point
"""
import customtkinter as ctk
from crud import ensure_default_admin_exists
from views.login import LoginFrame
from views.dashboard import DashboardFrame
from views.colors import COLORS


class App(ctk.CTk):
    """Main application class for FitZone gym management system"""

    def __init__(self):
        super().__init__()
        ensure_default_admin_exists()
        self.current_admin = None
        self.window_config()
        self.show_login()

    def window_config(self):
        """Configure main window properties and layout"""
        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Window configuration
        self.title("FitZone - Management System")
        self.configure(fg_color=COLORS["neutral_bg"])

        # Set window size
        window_width = 1200
        window_height = 720
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(window_width, window_height)
        self.resizable(True, True)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create header
        self._create_header()

        # Create main content area
        self._create_main_frame()

    def _create_header(self):
        """Create the application header with title and branding"""
        self.header_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["primary"][0],
            height=60,
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self.header_frame,
            text="FITZONE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white",
        )
        title_label.pack(pady=(10, 5))

        subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Gym Management System",
            font=ctk.CTkFont(size=14),
            text_color="white",
        )
        subtitle_label.pack(pady=(0, 10))

    def _create_main_frame(self):
        """Create the main content frame"""
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["neutral_bg"]
        )
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_login(self):
        """Display the login screen"""
        self.clear_main_frame()
        login_frame = LoginFrame(self.main_frame, self.on_login_success)
        login_frame.pack(expand=True, fill="both")

    def on_login_success(self, admin):
        """Handle successful login"""
        self.current_admin = admin
        self.show_dashboard()

    def show_dashboard(self):
        """Display the main dashboard"""
        self.clear_main_frame()
        dashboard_frame = DashboardFrame(
            self.main_frame, self.on_logout, self.current_admin
        )
        dashboard_frame.pack(expand=True, fill="both")

    def on_logout(self):
        """Handle user logout"""
        self.current_admin = None
        self.show_login()


def main():
    """Main entry point of the application"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
