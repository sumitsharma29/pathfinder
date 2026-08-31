import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, description="Full name of user")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 characters)")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Account password")


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class AuthData(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    success: bool = True
    data: AuthData
    message: str


class UserMeResponse(BaseModel):
    success: bool = True
    data: UserResponse
    message: str = "Authenticated user"
