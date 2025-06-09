import customtkinter as ctk
from controllers.crud import get_admin, update_admin
from views.colors import COLORS
import tkinter.messagebox as messagebox
import re


class AdminConfigFrame(ctk.CTkFrame):
    def __init__(self, master, current_admin):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.current_admin = current_admin
        self.edit_mode = False

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create widgets (sin header, solo el form)
        self._create_form()

    def _create_form(self):
        # Main form container - sin header ya que el dashboard lo maneja
        form_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        form_frame.grid_columnconfigure(0, weight=1)

        # Get admin data
        admin = get_admin(self.current_admin.username)

        if admin:
            # Profile section (read-only info)
            self._create_profile_section(form_frame, admin)

            # Editable section
            self._create_editable_section(form_frame, admin)

            # Button section
            self._create_button_section(form_frame)

    def _create_profile_section(self, parent, admin):
        """Create profile info section (read-only) - Compact horizontal layout"""
        # Profile info frame with horizontal layout (3 columns)
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=("gray92", "gray22"),
            corner_radius=12,
            border_width=1,
            border_color=("gray85", "gray30"),
            height=80
        )
        info_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 25))
        info_frame.grid_columnconfigure((0, 1, 2), weight=1)
        info_frame.grid_propagate(False)

        # Username info (left column)
        username_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        username_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        username_container.grid_columnconfigure(0, weight=1)

        username_icon_label = ctk.CTkLabel(
            username_container,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray50", "gray60"),
            anchor="w"
        )
        username_icon_label.pack(anchor="w")

        username_value = ctk.CTkLabel(
            username_container,
            text=admin.username,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        username_value.pack(anchor="w", pady=(2, 0))

        # Vertical separator 1
        separator1 = ctk.CTkFrame(
            info_frame,
            width=1,
            fg_color=("gray80", "gray35")
        )
        separator1.grid(row=0, column=0, sticky="nse", padx=(0, 15))

        # Role info (center column)
        role_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        role_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        role_container.grid_columnconfigure(0, weight=1)

        role_icon_label = ctk.CTkLabel(
            role_container,
            text="Role",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray50", "gray60"),
            anchor="w"
        )
        role_icon_label.pack(anchor="w")

        role_value = ctk.CTkLabel(
            role_container,
            text=str(admin.role).capitalize(),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        role_value.pack(anchor="w", pady=(2, 0))

        # Vertical separator 2
        separator2 = ctk.CTkFrame(
            info_frame,
            width=1,
            fg_color=("gray80", "gray35")
        )
        separator2.grid(row=0, column=1, sticky="nse", padx=(0, 15))

        # Created date info (right column)
        date_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        date_container.grid(row=0, column=2, sticky="nsew", padx=15, pady=15)
        date_container.grid_columnconfigure(0, weight=1)

        date_icon_label = ctk.CTkLabel(
            date_container,
            text="Member Since",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray50", "gray60"),
            anchor="w"
        )
        date_icon_label.pack(anchor="w")

        # Format the creation date nicely
        created_text = self._format_creation_date(admin.created_at)
        date_value = ctk.CTkLabel(
            date_container,
            text=created_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        date_value.pack(anchor="w", pady=(2, 0))

    def _create_editable_section(self, parent, admin):
        """Create editable fields section (initially hidden)"""
        # Editable container frame
        self.editable_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.editable_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 20))
        self.editable_frame.grid_columnconfigure(0, weight=1)

        # Initially hide the editable section
        self.editable_frame.grid_remove()

        # Editable header
        edit_header = ctk.CTkLabel(
            self.editable_frame,
            text="Edit Configuration",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        edit_header.grid(row=0, column=0, sticky="w", padx=0, pady=(0, 10))

        # Username field
        username_label = ctk.CTkLabel(
            self.editable_frame,
            text="Username",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        username_label.grid(row=1, column=0, sticky="w", padx=0, pady=(10, 5))

        self.username_entry = ctk.CTkEntry(
            self.editable_frame,
            placeholder_text="Enter your username",
            height=40,
            corner_radius=8,
            state="disabled",
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 15))
        self.username_entry.insert(0, admin.username)

        # Bind key events for username field
        self.username_entry.bind("<Command-BackSpace>", self.clear_username)

        # Password field
        password_label = ctk.CTkLabel(
            self.editable_frame,
            text="New Password",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        password_label.grid(row=3, column=0, sticky="w", padx=0, pady=(10, 5))

        self.password_entry = ctk.CTkEntry(
            self.editable_frame,
            placeholder_text="Enter new password (optional)",
            height=40,
            corner_radius=8,
            state="disabled",
            show="*",
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.grid(row=4, column=0, sticky="ew", padx=0, pady=(0, 15))

        # Bind key events for password field
        self.password_entry.bind("<Command-BackSpace>", self.clear_password)

        # Confirm Password field
        confirm_password_label = ctk.CTkLabel(
            self.editable_frame,
            text="Confirm New Password",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        confirm_password_label.grid(row=5, column=0, sticky="w", padx=0, pady=(10, 5))

        self.confirm_password_entry = ctk.CTkEntry(
            self.editable_frame,
            placeholder_text="Confirm your new password",
            height=40,
            corner_radius=8,
            state="disabled",
            show="*",
            font=ctk.CTkFont(size=14)
        )
        self.confirm_password_entry.grid(row=6, column=0, sticky="ew", padx=0, pady=(0, 10))

        # Bind key events for confirm password field
        self.confirm_password_entry.bind("<Command-BackSpace>", self.clear_confirm_password)

        # Error label for validation messages
        self.error_label = ctk.CTkLabel(
            self.editable_frame,
            text="",
            text_color=COLORS["danger"][0],
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.error_label.grid(row=7, column=0, sticky="w", padx=0, pady=(0, 20))

    def _create_button_section(self, parent):
        """Create button section"""
        # Button frame
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 0))
        button_frame.grid_columnconfigure((0, 1), weight=1)

        # Edit/Save button
        self.edit_button = ctk.CTkButton(
            button_frame,
            text="Edit Profile",
            command=self._toggle_edit_mode,
            height=45,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["accent"],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.edit_button.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Cancel button (initially hidden)
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel_edit,
            height=45,
            corner_radius=8,
            fg_color=COLORS["danger"][0],
            hover_color=COLORS["danger"][1],
            font=ctk.CTkFont(size=14, weight="bold")
        )

    def _format_creation_date(self, created_at):
        """Format the creation date nicely"""
        try:
            from datetime import datetime
            if isinstance(created_at, str):
                # Try to parse the date string
                try:
                    date_parts = created_at.split(" ")
                    if date_parts and len(date_parts) > 0:
                        date_part = date_parts[0]
                        dt = datetime.strptime(date_part, "%Y-%m-%d")
                        return dt.strftime("%B %d, %Y")
                    else:
                        return created_at
                except (ValueError, IndexError):
                    return created_at
            else:
                # It's a datetime object
                return created_at.strftime("%B %d, %Y")
        except Exception:
            return str(created_at)

    def clear_username(self, event=None):
        """Clear the username entry field"""
        self.username_entry.delete(0, "end")
        return "break"  # Prevent default behavior

    def clear_password(self, event=None):
        """Clear the password entry field"""
        self.password_entry.delete(0, "end")
        return "break"  # Prevent default behavior

    def clear_confirm_password(self, event=None):
        """Clear the confirm password entry field"""
        self.confirm_password_entry.delete(0, "end")
        return "break"  # Prevent default behavior

    def _validate_username(self, username):
        """Validate username format - only letters, numbers, dots and hyphens allowed"""
        if not username:
            self._show_username_error("Username cannot be empty.")
            return False

        if len(username) < 3:
            self._show_username_error("Username must be at least 3 characters long.")
            return False

        # Pattern: only letters, numbers, dots and hyphens
        pattern = r'^[a-zA-Z0-9.-]+$'
        if not re.match(pattern, username):
            self._show_username_error(
                "Username can only contain letters, numbers, dots (.) and hyphens (-)."
            )
            return False

        return True

    def _show_username_error(self, message):
        """Show username validation error with visual feedback"""
        self.error_label.configure(text=message)
        self.username_entry.configure(border_color=COLORS["danger"][0])

    def _show_password_error(self, message):
        """Show password validation error with visual feedback"""
        self.error_label.configure(text=message)
        self.password_entry.configure(border_color=COLORS["danger"][0])
        self.confirm_password_entry.configure(border_color=COLORS["danger"][0])

    def _clear_error_states(self):
        """Clear error states and messages"""
        self.error_label.configure(text="")
        self.username_entry.configure(border_color="gray")
        self.password_entry.configure(border_color="gray")
        self.confirm_password_entry.configure(border_color="gray")

    def _toggle_edit_mode(self):
        if not self.edit_mode:
            # Enter edit mode
            self.edit_mode = True
            # Show the editable section
            self.editable_frame.grid()
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            self.confirm_password_entry.configure(state="normal")
            self.edit_button.configure(text="Save", command=self._save_changes)
            self.cancel_button.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        else:
            self._save_changes()

    def _save_changes(self):
        try:
            # Clear previous error states
            self._clear_error_states()

            # Frontend validation - username format (Vista responsibility)
            new_username = self.username_entry.get().strip()
            if not self._validate_username(new_username):
                return

            # Frontend validation - passwords match (Vista responsibility)
            new_password = self.password_entry.get()
            confirm_password = self.confirm_password_entry.get()

            # Validate password confirmation if password is provided
            if new_password.strip() or confirm_password.strip():
                if new_password != confirm_password:
                    self._show_password_error("Passwords do not match. Please check and try again.")
                    return

                if len(new_password) < 3:  # Basic length validation
                    self._show_password_error("Password must be at least 3 characters long.")
                    return

            # Get the current admin object
            admin = get_admin(self.current_admin.username)
            if not admin:
                messagebox.showerror(
                    "Error", "Could not retrieve admin information"
                )
                return

            # Update admin object with new values
            admin.username = new_username

            # Update password if provided (already validated above)
            if new_password.strip():
                admin.set_password(new_password)

            # Use controller function to update admin
            success = update_admin(admin)

            if success:
                # Update current_admin object
                self.current_admin.username = new_username

                # Clear password fields for security
                self.password_entry.delete(0, "end")
                self.confirm_password_entry.delete(0, "end")

                # Exit edit mode
                self._exit_edit_mode()

                messagebox.showinfo("Success", "Data updated successfully")
            else:
                messagebox.showerror("Error", "Error updating data")

        except Exception as e:
            messagebox.showerror("Error", f"Update error: {str(e)}")

    def _cancel_edit(self):
        # Clear error states when canceling
        self._clear_error_states()

        # Restore original values from database
        admin = get_admin(self.current_admin.username)

        if admin:
            self.username_entry.delete(0, "end")
            self.username_entry.insert(0, admin.username)
            # Clear password fields
            self.password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")

        self._exit_edit_mode()

    def _exit_edit_mode(self):
        self.edit_mode = False
        # Hide the editable section
        self.editable_frame.grid_remove()
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.confirm_password_entry.configure(state="disabled")
        self.edit_button.configure(text="Edit Profile", command=self._toggle_edit_mode)
        self.cancel_button.grid_remove()
