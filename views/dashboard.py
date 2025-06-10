import customtkinter as ctk
from views.sidebar import Sidebar
from views.admin_config import AdminConfigFrame
from views.colors import COLORS
from controllers.dashboard_controller import DashboardController
from views.components.table_with_header import TableWithHeaderView
from views.components.view_with_header import ViewWithHeaderView


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, on_logout_callback, current_admin):
        super().__init__(master, fg_color=COLORS["neutral_bg"], corner_radius=0)
        self.current_admin = current_admin

        # Inject the controller - Dependency Inversion Principle
        self.controller = DashboardController()

        # Configure grid
        self.grid_columnconfigure(1, weight=1)  # Content takes remaining space
        self.grid_rowconfigure(0, weight=1)  # Single row with full height

        # Create Sidebar
        self.sidebar = Sidebar(
            self,
            current_admin=current_admin,
            on_section_change=self.show_content,
            on_logout=on_logout_callback,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Create Content Frame
        self._create_content_frame()

        # Show default content
        self._show_default_content()

    def _create_content_frame(self):
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["neutral_bg"],
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.content_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=8,
            fg_color=("white", "gray17"),
        )
        self.content_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

    def _show_default_content(self):
        default_section = self.controller.get_default_section(self.current_admin)
        self.show_content(default_section)

    def show_content(self, section_name):
        if self.controller.should_show_configuration(section_name):
            username = self.controller.extract_username_from_config_section(section_name)
            self._show_user_configuration(username)
        else:
            for widget in self.content_container.winfo_children():
                widget.destroy()

            self.sidebar.set_active_section(section_name)

            if section_name == "Admins":
                self._show_admins_table()
            elif section_name == "Trainers":
                self._show_trainers_table()
            elif section_name == "Users":
                self._show_users_table()
            else:
                self.content_label = ctk.CTkLabel(
                    self.content_container,
                    text=f"{section_name} Content",
                    font=ctk.CTkFont(size=24, weight="bold"),
                )
                self.content_label.grid(row=0, column=0, padx=20, pady=20)

    def _show_admins_table(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()

        admins_data = self.controller.get_admin_data()

        self.admin_view = TableWithHeaderView(
            self.content_container,
            title="Admin Management",
            description="View and manage system administrators",
            headers=["ID", "Username", "Role", "Created At"],
            data=admins_data,
            column_weights=[1, 3, 2, 2],
            table_name="Admins"
        )
        self.admin_view.pack(fill="both", expand=True)

    def _show_trainers_table(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()

        trainers_data = self.controller.get_trainer_data()

        self.trainer_view = TableWithHeaderView(
            self.content_container,
            title="Trainer Management",
            description="View and manage gym trainers",
            headers=["ID", "Name", "Specialty", "Schedule"],
            data=trainers_data,
            column_weights=[1, 3, 2, 2],
            table_name="Trainers"
        )
        self.trainer_view.pack(fill="both", expand=True)

    def _show_users_table(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()

        users_data = self.controller.get_user_data()

        self.user_view = TableWithHeaderView(
            self.content_container,
            title="Member Management",
            description="View and manage gym members",
            headers=["ID", "Name", "Membership", "Status", "Join Date"],
            data=users_data,
            column_weights=[1, 3, 2, 2, 2],
            table_name="Users"
        )
        self.user_view.pack(fill="both", expand=True)

    def _show_user_configuration(self, username):
        for widget in self.content_container.winfo_children():
            widget.destroy()

        config_view = ViewWithHeaderView(
            self.content_container,
            title="Account Information"
        )
        config_view.pack(fill="both", expand=True)

        if username == self.current_admin.username:
            admin_config = AdminConfigFrame(
                config_view.content_area,
                current_admin=self.current_admin,
                update_sidebar_callback=self.update_sidebar
            )
            config_view.add_content(admin_config)
        else:
            fallback_label = ctk.CTkLabel(
                config_view.content_area,
                text=f"Configuration not available for user: {username}",
                font=ctk.CTkFont(size=16),
                text_color=COLORS["text_secondary"],
            )
            config_view.add_content(fallback_label)

    def update_sidebar(self):
        """Update sidebar information after user profile changes"""
        if hasattr(self, "sidebar"):
            self.sidebar.update_username()
