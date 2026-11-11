"""FastAPI entrypoint for the Inteliedu 3D Generation Agent."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import router as agent_router
from app.config import Settings, get_settings
from app.utils.error_handler import register_exception_handlers
from app.utils.logger import get_logger

logger = get_logger("inteliedu.3d_agent.main")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    caps = settings.capabilities_report()
    logger.info(
        "Inteliedu 3D Generation Agent v%s started (env=%s, port=%s, ffmpeg=%s, blender_cli=%s, blender_mcp_cfg=%s, runway_api_cfg=%s, llm_cfg=%s)",
        __version__,
        settings.app_env,
        settings.app_port,
        caps["ffmpeg"]["available"],
        caps["blender_cli"]["available"],
        caps["blender_mcp"]["configured"],
        caps["runway_api"]["configured"],
        caps["llm"]["configured"],
    )
    yield


def create_app(custom_settings: Settings | None = None) -> FastAPI:
    settings = custom_settings or get_settings()
    app = FastAPI(
        title="Inteliedu 3D Generation Agent",
        description="LangGraph + MCP orchestrator for automated educational 3D & AI video generation.",
        version=__version__,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.cors_origin, "http://localhost:5173", "http://localhost:5000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(agent_router, prefix=settings.agent_api_prefix)

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "Inteliedu 3D Generation Agent",
            "version": __version__,
            "capabilities": settings.capabilities_report(),
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    cfg = get_settings()
    uvicorn.run("app.main:app", host=cfg.app_host, port=cfg.app_port, reload=cfg.app_env == "development")

