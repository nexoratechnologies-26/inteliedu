from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.routes.health_routes import router as health_router
from src.routes.auth_routes import router as auth_router

app = FastAPI(title="Inteliedu API")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(p) for p in e["loc"] if p != "body"),
            "message": e["msg"],
        }
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": None,
            "message": "Validation failed",
            "errors": errors,
        },
    )


@app.get("/")
def root():
    return {"message": "Inteliedu API is running"}


app.include_router(health_router)
app.include_router(auth_router)
