from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema of User"""
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr

class UserPydantic(UserBase):
    """Public schema of User model"""
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    """Schema for User creation"""
    password: str

class UserUpdate(UserBase):
    """Schema for User update"""
    username: str | None = Field(default=None, min_length=3, max_length=30)
    email: EmailStr | None = None
    password: str | None = None

class UserInDB(UserBase):
    """Schema to represent User in Database"""
    id: int
    hashed_password: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class ChangePassword(BaseModel):
    """Schema to change user password"""
    current_password: str
    new_password: str