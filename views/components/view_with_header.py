"""
Reusable component to display views with a header.
Used for screens like settings that need a consistent header.
"""
import customtkinter as ctk
from views.colors import COLORS


class ViewWithHeaderView(ctk.CTkFrame):
    """
    Reusable component that provides a consistent header for any view.
    """

    def __init__(self, master, title, description=None):
        super().__init__(master, fg_color="transparent")

        self.title = title
        self.description = description

        self._create_header()
        self._create_content_area()

    def _create_header(self):
        """Creates the header with title and optional description"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text=self.title,
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        )
        title_label.pack(anchor="w", pady=(0, 3) if self.description else (0, 0))

        # Only create description label if description is provided
        if self.description:
            description_label = ctk.CTkLabel(
                header_frame,
                text=self.description,
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_secondary"],
                anchor="w",
            )
            description_label.pack(anchor="w")

    def _create_content_area(self):
        """Creates the content area where any widget can be added"""
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=20, pady=(5, 15))

    def add_content(self, widget):
        """Allows adding content to the content area"""
        widget.pack(fill="both", expand=True, in_=self.content_area)
