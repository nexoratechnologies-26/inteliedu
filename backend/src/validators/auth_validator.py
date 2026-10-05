from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class SelfRegisterRole(str, Enum):
    student = "student"
    teacher = "teacher"


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    role: SelfRegisterRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class UserOut(BaseModel):
    full_name: str
    email: EmailStr
    role: str


class RegisterResponse(BaseModel):
    message: str
    user: UserOut


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str