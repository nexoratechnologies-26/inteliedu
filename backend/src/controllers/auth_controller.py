from src.validators.auth_validator import RegisterRequest, LoginRequest


def register_user(data: RegisterRequest):
    # TEMPORARY: dummy response. Real Supabase call comes later via services/
    return {
        "message": "Registration endpoint works (dummy)",
        "user": {
            "full_name": data.full_name,
            "email": data.email,
            "role": data.role,
        },
    }


def login_user(data: LoginRequest):
    # TEMPORARY: dummy response
    return {
        "message": "Login endpoint works (dummy)",
        "access_token": "dummy-token",
        "token_type": "bearer",
    }