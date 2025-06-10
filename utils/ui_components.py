import customtkinter as ctk


class CircularBadge(ctk.CTkFrame):
    """A circular badge notification component that displays success or error status"""

    def __init__(self, master, size=50, success=True, duration=2000, **kwargs):
        """
        Create a circular badge with success or error status

        Args:
            master: Parent widget
            size (int): Size of the badge in pixels
            success (bool): If True, shows success (checkmark); if False, shows error (X)
            duration (int): Auto-hide duration in milliseconds
            **kwargs: Additional arguments passed to CTkFrame
        """
        # Default color schemes
        SUCCESS_COLORS = {
            "bg": ("green", "#27ae60"),
            "fg": ("white", "white")
        }
        ERROR_COLORS = {
            "bg": ("firebrick", "#e74c3c"),
            "fg": ("white", "white")
        }

        # Set appearance based on status
        colors = SUCCESS_COLORS if success else ERROR_COLORS

        # Initialize the frame with a circular shape
        super().__init__(
            master,
            width=size,
            height=size,
            fg_color=colors["bg"],
            corner_radius=size//2,
            **kwargs
        )

        # Ensure the widget keeps its size
        self.grid_propagate(False)
        self.pack_propagate(False)

        # Center contents
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create the symbol (✓ or ✗)
        symbol = "✓" if success else "✗"
        self.symbol_label = ctk.CTkLabel(
            self,
            text=symbol,
            text_color=colors["fg"],
            font=ctk.CTkFont(size=size//2, weight="bold")
        )
        self.symbol_label.place(relx=0.5, rely=0.5, anchor="center")

        # Auto-hide after duration
        if duration > 0:
            self.after(duration, self.hide)

    def show(self):
        """Show the badge with a fade-in effect"""
        self.grid()
        self.tkraise()  # Ensure it's on top

    def hide(self):
        """Hide the badge"""
        self.grid_remove()
