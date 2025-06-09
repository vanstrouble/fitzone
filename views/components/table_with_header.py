"""
Reusable component to display tables with a header.
Applies the DRY (Don't Repeat Yourself) Principle - eliminates code duplication.
"""
import customtkinter as ctk
from views.data_table import DataTable
from views.colors import COLORS


class TableWithHeaderView(ctk.CTkFrame):
    """
    Reusable component that combines a header with title/description and a table.
    This eliminates code duplication in dashboard views.
    """

    def __init__(self, master, title, description, headers, data, column_weights, table_name):
        super().__init__(master, fg_color="transparent")

        # Store configuration
        self.title = title
        self.description = description
        self.headers = headers
        self.data = data
        self.column_weights = column_weights
        self.table_name = table_name

        self._create_header()
        self._create_table()

    def _create_header(self):
        """Creates the header with title and description"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.title,
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        )
        title_label.pack(anchor="w", pady=(0, 3))

        # Description
        description_label = ctk.CTkLabel(
            header_frame,
            text=self.description,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        description_label.pack(anchor="w")

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

    def update_data(self, new_data):
        """Updates the table data without recreating the entire component"""
        self.data = new_data
        # Recreate only the table
        self.table.destroy()
        self._create_table()
