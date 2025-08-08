from typing import Dict, List
from ..models.users import UserInDB

# Esta es nuestra "base de datos" de usuarios
fake_users_db: Dict[int, UserInDB] = {}

def get_next_user_id() -> int:
    """Genera un nuevo ID para el usuario."""
    return len(fake_users_db) + 1