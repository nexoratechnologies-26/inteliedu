from fastapi import APIRouter
from src.validators.auth_validator import SignupRequest, LoginRequest, ApiResponse
from src.controllers import auth_controller

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/signup", response_model=ApiResponse)
def signup(data: SignupRequest):
    return auth_controller.signup_user(data)


@router.post("/login", response_model=ApiResponse)
def login(data: LoginRequest):
    return auth_controller.login_user(data)
