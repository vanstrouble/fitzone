"""
Controller to handle dashboard logic.
Applies the MVC pattern correctly: the controller handles business logic
and coordination between the model (data) and the view (UI).
"""

from controllers.crud import (
    create_admin,
    is_admin,
    delete_trainer,
    delete_user,
    delete_admin_by_username,
)
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
            elif table_name == "users_with_real_ids":
                # Real user IDs aligned with the standard users table ordering
                try:
                    self._data_cache[table_name] = (
                        self.data_formatter.get_formatted_user_data_with_real_ids()
                    )
                except Exception:
                    # Fallback to basic user data if extended method is unavailable
                    self._data_cache[table_name] = self._data_cache.get("users", [])
            elif table_name == "available trainers":
                # Handle available trainers for search (4 columns without Manager column)
                self._data_cache[table_name] = self.get_available_trainers_for_form()
            else:
                # Handle unknown table names gracefully
                print(f"Warning: Unknown table name '{table_name}', returning empty data")
                self._data_cache[table_name] = []

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

        # Handle dependent cache invalidations
        dependencies = {
            "admins": ["admins_extended"],
            "trainers": ["trainers_with_real_ids"],
            "users": ["users_with_real_ids"],
        }

        for dependent in dependencies.get(table_name, []):
            self._cache_dirty[dependent] = True
            self._clear_filter_cache(dependent)

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
        self, admin_id: str, from_cache: bool = True, by_sequential_id: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Unified method to get admin data by ID from cache or database

        Args:
            admin_id: Admin ID (real ID or sequential ID based on by_sequential_id flag)
            from_cache: If True, use cached data; if False, query database directly
            by_sequential_id: If True, treat admin_id as sequential ID from table display

        Returns:
            Dict with admin data or None if not found
        """
        try:
            if by_sequential_id:
                # Get username from sequential ID, then get full data
                username = self.get_admin_username_from_sequential_id(admin_id)
                if not username:
                    return None

                # Get admin data by username from cache
                admin_data_list = self._get_cached_data("admins_extended")
                admin_row = next(
                    (row for row in admin_data_list if row[1] == username), None
                )

                if admin_row:
                    return {
                        "id": admin_row[0],
                        "username": admin_row[1],
                        "role": admin_row[2].lower(),
                        "created_at": admin_row[3],
                        "unique_id": admin_row[0],
                        "trainer_id": admin_row[4] if len(admin_row) > 4 else None,
                    }
                return None

            elif from_cache:
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
                        "trainer_id": admin_row[4] if len(admin_row) > 4 else None,
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
                    "role": admin.role.lower() if admin.role else "admin",
                    "created_at": admin.created_at,
                    "unique_id": admin.unique_id,
                    "trainer_id": getattr(admin, 'trainer_id', None),
                }
        except Exception:
            return None

    def get_admin_username_from_cache(self, admin_id: str) -> str:
        """
        Get admin username by sequential ID from cached data (for deletion confirmations)

        Args:
            admin_id: Sequential ID from the table display (1, 2, 3, etc.)

        Returns:
            Username of the admin or fallback if not found
        """
        username = self.get_admin_username_from_sequential_id(admin_id)
        return username if username else "administrator"

    def get_admin_username_from_sequential_id(self, sequential_id: str) -> Optional[str]:
        """
        Get admin username from sequential ID shown in table

        Args:
            sequential_id: Sequential ID shown in the table (1, 2, 3, etc.)

        Returns:
            Username of the admin or None if not found
        """
        try:
            admin_data_list = self._get_cached_data("admins")
            sequential_id_int = int(sequential_id)

            # Sequential IDs start from 1, list indices start from 0
            if 1 <= sequential_id_int <= len(admin_data_list):
                admin_row = admin_data_list[sequential_id_int - 1]
                # Username is typically in the second column (index 1)
                return admin_row[1] if len(admin_row) > 1 else None

            return None
        except (ValueError, IndexError, Exception):
            return None

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

    def _is_person_email_in_use(self, email: Optional[str]) -> bool:
        """Return True if email is already used by any User or Trainer."""
        if not email:
            return False
        email_n = str(email).strip().lower()
        try:
            from controllers.crud import get_all_users, get_all_trainers
            for u in get_all_users() or []:
                if str(getattr(u, "email", "")).strip().lower() == email_n:
                    return True
            for t in get_all_trainers() or []:
                if str(getattr(t, "email", "")).strip().lower() == email_n:
                    return True
            return False
        except Exception:
            # If check fails, do not block; let DB enforce uniqueness
            return False

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
        if "UNIQUE constraint failed: persons.email" in error_message:
            return {
                "success": False,
                "message": "Email already in use. Use a different email.",
            }
        elif "UNIQUE constraint failed: admins.username" in error_message:
            return {
                "success": False,
                "message": f"Username '{username}' already taken. Choose a different one.",
            }
        elif "UNIQUE constraint failed" in error_message:
            return {"success": False, "message": "Data already in use. Check your input."}
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
            admin_data: Dict with admin data (username, password, role, trainer_id, etc.)
            admin_form_or_id: Can be:
                - AdminFormView object (has admin_to_edit attribute) for form operations
                - String/Int ID for direct profile updates
                - None for creating new admin

        Returns:
            Dict with success status and message
        """
        # Protection against double execution
        import time
        current_time = time.time()
        last_call_key = f"save_admin_{admin_data.get('username', '')}"

        if hasattr(self, '_last_save_calls'):
            if last_call_key in self._last_save_calls:
                time_diff = current_time - self._last_save_calls[last_call_key]
                if time_diff < 1.0:  # Less than 1 second apart
                    print(f"DEBUG: Ignoring duplicate save call for {admin_data.get('username')} "
                          f"(time diff: {time_diff:.2f}s)")
                    return {"success": False, "message": "Operation already in progress"}
        else:
            self._last_save_calls = {}

        self._last_save_calls[last_call_key] = current_time

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
                    # This could be a sequential ID, need to get the real ID
                    sequential_id = admin_form_or_id.admin_to_edit
                    admin_data_from_cache = self.get_admin_data_unified(
                        sequential_id, from_cache=True, by_sequential_id=True
                    )
                    if admin_data_from_cache:
                        admin_id_to_update = str(admin_data_from_cache["unique_id"])
                    else:
                        # Fallback: try treating it as a real ID
                        admin_id_to_update = str(sequential_id)

            if admin_id_to_update:
                # UPDATE EXISTING ADMIN
                from controllers.crud import get_admin, update_admin

                # Get existing admin first
                existing_admin = get_admin(admin_id_to_update)
                if not existing_admin:
                    return {"success": False, "message": "Admin not found"}

                # Update only provided fields (non-empty values)
                if admin_data.get("username") and admin_data["username"].strip():
                    existing_admin.username = admin_data["username"].strip()

                # Only update password if provided and not empty
                if admin_data.get("password") and admin_data["password"].strip():
                    existing_admin.set_password(admin_data["password"])

                # Update role if provided
                if admin_data.get("role") and admin_data["role"].strip():
                    existing_admin.role = admin_data["role"]

                # Handle trainer association for managers
                if admin_data.get("role") == "manager":
                    trainer_id = admin_data.get("trainer_id")

                    # ALWAYS clear existing associations for this admin first
                    username = str(existing_admin.username) if existing_admin.username else ""
                    if username:
                        self._clear_trainer_admin_association(username)
                        # Force cache invalidation to ensure fresh data
                        self.invalidate_cache("trainers")

                    if trainer_id and trainer_id.strip():
                        # Convert sequential ID to real trainer ID if needed
                        real_trainer_id = self._get_real_trainer_id(trainer_id.strip())

                        # Update trainer to point to this admin
                        from controllers.crud import get_trainer, update_trainer
                        trainer = get_trainer(real_trainer_id)
                        if trainer:
                            current_admin_username = getattr(trainer, 'admin_username', None)

                            # ALWAYS clear any existing association for this trainer first
                            if current_admin_username:
                                setattr(trainer, 'admin_username', None)
                                update_trainer(trainer)

                            # Set new admin_username attribute
                            setattr(trainer, 'admin_username', existing_admin.username)

                            # Update trainer in database
                            success = update_trainer(trainer)
                            if not success:
                                print(f"Warning: Failed to update trainer {real_trainer_id}")
                else:
                    # Not a manager role, clear trainer association
                    username = str(existing_admin.username) if existing_admin.username else ""
                    if username:
                        self._clear_trainer_admin_association(username)

                # Attempt to update - CRUD will raise exceptions on errors
                update_admin(existing_admin)

                # If we reach here, update was successful
                self.invalidate_cache("admins")
                self.invalidate_cache("trainers")  # Trainer associations might have changed
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

                # Handle trainer association for new managers
                if admin_data.get("role") == "manager":
                    trainer_id = admin_data.get("trainer_id")
                    if trainer_id and trainer_id.strip():
                        # Convert sequential ID to real trainer ID if needed
                        real_trainer_id = self._get_real_trainer_id(trainer_id.strip())

                        # Create admin first, then associate trainer
                        create_admin(admin)

                        # Now associate trainer with this admin
                        from controllers.crud import get_trainer, update_trainer
                        trainer = get_trainer(real_trainer_id)
                        if trainer:
                            current_admin_username = getattr(trainer, 'admin_username', None)

                            # Clear any existing association for this trainer
                            if current_admin_username:
                                setattr(trainer, 'admin_username', None)
                                update_trainer(trainer)

                            setattr(trainer, 'admin_username', admin.username)

                            success = update_trainer(trainer)
                            if not success:
                                print(f"Warning: Failed to update trainer {real_trainer_id}")
                    else:
                        # Create admin without trainer association
                        create_admin(admin)
                else:
                    # Not a manager, just create admin
                    create_admin(admin)

                # If we reach here, creation was successful
                self.invalidate_cache("admins")
                self.invalidate_cache("trainers")  # Trainer associations might have changed
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

    def get_available_trainers(self, for_form: bool = False) -> List[List[Any]]:
        """
        Get trainers that are not yet associated with any manager account

        Args:
            for_form: If True, returns only 4 columns for form compatibility.
                     If False, returns 5 columns including Manager column.

        Returns:
            List of trainer data for trainers not associated with managers
            (with sequential IDs for display)
        """
        try:
            # Get trainers with real IDs for filtering logic
            trainers_with_real_ids = self._get_cached_data("trainers_with_real_ids")
            extended_admin_data = self._get_cached_data("admins_extended")

            # Extract trainer IDs that are already associated with managers
            associated_trainer_ids = {
                str(admin_row[4]) for admin_row in extended_admin_data
                if len(admin_row) >= 5 and admin_row[4] is not None
            }

            # Filter available trainers using list comprehension
            available_trainers_with_real_ids = [
                trainer_row for trainer_row in trainers_with_real_ids
                if str(trainer_row[0]) not in associated_trainer_ids
            ]

            # Convert to display format with sequential IDs
            if for_form:
                # Only 4 columns for form compatibility
                return [
                    [str(idx + 1), trainer_row[1], trainer_row[2], trainer_row[3]]
                    for idx, trainer_row in enumerate(available_trainers_with_real_ids)
                ]
            else:
                # Full 5 columns including Manager column
                return [
                    [str(idx + 1), trainer_row[1], trainer_row[2], trainer_row[3], trainer_row[4]]
                    for idx, trainer_row in enumerate(available_trainers_with_real_ids)
                ]

        except Exception as e:
            # If extended data fails, fallback to basic trainer data
            print(f"Warning: Could not filter trainers by association: {e}")
            basic_trainers = self._get_cached_data("trainers")

            if for_form:
                # Ensure we only return 4 columns even from basic data
                return [trainer[:4] for trainer in basic_trainers]
            else:
                return basic_trainers

    def get_available_trainers_for_manager(self) -> List[List[Any]]:
        """
        Get trainers available for manager view (5 columns including Manager)

        Returns:
            List of trainer data for trainers not associated with managers
        """
        return self.get_available_trainers(for_form=False)

    def get_available_trainers_for_form(self) -> List[List[Any]]:
        """
        Get trainers available for manager association - FOR ADMIN FORM USE ONLY
        Returns only 4 columns (without Manager column) for form compatibility

        Returns:
            List of trainer data [ID, Name, Specialty, Schedule] for form display
        """
        return self.get_available_trainers(for_form=True)

    def _validate_admin_deletion(
        self, current_admin, target_username: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validate if admin deletion is allowed. Returns error dict if not allowed, None if valid.

        Args:
            current_admin: Admin object of the currently logged-in user
            target_username: Username of the admin to delete

        Returns:
            Dict with error if validation fails, None if validation passes
        """
        # Prevent deletion of default admin
        if target_username == "admin":
            return {
                "success": False,
                "message": (
                    f"Cannot delete '{target_username}' - this is the default "
                    f"system administrator account and must be preserved."
                )
            }

        # Get current admin ID
        current_id = getattr(current_admin, "unique_id", None) or getattr(
            current_admin, "id", None
        )

        if not current_id:
            return {
                "success": False,
                "message": "Authentication error. Please log in again and try."
            }

        # Prevent self-deletion
        if current_admin.username == target_username:
            return {
                "success": False,
                "message": (
                    f"You cannot delete your own account ('{target_username}'). "
                    f"Ask another administrator to remove your account if needed."
                )
            }

        return None  # Validation passed

    def delete_admin_with_permissions(self, current_admin, admin_id_to_delete) -> Dict[str, Any]:
        """
        Legacy method - delegates to universal delete_entity for backward compatibility
        """
        return self.delete_entity(current_admin, "admin", admin_id_to_delete)

    def delete_entity(
        self, current_admin, entity_type: str, entity_id_to_delete
    ) -> Dict[str, Any]:
        """
        Universal delete function for all entity types (admins, trainers, users).
        Maintains existing admin deletion hierarchy: Admin can delete anyone,
        Manager can only delete other managers.
        For trainers and users: Both Admin and Manager can delete them since
        they don't access the system.

        Args:
            current_admin: Admin object of the currently logged-in user
            entity_type: Type of entity to delete ("admin", "trainer", "user")
            entity_id_to_delete: Sequential ID of the entity to delete (from table display)

        Returns:
            Dict with success status and message
        """
        try:
            entity_type = entity_type.lower().strip()

            # Get entity identifier (username for admins, name for others)
            entity_identifier = self._get_entity_identifier(entity_type, entity_id_to_delete)

            if not entity_identifier:
                entity_name = {"admin": "Administrator", "trainer": "Trainer", "user": "Member"}
                return {
                    "success": False,
                    "message": (
                        f"{entity_name.get(entity_type, 'Entity')} not found. "
                        f"Please refresh the page and try again."
                    )
                }

            # Special validation for admin deletion
            if entity_type == "admin":
                validation_error = self._validate_admin_deletion(current_admin, entity_identifier)
                if validation_error:
                    return validation_error

            # Check permissions
            current_user_is_admin = self.can_create_admin_accounts(current_admin)

            # Get target entity data for permission checking
            target_entity_data = None
            target_role = None

            if entity_type == "admin":
                target_entity_data = self.get_admin_data_unified(
                    entity_id_to_delete, from_cache=True, by_sequential_id=True
                )
                if target_entity_data:
                    target_role = target_entity_data.get("role", "").lower().strip()
                else:
                    # Fallback to direct DB query
                    from controllers.crud import get_admin_by_username
                    target_admin = get_admin_by_username(entity_identifier)
                    if not target_admin:
                        return {
                            "success": False,
                            "message": (
                                f"Administrator '{entity_identifier}' not found in the system."
                            )
                        }
                    target_role = (target_admin.role or "").lower().strip()

            # Permission check: Admin can delete anyone, Manager can only delete managers
            if entity_type == "admin" and not current_user_is_admin:  # Current user is Manager
                if target_role == "admin":
                    return {
                        "success": False,
                        "message": (
                            f"Access denied. As a Manager, you cannot delete "
                            f"'{entity_identifier}' who has Administrator privileges. "
                            f"Only Administrators can delete other Administrators."
                        )
                    }

            # For trainers and users, both Admin and Manager can delete them
            # No additional permission checks needed since they don't access the system

            # Attempt deletion
            success = self._perform_entity_deletion(
                entity_type, entity_identifier, entity_id_to_delete
            )

            if success:
                # Invalidate relevant caches
                self.invalidate_cache(entity_type + "s")  # "admins", "trainers", "users"
                if entity_type == "admin":
                    # Admin deletion might affect trainer associations
                    self.invalidate_cache("trainers")

                # Success messages
                if entity_type == "admin":
                    if target_role == "manager":
                        return {
                            "success": True,
                            "message": (
                                f"Manager '{entity_identifier}' has been deleted successfully. "
                                f"Associated trainers are now available for reassignment."
                            )
                        }
                    else:
                        return {
                            "success": True,
                            "message": (
                                f"Administrator '{entity_identifier}' has been "
                                f"deleted successfully."
                            )
                        }
                elif entity_type == "trainer":
                    return {
                        "success": True,
                        "message": f"Trainer '{entity_identifier}' has been deleted successfully."
                    }
                elif entity_type == "user":
                    return {
                        "success": True,
                        "message": f"Member '{entity_identifier}' has been deleted successfully."
                    }
                else:
                    # Fallback for unknown entity types
                    return {
                        "success": True,
                        "message": f"Entity '{entity_identifier}' has been deleted successfully."
                    }
            else:
                # Failure messages
                if entity_type == "admin":
                    return {
                        "success": False,
                        "message": (
                            f"Failed to delete '{entity_identifier}'. This may be the last "
                            f"Administrator in the system, which cannot be removed to "
                            f"maintain system access."
                        )
                    }
                else:
                    entity_name = {"trainer": "Trainer", "user": "Member"}
                    return {
                        "success": False,
                        "message": (
                            f"Failed to delete {entity_name.get(entity_type, 'entity')} "
                            f"'{entity_identifier}'."
                        )
                    }

        except Exception as e:
            entity_name = {"admin": "administrator", "trainer": "trainer", "user": "member"}
            return {
                "success": False,
                "message": (
                    f"System error occurred while deleting "
                    f"{entity_name.get(entity_type, 'entity')}: {str(e)}"
                )
            }

    def _get_entity_identifier(self, entity_type: str, entity_id: str) -> Optional[str]:
        """
        Get entity identifier (username for admins, name for trainers/users) from sequential ID

        Args:
            entity_type: Type of entity ("admin", "trainer", "user")
            entity_id: Sequential ID from table display

        Returns:
            Entity identifier string or None if not found
        """
        try:
            if entity_type == "admin":
                return self.get_admin_username_from_sequential_id(entity_id)
            elif entity_type == "trainer":
                trainer_data = self._get_cached_data("trainers")
                sequential_id_int = int(entity_id)
                if 1 <= sequential_id_int <= len(trainer_data):
                    trainer_row = trainer_data[sequential_id_int - 1]
                    # Return name (typically in second column)
                    return trainer_row[1] if len(trainer_row) > 1 else None
            elif entity_type == "user":
                user_data = self._get_cached_data("users")
                sequential_id_int = int(entity_id)
                if 1 <= sequential_id_int <= len(user_data):
                    user_row = user_data[sequential_id_int - 1]
                    # Return name (typically in second column)
                    return user_row[1] if len(user_row) > 1 else None
            return None
        except (ValueError, IndexError, Exception):
            return None

    def _perform_entity_deletion(
        self, entity_type: str, entity_identifier: str, entity_id: str
    ) -> bool:
        """
        Perform the actual deletion of an entity

        Args:
            entity_type: Type of entity ("admin", "trainer", "user")
            entity_identifier: Entity identifier (username for admins, name for others)
            entity_id: Sequential ID for conversion to real ID if needed

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if entity_type == "admin":
                return delete_admin_by_username(entity_identifier)
            elif entity_type == "trainer":
                # Convert sequential ID to real trainer ID
                real_trainer_id = self._get_real_trainer_id(entity_id)
                if real_trainer_id:
                    return delete_trainer(real_trainer_id)
                return False
            elif entity_type == "user":
                # Convert sequential ID to real user ID
                real_user_id = self._get_real_user_id(entity_id)
                if real_user_id:
                    return delete_user(real_user_id)
                return False
            return False
        except Exception as e:
            print(f"Error deleting {entity_type}: {e}")
            return False

    def _get_real_trainer_id(self, sequential_or_real_id: str) -> Optional[str]:
        """
        Convert sequential trainer ID to real trainer ID

        Args:
            sequential_or_real_id: Either sequential ID (1, 2, 3...) or real DB ID

        Returns:
            Real trainer ID from database or None if not found
        """
        try:
            # Try to convert to int to see if it's a sequential ID
            sequential_id_int = int(sequential_or_real_id)

            # If it's a small number (1-1000), treat as sequential ID
            if 1 <= sequential_id_int <= 1000:
                # Get trainers with real IDs
                trainers_with_real_ids = self._get_cached_data("trainers_with_real_ids")

                # Sequential IDs start from 1, list indices start from 0
                if 1 <= sequential_id_int <= len(trainers_with_real_ids):
                    trainer_row = trainers_with_real_ids[sequential_id_int - 1]
                    # Real ID is typically in the first column (index 0)
                    return str(trainer_row[0]) if len(trainer_row) > 0 else None

                return None
            else:
                # If it's a large number, assume it's already a real ID
                return str(sequential_or_real_id)

        except (ValueError, IndexError, Exception):
            # If conversion fails, assume it's already a real ID
            return str(sequential_or_real_id) if sequential_or_real_id else None

    def _clear_trainer_admin_association(self, admin_username: str):
        """
        Clear any trainer associations for the given admin username

        Args:
            admin_username: Username of the admin whose trainer associations to clear
        """
        try:
            from controllers.crud import get_all_trainers, update_trainer

            # Get all trainers directly from database (fresh data)
            all_trainers = get_all_trainers()

            cleared_count = 0
            # Find trainers associated with this admin and clear association
            for trainer in all_trainers:
                current_admin_username = getattr(trainer, 'admin_username', None)

                if current_admin_username == admin_username:
                    setattr(trainer, 'admin_username', None)
                    success = update_trainer(trainer)
                    if success:
                        cleared_count += 1

            # Only print if there were associations to clear
            if cleared_count > 0:
                print(f"Cleared {cleared_count} trainer associations for admin {admin_username}")

        except Exception as e:
            print(f"Error clearing trainer associations: {e}")

    def create_entity_data(
        self,
        entity_type: str,
        entity_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create Admin, Trainer, or User (single-responsibility)."""
        entity_type = (entity_type or "").strip().lower()

        # Anti double-execution guard
        import time
        name_key = entity_data.get("name", entity_data.get("username", ""))
        last_call_key = f"create_{entity_type}_{name_key}"
        if hasattr(self, "_last_save_calls") and last_call_key in self._last_save_calls:
            if time.time() - self._last_save_calls[last_call_key] < 1.0:
                return {"success": False, "message": "Operation already in progress"}
        else:
            self._last_save_calls = {}
        self._last_save_calls[last_call_key] = time.time()

        try:
            if entity_type == "admin":
                # Leverage existing implementation
                return self.save_admin_data(entity_data, None)

            if entity_type == "trainer":
                # Prevent duplicate emails across persons before DB insert
                email_in = entity_data.get("email")
                if self._is_person_email_in_use(email_in):
                    return {
                        "success": False,
                        "message": "Email already in use. Use a different email.",
                    }
                from types import SimpleNamespace
                from datetime import datetime
                trainer = SimpleNamespace()
                for key in [
                    "name", "lastname", "email", "phone",
                    "age", "specialty", "start_time", "end_time",
                ]:
                    val = entity_data.get(key)
                    if key == "age" and val not in (None, ""):
                        try:
                            val = int(val)
                        except Exception:
                            val = None
                    if isinstance(val, str):
                        val = val.strip()
                    if val not in (None, ""):
                        setattr(trainer, key, val)
                # Required/expected attributes by converters/DB schema
                if not hasattr(trainer, "age"):
                    setattr(trainer, "age", None)
                if not hasattr(trainer, "created_at"):
                    setattr(trainer, "created_at", datetime.now().strftime("%Y-%m-%d %H:00"))
                if "admin_username" in entity_data:
                    setattr(trainer, "admin_username", entity_data.get("admin_username"))

                from controllers.crud import create_trainer
                created = create_trainer(trainer)
                if not created:
                    return {"success": False, "message": "Failed to create trainer"}

                self.invalidate_cache("trainers")
                self.invalidate_cache("admins")
                return {
                    "success": True,
                    "message": f"Trainer '{getattr(trainer, 'name', '')}' created successfully",
                }

            if entity_type == "user":
                # Prevent duplicate emails across persons before DB insert
                email_in = entity_data.get("email")
                if self._is_person_email_in_use(email_in):
                    return {
                        "success": False,
                        "message": "Email already in use. Use a different email.",
                    }
                from types import SimpleNamespace
                from datetime import datetime
                user = SimpleNamespace()
                for key in [
                    "name", "lastname", "email", "phone",
                    "age", "membership_type", "status",
                ]:
                    val = entity_data.get(key)
                    if key == "membership_type" and (val is None or val == ""):
                        val = "Basic"
                    if key == "age" and val not in (None, ""):
                        try:
                            val = int(val)
                        except Exception:
                            val = None
                    if isinstance(val, str):
                        val = val.strip()
                    if val not in (None, ""):
                        setattr(user, key, val)
                # Required/expected attributes by converters/DB schema
                if not hasattr(user, "age"):
                    setattr(user, "age", None)
                if not hasattr(user, "created_at"):
                    setattr(user, "created_at", datetime.now().strftime("%Y-%m-%d %H:00"))
                if not hasattr(user, "renovation_date"):
                    setattr(user, "renovation_date", None)

                from controllers.crud import create_user
                created = create_user(user)
                if not created:
                    return {"success": False, "message": "Failed to create member"}

                self.invalidate_cache("users")
                return {
                    "success": True,
                    "message": f"Member '{getattr(user, 'name', '')}' created successfully",
                }

            # Fallback for unknown entity types to satisfy return type
            return {"success": False, "message": f"Unknown entity type '{entity_type}'"}
        except Exception as e:
            username = entity_data.get("username", entity_data.get("name", ""))
            return self._handle_database_error(e, str(username))

    def update_entity_data(
        self,
        entity_type: str,
        entity_data: Dict[str, Any],
        form_or_id=None,
    ) -> Dict[str, Any]:
        """Update Admin, Trainer, or User (single-responsibility)."""
        entity_type = (entity_type or "").strip().lower()

        # Anti double-execution guard
        import time
        name_key = entity_data.get("name", entity_data.get("username", ""))
        last_call_key = f"update_{entity_type}_{name_key}"
        if hasattr(self, "_last_save_calls") and last_call_key in self._last_save_calls:
            if time.time() - self._last_save_calls[last_call_key] < 1.0:
                return {"success": False, "message": "Operation already in progress"}
        else:
            self._last_save_calls = {}
        self._last_save_calls[last_call_key] = time.time()

        try:
            if entity_type == "admin":
                return self.save_admin_data(entity_data, form_or_id)

            if entity_type == "trainer":
                # Resolve ID
                trainer_id = None
                if isinstance(form_or_id, (str, int)):
                    trainer_id = self._get_real_trainer_id(str(form_or_id))
                else:
                    to_edit = getattr(form_or_id, "trainer_to_edit", None)
                    if to_edit:
                        trainer_id = self._get_real_trainer_id(str(to_edit))

                from controllers.crud import get_trainer, update_trainer
                trainer = get_trainer(trainer_id)
                if not trainer:
                    return {"success": False, "message": "Trainer not found"}

                for key in [
                    "name", "lastname", "email", "phone",
                    "age", "specialty", "start_time", "end_time",
                ]:
                    if key in entity_data and entity_data.get(key) is not None:
                        val = entity_data.get(key)
                        if key == "age" and val not in (None, ""):
                            try:
                                val = int(val)
                            except Exception:
                                val = None
                        if isinstance(val, str):
                            val = val.strip()
                        if val != "":
                            setattr(trainer, key, val)
                if "admin_username" in entity_data:
                    setattr(trainer, "admin_username", entity_data.get("admin_username"))

                success = update_trainer(trainer)
                if not success:
                    return {"success": False, "message": "Failed to update trainer"}

                self.invalidate_cache("trainers")
                self.invalidate_cache("admins")
                return {
                    "success": True,
                    "message": (
                        f"Trainer '{getattr(trainer, 'name', 'record')}' "
                        "updated successfully"
                    ),
                }

            if entity_type == "user":
                # Resolve ID
                user_id = None
                if isinstance(form_or_id, (str, int)):
                    user_id = self._get_real_user_id(str(form_or_id))
                else:
                    to_edit = getattr(form_or_id, "user_to_edit", None)
                    if to_edit:
                        user_id = self._get_real_user_id(str(to_edit))

                from controllers.crud import get_user, update_user
                user = get_user(user_id)
                if not user:
                    return {"success": False, "message": "Member not found"}

                for key in [
                    "name", "lastname", "email", "phone",
                    "age", "membership_type", "status",
                ]:
                    if key in entity_data and entity_data.get(key) is not None:
                        val = entity_data.get(key)
                        if key == "age" and val not in (None, ""):
                            try:
                                val = int(val)
                            except Exception:
                                val = None
                        if isinstance(val, str):
                            val = val.strip()
                        if val != "":
                            setattr(user, key, val)

                success = update_user(user)
                if not success:
                    return {"success": False, "message": "Failed to update member"}

                self.invalidate_cache("users")
                return {
                    "success": True,
                    "message": (
                        f"Member '{getattr(user, 'name', 'record')}' "
                        "updated successfully"
                    ),
                }

            return {"success": False, "message": f"Unknown entity type '{entity_type}'"}
        except Exception as e:
            username = entity_data.get("username", entity_data.get("name", ""))
            return self._handle_database_error(e, str(username))

    def save_entity_data(
        self,
        entity_type: str,
        entity_data: Dict[str, Any],
        form_or_id=None,
    ) -> Dict[str, Any]:
        """
        Backward-compatible unified method that delegates to create or update
        based on the presence of form_or_id (or *to_edit fields).
        """
        entity_type_l = (entity_type or "").strip().lower()
        # Detect update context if explicit ID or form has *to_edit
        is_update = bool(form_or_id and (
            isinstance(form_or_id, (str, int))
            or hasattr(form_or_id, "trainer_to_edit")
            or hasattr(form_or_id, "user_to_edit")
            or hasattr(form_or_id, "admin_to_edit")
        ))
        if is_update:
            return self.update_entity_data(entity_type_l, entity_data, form_or_id)
        return self.create_entity_data(entity_type_l, entity_data)

    def _get_real_user_id(self, sequential_or_real_id: str) -> Optional[str]:
        """
        Convert sequential user ID to real DB ID using cached data where possible.

        Args:
            sequential_or_real_id: Either sequential ID (1, 2, 3...) or real DB ID

        Returns:
            Real user ID as string, or None if not found
        """
        try:
            seq = int(sequential_or_real_id)
            if 1 <= seq <= 100000:
                users_real = self._get_cached_data("users_with_real_ids")
                if 1 <= seq <= len(users_real):
                    row = users_real[seq - 1]
                    return str(row[0]) if len(row) > 0 else None
                return None
            return str(sequential_or_real_id)
        except (ValueError, IndexError, Exception):
            return str(sequential_or_real_id) if sequential_or_real_id else None

    def save_trainer_data(self, trainer_data: Dict[str, Any], form_or_id=None) -> Dict[str, Any]:
        """Compatibility wrapper for saving trainer records."""
        is_update = bool(
            form_or_id and (
                isinstance(form_or_id, (str, int))
                or getattr(form_or_id, "trainer_to_edit", None)
            )
        )
        if is_update:
            return self.update_entity_data("trainer", trainer_data, form_or_id)
        return self.create_entity_data("trainer", trainer_data)

    def save_user_data(self, user_data: Dict[str, Any], form_or_id=None) -> Dict[str, Any]:
        """Compatibility wrapper for saving user (member) records."""
        is_update = bool(
            form_or_id and (
                isinstance(form_or_id, (str, int))
                or getattr(form_or_id, "user_to_edit", None)
            )
        )
        if is_update:
            return self.update_entity_data("user", user_data, form_or_id)
        return self.create_entity_data("user", user_data)
