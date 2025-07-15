import customtkinter as ctk
from views.colors import COLORS
from controllers.dashboard_controller import DashboardController
from views.components.table_with_header import TableWithHeaderView
from views.components.form_buttons import FormButtons


class AdminFormView(ctk.CTkFrame):
    def __init__(self, master, on_save=None, on_cancel=None, admin_to_edit=None):
        super().__init__(master, fg_color=("white", "gray17"), corner_radius=15)
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.admin_to_edit = admin_to_edit

        # Controller for trainer data
        self.controller = DashboardController()

        # Create the form
        self._create_widgets()

    def _create_widgets(self):
        # Main scrollable container for the entire form
        self.scrollable_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scrollable_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Title and description
        title_frame = ctk.CTkFrame(self.scrollable_container, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            title_frame,
            text="Add Administrator" if not self.admin_to_edit else "Edit Administrator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w")

        desc_label = ctk.CTkLabel(
            title_frame,
            text="Enter the details for the administrator account",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        # Form fields
        form_frame = ctk.CTkFrame(self.scrollable_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Username field
        username_label = ctk.CTkLabel(
            form_frame,
            text="Username:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        username_label.pack(anchor="w", pady=(0, 5))

        self.username_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="Enter username",
            corner_radius=8
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        # Bind event to validate form when username changes
        self.username_entry.bind('<KeyRelease>', self._validate_form)

        # Password field
        password_label = ctk.CTkLabel(
            form_frame,
            text="Password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        password_label.pack(anchor="w", pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="Enter password",
            show="•",
            corner_radius=8
        )
        self.password_entry.pack(fill="x", pady=(0, 15))
        # Bind event to validate form when password changes
        self.password_entry.bind('<KeyRelease>', self._validate_form)

        # Repeat password field
        repeat_password_label = ctk.CTkLabel(
            form_frame,
            text="Repeat password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        repeat_password_label.pack(anchor="w", pady=(0, 5))

        # Error message for password mismatch (initially hidden)
        self.password_error_label = ctk.CTkLabel(
            form_frame,
            text="Passwords do not match",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w"
        )
        # Don't pack initially - will be shown/hidden based on validation

        self.repeat_password_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="Repeat password",
            show="•",
            corner_radius=8
        )
        self.repeat_password_entry.pack(fill="x", pady=(0, 15))
        # Bind event to validate form when repeat password changes
        self.repeat_password_entry.bind('<KeyRelease>', self._validate_form)

        # Role selection
        role_label = ctk.CTkLabel(
            form_frame,
            text="Role:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        role_label.pack(anchor="w", pady=(0, 5))

        self.role_var = ctk.StringVar(value="admin")

        role_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        role_frame.pack(fill="x", pady=(0, 15))

        self.admin_radio = ctk.CTkRadioButton(
            role_frame,
            text="Administrator",
            variable=self.role_var,
            value="admin",
            font=ctk.CTkFont(size=14),
            border_width_checked=6,
            fg_color=COLORS["primary"][0],
            command=self._on_role_change
        )
        self.admin_radio.pack(side="left", padx=(0, 20))

        self.manager_radio = ctk.CTkRadioButton(
            role_frame,
            text="Manager",
            variable=self.role_var,
            value="manager",
            font=ctk.CTkFont(size=14),
            border_width_checked=6,
            fg_color=COLORS["primary"][0],
            command=self._on_role_change
        )
        self.manager_radio.pack(side="left")

        # Trainer selection section (only shown for manager role)
        self.trainer_selection_frame = ctk.CTkFrame(form_frame, fg_color="transparent")

        # Initially hide trainer selection
        self._update_trainer_selection_visibility()

        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.form_buttons = FormButtons(
            buttons_frame,
            on_save=self.on_save,
            on_cancel=self.on_cancel,
            get_form_data=self.get_form_data
        )
        self.form_buttons.pack(fill="x")

        # Initially disable save button
        self.form_buttons.set_save_enabled(False)

        # If editing, populate fields
        if self.admin_to_edit:
            self._populate_fields()

    def _validate_form(self, event=None):
        """Validate form fields and enable/disable save button"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        repeat_password = self.repeat_password_entry.get().strip()

        # Check if passwords match
        passwords_match = password == repeat_password if password and repeat_password else True

        # Show/hide error message and change field colors
        if password and repeat_password and not passwords_match:
            # Show error message between label and input
            self.password_error_label.pack(
                anchor="w", pady=(0, 5), before=self.repeat_password_entry
            )

            # Change password fields to red using danger color
            self.password_entry.configure(border_color=COLORS["danger"][0])
            self.repeat_password_entry.configure(border_color=COLORS["danger"][0])
        else:
            # Hide error message
            self.password_error_label.pack_forget()

            # Reset password fields to normal color (same as login.py)
            self.password_entry.configure(border_color=("gray60", "gray40"))
            self.repeat_password_entry.configure(border_color=("gray60", "gray40"))

        # Enable save button only if all fields have text and passwords match
        is_valid = bool(username and password and repeat_password and passwords_match)
        self.form_buttons.set_save_enabled(is_valid)

    def _populate_fields(self):
        if self.admin_to_edit:
            # Assuming admin_to_edit is a dict or object with username and role
            if hasattr(self.admin_to_edit, 'username'):
                self.username_entry.insert(0, self.admin_to_edit.username)
                self.role_var.set(self.admin_to_edit.role)
            elif isinstance(self.admin_to_edit, dict):
                if 'username' in self.admin_to_edit:
                    self.username_entry.insert(0, self.admin_to_edit['username'])
                if 'role' in self.admin_to_edit:
                    self.role_var.set(self.admin_to_edit['role'])

            # Validate form after populating fields
            self._validate_form()

    def _on_role_change(self):
        """Handle role change - show/hide trainer selection"""
        self._update_trainer_selection_visibility()

    def _update_trainer_selection_visibility(self):
        """Show/hide trainer selection based on selected role"""
        if self.role_var.get() == "manager":
            self.trainer_selection_frame.pack(fill="both", expand=True, pady=(0, 15))
            self._show_trainers_table()
        else:
            self.trainer_selection_frame.pack_forget()

    def _show_trainers_table(self):
        """Show trainers table using TableWithHeaderView"""
        # Clear existing widgets
        for widget in self.trainer_selection_frame.winfo_children():
            widget.destroy()

        trainers_data = self.controller.get_trainer_data()

        self.trainer_view = TableWithHeaderView(
            self.trainer_selection_frame,
            title="Associate Trainer",
            description="You can associate a trainer as manager (optional)",
            headers=["ID", "Name", "Specialty", "Schedule"],
            data=trainers_data,
            column_weights=[1, 3, 2, 2],
            table_name="Trainers",
            controller=self.controller,
            show_crud_buttons=False
        )
        self.trainer_view.pack(fill="both", expand=True, padx=0, pady=0)

    def get_form_data(self):
        # Get selected trainer from the table if manager role is selected
        trainer_id = None
        if self.role_var.get() == "manager" and hasattr(self, 'trainer_view'):
            trainer_id = self.trainer_view.table.get_selected_id()

        return {
            'username': self.username_entry.get(),
            'password': self.password_entry.get(),
            'role': self.role_var.get(),
            'trainer_id': trainer_id
        }
