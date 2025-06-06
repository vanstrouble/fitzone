import customtkinter as ctk
from controllers.crud import is_admin, get_all_admins, get_all_trainers, get_all_users
from views.sidebar import Sidebar
from views.data_table import DataTable
from views.colors import COLORS


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, on_logout_callback, current_admin):
        # Use the main background color of the application instead of transparent
        super().__init__(master, fg_color=COLORS["neutral_bg"], corner_radius=0)
        self.current_admin = current_admin

        # Configure grid
        self.grid_columnconfigure(1, weight=1)  # Content takes remaining space
        self.grid_rowconfigure(0, weight=1)  # Single row with full height

        # Create Sidebar with the appropriate color
        self.sidebar = Sidebar(
            self,
            current_admin=current_admin,
            on_section_change=self.show_content,
            on_logout=on_logout_callback,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)  # No padding

        # Create Content Frame
        self._create_content_frame()

        # Show default content
        self._show_default_content()

    def _create_content_frame(self):
        # Change the background color of content_frame to match the general style
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,  # No rounded borders
            fg_color=COLORS["neutral_bg"],  # Use the same neutral background color
        )
        # Remove right padding to avoid gray space
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Main content with a lighter background to differentiate it
        self.content_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=8,  # Slightly rounded corners
            fg_color=("white", "gray17"),  # Light/dark background for the content
        )
        self.content_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(
            1, weight=1
        )  # Make the table row expandable

    def _show_default_content(self):
        default_section = (
            "Admins" if is_admin(self.current_admin.username) else "Trainers"
        )
        self.show_content(default_section)

    def show_content(self, section_name):
        # Check if this is a configuration section
        if section_name.startswith("Configuration "):
            username = section_name.split(" ", 1)[1]
            self._show_user_configuration(username)
        else:
            # Clear previous content
            for widget in self.content_container.winfo_children():
                widget.destroy()

            # Update sidebar active section
            self.sidebar.set_active_section(section_name)

            # Show the appropriate content based on section_name
            if section_name == "Admins":
                self._show_admins_table()
            elif section_name == "Trainers":
                self._show_trainers_table()
            elif section_name == "Users":
                self._show_users_table()
            else:
                # Fallback for unknown sections
                self.content_label = ctk.CTkLabel(
                    self.content_container,
                    text=f"{section_name} Content",
                    font=ctk.CTkFont(size=24, weight="bold"),
                )
                self.content_label.grid(row=0, column=0, padx=20, pady=20)

    def _show_admins_table(self):
        # Clear previous content
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Configure grid for the content container - table takes all remaining space
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(1, weight=1)  # Table row expands

        # Header section with title and description
        header_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Admin Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 3))

        # Description
        description_label = ctk.CTkLabel(
            header_frame,
            text="View and manage system administrators",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        description_label.grid(row=1, column=0, sticky="w")

        # Get admin data and format it
        admins_data = self._get_formatted_admin_data()

        # Create reusable table - fills all remaining space
        self.admin_table = DataTable(
            self.content_container,
            headers=["ID", "Username", "Role", "Created At"],
            data=admins_data,
            column_weights=[
                1,
                3,
                2,
                2,
            ],  # ID narrow, Username expandable, Role medium, Date medium
            table_name="Admins",
        )
        self.admin_table.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 15))

    def _get_formatted_admin_data(self):
        """Get and format admin data for the table"""
        admins_data = get_all_admins()
        formatted_data = []

        for idx, admin in enumerate(admins_data):
            # Format created_at date if available
            created_at_str = "N/A"
            if hasattr(admin, "created_at") and admin.created_at:
                from datetime import datetime

                if isinstance(admin.created_at, str):
                    try:
                        # Assume format is "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD"
                        date_part = admin.created_at.split(" ")[0]
                        dt = datetime.strptime(date_part, "%Y-%m-%d")
                        created_at_str = dt.strftime("%d/%m/%Y")
                    except (ValueError, IndexError):
                        created_at_str = str(admin.created_at)
                else:
                    # It's a datetime object
                    created_at_str = admin.created_at.strftime("%d/%m/%Y")

            formatted_data.append(
                [
                    str(idx + 1),  # Use sequential ID starting from 1
                    admin.username,
                    admin.role.capitalize() if admin.role else "Admin",
                    created_at_str,
                ]
            )

        return formatted_data

    def _show_trainers_table(self):
        # Clear previous content
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Configure grid for the content container
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(1, weight=1)

        # Header section with title and description
        header_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Trainer Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 3))

        # Description
        description_label = ctk.CTkLabel(
            header_frame,
            text="View and manage gym trainers",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        description_label.grid(row=1, column=0, sticky="w")

        # Get trainer data and format it
        trainers_data = self._get_formatted_trainer_data()

        # Create reusable table
        self.trainer_table = DataTable(
            self.content_container,
            headers=["ID", "Name", "Specialty", "Schedule"],
            data=trainers_data,
            column_weights=[1, 3, 2, 2],  # Same structure as admin table
            table_name="Trainers",
        )
        self.trainer_table.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 15))

    def _get_formatted_trainer_data(self):
        """Get and format trainer data for the table"""
        try:
            trainers_data = get_all_trainers()
            formatted_data = []

            for idx, trainer in enumerate(trainers_data):
                # Format start_time and end_time if available
                schedule_str = "N/A"
                if hasattr(trainer, "start_time") and hasattr(trainer, "end_time"):
                    if trainer.start_time and trainer.end_time:
                        schedule_str = f"{trainer.start_time} - {trainer.end_time}"
                    elif trainer.start_time:
                        schedule_str = f"From {trainer.start_time}"
                    elif trainer.end_time:
                        schedule_str = f"Until {trainer.end_time}"

                # Get trainer name safely
                trainer_name = getattr(trainer, "name", "Unknown")
                trainer_lastname = getattr(trainer, "lastname", "")
                full_name = f"{trainer_name} {trainer_lastname}".strip()

                # Get specialty safely
                specialty = getattr(trainer, "specialty", "Trainer")

                formatted_data.append(
                    [
                        str(idx + 1),  # Use sequential ID starting from 1
                        full_name,
                        specialty,
                        schedule_str,
                    ]
                )

            return formatted_data
        except Exception as e:
            print(f"Error formatting trainer data: {e}")
            return []

    def _show_users_table(self):
        # Clear previous content
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Configure grid for the content container
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(1, weight=1)

        # Header section with title and description
        header_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Member Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 3))

        # Description
        description_label = ctk.CTkLabel(
            header_frame,
            text="View and manage gym members",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        description_label.grid(row=1, column=0, sticky="w")

        # Get user data and format it
        users_data = self._get_formatted_user_data()

        # Create reusable table
        self.user_table = DataTable(
            self.content_container,
            headers=["ID", "Name", "Membership", "Status", "Join Date"],
            data=users_data,
            column_weights=[1, 3, 2, 2, 2],  # 5 columns with different weights
            table_name="Users",
        )
        self.user_table.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 15))

    def _get_formatted_user_data(self):
        """Get and format user data for the table"""
        try:
            users_data = get_all_users()
            formatted_data = []

            for idx, user in enumerate(users_data):
                # Format membership type
                membership_type = getattr(user, "membership_type", "Basic")

                # Format status (assuming active by default if not specified)
                status = (
                    "Active"  # Could be extended if status field exists in user model
                )

                # Format join date (created_at)
                join_date_str = "N/A"
                if hasattr(user, "created_at") and user.created_at:
                    from datetime import datetime

                    if isinstance(user.created_at, str):
                        try:
                            date_part = user.created_at.split(" ")[0]
                            dt = datetime.strptime(date_part, "%Y-%m-%d")
                            join_date_str = dt.strftime("%d/%m/%Y")
                        except (ValueError, IndexError):
                            join_date_str = str(user.created_at)
                    else:
                        join_date_str = user.created_at.strftime("%d/%m/%Y")

                # Get user name safely
                user_name = getattr(user, "name", "Unknown")
                user_lastname = getattr(user, "lastname", "")
                full_name = f"{user_name} {user_lastname}".strip()

                formatted_data.append(
                    [
                        str(idx + 1),  # Use sequential ID starting from 1
                        full_name,
                        membership_type.capitalize(),
                        status,
                        join_date_str,
                    ]
                )

            return formatted_data
        except Exception as e:
            print(f"Error formatting user data: {e}")
            return []

    def _show_user_configuration(self, username):
        # Clear previous content
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Create a title
        title_label = ctk.CTkLabel(
            self.content_container,
            text=f"User Configuration: {username}",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=20, pady=20)

        # Configuration content would go here
