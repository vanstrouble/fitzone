import customtkinter as ctk
from views.colors import COLORS
from controllers.dashboard_controller import DashboardController
from views.components.form_buttons import FormButtons


class UserFormView(ctk.CTkFrame):
    """Formulario para crear/editar Users (miembros).

    Campos: Name, Lastname, Email, Phone, Membership Type, Status, Join Date (opcional)
    """

    EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    def __init__(
        self,
        master,
        on_save=None,
        on_cancel=None,
        user_to_edit=None,
        current_admin=None,
    ):
        super().__init__(master, fg_color=("white", "gray17"), corner_radius=15)
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.user_to_edit = user_to_edit
        self.current_admin = current_admin

        self.controller = DashboardController()
        self._validation_timer = None

        self._create_widgets()

        if self.user_to_edit:
            self._load_existing_user_data()

    def _create_widgets(self):
        self.scrollable = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.scrollable.pack(fill="both", expand=True, padx=0, pady=0)

        title_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            title_frame,
            text=("Add Member" if not self.user_to_edit else "Update Member"),
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(anchor="w")

        desc_label = ctk.CTkLabel(
            title_frame,
            text=(
                "Enter member details"
                if not self.user_to_edit
                else "Modify member details"
            ),
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        form = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=10)

        # Name
        self.name_label = ctk.CTkLabel(
            form, text="Name:", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.name_label.pack(anchor="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(
            form, height=36, placeholder_text="Enter name", corner_radius=8
        )
        self.name_entry.pack(fill="x", pady=(0, 10))
        self.name_entry.bind("<KeyRelease>", self._on_field_change)

        # Lastname
        self.lastname_label = ctk.CTkLabel(
            form, text="Lastname:", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lastname_label.pack(anchor="w", pady=(0, 5))
        self.lastname_entry = ctk.CTkEntry(
            form, height=36, placeholder_text="Enter lastname", corner_radius=8
        )
        self.lastname_entry.pack(fill="x", pady=(0, 10))
        self.lastname_entry.bind("<KeyRelease>", self._on_field_change)

        # Email
        self.email_label = ctk.CTkLabel(
            form, text="Email:", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.email_label.pack(anchor="w", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(
            form, height=36, placeholder_text="Enter email", corner_radius=8
        )
        self.email_entry.pack(fill="x", pady=(0, 10))
        self.email_entry.bind("<KeyRelease>", self._on_field_change)

        # Phone
        self.phone_label = ctk.CTkLabel(
            form, text="Phone:", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.phone_label.pack(anchor="w", pady=(0, 5))
        self.phone_entry = ctk.CTkEntry(
            form, height=36, placeholder_text="Enter phone (optional)", corner_radius=8
        )
        self.phone_entry.pack(fill="x", pady=(0, 10))

        # Membership type and status
        ms_frame = ctk.CTkFrame(form, fg_color="transparent")
        ms_frame.pack(fill="x", pady=(0, 10))
        ms_frame.grid_columnconfigure(0, weight=1)
        ms_frame.grid_columnconfigure(1, weight=1)

        self.membership_label = ctk.CTkLabel(
            ms_frame, text="Membership:", font=ctk.CTkFont(size=14)
        )
        self.membership_label.grid(row=0, column=0, sticky="w")
        self.membership_combo = ctk.CTkComboBox(
            ms_frame, values=["Basic", "Premium", "VIP"], height=36, corner_radius=8
        )
        self.membership_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        self.status_label = ctk.CTkLabel(
            ms_frame, text="Status:", font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=0, column=1, sticky="w")
        self.status_combo = ctk.CTkComboBox(
            ms_frame,
            values=["Active", "Suspended", "Expired"],
            height=36,
            corner_radius=8,
        )
        self.status_combo.grid(row=1, column=1, sticky="ew")

        # Join date (optional free text or datepicker later)
        self.join_label = ctk.CTkLabel(
            form,
            text="Join Date (YYYY-MM-DD, optional):",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.join_label.pack(anchor="w", pady=(0, 5))
        self.join_entry = ctk.CTkEntry(
            form, height=36, placeholder_text="2024-01-01", corner_radius=8
        )
        self.join_entry.pack(fill="x", pady=(0, 10))

        # Buttons
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.form_buttons = FormButtons(
            buttons_frame,
            on_save=self.on_save,
            on_cancel=self.on_cancel,
            get_form_data=self.get_form_data,
        )
        self.form_buttons.pack(fill="x")
        self.form_buttons.set_save_enabled(False)

    def _on_field_change(self, event=None):
        if self._validation_timer:
            self.after_cancel(self._validation_timer)
        self._validation_timer = self.after(700, self._validate_form)

    def _validate_form(self):
        name = self.name_entry.get().strip()
        lastname = self.lastname_entry.get().strip()
        email = self.email_entry.get().strip()

        import re

        email_valid = True
        if email:
            email_valid = bool(re.match(self.EMAIL_PATTERN, email))

        is_valid = bool(name and lastname and email_valid)
        self.form_buttons.set_save_enabled(is_valid)

    def get_form_data(self):
        return {
            "name": self.name_entry.get().strip(),
            "lastname": self.lastname_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "phone": self.phone_entry.get().strip() or None,
            "membership_type": self.membership_combo.get(),
            "status": self.status_combo.get(),
            "join_date": self.join_entry.get().strip() or None,
        }

    def _load_existing_user_data(self):
        try:
            if not self.user_to_edit:
                return
            users = self.controller.get_user_data()
            idx = int(self.user_to_edit) - 1
            if 0 <= idx < len(users):
                row = users[idx]
                if len(row) >= 2:
                    self.name_entry.delete(0, "end")
                    self.name_entry.insert(0, row[1])
        except Exception:
            pass
