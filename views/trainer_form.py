import customtkinter as ctk
from views.colors import COLORS
from controllers.dashboard_controller import DashboardController
from views.components.form_buttons import FormButtons
from views.components.table_with_header import TableWithHeaderView


class TrainerFormView(ctk.CTkFrame):
    """Formulario para crear/editar Trainers.

    Campos: Name, Lastname, Email, Phone, Specialty, Start time, End time, Manager (opcional)
    Sigue el patrón de AdminFormView: validación con debounce y botones usando FormButtons.
    """

    EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    def __init__(self, master, on_save=None, on_cancel=None, trainer_to_edit=None, current_admin=None):
        super().__init__(master, fg_color=("white", "gray17"), corner_radius=15)
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.trainer_to_edit = trainer_to_edit
        self.current_admin = current_admin

        self.controller = DashboardController()
        self._validation_timer = None

        self._create_widgets()

        if self.trainer_to_edit:
            self._load_existing_trainer_data()

    def _create_widgets(self):
        # Contenedor scrollable
        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scrollable.pack(fill="both", expand=True, padx=0, pady=0)

        title_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            title_frame,
            text=("Add Trainer" if not self.trainer_to_edit else "Update Trainer"),
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(anchor="w")

        desc_label = ctk.CTkLabel(
            title_frame,
            text=("Enter trainer details" if not self.trainer_to_edit else "Modify trainer details"),
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        form = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=10)

        # Name
        self.name_label = ctk.CTkLabel(form, text="Name:", font=ctk.CTkFont(size=14, weight="bold"))
        self.name_label.pack(anchor="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(form, height=36, placeholder_text="Enter name", corner_radius=8)
        self.name_entry.pack(fill="x", pady=(0, 10))
        self.name_entry.bind("<KeyRelease>", self._on_field_change)

        # Lastname
        self.lastname_label = ctk.CTkLabel(form, text="Lastname:", font=ctk.CTkFont(size=14, weight="bold"))
        self.lastname_label.pack(anchor="w", pady=(0, 5))
        self.lastname_entry = ctk.CTkEntry(form, height=36, placeholder_text="Enter lastname", corner_radius=8)
        self.lastname_entry.pack(fill="x", pady=(0, 10))
        self.lastname_entry.bind("<KeyRelease>", self._on_field_change)

        # Email
        self.email_label = ctk.CTkLabel(form, text="Email:", font=ctk.CTkFont(size=14, weight="bold"))
        self.email_label.pack(anchor="w", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(form, height=36, placeholder_text="Enter email", corner_radius=8)
        self.email_entry.pack(fill="x", pady=(0, 10))
        self.email_entry.bind("<KeyRelease>", self._on_field_change)

        # Phone
        self.phone_label = ctk.CTkLabel(form, text="Phone:", font=ctk.CTkFont(size=14, weight="bold"))
        self.phone_label.pack(anchor="w", pady=(0, 5))
        self.phone_entry = ctk.CTkEntry(form, height=36, placeholder_text="Enter phone (optional)", corner_radius=8)
        self.phone_entry.pack(fill="x", pady=(0, 10))

        # Specialty
        self.specialty_label = ctk.CTkLabel(form, text="Specialty:", font=ctk.CTkFont(size=14, weight="bold"))
        self.specialty_label.pack(anchor="w", pady=(0, 5))
        self.specialty_entry = ctk.CTkEntry(form, height=36, placeholder_text="Enter specialty", corner_radius=8)
        self.specialty_entry.pack(fill="x", pady=(0, 10))
        self.specialty_entry.bind("<KeyRelease>", self._on_field_change)

        # Start and End time
        time_frame = ctk.CTkFrame(form, fg_color="transparent")
        time_frame.pack(fill="x", pady=(0, 10))
        time_frame.grid_columnconfigure(0, weight=1)
        time_frame.grid_columnconfigure(1, weight=1)

        self.start_label = ctk.CTkLabel(time_frame, text="Start (HH:MM):", font=ctk.CTkFont(size=14))
        self.start_label.grid(row=0, column=0, sticky="w")
        self.start_entry = ctk.CTkEntry(time_frame, height=36, placeholder_text="08:00", corner_radius=8)
        self.start_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        self.start_entry.bind("<KeyRelease>", self._on_field_change)

        self.end_label = ctk.CTkLabel(time_frame, text="End (HH:MM):", font=ctk.CTkFont(size=14))
        self.end_label.grid(row=0, column=1, sticky="w")
        self.end_entry = ctk.CTkEntry(time_frame, height=36, placeholder_text="17:00", corner_radius=8)
        self.end_entry.grid(row=1, column=1, sticky="ew")
        self.end_entry.bind("<KeyRelease>", self._on_field_change)

        # Optional Manager selection (list of admin usernames with role manager)
        managers = []
        try:
            admins = self.controller.get_admin_data()
            # admin rows: [ID, username, role, created_at]
            managers = [row[1] for row in admins if len(row) > 2 and str(row[2]).lower() == "manager"]
        except Exception:
            managers = []

        self.manager_label = ctk.CTkLabel(form, text="Assign Manager (optional):", font=ctk.CTkFont(size=14, weight="bold"))
        self.manager_label.pack(anchor="w", pady=(0, 5))
        self.manager_combo = ctk.CTkComboBox(form, values=[""] + managers, height=36, corner_radius=8)
        self.manager_combo.pack(fill="x", pady=(0, 15))

        # Buttons
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.form_buttons = FormButtons(buttons_frame, on_save=self.on_save, on_cancel=self.on_cancel, get_form_data=self.get_form_data)
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
        specialty = self.specialty_entry.get().strip()

        import re

        email_valid = True
        if email:
            email_valid = bool(re.match(self.EMAIL_PATTERN, email))

        is_valid = bool(name and lastname and specialty and email_valid)

        self.form_buttons.set_save_enabled(is_valid)

    def get_form_data(self):
        return {
            "name": self.name_entry.get().strip(),
            "lastname": self.lastname_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "phone": self.phone_entry.get().strip() or None,
            "specialty": self.specialty_entry.get().strip(),
            "start_time": self.start_entry.get().strip() or None,
            "end_time": self.end_entry.get().strip() or None,
            "admin_username": self.manager_combo.get() or None,
        }

    def _load_existing_trainer_data(self):
        try:
            if not self.trainer_to_edit:
                return
            trainers = self.controller.get_trainer_data()
            # Sequential ID -> index mapping
            idx = int(self.trainer_to_edit) - 1
            if 0 <= idx < len(trainers):
                row = trainers[idx]
                # row expected: [ID, Name, Specialty, Schedule, Manager] or similar
                # Try to map common positions
                if len(row) >= 2:
                    self.name_entry.delete(0, "end")
                    self.name_entry.insert(0, row[1])
                # If more structured data is required, caller can prefill via callback
        except Exception:
            pass
