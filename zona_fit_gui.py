import customtkinter as tk


class App(tk.CTk):
    def __init__(self):
        super().__init__()
        self.window_config()

    def window_config(self):
        # Configure theme
        tk.set_appearance_mode("light")
        tk.set_default_color_theme("blue")  # Puedes usar: "blue", "green", "dark-blue"

        # Configure main window
        self.title("FitZone - Management System")
        self.geometry("1200x720")
        self.resizable(True, True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create a header that spans the entire top section
        self.header_frame = tk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=("#3a7ebf", "#1f538d"),  # Azul para destacarlo
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        # Ensure the header spans the entire width
        self.header_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.CTkLabel(
            self.header_frame,
            text="FITZONE",
            font=tk.CTkFont(size=28, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=(10, 5))

        subtitle_label = tk.CTkLabel(
            self.header_frame,
            text="Gym Management System",
            font=tk.CTkFont(size=14),
            text_color="#ffffff"
        )
        subtitle_label.pack(pady=(0, 10))

        self.main_frame = tk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=("gray90", "gray16")
        )
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
