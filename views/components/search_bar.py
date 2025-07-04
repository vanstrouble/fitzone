"""
Reusable and stylish search bar component.
"""

import customtkinter as ctk
from views.colors import COLORS
from typing import Callable, Optional


class SearchBar(ctk.CTkFrame):
    """Stylish and reusable search bar"""

    def __init__(
        self,
        master,
        on_search_callback: Optional[Callable] = None,
        placeholder_text: str = "Search...",
        width: int = 300,
        height: int = 40,
    ):
        super().__init__(master, fg_color="transparent")

        self.on_search_callback = on_search_callback
        self.placeholder_text = placeholder_text
        self.width = width
        self.height = height

        # Debouncing for performance
        self._search_timer = None
        self._debounce_delay = 300  # 300ms delay

        # Focus state tracking
        self._is_focused = False

        self._create_search_bar()

    def _create_search_bar(self):
        """Create the search bar"""
        # Main container
        self.search_container = ctk.CTkFrame(
            self,
            width=self.width,
            height=self.height,
            fg_color=("white", "gray20"),
            border_width=1,
            border_color=("gray70", "gray30"),
            corner_radius=20,
        )
        self.search_container.pack(fill="both", expand=True)
        self.search_container.pack_propagate(False)

        # Search entry
        self.search_entry = ctk.CTkEntry(
            self.search_container,
            placeholder_text=self.placeholder_text,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=0,
            height=self.height - 4,
        )
        self.search_entry.pack(
            side="left", fill="both", expand=True, padx=(15, 5), pady=2
        )

        # Search icon
        self.search_icon = ctk.CTkLabel(
            self.search_container,
            text="🔍",
            font=ctk.CTkFont(size=16),
            width=30,
            text_color=("gray50", "gray60"),
        )
        self.search_icon.pack(side="right", padx=(5, 15))

        # Bind events
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        self.search_entry.bind("<Return>", self._on_search_enter)
        self.search_entry.bind("<FocusIn>", self._on_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_focus_out)

        # Advanced keyboard shortcuts
        self._bind_keyboard_shortcuts()

    def _bind_keyboard_shortcuts(self):
        """Bind advanced keyboard shortcuts for better typing experience"""
        import platform

        # Detect operating system for correct modifier keys
        is_mac = platform.system() == "Darwin"

        if is_mac:
            # macOS shortcuts
            self.search_entry.bind("<Command-BackSpace>", self._delete_to_beginning)
            self.search_entry.bind("<Option-BackSpace>", self._delete_word_backward)
        else:
            # Windows/Linux shortcuts
            self.search_entry.bind("<Control-BackSpace>", self._delete_word_backward)
            self.search_entry.bind("<Control-Shift-BackSpace>", self._delete_to_beginning)

        # Universal shortcuts (work on all platforms)
        self.search_entry.bind("<Escape>", self._unfocus_search_bar)

        # Additional useful shortcuts
        self.search_entry.bind("<Control-a>", self._select_all)
        if is_mac:
            self.search_entry.bind("<Command-a>", self._select_all)

    def _delete_to_beginning(self, event):
        """Delete from cursor position to the beginning of the line (Cmd/Ctrl + Backspace)"""
        cursor_pos = self.search_entry.index(ctk.INSERT)
        if cursor_pos > 0:
            self.search_entry.delete(0, cursor_pos)
            # Trigger search after deletion
            self._on_search_change(event)
        return "break"  # Prevent default behavior

    def _delete_word_backward(self, event):
        """Delete word backward from cursor position (Alt/Option + Backspace)"""
        text = self.search_entry.get()
        cursor_pos = self.search_entry.index(ctk.INSERT)

        if cursor_pos == 0:
            return "break"

        # Find the start of the current word
        start_pos = cursor_pos - 1

        # Skip whitespace
        while start_pos >= 0 and text[start_pos].isspace():
            start_pos -= 1

        # Find word boundary
        while start_pos >= 0 and not text[start_pos].isspace():
            start_pos -= 1

        start_pos += 1  # Move to the beginning of the word

        # Delete the word
        if start_pos < cursor_pos:
            self.search_entry.delete(start_pos, cursor_pos)
            # Trigger search after deletion
            self._on_search_change(event)

        return "break"  # Prevent default behavior

    def _unfocus_search_bar(self, event):
        """Unfocus the search bar when Escape is pressed"""
        self.search_entry.master.focus()  # Focus parent to remove focus from entry
        return "break"

    def _select_all(self, event):
        """Select all text in the search bar (Ctrl/Cmd + A)"""
        self.search_entry.select_range(0, ctk.END)
        return "break"  # Prevent default behavior

    def _on_search_change(self, event):
        """Handle changes in the search text with debouncing"""
        # Cancel previous timer if exists
        if self._search_timer:
            self.after_cancel(self._search_timer)

        # Set new timer for debounced search
        self._search_timer = self.after(
            self._debounce_delay,
            self._execute_search
        )

    def _execute_search(self):
        """Execute the actual search after debounce delay"""
        query = self.search_entry.get().strip()
        if self.on_search_callback:
            self.on_search_callback(query)
        self._search_timer = None

    def _on_search_enter(self, event):
        """Handle Enter key"""
        query = self.search_entry.get().strip()
        if self.on_search_callback:
            self.on_search_callback(query)

    def _on_focus_in(self, event):
        """Handle focus in - highlight the search bar"""
        self._is_focused = True
        self._update_search_bar_style()

    def _on_focus_out(self, event):
        """Handle focus out - remove highlight"""
        self._is_focused = False
        self._update_search_bar_style()

    def _update_search_bar_style(self):
        """Update search bar appearance based on focus state"""
        if self._is_focused:
            # Focused state - primary color border (same width)
            self.search_container.configure(
                border_color=COLORS["primary"][0]
            )
            # Make icon more prominent when focused
            self.search_icon.configure(
                text_color=COLORS["primary"][0]
            )
        else:
            # Normal state - subtle border
            self.search_container.configure(
                border_color=("gray70", "gray30")
            )
            # Return icon to normal state
            self.search_icon.configure(
                text_color=("gray50", "gray60")
            )

    def get_search_query(self) -> str:
        """Get the current search text"""
        return self.search_entry.get().strip()

    def clear_search(self):
        """Clear the search"""
        self.search_entry.delete(0, "end")
        if self.on_search_callback:
            self.on_search_callback("")

    def focus(self):
        """Focus the search bar"""
        self.search_entry.focus()

    def set_placeholder(self, text: str):
        """Change the placeholder text"""
        self.search_entry.configure(placeholder_text=text)
