from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any

class UserPreferences(BaseModel):
    theme: str = "light"
    language: str = "en"
    timezone: str = "UTC"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime = datetime.utcnow()
    preferences: UserPreferences = UserPreferences()

    class Config:
        # Esto permite que Pydantic maneje tipos de datos no estándar como `datetime`
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None