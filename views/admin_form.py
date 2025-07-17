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

        # Debounce system for validation (300ms delay)
        self._validation_timer = None

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
        self.username_label = ctk.CTkLabel(
            form_frame,
            text="Username:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.username_label.pack(anchor="w", pady=(0, 5))

        self.username_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="Enter username",
            corner_radius=8
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        # Bind event to validate form when username changes (with debounce)
        self.username_entry.bind('<KeyRelease>', self._on_field_change)

        # Password field
        self.password_label = ctk.CTkLabel(
            form_frame,
            text="Password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.password_label.pack(anchor="w", pady=(0, 5))

        # Password input with toggle button container
        password_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_container.pack(fill="x", pady=(0, 15))
        password_container.grid_columnconfigure(0, weight=1)

        self.password_entry = ctk.CTkEntry(
            password_container,
            height=40,
            placeholder_text="Enter password",
            show="•",
            corner_radius=8
        )
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        # Bind event to validate form when password changes (with debounce)
        self.password_entry.bind('<KeyRelease>', self._on_field_change)

        # Toggle password visibility button
        self.password_toggle_btn = ctk.CTkButton(
            password_container,
            width=40,
            height=40,
            text="🙈",
            font=ctk.CTkFont(size=16),
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            corner_radius=8,
            command=self._toggle_password_visibility
        )
        self.password_toggle_btn.grid(row=0, column=1, sticky="e")

        # Track password visibility state
        self.password_visible = False

        # Repeat password field
        repeat_password_label = ctk.CTkLabel(
            form_frame,
            text="Repeat password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        repeat_password_label.pack(anchor="w", pady=(0, 5))

        # Repeat password input with toggle button container
        repeat_password_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        repeat_password_container.pack(fill="x", pady=(0, 15))
        repeat_password_container.grid_columnconfigure(0, weight=1)

        self.repeat_password_entry = ctk.CTkEntry(
            repeat_password_container,
            height=40,
            placeholder_text="Repeat password",
            show="•",
            corner_radius=8
        )
        self.repeat_password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        # Bind event to validate form when repeat password changes (with debounce)
        self.repeat_password_entry.bind('<KeyRelease>', self._on_field_change)

        # Toggle repeat password visibility button
        self.repeat_password_toggle_btn = ctk.CTkButton(
            repeat_password_container,
            width=40,
            height=40,
            text="🙈",
            font=ctk.CTkFont(size=16),
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            corner_radius=8,
            command=self._toggle_repeat_password_visibility
        )
        self.repeat_password_toggle_btn.grid(row=0, column=1, sticky="e")

        # Track repeat password visibility state
        self.repeat_password_visible = False

        # Error message for password mismatch (initially hidden)
        self.password_error_label = ctk.CTkLabel(
            form_frame,
            text="Passwords do not match",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w"
        )
        # Don't pack initially - will be shown/hidden based on validation

        # Error message for username validation (initially hidden)
        self.username_error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w"
        )
        # Don't pack initially - will be shown/hidden based on validation

        # Error message for password validation (initially hidden)
        self.password_validation_error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w"
        )
        # Don't pack initially - will be shown/hidden based on validation

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

    def _on_field_change(self, event=None):
        """Handle field changes with debounce - wait 300ms before validating"""
        # Cancel previous timer if it exists
        if self._validation_timer:
            self.after_cancel(self._validation_timer)

        # Set new timer for 300ms delay
        self._validation_timer = self.after(700, self._validate_form)

    def _validate_form(self, event=None):
        """Validate form fields and enable/disable save button"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        repeat_password = self.repeat_password_entry.get().strip()

        # Validate username
        username_valid, username_error = self._validate_username(username)

        # Validate password
        password_valid, password_error = self._validate_password(password)

        # Check if passwords match
        passwords_match = password == repeat_password if password and repeat_password else True

        # Show/hide username error message
        if username and not username_valid:
            self.username_error_label.configure(text=username_error)
            self.username_error_label.pack(anchor="w", pady=(0, 5), after=self.username_label)
            self.username_entry.configure(border_color=COLORS["danger"][0])
        else:
            self.username_error_label.pack_forget()
            self.username_entry.configure(border_color=("gray60", "gray40"))

        # Show/hide password validation error message
        if password and not password_valid:
            self.password_validation_error_label.configure(text=password_error)
            self.password_validation_error_label.pack(
                anchor="w", pady=(0, 5), after=self.password_label
            )
            self.password_entry.configure(border_color=COLORS["danger"][0])
        else:
            self.password_validation_error_label.pack_forget()
            if passwords_match:  # Only reset color if passwords match
                self.password_entry.configure(border_color=("gray60", "gray40"))

        # Show/hide password match error message
        if password and repeat_password and not passwords_match:
            self.password_error_label.pack(
                anchor="w", pady=(0, 5), before=self.repeat_password_entry
            )
            self.password_entry.configure(border_color=COLORS["danger"][0])
            self.repeat_password_entry.configure(border_color=COLORS["danger"][0])
        else:
            self.password_error_label.pack_forget()
            if password_valid or not password:  # Only reset if password is valid or empty
                self.repeat_password_entry.configure(border_color=("gray60", "gray40"))

        # Enable save button only if all validations pass
        is_valid = bool(
            username and password and repeat_password and
            username_valid and password_valid and passwords_match
        )
        self.form_buttons.set_save_enabled(is_valid)

    def _validate_username(self, username):
        """Validate username format and requirements"""
        if not username:
            return True, ""  # Empty is valid (will be handled by form validation)

        # Username requirements
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"

        if len(username) > 20:
            return False, "Username must be less than 20 characters"

        # Only alphanumeric characters, underscore, and hyphen allowed
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscore, and hyphen"

        # Must start with a letter
        if not username[0].isalpha():
            return False, "Username must start with a letter"

        return True, ""

    def _validate_password(self, password):
        """Validate password format and requirements"""
        if not password:
            return True, ""  # Empty is valid (will be handled by form validation)

        # Password requirements
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"

        if len(password) > 20:
            return False, "Password must be less than 20 characters"

        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        # Check for at least one lowercase letter
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"

        # Check for at least one special character
        import re
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"

        return True, ""

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

    def _toggle_password_visibility(self):
        """Toggle password visibility between hidden and visible"""
        if self.password_visible:
            # Hide password
            self.password_entry.configure(show="•")
            self.password_toggle_btn.configure(text="🙈")
            self.password_visible = False
        else:
            # Show password
            self.password_entry.configure(show="")
            self.password_toggle_btn.configure(text="🤫")
            self.password_visible = True

    def _toggle_repeat_password_visibility(self):
        """Toggle repeat password visibility between hidden and visible"""
        if self.repeat_password_visible:
            # Hide password
            self.repeat_password_entry.configure(show="•")
            self.repeat_password_toggle_btn.configure(text="🙈")
            self.repeat_password_visible = False
        else:
            # Show password
            self.repeat_password_entry.configure(show="")
            self.repeat_password_toggle_btn.configure(text="🤫")
            self.repeat_password_visible = True
