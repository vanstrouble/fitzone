import customtkinter as ctk
from views.colors import COLORS
from utils.validators import AdminValidator
from utils.ui_styles import AdminConfigStyles
from utils.ui_components import CircularBadge
from views.components.form_buttons import FormButtons
import tkinter.messagebox as messagebox
from datetime import datetime


class UserConfigFrame(ctk.CTkFrame):
    def __init__(self, master, current_admin, controller, update_sidebar_callback=None):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.current_admin = current_admin
        self.controller = controller
        self.edit_mode = False
        self.update_sidebar_callback = update_sidebar_callback
        self._configure_layout()
        self._create_form()

    def _configure_layout(self):
        """Configure grid layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _create_form(self):
        """Create main form"""
        form_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        form_frame.grid_columnconfigure(0, weight=1)

        admin_data = self.controller.get_admin_data_unified(
            self.current_admin.unique_id, from_cache=False
        )
        if admin_data:
            self._create_profile_section(form_frame, admin_data)
            self._create_editable_section(form_frame, admin_data)
            self._create_button_section(form_frame)

    def _create_profile_section(self, parent, admin):
        """Create profile card with admin info"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=0,
            pady=(0, AdminConfigStyles.SECTION_SPACING),
        )
        container.grid_columnconfigure(0, weight=1)

        profile_card = ctk.CTkFrame(
            container,
            fg_color=("white", "gray20"),
            corner_radius=AdminConfigStyles.CARD_RADIUS,
            border_width=2,
            border_color=COLORS["primary"][0],
        )
        profile_card.grid(
            row=0, column=0, padx=AdminConfigStyles.PROFILE_CARD_PADX, pady=0
        )

        self._create_profile_content(profile_card, admin)

    def _create_profile_content(self, card, admin):
        """Create content inside profile card"""
        # Header
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(
            fill="x", padx=25, pady=(20, AdminConfigStyles.ELEMENT_SPACING)
        )

        ctk.CTkLabel(
            header_frame,
            text=admin.get('username', 'Unknown'),
            font=ctk.CTkFont(size=AdminConfigStyles.TITLE_FONT_SIZE, weight="bold"),
            text_color=COLORS["primary"][0],
        ).pack(anchor="center")

        ctk.CTkLabel(
            header_frame,
            text=f"{str(admin.get('role', 'admin')).capitalize()} Account",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40"),
        ).pack(anchor="center", pady=(2, 0))

        # Separator
        ctk.CTkFrame(card, height=1, fg_color=("gray90", "gray30")).pack(
            fill="x", padx=25, pady=(0, AdminConfigStyles.ELEMENT_SPACING)
        )

        # Date info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=25, pady=(0, 20))

        created_text = self._format_creation_date(admin.get('created_at'))
        ctk.CTkLabel(
            info_frame,
            text=f"Member since {created_text}",
            font=ctk.CTkFont(size=AdminConfigStyles.SMALL_FONT_SIZE),
            text_color=("gray60", "gray40"),
        ).pack(anchor="center")

    def _create_editable_section(self, parent, admin):
        """Create editable form section"""
        self.editable_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.editable_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 20))
        self.editable_frame.grid_columnconfigure(0, weight=1)
        self.editable_frame.grid_remove()  # Initially hidden

        # Header
        ctk.CTkLabel(
            self.editable_frame,
            text="Edit Configuration",
            font=ctk.CTkFont(size=AdminConfigStyles.HEADER_FONT_SIZE, weight="bold"),
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=0,
            pady=(0, AdminConfigStyles.ELEMENT_SPACING),
        )

        # Form container
        form_container = ctk.CTkFrame(
            self.editable_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=AdminConfigStyles.CONTAINER_RADIUS,
            border_width=1,
            border_color=("gray85", "gray30"),
        )
        form_container.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        form_container.grid_columnconfigure(0, weight=1)

        self._create_form_fields(form_container)
        self._create_error_label()

    def _create_form_fields(self, parent):
        """Create form input fields"""
        # Username field
        self._create_username_field(parent)
        # Password fields
        self._create_password_fields(parent)

    def _create_username_field(self, parent):
        """Create username input field"""
        ctk.CTkLabel(
            parent,
            text="Username",
            font=ctk.CTkFont(size=AdminConfigStyles.LABEL_FONT_SIZE, weight="bold"),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=AdminConfigStyles.FORM_PADDING,
            pady=(AdminConfigStyles.FORM_PADDING, AdminConfigStyles.MICRO_SPACING),
        )

        self.username_entry = ctk.CTkEntry(
            parent,
            height=AdminConfigStyles.ENTRY_HEIGHT,
            corner_radius=AdminConfigStyles.ENTRY_RADIUS,
            state="disabled",
            font=ctk.CTkFont(size=AdminConfigStyles.LABEL_FONT_SIZE),
        )
        self.username_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=AdminConfigStyles.FORM_PADDING,
            pady=(0, AdminConfigStyles.COMPACT_SPACING),
        )

    def _create_password_fields(self, parent):
        """Create password input fields"""
        password_container = ctk.CTkFrame(parent, fg_color="transparent")
        password_container.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=AdminConfigStyles.FORM_PADDING,
            pady=(AdminConfigStyles.MICRO_SPACING, AdminConfigStyles.FORM_PADDING),
        )
        password_container.grid_columnconfigure((0, 1), weight=1)

        # New Password
        ctk.CTkLabel(
            password_container,
            text="New Password",
            font=ctk.CTkFont(size=AdminConfigStyles.LABEL_FONT_SIZE, weight="bold"),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, AdminConfigStyles.COMPACT_SPACING),
            pady=(0, AdminConfigStyles.MICRO_SPACING),
        )

        self.password_entry = ctk.CTkEntry(
            password_container,
            height=AdminConfigStyles.ENTRY_HEIGHT,
            corner_radius=AdminConfigStyles.ENTRY_RADIUS,
            state="disabled",
            show="*",
            font=ctk.CTkFont(size=AdminConfigStyles.LABEL_FONT_SIZE),
        )
        self.password_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(0, AdminConfigStyles.MICRO_SPACING),
            pady=0,
        )

        # Confirm Password
        ctk.CTkLabel(
            password_container,
            text="Confirm Password",
            font=ctk.CTkFont(size=AdminConfigStyles.LABEL_FONT_SIZE, weight="bold"),
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(AdminConfigStyles.MICRO_SPACING, 0),
            pady=(0, AdminConfigStyles.MICRO_SPACING),
        )

        self.confirm_password_entry = ctk.CTkEntry(
            password_container,
            height=AdminConfigStyles.ENTRY_HEIGHT,
            corner_radius=AdminConfigStyles.ENTRY_RADIUS,
            state="disabled",
            show="*",
            font=ctk.CTkFont(size=AdminConfigStyles.LABEL_FONT_SIZE),
        )
        self.confirm_password_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(AdminConfigStyles.MICRO_SPACING, 0),
            pady=0,
        )

    def _create_error_label(self):
        """Create error display label"""
        self.error_label = ctk.CTkLabel(
            self.editable_frame,
            text="",
            text_color=COLORS["danger"][0],
            font=ctk.CTkFont(size=AdminConfigStyles.ERROR_FONT_SIZE, weight="bold"),
        )
        self.error_label.grid(row=2, column=0, sticky="w", padx=0, pady=(8, 0))

    def _create_button_section(self, parent):
        """Create button section using FormButtons component"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 0))
        container.grid_columnconfigure(0, weight=1)

        button_container = ctk.CTkFrame(container, fg_color="transparent")
        button_container.grid(
            row=0, column=0, padx=AdminConfigStyles.PROFILE_CARD_PADX, pady=0
        )

        # Use FormButtons component
        self.form_buttons = FormButtons(
            button_container,
            on_save=self._handle_save,
            on_cancel=self._handle_cancel,
            get_form_data=self._get_form_data
        )
        self.form_buttons.pack(fill="x")

        # Initially hide the form buttons (they'll be shown in edit mode)
        button_container.grid_remove()
        self.button_container = button_container

        # Create the edit button (always visible)
        self.edit_button = ctk.CTkButton(
            container,
            text="Edit Profile",
            command=self._enter_edit_mode,
            height=AdminConfigStyles.BUTTON_HEIGHT,
            corner_radius=AdminConfigStyles.CONTAINER_RADIUS,
            fg_color=COLORS["primary"],
            hover_color=COLORS["accent"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.edit_button.grid(row=0, column=0, padx=AdminConfigStyles.PROFILE_CARD_PADX, pady=0)

    def _format_creation_date(self, created_at):
        """Format creation date for display"""
        try:
            if isinstance(created_at, str):
                date_parts = created_at.split(" ")
                if date_parts:
                    dt = datetime.strptime(date_parts[0], "%Y-%m-%d")
                    return dt.strftime("%B %d, %Y")
                return created_at
            return created_at.strftime("%B %d, %Y")
        except Exception:
            return str(created_at)

    def _refresh_profile_data(self):
        """Refresh profile section with updated data"""
        admin_data = self.controller.refresh_admin_profile(self.current_admin.unique_id)
        if admin_data:
            # Recreate the form with updated data
            for widget in self.winfo_children():
                widget.destroy()
            self._create_form()

    def _get_form_data(self):
        """Get form data for saving"""
        # Safely get values with fallbacks to empty string
        username = self.username_entry.get() if self.username_entry.get() else ""
        password = self.password_entry.get() if self.password_entry.get() else ""

        return {
            'username': username.strip() if username else self.current_admin.username,
            'password': password.strip() if password else None
        }

    def _handle_save(self, form_data):
        """Handle save button click from FormButtons"""
        try:
            self._clear_error_states()

            # Safely extract and validate form data
            new_username = form_data.get('username', '') if form_data.get('username') else ''
            new_password = form_data.get('password', '') if form_data.get('password') else ''
            confirm_password = self.confirm_password_entry.get() or ''

            # Strip strings safely
            new_username = new_username.strip() if new_username else ''
            new_password = new_password.strip() if new_password else ''
            confirm_password = confirm_password.strip() if confirm_password else ''

            # Validate inputs
            if not self._validate_inputs(new_username, new_password, confirm_password):
                return

            # Use controller's unified save method - pass admin ID for update
            result = self.controller.save_admin_data(form_data, self.current_admin.unique_id)

            if result["success"]:
                # Update current admin username if it changed
                if result.get("updated_username"):
                    self.current_admin.username = result["updated_username"]

                self._handle_successful_update()
            else:
                self._show_notification_badge(success=False)
                messagebox.showerror("Error", result["message"])

        except Exception as e:
            self._show_notification_badge(success=False)
            messagebox.showerror("Error", f"Update error: {str(e)}")

    def _handle_cancel(self):
        """Handle cancel button click from FormButtons"""
        self._clear_error_states()
        self._clear_all_fields()
        self._exit_edit_mode()

    def _enter_edit_mode(self):
        """Enter edit mode"""
        self.edit_mode = True
        self.editable_frame.grid()
        self._enable_entries()

        # Hide edit button and show form buttons
        self.edit_button.grid_remove()
        self.button_container.grid()

    def _exit_edit_mode(self):
        """Exit edit mode and return to view mode"""
        self.edit_mode = False
        self.editable_frame.grid_remove()
        self._disable_entries()

        # Show edit button and hide form buttons
        self.button_container.grid_remove()
        self.edit_button.grid()

    def _handle_successful_update(self):
        """Handle successful update"""
        self._clear_password_fields()

        # First exit edit mode to hide the editing section
        self._exit_edit_mode()

        # Then refresh profile data
        self._refresh_profile_data()

        # Update sidebar if callback is provided
        if self.update_sidebar_callback:
            self.update_sidebar_callback()

        # Now show success notification badge just below the edit button
        self.after(100, lambda: self._show_notification_badge(success=True))

    def _show_notification_badge(self, success=True):
        """Show a notification badge indicating success or error

        Args:
            success (bool): True for success, False for error
        """
        # Create a circular badge
        badge = CircularBadge(
            self,
            size=60,
            success=success,
            duration=2000
        )

        # Get the coordinates of the edit button for better positioning
        button_x = self.edit_button.winfo_rootx() + self.edit_button.winfo_width() // 2
        button_y = self.edit_button.winfo_rooty() + self.edit_button.winfo_height() + 10

        # Convert to widget coordinates
        relative_x = button_x - self.winfo_rootx()
        relative_y = button_y - self.winfo_rooty()

        # Position the badge just below the edit button
        badge.place(x=relative_x, y=relative_y, anchor="center")

        # Show the badge and bring it to the front
        badge.show()

    def _clear_error_states(self):
        """Clear all error states and messages"""
        self.error_label.configure(text="")
        for entry in [
            self.username_entry,
            self.password_entry,
            self.confirm_password_entry,
        ]:
            entry.configure(border_color="gray")

    def _enable_entries(self):
        """Enable all entry fields"""
        for entry in [
            self.username_entry,
            self.password_entry,
            self.confirm_password_entry,
        ]:
            entry.configure(state="normal")

    def _disable_entries(self):
        """Disable all entry fields"""
        for entry in [
            self.username_entry,
            self.password_entry,
            self.confirm_password_entry,
        ]:
            entry.configure(state="disabled")

    def _validate_inputs(self, username, password, confirm_password):
        """Validate all form inputs"""
        # Username validation
        if not username:
            username = self.current_admin.username
        else:
            is_valid, error_msg = AdminValidator.validate_username(username)
            if not is_valid:
                self._show_error(error_msg, "username")
                return False

        # Password validation
        if password.strip() or confirm_password.strip():
            is_valid, error_msg = AdminValidator.validate_password_match(
                password, confirm_password
            )
            if not is_valid:
                self._show_error(error_msg, "password")
                return False

            is_valid, error_msg = AdminValidator.validate_password(password)
            if not is_valid:
                self._show_error(error_msg, "password")
                return False

        return True

    def _clear_password_fields(self):
        """Clear password fields for security"""
        self.password_entry.delete(0, "end")
        self.confirm_password_entry.delete(0, "end")

    def _clear_all_fields(self):
        """Clear all form fields"""
        for entry in [
            self.username_entry,
            self.password_entry,
            self.confirm_password_entry,
        ]:
            entry.delete(0, "end")

    def _show_error(self, message, field_type="general"):
        """Display error message with visual feedback"""
        self.error_label.configure(text=message)

        if field_type == "username":
            self.username_entry.configure(border_color=COLORS["danger"][0])
        elif field_type == "password":
            self.password_entry.configure(border_color=COLORS["danger"][0])
            self.confirm_password_entry.configure(border_color=COLORS["danger"][0])
