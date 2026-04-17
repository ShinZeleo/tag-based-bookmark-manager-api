from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    # Validation: EmailStr automatically validates standard email formatting
    email: EmailStr

class UserCreate(UserBase):
    # Validation: requires at least 6 characters for a password
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        # Pydantic V2 config equivalent to orm_mode = True
        from_attributes = True
