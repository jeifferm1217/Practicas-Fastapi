from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from ..models.users import UserInDB, UserBase, UserUpdate
from ..core.database import fake_users_db, get_next_user_id
from datetime import datetime

router = APIRouter()

# Variable para simular un usuario autenticado (para GET/PUT/DELETE /me)
current_user_id = 1

def get_current_user():
    """Función de dependencia para obtener el usuario actual."""
    user = fake_users_db.get(current_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserBase):
    """
    **Registra un nuevo usuario.**
    - Valida que el nombre de usuario y el email no existan.
    - Crea un nuevo usuario con los datos proporcionados.
    """
    for user in fake_users_db.values():
        if user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        if user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    new_user_id = get_next_user_id()
    new_user = UserInDB(id=new_user_id, **user_data.dict())
    fake_users_db[new_user_id] = new_user
    return new_user

@router.get("/me", response_model=UserInDB)
def get_current_user_profile(user: UserInDB = Depends(get_current_user)):
    """
    **Obtiene el perfil del usuario actual.**
    """
    return user

@router.put("/me", response_model=UserInDB)
def update_user_profile(user_update: UserUpdate, user: UserInDB = Depends(get_current_user)):
    """
    **Actualiza el perfil del usuario actual.**
    - Permite actualizar el nombre completo y las preferencias.
    """
    user_data_dict = user.dict()
    user_update_dict = user_update.dict(exclude_unset=True)

    for key, value in user_update_dict.items():
        if key == "preferences":
            user.preferences = user.preferences.copy(update=value)
        else:
            setattr(user, key, value)
    
    fake_users_db[user.id] = user
    return user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(user: UserInDB = Depends(get_current_user)):
    """
    **Elimina la cuenta del usuario actual.**
    """
    del fake_users_db[user.id]
    return

