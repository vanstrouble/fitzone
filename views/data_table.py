import customtkinter as ctk
from views.colors import COLORS


class DataTable(ctk.CTkFrame):
    """Reusable data table component with fixed headers and scrollable content"""

    def __init__(
        self, master, headers, data, column_weights=None, table_name=None, **kwargs
    ):
        super().__init__(master, fg_color=("white", "gray17"), **kwargs)

        # Validations
        self._validate_inputs(headers, data, column_weights)

        # Store parameters
        self.headers = headers
        self.data = data
        self.column_weights = column_weights or [1] * len(headers)
        self.table_name = table_name or "Unknown"

        # Selection tracking - optimized with tuple (table_name, item_id)
        self.selection = None  # ("table_name", "item_id") or None for deselection
        self.row_widgets = {}

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create table components
        self._create_table()

    def _validate_inputs(self, headers, data, column_weights):
        """Validate input parameters"""
        if not headers:
            raise ValueError("Headers cannot be empty")

        if data and len(data[0]) != len(headers):
            raise ValueError(
                f"Data columns ({len(data[0])}) must match headers ({len(headers)})"
            )

        if column_weights and len(column_weights) != len(headers):
            raise ValueError("Column weights must match headers")

        # Validate all data rows have same number of columns
        for i, row in enumerate(data):
            if len(row) != len(headers):
                raise ValueError(
                    f"Row {i} has {len(row)} columns, expected {len(headers)}"
                )

    def _create_table(self):
        """Create the table structure with fixed headers and scrollable content"""
        # Fixed header frame with primary color gradient
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["primary"][1])
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 2))

        # Configure header columns
        for col_idx, weight in enumerate(self.column_weights):
            minsize = 60 if weight == 1 else (120 if weight >= 3 else 100)
            header_frame.grid_columnconfigure(col_idx, weight=weight, minsize=minsize)

        # Create header labels with professional gradient
        for col_idx, header in enumerate(self.headers):
            # Primary color for first column (ID), gradient for others
            if col_idx == 0:
                header_bg = COLORS["primary"][0]
            else:
                header_bg = COLORS["primary"][1]

            header_label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=header_bg,
                text_color=("white", "white"),
                corner_radius=6,
                height=35,
            )
            header_label.grid(row=0, column=col_idx, sticky="ew", padx=2, pady=2)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["neutral_fg"],
            corner_radius=6,
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Configure scrollable frame columns (same as header)
        for col_idx, weight in enumerate(self.column_weights):
            minsize = 60 if weight == 1 else (120 if weight >= 3 else 100)
            self.scrollable_frame.grid_columnconfigure(
                col_idx, weight=weight, minsize=minsize
            )

        # Populate data
        self._populate_data()

    def _populate_data(self):
        """Populate the scrollable frame with data"""
        # Clear existing data
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.row_widgets.clear()

        # Create data rows
        for row_idx, row_data in enumerate(self.data):
            self.row_widgets[row_idx] = []

            for col_idx, cell_data in enumerate(row_data):
                # Professional alternating row colors using our color palette
                if row_idx % 2 == 0:
                    # Even rows - lighter neutral tones
                    bg_color = ("white", COLORS["neutral_fg"][1])
                else:
                    # Odd rows - subtle contrast
                    bg_color = (COLORS["neutral_bg"][0], "gray20")

                # Special highlighting for first column (ID) with accent color hints
                if col_idx == 0:
                    if row_idx % 2 == 0:
                        bg_color = ("#f8f5ff", "gray28")  # Subtle primary tint
                    else:
                        bg_color = ("#f0ebf7", "gray23")  # Slightly darker primary tint

                cell_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text=str(cell_data),
                    font=ctk.CTkFont(size=13),
                    fg_color=bg_color,
                    corner_radius=4,
                    height=30,
                )
                cell_label.grid(
                    row=row_idx, column=col_idx, sticky="ew", padx=2, pady=1
                )

                # Make cell clickable
                cell_label.bind(
                    "<Button-1>", lambda e, idx=row_idx: self._select_row(idx)
                )

                # Store widget reference
                self.row_widgets[row_idx].append(cell_label)

    def _select_row(self, row_idx):
        """Universal row selection handler - optimized with tuple storage"""
        # Get current selection info
        current_selection = self._get_row_from_selection()

        # Deselect previous row if exists
        if current_selection is not None:
            self._restore_row_colors(current_selection)

        # Select new row
        if row_idx == current_selection:
            # Deselect if clicking same row
            self.selection = None
            print(f"{self.table_name} row deselected")
        else:
            # Store selection as optimized tuple (table, id)
            item_id = str(self.data[row_idx][0])
            self.selection = (self.table_name, item_id)

            # Highlight selected row
            selected_widgets = self.row_widgets[row_idx]
            for widget in selected_widgets:
                widget.configure(fg_color=COLORS["accent"])

            # Print selection info using tuple elements
            table_name, selected_id = self.selection
            print(f"{table_name} selected: ID={selected_id}")

    def _get_row_from_selection(self):
        """Get row index from current selection tuple - used internally"""
        if not self.selection:
            return None

        _, selected_id = self.selection
        # Find row index by matching ID (first column)
        for idx, row in enumerate(self.data):
            if str(row[0]) == selected_id:
                return idx
        return None

    def get_selection(self):
        """Get current selection as tuple (table_name, item_id) or None"""
        return self.selection

    def get_selected_id(self):
        """Get the ID of the currently selected item"""
        return self.selection[1] if self.selection else None

    def get_selected_table(self):
        """Get the name of this table"""
        return self.selection[0] if self.selection else self.table_name

    def get_selection_info(self):
        """Get complete selection information - backward compatibility"""
        if not self.selection:
            return {
                "table_name": self.table_name,
                "selected_id": None,
                "selected_row": None,
                "selected_data": None,
            }

        table_name, selected_id = self.selection
        selected_row = self._get_row_from_selection()

        return {
            "table_name": table_name,
            "selected_id": selected_id,
            "selected_row": selected_row,
            "selected_data": (
                self.data[selected_row] if selected_row is not None else None
            ),
        }

    def _restore_row_colors(self, row_idx):
        """Restore original colors for a row"""
        old_row_widgets = self.row_widgets[row_idx]
        for col_idx, widget in enumerate(old_row_widgets):
            # Restore original color based on the same logic as _populate_data
            if row_idx % 2 == 0:
                # Even rows - lighter neutral tones
                original_color = ("white", COLORS["neutral_fg"][1])
            else:
                # Odd rows - subtle contrast
                original_color = (COLORS["neutral_bg"][0], "gray20")

            # Special highlighting for first column (ID) with accent color hints
            if col_idx == 0:
                if row_idx % 2 == 0:
                    original_color = ("#f8f5ff", "gray28")  # Subtle primary tint
                else:
                    original_color = (
                        "#f0ebf7",
                        "gray23",
                    )  # Slightly darker primary tint

            widget.configure(fg_color=original_color)

    def update_data(self, new_data):
        """Update table data and refresh display"""
        self._validate_inputs(self.headers, new_data, self.column_weights)
        self.data = new_data
        self.selection = None  # Clear selection with optimized tuple approach
        self._populate_data()

    def get_selected_data(self):
        """Get the currently selected row data - computed when needed"""
        if not self.selection:
            return None

        selected_row = self._get_row_from_selection()
        if selected_row is not None and selected_row < len(self.data):
            return self.data[selected_row]
        return None
