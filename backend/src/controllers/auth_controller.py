from src.validators.auth_validator import SignupRequest, LoginRequest
from src.utils.response import success_response


def signup_user(data: SignupRequest):
    # TEMPORARY: dummy response. Real Supabase call comes later via services/
    return success_response(
        data={
            "user": {
                "full_name": data.full_name,
                "email": data.email,
                "role": data.role,
            }
        },
        message="Signup endpoint works (dummy)",
    )


def login_user(data: LoginRequest):
    # TEMPORARY: dummy response
    return success_response(
        data={"access_token": "dummy-token", "token_type": "bearer"},
        message="Login endpoint works (dummy)",
    )
