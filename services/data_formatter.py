"""
Servicio para formatear datos de diferentes entidades.
Aplica el Principio de Responsabilidad Única: cada formateador se encarga de un tipo de dato.
"""
from datetime import datetime
from controllers.crud import get_all_admins, get_all_trainers, get_all_users


class DataFormatter:
    """Servicio principal para coordinar el formateo de datos"""

    def get_formatted_admin_data(self):
        """Obtiene y formatea datos de administradores"""
        admins_data = get_all_admins()
        formatted_data = []

        for idx, admin in enumerate(admins_data):
            # Format created_at date if available
            created_at_str = self._format_date(admin.created_at)

            formatted_data.append([
                str(idx + 1),  # Use sequential ID starting from 1
                admin.username,
                admin.role.capitalize() if admin.role else "Admin",
                created_at_str,
            ])

        return formatted_data

    def get_formatted_admin_data_extended(self):
        """
        Obtiene datos de administradores con IDs reales y asociaciones de trainers
        Mantiene compatibilidad pero agrega información necesaria para filtros
        """
        admins_data = get_all_admins()
        formatted_data = []

        for admin in admins_data:
            # Format created_at date if available
            created_at_str = self._format_date(admin.created_at)

            # Get real admin ID safely
            admin_id = getattr(admin, 'unique_id', None) or getattr(admin, 'id', None)

            # Get associated trainer ID using the new trainer_id property
            trainer_id = getattr(admin, 'trainer_id', None)

            formatted_data.append([
                str(admin_id) if admin_id else "N/A",  # Real admin ID
                admin.username,
                admin.role.capitalize() if admin.role else "Admin",
                created_at_str,
                trainer_id,  # Associated trainer ID from the model
            ])

        return formatted_data

    def get_formatted_trainer_data(self):
        """Obtiene y formatea datos de entrenadores"""
        try:
            trainers_data = get_all_trainers()
            formatted_data = []

            for trainer in trainers_data:
                # Format start_time and end_time if available
                schedule_str = self._format_schedule(trainer)

                # Get trainer name safely
                full_name = self._format_full_name(trainer)

                # Get specialty safely
                specialty = getattr(trainer, "specialty", "Trainer")

                # Get real trainer ID safely (for proper association filtering)
                trainer_id = getattr(trainer, 'unique_id', None) or getattr(trainer, 'id', None)

                formatted_data.append([
                    str(trainer_id) if trainer_id else "N/A",  # Use real ID for proper filtering
                    full_name,
                    specialty,
                    schedule_str,
                ])

            return formatted_data
        except Exception as e:
            print(f"Error formatting trainer data: {e}")
            return []

    def get_formatted_user_data(self):
        """Obtiene y formatea datos de usuarios"""
        try:
            users_data = get_all_users()
            formatted_data = []

            for idx, user in enumerate(users_data):
                # Format membership type
                membership_type = getattr(user, "membership_type", "Basic")

                # Format status (assuming active by default if not specified)
                status = "Active"  # Could be extended if status field exists in user model

                # Format join date (created_at)
                join_date_str = self._format_date(user.created_at)

                # Get user name safely
                full_name = self._format_full_name(user)

                formatted_data.append([
                    str(idx + 1),  # Use sequential ID starting from 1
                    full_name,
                    membership_type.capitalize(),
                    status,
                    join_date_str,
                ])

            return formatted_data
        except Exception as e:
            print(f"Error formatting user data: {e}")
            return []

    def _format_date(self, date_value):
        """Método utilitario para formatear fechas de manera consistente"""
        if not hasattr(date_value, '__str__') or not date_value:
            return "N/A"

        try:
            if isinstance(date_value, str):
                # Assume format is "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD"
                date_part = date_value.split(" ")[0]
                dt = datetime.strptime(date_part, "%Y-%m-%d")
                return dt.strftime("%d/%m/%Y")
            else:
                # It's a datetime object
                return date_value.strftime("%d/%m/%Y")
        except (ValueError, IndexError):
            return str(date_value)

    def _format_schedule(self, trainer):
        """Método utilitario para formatear horarios de entrenadores"""
        if hasattr(trainer, "start_time") and hasattr(trainer, "end_time"):
            if trainer.start_time and trainer.end_time:
                return f"{trainer.start_time} - {trainer.end_time}"
            elif trainer.start_time:
                return f"From {trainer.start_time}"
            elif trainer.end_time:
                return f"Until {trainer.end_time}"
        return "N/A"

    def _format_full_name(self, person):
        """Método utilitario para formatear nombres completos"""
        name = getattr(person, "name", "Unknown")
        lastname = getattr(person, "lastname", "")
        return f"{name} {lastname}".strip()
