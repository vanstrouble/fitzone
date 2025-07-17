import customtkinter as ctk
from views.colors import COLORS


class CRUDButtons(ctk.CTkFrame):
    def __init__(
        self,
        master=None,
        table=None,
        on_add=None,
        on_update=None,
        on_delete=None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.table = table
        self.on_add = on_add
        self.on_update = on_update
        self.on_delete = on_delete
        self._create_buttons()
        self._update_buttons_visibility()
        if self.table is not None:
            self.table.bind("<<SelectionChanged>>", self._on_selection_change)
            self._poll_selection()

    def _create_buttons(self):
        self.btn_delete = ctk.CTkButton(
            self,
            text="Delete",
            fg_color=COLORS["danger"][0],
            hover_color=COLORS["danger"][1],
            text_color="white",
            corner_radius=6,
            height=38,
            anchor="center",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_delete_click,
        )
        self.btn_update = ctk.CTkButton(
            self,
            text="Update",
            fg_color=COLORS["accent"][0],
            hover_color=COLORS["accent"][1],
            text_color="#303030",
            corner_radius=6,
            height=38,
            anchor="center",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_update_click,
        )
        self.btn_add = ctk.CTkButton(
            self,
            text="Add",
            fg_color=COLORS["primary"][0],
            hover_color=COLORS["primary"][1],
            text_color="white",
            corner_radius=6,
            height=38,
            anchor="center",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_add_click,
        )
        # Solo empacamos Add por defecto, los otros se empacan según selección
        # Sin padx en el botón Add para alinearlo correctamente con la tabla
        self.btn_add.pack(side="right", padx=0)

    def _update_buttons_visibility(self):
        selected = False
        if self.table is not None and hasattr(self.table, "get_selected_id"):
            selected = self.table.get_selected_id() is not None

        # Add siempre habilitado
        self.btn_add.configure(
            state="normal",
            fg_color=COLORS["primary"][0],
            hover_color=COLORS["primary"][1],
            text_color="white",
        )

        # Delete y Update habilitados solo si hay selección
        if selected:
            self.btn_delete.configure(
                state="normal",
                fg_color=COLORS["danger"][0],
                hover_color=COLORS["danger"][1],
                text_color="white",
            )
            self.btn_update.configure(
                state="normal",
                fg_color=COLORS["accent"][0],
                hover_color=COLORS["accent"][1],
                text_color="#303030",
            )
        else:
            self.btn_delete.configure(
                state="disabled",
                fg_color="#e0e0e0",
                hover_color="#e0e0e0",
                text_color="#a0a0a0",
                cursor="arrow",
            )
            self.btn_update.configure(
                state="disabled",
                fg_color="#e0e0e0",
                hover_color="#e0e0e0",
                text_color="#a0a0a0",
                cursor="arrow",
            )

        if not self.btn_add.winfo_ismapped():
            self.btn_add.pack(side="right", padx=0)
        if not self.btn_update.winfo_ismapped():
            self.btn_update.pack(side="right", padx=(8, 8))
        if not self.btn_delete.winfo_ismapped():
            self.btn_delete.pack(side="right", padx=(8, 0))

    def _on_selection_change(self, event=None):
        self._update_buttons_visibility()

    def _poll_selection(self):
        current = self.table.get_selected_id() if self.table else None
        if not hasattr(self, "_last_selection") or self._last_selection != current:
            self._last_selection = current
            self._update_buttons_visibility()
        self.after(200, self._poll_selection)

    def _on_add_click(self):
        if self.on_add:
            self.on_add()

    def _on_update_click(self):
        has_selection = (
            self.table
            and hasattr(self.table, "get_selected_id")
            and self.table.get_selected_id() is not None
        )
        if self.on_update and has_selection:
            self.on_update()

    def _on_delete_click(self):
        has_selection = (
            self.table
            and hasattr(self.table, "get_selected_id")
            and self.table.get_selected_id() is not None
        )
        if self.on_delete and has_selection:
            self.on_delete()
