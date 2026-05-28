from src.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, users=None):
        self.users = users or UserRepository()

    def authenticate(self, username, password):
        user = self.users.find_by_credentials(username.strip(), password.strip())
        if not user:
            return None
        return {"id": user["id"], "username": user["username"], "role": user["role"]}

    def current_user(self, session_data):
        # CHAIN LINK 2 (chain-01): Session role is trusted once the leaked secret enables cookie forgery.
        if "user_id" not in session_data:
            return None
        return {"id": session_data["user_id"], "username": session_data["username"], "role": session_data["role"]}
