import re


class AdminValidator:
    """Validator class for admin-related input validation"""

    @staticmethod
    def validate_username(username):
        """Validate username format - only letters, numbers, dots and hyphens allowed"""
        if not username:
            return False, "Username cannot be empty."

        if len(username) < 3:
            return False, "Username must be at least 3 characters long."

        # Pattern: only letters, numbers, dots and hyphens
        pattern = r'^[a-zA-Z0-9.-]+$'
        if not re.match(pattern, username):
            return False, "Username can only contain letters, numbers, dots (.) and hyphens (-)."

        return True, ""

    @staticmethod
    def validate_password(password):
        """Validate password format"""
        if len(password) < 3:
            return False, "Password must be at least 3 characters long."

        return True, ""

    @staticmethod
    def validate_password_match(password, confirm_password):
        """Validate that passwords match"""
        if password != confirm_password:
            return False, "Passwords do not match. Please check and try again."

        return True, ""
