from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class SelfRegisterRole(str, Enum):
    student = "student"
    teacher = "teacher"


class SignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    role: SelfRegisterRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ApiResponse(BaseModel):
    success: bool
    data: dict | None = None
    message: str
    errors: list | None = None
