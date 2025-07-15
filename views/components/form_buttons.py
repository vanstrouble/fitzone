"""
Reusable form buttons component for Save and Cancel actions.
Applies the DRY principle - eliminates code duplication across forms.
"""

import customtkinter as ctk
from views.colors import COLORS


class FormButtons(ctk.CTkFrame):
    """
    Reusable component for form action buttons (Save and Cancel).
    Provides consistent styling and behavior across all forms.
    """

    def __init__(
        self,
        master,
        on_save=None,
        on_cancel=None,
        get_form_data=None,
        validate_form=None,
        save_text="Save",
        cancel_text="Cancel",
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.on_save = on_save
        self.on_cancel = on_cancel
        self.get_form_data = get_form_data
        self.validate_form = validate_form

        self._create_buttons(save_text, cancel_text)

    def _create_buttons(self, save_text, cancel_text):
        """Create the Save and Cancel buttons with consistent styling"""

        # Cancel button (left side)
        self.cancel_button = ctk.CTkButton(
            self,
            text=cancel_text,
            fg_color="#e0e0e0",
            hover_color="#d0d0d0",
            text_color="#303030",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            command=self._on_cancel
        )
        self.cancel_button.pack(side="left", padx=(0, 10))

        # Save button (right side)
        self.save_button = ctk.CTkButton(
            self,
            text=save_text,
            fg_color=COLORS["primary"][0],
            hover_color=COLORS["primary"][1],
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_save
        )
        self.save_button.pack(side="right")

    def _on_save(self):
        """Handle save button click"""
        if self.on_save:
            # If get_form_data is provided, collect form data and pass it to callback
            if self.get_form_data:
                form_data = self.get_form_data()
                self.on_save(form_data)
            else:
                # Fallback to simple callback without data
                self.on_save()

    def _on_cancel(self):
        """Handle cancel button click"""
        if self.on_cancel:
            self.on_cancel()

    def update_save_button_state(self):
        """Update save button state based on form validation"""
        if self.validate_form:
            is_valid = self.validate_form()
            if is_valid:
                self.save_button.configure(
                    state="normal",
                    fg_color=COLORS["primary"][0],
                    hover_color=COLORS["primary"][1],
                    text_color="white"
                )
            else:
                self.save_button.configure(
                    state="disabled",
                    fg_color="#e0e0e0",
                    hover_color="#e0e0e0",
                    text_color="#a0a0a0"
                )

    def set_save_enabled(self, enabled=True):
        """Enable or disable the save button"""
        if enabled:
            self.save_button.configure(
                state="normal",
                fg_color=COLORS["primary"][0],
                hover_color=COLORS["primary"][1],
                text_color="white"
            )
        else:
            self.save_button.configure(
                state="disabled",
                fg_color="#e0e0e0",
                hover_color="#e0e0e0",
                text_color="#a0a0a0"
            )

    def set_cancel_enabled(self, enabled=True):
        """Enable or disable the cancel button"""
        if enabled:
            self.cancel_button.configure(state="normal")
        else:
            self.cancel_button.configure(state="disabled")

    def set_save_text(self, text):
        """Update the save button text"""
        self.save_button.configure(text=text)

    def set_cancel_text(self, text):
        """Update the cancel button text"""
        self.cancel_button.configure(text=text)
