"""
Reusable and stylish search bar component.
"""

import customtkinter as ctk
from views.colors import COLORS
from typing import Callable, Optional


class SearchBar(ctk.CTkFrame):
    """Stylish and reusable search bar"""

    def __init__(
        self,
        master,
        on_search_callback: Optional[Callable] = None,
        placeholder_text: str = "Search...",
        width: int = 300,
        height: int = 40,
    ):
        super().__init__(master, fg_color="transparent")

        self.on_search_callback = on_search_callback
        self.placeholder_text = placeholder_text
        self.width = width
        self.height = height

        self._create_search_bar()

    def _create_search_bar(self):
        """Create the search bar"""
        # Main container
        self.search_container = ctk.CTkFrame(
            self,
            width=self.width,
            height=self.height,
            fg_color=("white", "gray20"),
            border_width=1,
            border_color=("gray70", "gray30"),
            corner_radius=20,
        )
        self.search_container.pack(fill="both", expand=True)
        self.search_container.pack_propagate(False)

        # Search entry
        self.search_entry = ctk.CTkEntry(
            self.search_container,
            placeholder_text=self.placeholder_text,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=0,
            height=self.height - 4,
        )
        self.search_entry.pack(
            side="left", fill="both", expand=True, padx=(15, 5), pady=2
        )

        # Search icon
        self.search_icon = ctk.CTkLabel(
            self.search_container,
            text="🔍",
            font=ctk.CTkFont(size=16),
            width=30,
            text_color=("gray50", "gray60"),
        )
        self.search_icon.pack(side="right", padx=(5, 15))

        # Bind events
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        self.search_entry.bind("<Return>", self._on_search_enter)

    def _on_search_change(self, event):
        """Handle changes in the search text"""
        query = self.search_entry.get().strip()
        if self.on_search_callback:
            self.on_search_callback(query)

    def _on_search_enter(self, event):
        """Handle Enter key"""
        query = self.search_entry.get().strip()
        if self.on_search_callback:
            self.on_search_callback(query)

    def get_search_query(self) -> str:
        """Get the current search text"""
        return self.search_entry.get().strip()

    def clear_search(self):
        """Clear the search"""
        self.search_entry.delete(0, "end")
        if self.on_search_callback:
            self.on_search_callback("")

    def focus(self):
        """Focus the search bar"""
        self.search_entry.focus()

    def set_placeholder(self, text: str):
        """Change the placeholder text"""
        self.search_entry.configure(placeholder_text=text)
