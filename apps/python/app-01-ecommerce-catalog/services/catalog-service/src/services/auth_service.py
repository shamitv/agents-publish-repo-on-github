from src.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, users=None):
        self.users = users or UserRepository()

    def authenticate(self, username, password):
        user = self.users.find_by_credentials(username.strip(), password.strip())
        if not user:
            return None
        return {"id": user["id"], "username": user["username"], "role": user["role"]}

    def profile_for_session(self, session_data):
        user_id = session_data.get("user_id")
        if not user_id:
            return None
        user = self.users.find_by_id(user_id)
        if not user:
            return None
        return {"id": user["id"], "username": user["username"], "role": user["role"]}
