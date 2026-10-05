from fastapi import APIRouter
from src.validators.auth_validator import RegisterRequest, LoginRequest
from src.controllers import auth_controller

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register")
def register(data: RegisterRequest):
    return auth_controller.register_user(data)


@router.post("/login")
def login(data: LoginRequest):
    return auth_controller.login_user(data)
from fastapi import APIRouter
from src.validators.auth_validator import (
    RegisterRequest, LoginRequest, RegisterResponse, LoginResponse
)
from src.controllers import auth_controller

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest):
    return auth_controller.register_user(data)


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    return auth_controller.login_user(data)