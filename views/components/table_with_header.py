"""
Reusable component to display tables with a header.
Applies the DRY (Don't Repeat Yourself) Principle - eliminates code duplication.
"""

import customtkinter as ctk
from views.data_table import DataTable
from views.colors import COLORS
from views.components.search_bar import SearchBar


class TableWithHeaderView(ctk.CTkFrame):
    """
    Reusable component that combines a header with title/description and a table.
    This eliminates code duplication in dashboard views.
    """

    def __init__(
        self, master, title, description, headers, data, column_weights, table_name, controller=None
    ):
        super().__init__(master, fg_color="transparent")

        # Store configuration
        self.title = title
        self.description = description
        self.headers = headers
        self.data = data
        self.column_weights = column_weights
        self.table_name = table_name
        self.controller = controller  # Dashboard controller for filtering

        self._create_header()
        self._create_table()

    def _create_header(self):
        """Creates the header with title and description"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Configure grid for left and right alignment
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        # Left side - Title and description
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w")

        # Title
        title_label = ctk.CTkLabel(
            left_frame,
            text=self.title,
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        )
        title_label.pack(anchor="w", pady=(0, 3))

        # Description
        description_label = ctk.CTkLabel(
            left_frame,
            text=self.description,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        description_label.pack(anchor="w")

        # Right side - Search bar
        self.search_bar = SearchBar(
            header_frame,
            on_search_callback=self._on_search,
            placeholder_text="Search...",
            width=250,
            height=35,
        )
        self.search_bar.grid(row=0, column=1, sticky="e", padx=(20, 0))

    def _create_table(self):
        """Creates the data table"""
        self.table = DataTable(
            self,
            headers=self.headers,
            data=self.data,
            column_weights=self.column_weights,
            table_name=self.table_name,
        )
        self.table.pack(fill="both", expand=True, padx=20, pady=(5, 15))

    def _on_search(self, query):
        """Handle search functionality using controller's intelligent cache"""
        if self.controller:
            # Use controller's optimized filtering with cache
            filtered_data = self.controller.filter_data(self.table_name.lower(), query)
            self.data = filtered_data

            # Update the table with filtered data
            self.table.destroy()
            self._create_table()
        else:
            # Fallback: basic local filtering (for backward compatibility)
            pass

    def update_data(self, new_data):
        """Updates the table data without recreating the entire component"""
        self.data = new_data
        # Recreate only the table
        self.table.destroy()
        self._create_table()
