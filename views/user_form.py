import customtkinter as ctk
from views.colors import COLORS
from controllers.dashboard_controller import DashboardController
from views.components.form_buttons import FormButtons


class UserFormView(ctk.CTkFrame):
    """Form for creating/editing Users (members).

    Fields: Name, Lastname, Email, Phone, Membership Type, Status
    Follows the AdminFormView pattern: validation with debounce and buttons using FormButtons.
    """

    # Validation constants
    NAME_MIN_LENGTH = 2
    NAME_MAX_LENGTH = 30
    EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    PHONE_PATTERN = r"^[\d\s\-\+\(\)]+$"

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

        # Default save behavior if no external callback is provided
        if self.on_save is None:
            self.on_save = self._default_save

        self._create_widgets()

        if self.user_to_edit:
            self._load_existing_user_data()

    def _create_widgets(self):
        # Main scrollable container for the entire form
        self.scrollable_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.scrollable_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Title and description
        title_frame = ctk.CTkFrame(self.scrollable_container, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            title_frame,
            text=("Add Member" if not self.user_to_edit else "Update Member"),
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(anchor="w")

        if not self.user_to_edit:
            desc_text = "Enter the details for the new gym member"
        else:
            desc_text = "Modify the member information"

        desc_label = ctk.CTkLabel(
            title_frame,
            text=desc_text,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        # Form fields
        form_frame = ctk.CTkFrame(self.scrollable_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Name field
        self.name_label = ctk.CTkLabel(
            form_frame,
            text="Name:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self.name_label.pack(anchor="w", pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="Enter first name",
            corner_radius=8,
        )
        self.name_entry.pack(fill="x", pady=(0, 15))
        self.name_entry.bind("<KeyRelease>", self._on_field_change)

        # Error message for name validation (initially hidden)
        self.name_error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w",
        )

        # Lastname field
        self.lastname_label = ctk.CTkLabel(
            form_frame,
            text="Last Name:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self.lastname_label.pack(anchor="w", pady=(0, 5))

        self.lastname_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="Enter last name",
            corner_radius=8,
        )
        self.lastname_entry.pack(fill="x", pady=(0, 15))
        self.lastname_entry.bind("<KeyRelease>", self._on_field_change)

        # Error message for lastname validation (initially hidden)
        self.lastname_error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w",
        )

        # Email field
        self.email_label = ctk.CTkLabel(
            form_frame,
            text="Email Address:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self.email_label.pack(anchor="w", pady=(0, 5))

        self.email_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="Enter email address",
            corner_radius=8,
        )
        self.email_entry.pack(fill="x", pady=(0, 15))
        self.email_entry.bind("<KeyRelease>", self._on_field_change)

        # Error message for email validation (initially hidden)
        self.email_error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w",
        )

        # Phone field
        self.phone_label = ctk.CTkLabel(
            form_frame,
            text="Phone Number (Optional):",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self.phone_label.pack(anchor="w", pady=(0, 5))

        self.phone_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="Enter phone number",
            corner_radius=8,
        )
        self.phone_entry.pack(fill="x", pady=(0, 15))
        self.phone_entry.bind("<KeyRelease>", self._on_field_change)

        # Error message for phone validation (initially hidden)
        self.phone_error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w",
        )

        # Membership and Status section
        membership_label = ctk.CTkLabel(
            form_frame,
            text="Membership Details:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        membership_label.pack(anchor="w", pady=(0, 5))

        membership_desc = ctk.CTkLabel(
            form_frame,
            text="Set the member's subscription plan and current status",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        membership_desc.pack(anchor="w", pady=(0, 10))

        # Membership type and status container
        ms_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        ms_frame.pack(fill="x", pady=(0, 15))
        ms_frame.grid_columnconfigure(0, weight=1)
        ms_frame.grid_columnconfigure(1, weight=1)

        # Membership type
        self.membership_label = ctk.CTkLabel(
            ms_frame,
            text="Membership Plan:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.membership_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.membership_combo = ctk.CTkComboBox(
            ms_frame,
            values=["Basic", "Premium", "VIP"],
            height=40,
            corner_radius=8,
        )
        self.membership_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Status
        self.status_label = ctk.CTkLabel(
            ms_frame,
            text="Status:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.status_label.grid(row=0, column=1, sticky="w", pady=(0, 5))

        self.status_combo = ctk.CTkComboBox(
            ms_frame,
            values=["Active", "Suspended", "Expired"],
            height=40,
            corner_radius=8,
        )
        self.status_combo.grid(row=1, column=1, sticky="ew")

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
        """Validate form fields and enable/disable save button"""
        name = self.name_entry.get().strip()
        lastname = self.lastname_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()

        # Validate name
        name_valid, name_error = self._validate_name(name)

        # Validate lastname
        lastname_valid, lastname_error = self._validate_lastname(lastname)

        # Validate email
        email_valid, email_error = self._validate_email(email)

        # Validate phone (optional)
        phone_valid, phone_error = self._validate_phone(phone)

        # Show/hide name error message
        if name and not name_valid:
            self.name_error_label.configure(text=name_error)
            self.name_error_label.pack(anchor="w", pady=(0, 5), after=self.name_label)
            self.name_entry.configure(border_color=COLORS["danger"][0])
        else:
            self.name_error_label.pack_forget()
            self.name_entry.configure(border_color=("gray60", "gray40"))

        # Show/hide lastname error message
        if lastname and not lastname_valid:
            self.lastname_error_label.configure(text=lastname_error)
            self.lastname_error_label.pack(anchor="w", pady=(0, 5), after=self.lastname_label)
            self.lastname_entry.configure(border_color=COLORS["danger"][0])
        else:
            self.lastname_error_label.pack_forget()
            self.lastname_entry.configure(border_color=("gray60", "gray40"))

        # Show/hide email error message
        if email and not email_valid:
            self.email_error_label.configure(text=email_error)
            self.email_error_label.pack(anchor="w", pady=(0, 5), after=self.email_label)
            self.email_entry.configure(border_color=COLORS["danger"][0])
        else:
            self.email_error_label.pack_forget()
            self.email_entry.configure(border_color=("gray60", "gray40"))

        # Show/hide phone error message
        if phone and not phone_valid:
            self.phone_error_label.configure(text=phone_error)
            self.phone_error_label.pack(anchor="w", pady=(0, 5), after=self.phone_label)
            self.phone_entry.configure(border_color=COLORS["danger"][0])
        else:
            self.phone_error_label.pack_forget()
            self.phone_entry.configure(border_color=("gray60", "gray40"))

        # Enable save button only if all required validations pass
        is_valid = bool(
            name and lastname and email and
            name_valid and lastname_valid and email_valid and phone_valid
        )
        self.form_buttons.set_save_enabled(is_valid)

    def _validate_name(self, name):
        """Validate name format and requirements"""
        if not name:
            return True, ""  # Empty is valid (will be handled by form validation)

        if len(name) < self.NAME_MIN_LENGTH:
            return False, f"Name must be at least {self.NAME_MIN_LENGTH} characters long"

        if len(name) > self.NAME_MAX_LENGTH:
            return False, f"Name must be less than {self.NAME_MAX_LENGTH} characters"

        if not name.replace(' ', '').replace('-', '').isalpha():
            return False, "Name can only contain letters, spaces, and hyphens"

        return True, ""

    def _validate_lastname(self, lastname):
        """Validate lastname format and requirements"""
        if not lastname:
            return True, ""  # Empty is valid (will be handled by form validation)

        if len(lastname) < self.NAME_MIN_LENGTH:
            return False, f"Last name must be at least {self.NAME_MIN_LENGTH} characters long"

        if len(lastname) > self.NAME_MAX_LENGTH:
            return False, f"Last name must be less than {self.NAME_MAX_LENGTH} characters"

        if not lastname.replace(' ', '').replace('-', '').isalpha():
            return False, "Last name can only contain letters, spaces, and hyphens"

        return True, ""

    def _validate_email(self, email):
        """Validate email format"""
        if not email:
            return True, ""  # Empty is valid (will be handled by form validation)

        import re
        if not re.match(self.EMAIL_PATTERN, email):
            return False, "Please enter a valid email address"

        return True, ""

    def _validate_phone(self, phone):
        """Validate phone format (optional field)"""
        if not phone:
            return True, ""  # Empty is valid for optional field

        import re
        if not re.match(self.PHONE_PATTERN, phone):
            return False, "Please enter a valid phone number"

        # Remove formatting characters to count digits
        digits_only = phone.replace(' ', '').replace('-', '').replace('+', '')
        digits_only = digits_only.replace('(', '').replace(')', '')

        if len(digits_only) < 10:
            return False, "Phone number must contain at least 10 digits"

        return True, ""

    def get_form_data(self):
        return {
            "name": self.name_entry.get().strip(),
            "lastname": self.lastname_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "phone": self.phone_entry.get().strip() or None,
            "membership_type": self.membership_combo.get(),
            "status": self.status_combo.get(),
        }

    def _default_save(self, data=None):
        """Fallback Save action: persist user choosing create/update explicitly."""
        try:
            payload = data or self.get_form_data()
            if self.user_to_edit:
                return self.controller.update_entity_data("user", payload, self)
            return self.controller.create_entity_data("user", payload)
        except Exception as e:
            return {"success": False, "message": f"Error saving member: {e}"}

    def _load_existing_user_data(self):
        """Load existing user data into the form fields"""
        try:
            if not self.user_to_edit:
                print("Warning: No user ID to edit")
                return

            # Get user data
            users = self.controller.get_user_data()

            # Convert sequential ID to array index
            idx = int(self.user_to_edit) - 1

            if 0 <= idx < len(users):
                user_row = users[idx]

                # Parse user data based on expected format
                # Assuming format: [ID, Name, Membership, Status, Join_Date, Email, Phone, ...]
                if len(user_row) >= 2:
                    # Split name into first and last name if it's combined
                    full_name = str(user_row[1]).strip()
                    name_parts = full_name.split(' ', 1)

                    # Pre-fill name
                    self.name_entry.delete(0, "end")
                    self.name_entry.insert(0, name_parts[0] if name_parts else "")

                    # Pre-fill lastname if available
                    if len(name_parts) > 1:
                        self.lastname_entry.delete(0, "end")
                        self.lastname_entry.insert(0, name_parts[1])

                # Pre-fill membership type if available
                if len(user_row) >= 3:
                    membership = str(user_row[2]).strip()
                    try:
                        # Check if membership exists in combo box
                        current_values = self.membership_combo.cget("values")
                        if membership in current_values:
                            self.membership_combo.set(membership)
                        else:
                            # Set default if not found
                            self.membership_combo.set("Basic")
                    except Exception:
                        self.membership_combo.set("Basic")

                # Pre-fill status if available
                if len(user_row) >= 4:
                    status = str(user_row[3]).strip()
                    try:
                        # Check if status exists in combo box
                        current_values = self.status_combo.cget("values")
                        if status in current_values:
                            self.status_combo.set(status)
                        else:
                            # Set default if not found
                            self.status_combo.set("Active")
                    except Exception:
                        self.status_combo.set("Active")

                # Pre-fill email if available (assuming it's in a later column)
                if len(user_row) >= 6 and user_row[5]:
                    self.email_entry.delete(0, "end")
                    self.email_entry.insert(0, str(user_row[5]).strip())

                # Pre-fill phone if available
                if len(user_row) >= 7 and user_row[6]:
                    self.phone_entry.delete(0, "end")
                    self.phone_entry.insert(0, str(user_row[6]).strip())

                # Trigger validation to enable save button if data is valid
                self.after(100, self._validate_form)
            else:
                print(f"Warning: User index {idx} out of range")

        except Exception as e:
            print(f"Error loading user data: {e}")
