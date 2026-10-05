from fastapi import FastAPI
from src.routes.health_routes import router as health_router
from src.routes.auth_routes import router as auth_router

app = FastAPI(title="Inteliedu API")

app.include_router(health_router)
app.include_router(auth_router)
@app.get("/")
def root():
    return {"message": "Inteliedu API is running"}