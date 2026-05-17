from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)
    roll_number: str = Field(min_length=1, max_length=50)
    department: str = Field(min_length=1, max_length=120)
    year_level: int = Field(ge=1, le=6)


class AuthenticatedUser(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: AuthenticatedUser


class LogoutResponse(BaseModel):
    message: str
