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
        """Create profile info section (read-only) - Simple centered card"""
        # Main container for centering
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 30))
        container.grid_columnconfigure(0, weight=1)

        # Profile card - centered and compact
        profile_card = ctk.CTkFrame(
            container,
            fg_color=("white", "gray20"),
            corner_radius=16,
            border_width=2,
            border_color=COLORS["primary"][0]
        )
        profile_card.grid(row=0, column=0, padx=40, pady=0)

        # Card header with user info
        header_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 15))

        # Main user info - centered
        username_label = ctk.CTkLabel(
            header_frame,
            text=admin.username,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["primary"][0]
        )
        username_label.pack(anchor="center")

        role_label = ctk.CTkLabel(
            header_frame,
            text=f"{str(admin.role).capitalize()} Account",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        role_label.pack(anchor="center", pady=(2, 0))

        # Separator line
        separator = ctk.CTkFrame(
            profile_card,
            height=1,
            fg_color=("gray90", "gray30")
        )
        separator.pack(fill="x", padx=25, pady=(0, 15))

        # Additional info
        info_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
        info_frame.pack(fill="x", padx=25, pady=(0, 20))

        # Format the creation date nicely
        created_text = self._format_creation_date(admin.created_at)
        date_label = ctk.CTkLabel(
            info_frame,
            text=f"Member since {created_text}",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        date_label.pack(anchor="center")

    def _create_editable_section(self, parent, admin):
        """Create editable fields section (initially hidden) - Compact design"""
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
        edit_header.grid(row=0, column=0, sticky="w", padx=0, pady=(0, 15))

        # Compact form container
        form_container = ctk.CTkFrame(
            self.editable_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=8,
            border_width=1,
            border_color=("gray85", "gray30")
        )
        form_container.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        form_container.grid_columnconfigure(0, weight=1)

        # Username field - more compact
        username_label = ctk.CTkLabel(
            form_container,
            text="Username",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        username_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        self.username_entry = ctk.CTkEntry(
            form_container,
            height=35,
            corner_radius=6,
            state="disabled",
            font=ctk.CTkFont(size=13)
        )
        self.username_entry.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.username_entry.bind("<Command-BackSpace>", self.clear_username)

        # Password fields in a two-column layout for compactness
        password_container = ctk.CTkFrame(form_container, fg_color="transparent")
        password_container.grid(row=2, column=0, sticky="ew", padx=15, pady=(5, 15))
        password_container.grid_columnconfigure((0, 1), weight=1)

        # New Password (left column)
        password_label = ctk.CTkLabel(
            password_container,
            text="New Password",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        password_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            password_container,
            height=35,
            corner_radius=6,
            state="disabled",
            show="*",
            font=ctk.CTkFont(size=13)
        )
        self.password_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=0)
        self.password_entry.bind("<Command-BackSpace>", self.clear_password)

        # Confirm Password (right column)
        confirm_password_label = ctk.CTkLabel(
            password_container,
            text="Confirm Password",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        confirm_password_label.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=(0, 5))

        self.confirm_password_entry = ctk.CTkEntry(
            password_container,
            height=35,
            corner_radius=6,
            state="disabled",
            show="*",
            font=ctk.CTkFont(size=13)
        )
        self.confirm_password_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=0)
        self.confirm_password_entry.bind("<Command-BackSpace>", self.clear_confirm_password)

        # Error label - more compact
        self.error_label = ctk.CTkLabel(
            self.editable_frame,
            text="",
            text_color=COLORS["danger"][0],
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        self.error_label.grid(row=2, column=0, sticky="w", padx=0, pady=(8, 0))

    def _create_button_section(self, parent):
        """Create button section - centered below card"""
        # Main container for centering (same as profile card)
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 0))
        container.grid_columnconfigure(0, weight=1)

        # Button container with same width as profile card
        button_container = ctk.CTkFrame(container, fg_color="transparent")
        button_container.grid(row=0, column=0, padx=40, pady=0)  # Same padx as profile card
        button_container.grid_columnconfigure((0, 1), weight=1)

        # Edit/Save button
        self.edit_button = ctk.CTkButton(
            button_container,
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
            button_container,
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

    def _refresh_profile_data(self):
        """Refresh the profile section with updated data"""
        # Get updated admin data
        admin = get_admin(self.current_admin.username)
        if admin:
            # Find the existing profile card and destroy it
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    # This is the form_frame
                    for child in widget.winfo_children():
                        if child.grid_info().get('row') == 0:  # Profile section is at row 0
                            child.destroy()
                            break

                    # Recreate only the profile section
                    self._create_profile_section(widget, admin)
                    break

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

            # If username is empty, keep the current username
            if not new_username:
                new_username = self.current_admin.username
            else:
                # Validate only if user provided a new username
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

                # Refresh the profile section to show updated data
                self._refresh_profile_data()

                messagebox.showinfo("Success", "Data updated successfully")
            else:
                messagebox.showerror("Error", "Error updating data")

        except Exception as e:
            messagebox.showerror("Error", f"Update error: {str(e)}")

    def _cancel_edit(self):
        # Clear error states when canceling
        self._clear_error_states()

        # Clear all fields when canceling
        self.username_entry.delete(0, "end")
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
