"""
Controlador para manejar la lógica del dashboard.
Aplica el patrón MVC correctamente: el controlador maneja la lógica de negocio
y la coordinación entre el modelo (datos) y la vista (UI).
"""
from controllers.crud import is_admin
from services.data_formatter import DataFormatter


class DashboardController:
    """
    Controlador que maneja la lógica del dashboard.
    Separa la lógica de negocio de la vista, siguiendo el patrón MVC.
    """

    def __init__(self):
        # Inyección de dependencia del servicio de formateo
        self.data_formatter = DataFormatter()

    def get_admin_data(self):
        """
        Obtiene datos de administradores formateados para la vista.
        El controlador coordina entre el modelo (datos) y los servicios.
        """
        return self.data_formatter.get_formatted_admin_data()

    def get_trainer_data(self):
        """Obtiene datos de entrenadores formateados para la vista"""
        return self.data_formatter.get_formatted_trainer_data()

    def get_user_data(self):
        """Obtiene datos de usuarios formateados para la vista"""
        return self.data_formatter.get_formatted_user_data()

    def get_default_section(self, current_admin):
        """
        Determina qué sección mostrar por defecto según el tipo de usuario.
        Lógica de negocio que no pertenece en la vista.
        """
        return "Admins" if is_admin(current_admin.username) else "Trainers"

    def should_show_configuration(self, section_name):
        """Verifica si una sección es de configuración"""
        return section_name.startswith("Configuration ")

    def extract_username_from_config_section(self, section_name):
        """Extrae el nombre de usuario de una sección de configuración"""
        return section_name.split(" ", 1)[1]
