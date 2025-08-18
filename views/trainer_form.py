import customtkinter as ctk
from views.colors import COLORS
from controllers.dashboard_controller import DashboardController
from views.components.form_buttons import FormButtons
from views.components.table_with_header import TableWithHeaderView


class TrainerFormView(ctk.CTkFrame):
    """Form for creating/editing Trainers.

    Fields: Name, Lastname, Email, Phone, Specialty, Start time, End time, Manager (optional)
    Follows the AdminFormView pattern: validation with debounce and buttons using FormButtons.
    """

    # Validation constants
    NAME_MIN_LENGTH = 2
    NAME_MAX_LENGTH = 30
    EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    PHONE_PATTERN = r"^[\d\s\-\+\(\)]+$"
    SPECIALTY_MIN_LENGTH = 3
    SPECIALTY_MAX_LENGTH = 50
    TIME_PATTERN = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"

    def __init__(
        self,
        master,
        on_save=None,
        on_cancel=None,
        trainer_to_edit=None,
        current_admin=None,
    ):
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
            text=("Add Trainer" if not self.trainer_to_edit else "Update Trainer"),
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(anchor="w")

        if not self.trainer_to_edit:
            desc_text = "Enter the details for the new trainer"
        else:
            desc_text = "Modify the trainer information"

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

        # Specialty field
        self.specialty_label = ctk.CTkLabel(
            form_frame,
            text="Specialty:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self.specialty_label.pack(anchor="w", pady=(0, 5))

        self.specialty_entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text="Enter specialty (e.g., Personal Training, Yoga, CrossFit)",
            corner_radius=8,
        )
        self.specialty_entry.pack(fill="x", pady=(0, 15))
        self.specialty_entry.bind("<KeyRelease>", self._on_field_change)

        # Error message for specialty validation (initially hidden)
        self.specialty_error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w",
        )

        # Schedule section
        schedule_label = ctk.CTkLabel(
            form_frame,
            text="Work Schedule:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        schedule_label.pack(anchor="w", pady=(0, 5))

        schedule_desc = ctk.CTkLabel(
            form_frame,
            text="Set the trainer's working hours (optional)",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        schedule_desc.pack(anchor="w", pady=(0, 10))

        # Start and End time container
        time_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        time_frame.pack(fill="x", pady=(0, 15))
        time_frame.grid_columnconfigure(0, weight=1)
        time_frame.grid_columnconfigure(1, weight=1)

        # Start time
        self.start_label = ctk.CTkLabel(
            time_frame,
            text="Start Time:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.start_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.start_entry = ctk.CTkEntry(
            time_frame,
            height=40,
            placeholder_text="08:00",
            corner_radius=8,
        )
        self.start_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.start_entry.bind("<KeyRelease>", self._on_field_change)

        # End time
        self.end_label = ctk.CTkLabel(
            time_frame,
            text="End Time:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.end_label.grid(row=0, column=1, sticky="w", pady=(0, 5))

        self.end_entry = ctk.CTkEntry(
            time_frame,
            height=40,
            placeholder_text="17:00",
            corner_radius=8,
        )
        self.end_entry.grid(row=1, column=1, sticky="ew")
        self.end_entry.bind("<KeyRelease>", self._on_field_change)

        # Error message for time validation (initially hidden)
        self.time_error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["danger"][0],
            anchor="w",
        )

        # Optional Manager selection (list of admin usernames with role manager)
        managers = []
        try:
            admins = self.controller.get_admin_data()
            # admin rows: [ID, username, role, created_at]
            managers = [
                row[1]
                for row in admins
                if len(row) > 2 and str(row[2]).lower() == "manager"
            ]
        except Exception:
            managers = []

        self.manager_label = ctk.CTkLabel(
            form_frame,
            text="Assign Manager (Optional):",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self.manager_label.pack(anchor="w", pady=(0, 5))

        manager_desc = ctk.CTkLabel(
            form_frame,
            text="Select a manager to supervise this trainer",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        manager_desc.pack(anchor="w", pady=(0, 10))

        self.manager_combo = ctk.CTkComboBox(
            form_frame,
            values=["None"] + managers,
            height=40,
            corner_radius=8,
        )
        self.manager_combo.pack(fill="x", pady=(0, 15))

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
        specialty = self.specialty_entry.get().strip()
        start_time = self.start_entry.get().strip()
        end_time = self.end_entry.get().strip()

        import re

        # Validate name
        name_valid, name_error = self._validate_name(name)

        # Validate lastname
        lastname_valid, lastname_error = self._validate_lastname(lastname)

        # Validate email
        email_valid, email_error = self._validate_email(email)

        # Validate phone (optional)
        phone_valid, phone_error = self._validate_phone(phone)

        # Validate specialty
        specialty_valid, specialty_error = self._validate_specialty(specialty)

        # Validate time format (optional)
        time_valid, time_error = self._validate_time_schedule(start_time, end_time)

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

        # Show/hide specialty error message
        if specialty and not specialty_valid:
            self.specialty_error_label.configure(text=specialty_error)
            self.specialty_error_label.pack(anchor="w", pady=(0, 5), after=self.specialty_label)
            self.specialty_entry.configure(border_color=COLORS["danger"][0])
        else:
            self.specialty_error_label.pack_forget()
            self.specialty_entry.configure(border_color=("gray60", "gray40"))

        # Show/hide time error message
        if (start_time or end_time) and not time_valid:
            self.time_error_label.configure(text=time_error)
            self.time_error_label.pack(anchor="w", pady=(5, 0))
            if start_time and not re.match(self.TIME_PATTERN, start_time):
                self.start_entry.configure(border_color=COLORS["danger"][0])
            if end_time and not re.match(self.TIME_PATTERN, end_time):
                self.end_entry.configure(border_color=COLORS["danger"][0])
        else:
            self.time_error_label.pack_forget()
            if not start_time or re.match(self.TIME_PATTERN, start_time):
                self.start_entry.configure(border_color=("gray60", "gray40"))
            if not end_time or re.match(self.TIME_PATTERN, end_time):
                self.end_entry.configure(border_color=("gray60", "gray40"))

        # Enable save button only if all required validations pass
        is_valid = bool(
            name and lastname and email and specialty and
            name_valid and lastname_valid and email_valid and specialty_valid and
            phone_valid and time_valid
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

    def _validate_specialty(self, specialty):
        """Validate specialty format and requirements"""
        if not specialty:
            return True, ""  # Empty is valid (will be handled by form validation)

        if len(specialty) < self.SPECIALTY_MIN_LENGTH:
            return False, f"Specialty must be at least {self.SPECIALTY_MIN_LENGTH} characters long"

        if len(specialty) > self.SPECIALTY_MAX_LENGTH:
            return False, f"Specialty must be less than {self.SPECIALTY_MAX_LENGTH} characters"

        return True, ""

    def _validate_time_schedule(self, start_time, end_time):
        """Validate time format and schedule logic"""
        import re

        # If no times provided, it's valid (optional)
        if not start_time and not end_time:
            return True, ""

        # If only one time is provided, validate format
        if start_time and not end_time:
            if not re.match(self.TIME_PATTERN, start_time):
                return False, "Start time must be in HH:MM format (24-hour)"
            return True, ""

        if end_time and not start_time:
            if not re.match(self.TIME_PATTERN, end_time):
                return False, "End time must be in HH:MM format (24-hour)"
            return True, ""

        # Both times provided - validate format and logic
        if not re.match(self.TIME_PATTERN, start_time):
            return False, "Start time must be in HH:MM format (24-hour)"

        if not re.match(self.TIME_PATTERN, end_time):
            return False, "End time must be in HH:MM format (24-hour)"

        # Parse times and check if end is after start
        try:
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))

            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min

            if end_minutes <= start_minutes:
                return False, "End time must be after start time"

        except ValueError:
            return False, "Invalid time format"

        return True, ""

    def get_form_data(self):
        manager_value = self.manager_combo.get()
        # Convert "None" back to None for consistency
        if manager_value == "None":
            manager_value = None

        return {
            "name": self.name_entry.get().strip(),
            "lastname": self.lastname_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "phone": self.phone_entry.get().strip() or None,
            "specialty": self.specialty_entry.get().strip(),
            "start_time": self.start_entry.get().strip() or None,
            "end_time": self.end_entry.get().strip() or None,
            "admin_username": manager_value,
        }

    def _load_existing_trainer_data(self):
        """Load existing trainer data into the form fields"""
        try:
            if not self.trainer_to_edit:
                print("Warning: No trainer ID to edit")
                return

            # Get trainer data
            trainers = self.controller.get_trainer_data()

            # Convert sequential ID to array index
            idx = int(self.trainer_to_edit) - 1

            if 0 <= idx < len(trainers):
                trainer_row = trainers[idx]

                # Parse trainer data based on expected format
                # Assuming format: [ID, Name, Specialty, Schedule, Manager, Email, Phone, ...]
                if len(trainer_row) >= 2:
                    # Split name into first and last name if it's combined
                    full_name = str(trainer_row[1]).strip()
                    name_parts = full_name.split(' ', 1)

                    # Pre-fill name
                    self.name_entry.delete(0, "end")
                    self.name_entry.insert(0, name_parts[0] if name_parts else "")

                    # Pre-fill lastname if available
                    if len(name_parts) > 1:
                        self.lastname_entry.delete(0, "end")
                        self.lastname_entry.insert(0, name_parts[1])

                # Pre-fill specialty if available
                if len(trainer_row) >= 3:
                    self.specialty_entry.delete(0, "end")
                    self.specialty_entry.insert(0, str(trainer_row[2]).strip())

                # Parse schedule if available (format: "HH:MM - HH:MM" or similar)
                if len(trainer_row) >= 4 and trainer_row[3]:
                    schedule = str(trainer_row[3]).strip()
                    if ' - ' in schedule:
                        start_time, end_time = schedule.split(' - ', 1)
                        self.start_entry.delete(0, "end")
                        self.start_entry.insert(0, start_time.strip())
                        self.end_entry.delete(0, "end")
                        self.end_entry.insert(0, end_time.strip())

                # Set manager if available
                if len(trainer_row) >= 5 and trainer_row[4]:
                    manager_name = str(trainer_row[4]).strip()
                    try:
                        # Check if manager exists in combo box
                        current_values = self.manager_combo.cget("values")
                        if manager_name in current_values:
                            self.manager_combo.set(manager_name)
                    except Exception as e:
                        print(f"Warning: Could not set manager: {e}")

                # Pre-fill email if available (assuming it's in a later column)
                if len(trainer_row) >= 6 and trainer_row[5]:
                    self.email_entry.delete(0, "end")
                    self.email_entry.insert(0, str(trainer_row[5]).strip())

                # Pre-fill phone if available
                if len(trainer_row) >= 7 and trainer_row[6]:
                    self.phone_entry.delete(0, "end")
                    self.phone_entry.insert(0, str(trainer_row[6]).strip())

                # Trigger validation to enable save button if data is valid
                self.after(100, self._validate_form)
            else:
                print(f"Warning: Trainer index {idx} out of range")

        except Exception as e:
            print(f"Error loading trainer data: {e}")
