from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid


# ============================================
# LOGIN
# ============================================

class LoginRequest(BaseModel):
    username: str  # Pode ser email
    password: str


# ============================================
# USER
# ============================================

class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    roles: List[str]
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_user(cls, user):
        """Converte User model para UserResponse"""
        roles = []
        if user.is_admin:
            roles.append("ADMIN")
        roles.append("USER")
        
        return cls(
            id=str(user.id),
            email=user.email,
            name=user.name,
            roles=roles,
            avatar=None
        )


# LoginResponse agora vem DEPOIS de UserResponse estar definida
class LoginResponse(BaseModel):
    accessToken: str
    refreshToken: Optional[str] = None
    user: UserResponse  # Agora já está definida acima


class UserInDB(UserBase):
    id: uuid.UUID
    hashed_password: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================
# TOKEN
# ============================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
