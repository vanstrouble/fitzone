"""
Welcome screen component for FitZone dashboard.
Displays an elegant welcome message as the initial view.
"""

import customtkinter as ctk
from views.colors import COLORS


class WelcomeView(ctk.CTkFrame):
    """
    Elegant welcome screen with prominent FitZone branding.
    Designed to be fast-loading and visually appealing.
    """

    def __init__(self, master, current_admin):
        super().__init__(master, fg_color="transparent")
        self.current_admin = current_admin
        self._create_welcome_content()

    def _create_welcome_content(self):
        """Create the centered welcome message with elegant styling"""
        # Main container that centers everything
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(expand=True, fill="both")

        # Center frame
        center_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Welcome text (smaller, subtle)
        welcome_label = ctk.CTkLabel(
            center_frame,
            text="Welcome to",
            font=ctk.CTkFont(size=32, weight="normal"),
            text_color=COLORS["text_secondary"],
        )
        welcome_label.pack(pady=(0, 5))

        # FitZone text (large, prominent)
        fitzone_label = ctk.CTkLabel(
            center_frame,
            text="FITZONE",
            font=ctk.CTkFont(size=72, weight="bold"),
            text_color=COLORS["primary"][0],
        )
        fitzone_label.pack(pady=(0, 20))

        # Subtitle with user name
        subtitle_label = ctk.CTkLabel(
            center_frame,
            text=f"Hello, {self.current_admin.username}!",
            font=ctk.CTkFont(size=20, weight="normal"),
            text_color=COLORS["text_secondary"],
        )
        subtitle_label.pack(pady=(0, 10))

        # Instruction text
        instruction_label = ctk.CTkLabel(
            center_frame,
            text="Select a section from the sidebar to get started",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_muted"] if "text_muted" in COLORS else COLORS["text_secondary"],
        )
        instruction_label.pack(pady=(0, 30))

        # Decorative element - subtle gradient effect with frames
        self._create_decorative_elements(center_frame)

    def _create_decorative_elements(self, parent):
        """Add subtle decorative elements for visual appeal"""
        # Container for decorative elements
        decoration_frame = ctk.CTkFrame(parent, fg_color="transparent")
        decoration_frame.pack(pady=20)

        # Create subtle decorative dots/elements
        dots_frame = ctk.CTkFrame(decoration_frame, fg_color="transparent")
        dots_frame.pack()

        # Three decorative dots
        for i in range(3):
            dot = ctk.CTkFrame(
                dots_frame,
                width=8,
                height=8,
                corner_radius=4,
                fg_color=COLORS["primary"][0],
            )
            dot.pack(side="left", padx=8)
            dot.pack_propagate(False)
