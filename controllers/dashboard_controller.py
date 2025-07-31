"""
Controller to handle dashboard logic.
Applies the MVC pattern correctly: the controller handles business logic
and coordination between the model (data) and the view (UI).
"""

from controllers.crud import create_admin, is_admin
from services.data_formatter import DataFormatter
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
        Advanced search with multiple algorithms optimized with comprehensions:
        1. Exact match (highest priority)
        2. Fuzzy match
        3. Partial word match
        """
        if not query.strip():
            return data

        query = query.strip()

        # Use list comprehension with any() for O(n) complexity
        return [
            row for row in data
            if any(
                self._exact_match(str(cell), query)
                or self._fuzzy_match(str(cell), query, threshold=0.6)
                or self._partial_word_match(str(cell), query)
                for cell in row
            )
        ]

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
            elif table_name == "admins_extended":
                self._data_cache[table_name] = (
                    self.data_formatter.get_formatted_admin_data_extended()
                )
            elif table_name == "trainers":
                self._data_cache[table_name] = (
                    self.data_formatter.get_formatted_trainer_data()
                )
            elif table_name == "trainers_with_real_ids":
                self._data_cache[table_name] = (
                    self.data_formatter.get_formatted_trainer_data_with_real_ids()
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
        """Clear filter cache for specific table using optimized filtering"""
        # Use dict comprehension to rebuild cache without matching keys (O(n) single pass)
        self._filter_cache = {
            key: value for key, value in self._filter_cache.items()
            if not key.startswith(f"{table_name}_")
        }

    def invalidate_cache(self, table_name: str):
        """Invalidate cache for specific table (call after data changes)"""
        self._cache_dirty[table_name] = True
        self._clear_filter_cache(table_name)

        # If admins cache is invalidated, also invalidate extended cache
        if table_name == "admins":
            self._cache_dirty["admins_extended"] = True
            self._clear_filter_cache("admins_extended")

        # If trainers cache is invalidated, also invalidate real IDs cache
        if table_name == "trainers":
            self._cache_dirty["trainers_with_real_ids"] = True
            self._clear_filter_cache("trainers_with_real_ids")

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

    def get_admin_data_unified(
        self, admin_id: str, from_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Unified method to get admin data by ID from cache or database

        Args:
            admin_id: Admin ID
            from_cache: If True, use cached data; if False, query database directly

        Returns:
            Dict with admin data or None if not found
        """
        try:
            if from_cache:
                # Use cached extended data with real IDs for better matching
                admin_data_list = self._get_cached_data("admins_extended")
                admin_id_str = str(admin_id)

                # Use next() with generator for O(1) early termination
                admin_row = next(
                    (row for row in admin_data_list if str(row[0]) == admin_id_str),
                    None
                )

                if admin_row:
                    return {
                        "id": admin_row[0],
                        "username": admin_row[1],
                        "role": admin_row[2].lower(),
                        "created_at": admin_row[3],
                        "unique_id": admin_row[0],
                        "trainer_id": admin_row[4],
                    }
                return None
            else:
                # Query database directly (fresh data)
                from controllers.crud import get_admin

                admin = get_admin(admin_id)
                if not admin:
                    return None

                return {
                    "id": admin.unique_id,
                    "username": admin.username,
                    "role": admin.role,
                    "created_at": admin.created_at,
                    "unique_id": admin.unique_id,
                    "trainer_id": getattr(admin, 'trainer_id', None),
                }
        except Exception:
            return None

    def get_admin_username_from_cache(self, admin_id: str) -> str:
        """Get admin username by ID from cached data"""
        try:
            admin_data = self.get_admin_data_unified(admin_id, from_cache=True)
            return (
                admin_data.get("username", "administrator")
                if admin_data
                else "administrator"
            )
        except Exception:
            return "administrator"

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

    def _handle_database_error(
        self, error: Exception, username: str = ""
    ) -> Dict[str, Any]:
        """
        Handle database errors and return appropriate error messages

        Args:
            error: The exception that occurred
            username: The username involved in the operation (for context)

        Returns:
            Dict with success=False and appropriate error message
        """
        error_message = str(error)

        # Handle specific database constraint errors
        if "UNIQUE constraint failed: admins.username" in error_message:
            return {
                "success": False,
                "message": f"Username '{username}' is already taken. "
                f"Please choose a different username.",
            }
        elif "UNIQUE constraint failed" in error_message:
            return {
                "success": False,
                "message": "This information is already in use. Please check your input.",
            }
        elif "NOT NULL constraint failed" in error_message:
            return {
                "success": False,
                "message": "Required information is missing. Please fill all required fields.",
            }
        elif "Admin not found" in error_message or "not found" in error_message:
            return {
                "success": False,
                "message": "The administrator could not be found.",
            }
        else:
            return {"success": False, "message": f"Database error: {error_message}"}

    def save_admin_data(
        self, admin_data: Dict[str, Any], admin_form_or_id=None
    ) -> Dict[str, Any]:
        """
        Create or update an admin based on admin_form_or_id parameter.

        Args:
            admin_data: Dict with admin data (username, password, role, etc.)
            admin_form_or_id: Can be:
                - AdminFormView object (has admin_to_edit attribute) for form operations
                - String/Int ID for direct profile updates
                - None for creating new admin

        Returns:
            Dict with success status and message
        """
        try:
            # Determine if we're updating
            admin_id_to_update = None

            if admin_form_or_id:
                if isinstance(admin_form_or_id, (str, int)):
                    # Direct ID passed (from user_config.py) - can be string or int
                    admin_id_to_update = str(admin_form_or_id)
                elif (
                    hasattr(admin_form_or_id, "admin_to_edit")
                    and admin_form_or_id.admin_to_edit
                ):
                    # Form object with admin_to_edit (from admin_form.py)
                    admin_id_to_update = admin_form_or_id.admin_to_edit

            if admin_id_to_update:
                # UPDATE EXISTING ADMIN
                from controllers.crud import get_admin, update_admin

                # Get existing admin first
                existing_admin = get_admin(admin_id_to_update)
                if not existing_admin:
                    return {"success": False, "message": "Admin not found"}

                # Update only provided fields
                if admin_data.get("username"):
                    existing_admin.username = admin_data["username"]

                # Only update password if provided
                if admin_data.get("password"):
                    existing_admin.set_password(admin_data["password"])

                # Update role if provided
                if admin_data.get("role"):
                    existing_admin.role = admin_data["role"]

                # Attempt to update - CRUD will raise exceptions on errors
                update_admin(existing_admin)

                # If we reach here, update was successful
                self.invalidate_cache("admins")
                return {
                    "success": True,
                    "message": f"Administrator '{existing_admin.username}' "
                    f"updated successfully",
                    "updated_username": existing_admin.username,
                }
            else:
                # CREATE NEW ADMIN
                # For creation, password is required
                if not admin_data.get("password"):
                    return {
                        "success": False,
                        "message": "Password is required for new administrators",
                    }

                admin = Admin(
                    username=admin_data.get("username"),
                    password=admin_data.get("password"),
                    role=admin_data.get("role", "admin"),
                )

                # Attempt to create - CRUD will raise exceptions on errors
                create_admin(admin)

                # If we reach here, creation was successful
                self.invalidate_cache("admins")
                return {
                    "success": True,
                    "message": f"Administrator '{admin.username}' created successfully",
                }
        except Exception as e:
            # Use the centralized error handler
            username = admin_data.get("username", "")
            return self._handle_database_error(e, username)

    def refresh_admin_profile(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """Refresh and get updated admin profile data"""
        # Invalidate cache to ensure fresh data
        self.invalidate_cache("admins")
        return self.get_admin_data_unified(admin_id, from_cache=False)

    def can_create_admin_accounts(self, current_admin) -> bool:
        """
        Business logic: Check if current user can create admin accounts

        Args:
            current_admin: Current admin object from session

        Returns:
            True if user can create admin accounts, False otherwise
        """
        if not current_admin:
            return False

        # Get admin ID from current_admin object
        admin_id = getattr(current_admin, "unique_id", None) or getattr(
            current_admin, "id", None
        )

        if not admin_id:
            return False

        # Use existing method to get admin data
        admin_data = self.get_admin_data_unified(admin_id, from_cache=True)
        if not admin_data:
            return False

        role = admin_data.get("role", "").lower().strip()
        is_admin = role == "admin"

        return is_admin

    def get_available_trainers_for_manager(self) -> List[List[Any]]:
        """
        Get trainers that are not yet associated with any manager account
        Uses cached data efficiently with optimized algorithms

        Returns:
            List of trainer data for trainers not associated with managers
            (with sequential IDs for display)
        """
        try:
            # Get cached data efficiently
            trainers_with_real_ids = self._get_cached_data("trainers_with_real_ids")
            extended_admin_data = self._get_cached_data("admins_extended")

            # Extract associated trainer IDs using set comprehension (O(n) instead of O(n²))
            associated_trainer_ids = {
                str(admin_row[4]) for admin_row in extended_admin_data
                if len(admin_row) >= 5 and admin_row[4] is not None
            }

            # Filter available trainers using list comprehension with enumeration
            available_trainers_with_real_ids = [
                trainer_row for trainer_row in trainers_with_real_ids
                if str(trainer_row[0]) not in associated_trainer_ids
            ]

            # Convert to display format using list comprehension (O(n) single pass)
            return [
                [str(idx + 1), trainer_row[1], trainer_row[2], trainer_row[3]]
                for idx, trainer_row in enumerate(available_trainers_with_real_ids)
            ]

        except Exception as e:
            # If extended data fails, fallback to all trainers (with sequential IDs)
            print(f"Warning: Could not filter trainers by association: {e}")
            return self._get_cached_data("trainers")
