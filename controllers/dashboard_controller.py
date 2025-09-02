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
    get_admin,
    update_admin,
    get_trainer,
    update_trainer,
    get_user,
    update_user,
    get_all_trainers,
    create_trainer,
    create_user,
)
from services.data_formatter import DataFormatter
from models.admin import Admin
from typing import List, Dict, Any, Optional
import time


class DashboardController:
    """
    Controller that handles dashboard logic.
    Separates business logic from the view, following the MVC pattern.
    """

    def __init__(self):
        self.data_formatter = DataFormatter()
        self._cache = {}
        self._cache_dirty = {"admins": True, "trainers": True, "users": True}
        self._last_operations = {}

    def _get_cached_data(self, table_name: str) -> List[List[Any]]:
        """Get data from cache or fetch if cache is dirty"""
        if self._cache_dirty.get(table_name, True) or table_name not in self._cache:
            if table_name == "admins":
                self._cache[table_name] = self.data_formatter.get_formatted_admin_data()
            elif table_name == "admins_extended":
                self._cache[table_name] = (
                    self.data_formatter.get_formatted_admin_data_extended()
                )
            elif table_name == "trainers":
                self._cache[table_name] = (
                    self.data_formatter.get_formatted_trainer_data()
                )
            elif table_name == "trainers_with_real_ids":
                self._cache[table_name] = (
                    self.data_formatter.get_formatted_trainer_data_with_real_ids()
                )
            elif table_name == "users":
                self._cache[table_name] = self.data_formatter.get_formatted_user_data()
            elif table_name == "users_with_real_ids":
                try:
                    self._cache[table_name] = (
                        self.data_formatter.get_formatted_user_data_with_real_ids()
                    )
                except Exception:
                    self._cache[table_name] = self._cache.get("users", [])
            else:
                self._cache[table_name] = []

            self._cache_dirty[table_name] = False

        return self._cache[table_name]

    def invalidate_cache(self, table_name: str):
        """Invalidate cache for specific table"""
        self._cache_dirty[table_name] = True
        if table_name == "admins":
            self._cache_dirty["admins_extended"] = True
        elif table_name == "trainers":
            self._cache_dirty["trainers_with_real_ids"] = True
        elif table_name == "users":
            self._cache_dirty["users_with_real_ids"] = True

    def filter_data(self, table_name: str, query: str) -> List[List[Any]]:
        """Simple filter data functionality"""
        data = self._get_cached_data(table_name)
        if not query.strip():
            return data

        query_lower = query.lower()
        return [
            row for row in data if any(query_lower in str(cell).lower() for cell in row)
        ]

    # Basic data getters
    def get_admin_data(self):
        return self._get_cached_data("admins")

    def get_trainer_data(self):
        return self._get_cached_data("trainers")

    def get_user_data(self):
        return self._get_cached_data("users")

    def get_admin_username_from_sequential_id(
        self, sequential_id: str
    ) -> Optional[str]:
        """Get admin username from sequential ID"""
        try:
            admin_data = self._get_cached_data("admins")
            idx = int(sequential_id)
            if 1 <= idx <= len(admin_data):
                return admin_data[idx - 1][1]  # Username is in column 1
            return None
        except (ValueError, IndexError):
            return None

    def get_default_section(self, current_admin):
        """Determine default section based on user type"""
        return "Admins" if is_admin(current_admin.username) else "Trainers"

    def should_show_configuration(self, section_name):
        """Check if section is configuration"""
        return section_name.startswith("Configuration ")

    def extract_username_from_config_section(self, section_name):
        """Extract username from configuration section"""
        return section_name.split(" ", 1)[1]

    def can_create_admin_accounts(self, current_admin) -> bool:
        """Check if user can create admin accounts"""
        if not current_admin:
            return False

        admin_id = getattr(current_admin, "unique_id", None) or getattr(
            current_admin, "id", None
        )
        if not admin_id:
            return False

        # Get admin data from cache
        admin_data = self._get_cached_data("admins_extended")
        for row in admin_data:
            if str(row[0]) == str(admin_id):
                role = row[2].lower() if len(row) > 2 else "admin"
                return role == "admin"

        return False

    def _prevent_duplicate_operation(self, operation_key: str) -> bool:
        """Prevent duplicate operations within 1 second"""
        current_time = time.time()
        if operation_key in self._last_operations:
            if current_time - self._last_operations[operation_key] < 1.0:
                return True  # Duplicate operation
        self._last_operations[operation_key] = current_time
        return False

    def _handle_database_error(
        self, error: Exception, context: str = ""
    ) -> Dict[str, Any]:
        """Handle database errors with appropriate messages"""
        error_msg = str(error)

        if "UNIQUE constraint failed: persons.email" in error_msg:
            return {
                "success": False,
                "message": "Email already in use. Use a different email.",
            }
        elif "UNIQUE constraint failed: admins.username" in error_msg:
            return {"success": False, "message": f"Username '{context}' already taken."}
        elif "UNIQUE constraint failed" in error_msg:
            return {
                "success": False,
                "message": "Data already in use. Check your input.",
            }
        elif "NOT NULL constraint failed" in error_msg:
            return {"success": False, "message": "Required information is missing."}
        elif "not found" in error_msg:
            return {"success": False, "message": "Record not found."}
        else:
            return {"success": False, "message": f"Database error: {error_msg}"}

    def save_admin_data(
        self, admin_data: Dict[str, Any], admin_form_or_id=None
    ) -> Dict[str, Any]:
        """Create or update admin"""
        return self._save_entity_unified("admin", admin_data, admin_form_or_id)

    def save_trainer_data(
        self, trainer_data: Dict[str, Any], form_or_id=None
    ) -> Dict[str, Any]:
        """Save trainer data"""
        return self._save_entity_unified("trainer", trainer_data, form_or_id)

    def save_user_data(
        self, user_data: Dict[str, Any], form_or_id=None
    ) -> Dict[str, Any]:
        """Save user data"""
        return self._save_entity_unified("user", user_data, form_or_id)

    def _save_entity_unified(
        self, entity_type: str, entity_data: Dict[str, Any], form_or_id=None
    ) -> Dict[str, Any]:
        """Unified save method for all entity types"""
        # Get entity identifier for operation key
        identifier = self._get_entity_identifier_for_key(entity_type, entity_data)
        operation_key = f"save_{entity_type}_{identifier}"

        if self._prevent_duplicate_operation(operation_key):
            return {"success": False, "message": "Operation already in progress"}

        try:
            # Determine if updating
            entity_id_to_update = self._resolve_entity_id_for_update(
                entity_type, form_or_id
            )

            if entity_id_to_update:
                return self._update_entity(
                    entity_type, entity_data, entity_id_to_update
                )
            else:
                return self._create_entity(entity_type, entity_data)

        except Exception as e:
            return self._handle_database_error(e, identifier)

    def _get_entity_identifier_for_key(
        self, entity_type: str, entity_data: Dict[str, Any]
    ) -> str:
        """Get identifier for operation key"""
        if entity_type == "admin":
            return entity_data.get("username", "")
        else:  # trainer, user
            return entity_data.get("name", "")

    def _resolve_entity_id_for_update(
        self, entity_type: str, form_or_id=None
    ) -> Optional[str]:
        """Resolve entity ID for update operations"""
        if not form_or_id:
            return None

        # Direct ID passed
        if isinstance(form_or_id, (str, int)):
            if entity_type == "admin":
                return str(form_or_id)
            elif entity_type == "trainer":
                return self._get_real_trainer_id(str(form_or_id))
            elif entity_type == "user":
                return self._get_real_user_id(str(form_or_id))

        # Form object with entity_to_edit attribute
        edit_attr = f"{entity_type}_to_edit"
        if hasattr(form_or_id, edit_attr):
            entity_to_edit = getattr(form_or_id, edit_attr)
            if entity_to_edit:
                if entity_type == "admin":
                    # Convert sequential ID to real ID for admin
                    username_from_seq = self.get_admin_username_from_sequential_id(
                        entity_to_edit
                    )
                    if username_from_seq:
                        admin_data_list = self._get_cached_data("admins_extended")
                        for row in admin_data_list:
                            if row[1] == username_from_seq:
                                return str(row[0])
                elif entity_type == "trainer":
                    return self._get_real_trainer_id(str(entity_to_edit))
                elif entity_type == "user":
                    return self._get_real_user_id(str(entity_to_edit))

        return None

    def _update_entity(
        self, entity_type: str, entity_data: Dict[str, Any], entity_id: str
    ) -> Dict[str, Any]:
        """Update existing entity"""
        if entity_type == "admin":
            return self._update_admin(entity_data, entity_id)
        elif entity_type == "trainer":
            return self._update_trainer(entity_data, entity_id)
        elif entity_type == "user":
            return self._update_user(entity_data, entity_id)
        else:
            return {"success": False, "message": f"Unknown entity type: {entity_type}"}

    def _create_entity(
        self, entity_type: str, entity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new entity"""
        if entity_type == "admin":
            return self._create_admin(entity_data)
        elif entity_type == "trainer":
            return self._create_trainer(entity_data)
        elif entity_type == "user":
            return self._create_user(entity_data)
        else:
            return {"success": False, "message": f"Unknown entity type: {entity_type}"}

    def _update_admin(
        self, admin_data: Dict[str, Any], admin_id: str
    ) -> Dict[str, Any]:
        """Update existing admin"""
        existing_admin = get_admin(admin_id)
        if not existing_admin:
            return {"success": False, "message": "Admin not found"}

        if admin_data.get("username"):
            existing_admin.username = admin_data["username"].strip()
        if admin_data.get("password"):
            existing_admin.set_password(admin_data["password"])
        if admin_data.get("role"):
            existing_admin.role = admin_data["role"]

        # Handle trainer association for managers
        if admin_data.get("role") == "manager":
            trainer_id = admin_data.get("trainer_id")
            username_to_clear = getattr(existing_admin, "username", None)
            if username_to_clear:
                self._clear_trainer_admin_association(str(username_to_clear))

            if trainer_id:
                real_trainer_id = self._get_real_trainer_id(trainer_id)
                trainer = get_trainer(real_trainer_id)
                if trainer:
                    setattr(trainer, "admin_username", existing_admin.username)
                    update_trainer(trainer)
        else:
            username_to_clear = getattr(existing_admin, "username", None)
            if username_to_clear:
                self._clear_trainer_admin_association(str(username_to_clear))

        update_admin(existing_admin)
        self.invalidate_cache("admins")
        self.invalidate_cache("trainers")

        return {
            "success": True,
            "message": f"Administrator '{existing_admin.username}' updated successfully",
        }

    def _create_admin(self, admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new admin"""
        if not admin_data.get("password"):
            return {"success": False, "message": "Password is required"}

        admin = Admin(
            username=admin_data.get("username"),
            password=admin_data.get("password"),
            role=admin_data.get("role", "admin"),
        )

        create_admin(admin)

        # Handle trainer association for managers
        if admin_data.get("role") == "manager" and admin_data.get("trainer_id"):
            real_trainer_id = self._get_real_trainer_id(admin_data["trainer_id"])
            trainer = get_trainer(real_trainer_id)
            if trainer:
                setattr(trainer, "admin_username", admin.username)
                update_trainer(trainer)

        self.invalidate_cache("admins")
        self.invalidate_cache("trainers")

        return {
            "success": True,
            "message": f"Administrator '{admin.username}' created successfully",
        }

    def _update_trainer(
        self, trainer_data: Dict[str, Any], trainer_id: str
    ) -> Dict[str, Any]:
        """Update existing trainer"""
        trainer = get_trainer(trainer_id)
        if not trainer:
            return {"success": False, "message": "Trainer not found"}

        for key in [
            "name",
            "lastname",
            "email",
            "phone",
            "age",
            "specialty",
            "start_time",
            "end_time",
        ]:
            if key in trainer_data and trainer_data[key]:
                val = trainer_data[key]
                if key == "age" and val:
                    try:
                        val = int(val)
                    except (ValueError, TypeError):
                        val = None
                if isinstance(val, str):
                    val = val.strip()
                if val:
                    setattr(trainer, key, val)

        update_trainer(trainer)
        self.invalidate_cache("trainers")

        return {
            "success": True,
            "message": f"Trainer '{getattr(trainer, 'name', 'record')}' updated successfully",
        }

    def _create_trainer(self, trainer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new trainer"""
        from types import SimpleNamespace
        from datetime import datetime

        trainer = SimpleNamespace()
        for key in [
            "name",
            "lastname",
            "email",
            "phone",
            "age",
            "specialty",
            "start_time",
            "end_time",
        ]:
            val = trainer_data.get(key)
            if key == "age" and val:
                try:
                    val = int(val)
                except (ValueError, TypeError):
                    val = None
            if isinstance(val, str) and val:
                val = val.strip()
            if val:
                setattr(trainer, key, val)

        if not hasattr(trainer, "age"):
            setattr(trainer, "age", None)
        if not hasattr(trainer, "created_at"):
            setattr(trainer, "created_at", datetime.now().strftime("%Y-%m-%d %H:00"))

        create_trainer(trainer)
        self.invalidate_cache("trainers")

        return {
            "success": True,
            "message": f"Trainer '{getattr(trainer, 'name', '')}' created successfully",
        }

    def _update_user(self, user_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update existing user"""
        user = get_user(user_id)
        if not user:
            return {"success": False, "message": "Member not found"}

        for key in [
            "name",
            "lastname",
            "email",
            "phone",
            "age",
            "membership_type",
            "status",
        ]:
            if key in user_data and user_data[key]:
                val = user_data[key]
                if key == "age" and val:
                    try:
                        val = int(val)
                    except (ValueError, TypeError):
                        val = None
                if isinstance(val, str):
                    val = val.strip()
                if val:
                    setattr(user, key, val)

        update_user(user)
        self.invalidate_cache("users")

        return {
            "success": True,
            "message": f"Member '{getattr(user, 'name', 'record')}' updated successfully",
        }

    def _create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user"""
        from types import SimpleNamespace
        from datetime import datetime

        user = SimpleNamespace()
        for key in [
            "name",
            "lastname",
            "email",
            "phone",
            "age",
            "membership_type",
            "status",
        ]:
            val = user_data.get(key)
            if key == "membership_type" and not val:
                val = "Basic"
            if key == "age" and val:
                try:
                    val = int(val)
                except (ValueError, TypeError):
                    val = None
            if isinstance(val, str) and val:
                val = val.strip()
            if val:
                setattr(user, key, val)

        if not hasattr(user, "age"):
            setattr(user, "age", None)
        if not hasattr(user, "created_at"):
            setattr(user, "created_at", datetime.now().strftime("%Y-%m-%d %H:00"))

        create_user(user)
        self.invalidate_cache("users")

        return {
            "success": True,
            "message": f"Member '{getattr(user, 'name', '')}' created successfully",
        }

    def get_available_trainers_for_form(self) -> List[List[Any]]:
        """Get trainers available for manager association"""
        try:
            trainers_with_real_ids = self._get_cached_data("trainers_with_real_ids")
            extended_admin_data = self._get_cached_data("admins_extended")

            # Get associated trainer IDs
            associated_trainer_ids = {
                str(admin_row[4])
                for admin_row in extended_admin_data
                if len(admin_row) >= 5 and admin_row[4] is not None
            }

            # Filter available trainers
            available_trainers = [
                trainer_row
                for trainer_row in trainers_with_real_ids
                if str(trainer_row[0]) not in associated_trainer_ids
            ]

            # Return with sequential IDs (4 columns for form)
            return [
                [str(idx + 1), trainer_row[1], trainer_row[2], trainer_row[3]]
                for idx, trainer_row in enumerate(available_trainers)
            ]

        except Exception:
            return self._get_cached_data("trainers")[:4]  # Fallback

    def _get_real_trainer_id(self, sequential_or_real_id: str) -> Optional[str]:
        """Convert sequential trainer ID to real DB ID"""
        try:
            seq_id = int(sequential_or_real_id)
            if 1 <= seq_id <= 1000:  # Sequential ID range
                trainers = self._get_cached_data("trainers_with_real_ids")
                if 1 <= seq_id <= len(trainers):
                    return str(trainers[seq_id - 1][0])
                return None
            else:
                return str(sequential_or_real_id)  # Already real ID
        except (ValueError, IndexError):
            return str(sequential_or_real_id) if sequential_or_real_id else None

    def _get_real_user_id(self, sequential_or_real_id: str) -> Optional[str]:
        """Convert sequential user ID to real DB ID"""
        try:
            seq_id = int(sequential_or_real_id)
            if 1 <= seq_id <= 100000:  # Sequential ID range
                users = self._get_cached_data("users_with_real_ids")
                if 1 <= seq_id <= len(users):
                    return str(users[seq_id - 1][0])
                return None
            else:
                return str(sequential_or_real_id)  # Already real ID
        except (ValueError, IndexError):
            return str(sequential_or_real_id) if sequential_or_real_id else None

    def _clear_trainer_admin_association(self, admin_username: str):
        """Clear trainer associations for admin"""
        if not admin_username or not isinstance(admin_username, str):
            return  # Skip if username is None or not a string

        try:
            all_trainers = get_all_trainers()
            for trainer in all_trainers:
                current_admin_username = getattr(trainer, "admin_username", None)
                if current_admin_username and current_admin_username == admin_username:
                    setattr(trainer, "admin_username", None)
                    update_trainer(trainer)
        except Exception as e:
            print(f"Error clearing trainer associations: {e}")

    def delete_entity(
        self, current_admin, entity_type: str, entity_id: str
    ) -> Dict[str, Any]:
        """Universal delete function"""
        try:
            entity_type = entity_type.lower().strip()

            # Get entity identifier
            if entity_type == "admin":
                entity_identifier = self.get_admin_username_from_sequential_id(
                    entity_id
                )
                if not entity_identifier:
                    return {"success": False, "message": "Administrator not found"}

                # Validation checks
                if entity_identifier == "admin":
                    return {
                        "success": False,
                        "message": "Cannot delete default administrator",
                    }
                if current_admin.username == entity_identifier:
                    return {
                        "success": False,
                        "message": "Cannot delete your own account",
                    }

                # Permission check
                current_is_admin = self.can_create_admin_accounts(current_admin)
                if not current_is_admin:
                    # Check target role
                    admin_data = self._get_cached_data("admins_extended")
                    target_role = None
                    for row in admin_data:
                        if row[1] == entity_identifier:
                            target_role = row[2].lower()
                            break

                    if target_role == "admin":
                        return {
                            "success": False,
                            "message": "Managers cannot delete Administrators",
                        }

                success = delete_admin_by_username(entity_identifier)

            elif entity_type == "trainer":
                real_trainer_id = self._get_real_trainer_id(entity_id)
                success = delete_trainer(real_trainer_id) if real_trainer_id else False
                entity_identifier = "trainer"

            elif entity_type == "user":
                real_user_id = self._get_real_user_id(entity_id)
                success = delete_user(real_user_id) if real_user_id else False
                entity_identifier = "member"

            else:
                return {
                    "success": False,
                    "message": f"Unknown entity type: {entity_type}",
                }

            if success:
                self.invalidate_cache(entity_type + "s")
                if entity_type == "admin":
                    self.invalidate_cache("trainers")

                return {
                    "success": True,
                    "message": f"{entity_type.title()} '{entity_identifier}' deleted successfully",
                }
            else:
                return {"success": False, "message": f"Failed to delete {entity_type}"}

        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting {entity_type}: {str(e)}",
            }

    # Legacy compatibility methods
    def delete_admin_with_permissions(self, current_admin, admin_id) -> Dict[str, Any]:
        return self.delete_entity(current_admin, "admin", admin_id)

    def refresh_admin_profile(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """Refresh admin profile data"""
        self.invalidate_cache("admins")
        return self.get_admin_data_unified(admin_id, from_cache=False)

    def get_admin_data_unified(
        self, admin_id: str, from_cache: bool = True, by_sequential_id: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get admin data by ID"""
        try:
            if by_sequential_id:
                username = self.get_admin_username_from_sequential_id(admin_id)
                if not username:
                    return None
                admin_data = self._get_cached_data("admins_extended")
                for row in admin_data:
                    if row[1] == username:
                        return {
                            "id": row[0],
                            "username": row[1],
                            "role": row[2].lower(),
                            "created_at": row[3],
                            "unique_id": row[0],
                            "trainer_id": row[4] if len(row) > 4 else None,
                        }
            else:
                if from_cache:
                    admin_data = self._get_cached_data("admins_extended")
                    for row in admin_data:
                        if str(row[0]) == str(admin_id):
                            return {
                                "id": row[0],
                                "username": row[1],
                                "role": row[2].lower(),
                                "created_at": row[3],
                                "unique_id": row[0],
                                "trainer_id": row[4] if len(row) > 4 else None,
                            }
                else:
                    admin = get_admin(admin_id)
                    if admin:
                        return {
                            "id": admin.unique_id,
                            "username": admin.username,
                            "role": admin.role.lower() if admin.role else "admin",
                            "created_at": admin.created_at,
                            "unique_id": admin.unique_id,
                            "trainer_id": getattr(admin, "trainer_id", None),
                        }
            return None
        except Exception:
            return None
