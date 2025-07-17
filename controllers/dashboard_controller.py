"""
Controller to handle dashboard logic.
Applies the MVC pattern correctly: the controller handles business logic
and coordination between the model (data) and the view (UI).
"""

from controllers.crud import is_admin
from services.data_formatter import DataFormatter
from controllers.crud import create_admin, update_admin
from models.admin import Admin
from typing import List, Dict, Any, Optional
import difflib
import unicodedata


class DashboardController:
    """
    Controller that handles dashboard logic.
    Separates business logic from the view, following the MVC pattern.
    Implements smart caching to optimize queries and filtering.
    """

    def __init__(self):
        # Dependency injection of the formatting service
        self.data_formatter = DataFormatter()

        # Cache system with intelligent invalidation
        self._data_cache: Dict[str, List[List[Any]]] = {}
        self._filter_cache: Dict[str, List[List[Any]]] = {}
        self._cache_dirty: Dict[str, bool] = {
            "admins": True,
            "trainers": True,
            "users": True,
        }

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text by removing accents and converting to lowercase.
        Examples: 'María' -> 'maria', 'José' -> 'jose'
        """
        # Convert to string and lowercase
        text = str(text).lower()

        # Remove accents using Unicode normalization
        # NFD = Canonical Decomposition (separates base char from accent)
        normalized = unicodedata.normalize("NFD", text)

        # Filter out accent marks (combining characters)
        without_accents = "".join(
            char
            for char in normalized
            if unicodedata.category(char) != "Mn"  # Mn = Nonspacing_Mark (accents)
        )

        return without_accents

    def _fuzzy_match(self, text: str, query: str, threshold: float = 0.6) -> bool:
        """
        Fuzzy matching algorithm using difflib with accent normalization.
        Returns True if similarity ratio >= threshold
        """
        if not query:
            return True

        # Normalize both text and query (removes accents)
        text_normalized = self._normalize_text(text)
        query_normalized = self._normalize_text(query)

        # Exact substring match (highest priority)
        if query_normalized in text_normalized:
            return True

        # Fuzzy match using sequence matching
        similarity = difflib.SequenceMatcher(
            None, text_normalized, query_normalized
        ).ratio()
        return similarity >= threshold

    def _advanced_search(self, data: List[List[Any]], query: str) -> List[List[Any]]:
        """
        Advanced search with multiple algorithms:
        1. Exact match (highest priority)
        2. Fuzzy match
        3. Partial word match
        """
        if not query.strip():
            return data

        query = query.strip()
        results = []

        for row in data:
            match_found = False

            for cell in row:
                cell_str = str(cell)

                # Try different matching strategies
                if (
                    self._exact_match(cell_str, query)
                    or self._fuzzy_match(cell_str, query, threshold=0.6)
                    or self._partial_word_match(cell_str, query)
                ):
                    match_found = True
                    break

            if match_found:
                results.append(row)

        return results

    def _exact_match(self, text: str, query: str) -> bool:
        """Exact substring matching (case-insensitive, accent-insensitive)"""
        text_normalized = self._normalize_text(text)
        query_normalized = self._normalize_text(query)
        return query_normalized in text_normalized

    def _partial_word_match(self, text: str, query: str) -> bool:
        """Match if query words are found in text"""
        text_words = str(text).lower().split()
        query_words = query.lower().split()

        return any(
            any(query_word in text_word for text_word in text_words)
            for query_word in query_words
        )

    def _get_cached_data(self, table_name: str) -> List[List[Any]]:
        """Get data from cache or fetch if cache is dirty"""
        if (
            self._cache_dirty.get(table_name, True)
            or table_name not in self._data_cache
        ):
            # Cache is dirty or empty, fetch fresh data
            if table_name == "admins":
                self._data_cache[table_name] = (
                    self.data_formatter.get_formatted_admin_data()
                )
            elif table_name == "trainers":
                self._data_cache[table_name] = (
                    self.data_formatter.get_formatted_trainer_data()
                )
            elif table_name == "users":
                self._data_cache[table_name] = (
                    self.data_formatter.get_formatted_user_data()
                )

            # Mark as clean and clear related filter cache
            self._cache_dirty[table_name] = False
            self._clear_filter_cache(table_name)

        return self._data_cache[table_name]

    def _clear_filter_cache(self, table_name: str):
        """Clear filter cache for specific table"""
        keys_to_remove = [
            key for key in self._filter_cache.keys() if key.startswith(f"{table_name}_")
        ]
        for key in keys_to_remove:
            del self._filter_cache[key]

    def invalidate_cache(self, table_name: str):
        """Invalidate cache for specific table (call after data changes)"""
        self._cache_dirty[table_name] = True
        self._clear_filter_cache(table_name)

    def filter_data(self, table_name: str, query: str) -> List[List[Any]]:
        """Filter data with advanced search algorithms and caching"""
        if not query.strip():
            return self._get_cached_data(table_name)

        # Check filter cache
        cache_key = f"{table_name}_{query.lower()}"
        if cache_key in self._filter_cache:
            return self._filter_cache[cache_key]

        # Get original data and apply advanced search
        original_data = self._get_cached_data(table_name)
        filtered_data = self._advanced_search(original_data, query)

        # Cache the filtered result
        self._filter_cache[cache_key] = filtered_data
        return filtered_data

    def get_admin_data(self):
        """
        Gets formatted admin data for the view.
        The controller coordinates between the model (data) and the services.
        """
        return self._get_cached_data("admins")

    def get_trainer_data(self):
        """Gets formatted trainer data for the view"""
        return self._get_cached_data("trainers")

    def get_user_data(self):
        """Gets formatted user data for the view"""
        return self._get_cached_data("users")

    def get_admin_by_id_from_cache(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """Get admin data by ID from cached data"""
        try:
            admin_data_list = self.get_admin_data()  # Uses cached data

            # Find admin by ID in the cached formatted data
            for admin_row in admin_data_list:
                if admin_row[0] == admin_id:  # ID is at index 0
                    return {
                        'id': admin_row[0],
                        'username': admin_row[1],
                        'role': admin_row[2].lower(),  # Convert "Admin"/"Manager" to lowercase
                        'created_at': admin_row[3]
                    }
            return None
        except Exception:
            return None

    def get_admin_username_from_cache(self, admin_id: str) -> str:
        """Get admin username by ID from cached data"""
        try:
            admin_data = self.get_admin_by_id_from_cache(admin_id)
            return admin_data.get('username', 'administrator') if admin_data else 'administrator'
        except Exception:
            return 'administrator'

    def get_default_section(self, current_admin):
        """
        Determines which section to show by default according to the user type.
        Business logic that does not belong in the view.
        """
        return "Admins" if is_admin(current_admin.username) else "Trainers"

    def should_show_configuration(self, section_name):
        """Checks if a section is a configuration section"""
        return section_name.startswith("Configuration ")

    def extract_username_from_config_section(self, section_name):
        """Extracts the username from a configuration section"""
        return section_name.split(" ", 1)[1]

    def save_admin_data(self, admin_data: Dict[str, Any], admin_form) -> Dict[str, Any]:
        """
        Create or update an admin based on whether admin_form has admin_to_edit.
        Returns a dictionary with success status and message.
        """
        try:
            # Create Admin object from form data
            admin = Admin(
                username=admin_data.get("username"),
                password=admin_data.get("password"),
                role=admin_data.get("role", "admin")
            )

            # Check if we're updating (admin_form has admin_to_edit)
            if admin_form.admin_to_edit:

                # Set the ID for update
                admin.unique_id = admin_form.admin_to_edit

                success = update_admin(admin)

                if success:
                    # Invalidate cache after successful update
                    self.invalidate_cache("admins")
                    return {
                        "success": True,
                        "message": f"Administrator '{admin.username}' updated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to update administrator '{admin.username}'"
                    }
            else:
                # Create new admin
                created_admin = create_admin(admin)

                if created_admin:
                    # Invalidate cache after successful creation
                    self.invalidate_cache("admins")
                    return {
                        "success": True,
                        "message": f"Administrator '{admin.username}' created successfully"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Username '{admin.username}' already exists or creation failed"
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error saving admin: {str(e)}"
            }
