"""Configuration management for the Inteliedu 3D Generation Agent."""

from __future__ import annotations

import os
import shlex
import shutil
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

AGENT_ROOT = Path(__file__).resolve().parent.parent
MONOREPO_ROOT = AGENT_ROOT.parent

# Load monorepo root .env first (lower priority), then agent-local .env (higher priority)
_root_env = MONOREPO_ROOT / ".env"
_agent_env = AGENT_ROOT / ".env"
if _root_env.is_file():
    load_dotenv(_root_env, override=False)
if _agent_env.is_file():
    load_dotenv(_agent_env, override=True)


def _find_binary(preferred: str, fallbacks: Optional[List[str]] = None) -> str:
    """Resolve a binary path via explicit path, PATH lookup, or known install directories."""
    if preferred:
        p = Path(preferred)
        if p.is_file():
            return str(p)
        located = shutil.which(preferred)
        if located:
            return located
    for candidate in fallbacks or []:
        if Path(candidate).is_file():
            return candidate
        located = shutil.which(candidate)
        if located:
            return located
    return preferred


class Settings(BaseSettings):
    """Typed, validated configuration for the 3D Generation Agent."""

    model_config = SettingsConfigDict(
        env_file=(str(_root_env), str(_agent_env)),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_env: str = Field(default="development")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8001)
    agent_api_prefix: str = Field(default="/api/v1/3d-agent")
    log_level: str = Field(default="INFO")
    cors_origin: str = Field(default="http://localhost:5173")

    # Service authentication (optional shared key for internal INTELIEDU backend calls)
    agent_api_key: Optional[str] = Field(default=None)

    # LLM Provider
    llm_provider: str = Field(default="groq")
    llm_api_key: Optional[str] = Field(default=None)
    llm_model: Optional[str] = Field(default=None)
    llm_fallback_model: Optional[str] = Field(default=None)
    groq_api_key: Optional[str] = Field(default=None)
    groq_model: str = Field(default="openai/gpt-oss-120b")
    groq_fallback_model: str = Field(default="openai/gpt-oss-20b")
    gemini_api_key: Optional[str] = Field(default=None)
    gemini_model: str = Field(default="gemini-1.5-pro")

    # Blender & Blender MCP
    blender_executable_path: str = Field(
        default="C:/Program Files/Blender Foundation/Blender 4.3/blender.exe"
    )
    blender_mcp_command: str = Field(default="")
    blender_mcp_args: str = Field(default="")
    blender_mcp_host: str = Field(default="127.0.0.1")
    blender_mcp_port: int = Field(default=9876)
    blender_render_timeout_seconds: int = Field(default=600)
    blender_render_engine: str = Field(default="BLENDER_EEVEE_NEXT")
    blender_samples: int = Field(default=16)

    # Runway API & Optional MCP
    runway_api_key: Optional[str] = Field(default=None)
    runway_api_base_url: str = Field(default="https://api.dev.runwayml.com/v1")
    runway_api_version: str = Field(default="2024-11-06")
    runway_model: str = Field(default="gen4.5")
    runway_timeout_seconds: int = Field(default=300)
    runway_mcp_url: Optional[str] = Field(default=None)
    runway_mcp_command: Optional[str] = Field(default=None)
    runway_mcp_args: str = Field(default="")
    runway_mcp_token: Optional[str] = Field(default=None)

    # FFmpeg / Video Defaults
    ffmpeg_path: str = Field(default="ffmpeg")
    ffprobe_path: str = Field(default="ffprobe")
    video_default_width: int = Field(default=1920)
    video_default_height: int = Field(default=1080)
    video_default_fps: int = Field(default=30)
    video_max_size_mb: int = Field(default=250)
    video_allow_upscale: bool = Field(default=False)

    # Storage & Database
    generated_dir: str = Field(default=str(AGENT_ROOT / "generated"))
    storage_provider: str = Field(default="local")
    storage_bucket: str = Field(default="educational-videos")
    supabase_url: Optional[str] = Field(default=None)
    supabase_service_role_key: Optional[str] = Field(default=None)
    gcs_bucket_name: Optional[str] = Field(default=None)
    s3_endpoint_url: Optional[str] = Field(default=None)
    s3_access_key_id: Optional[str] = Field(default=None)
    s3_secret_access_key: Optional[str] = Field(default=None)
    database_url: Optional[str] = Field(default=None)

    # Guardrails & Cost Optimization
    max_concurrent_jobs: int = Field(default=2)
    enable_video_cache: bool = Field(default=True)
    allow_runway_fallback: bool = Field(default=True)
    max_video_duration_seconds: int = Field(default=300)
    max_retries: int = Field(default=2)

    @property
    def agent_root(self) -> Path:
        return AGENT_ROOT

    @property
    def monorepo_root(self) -> Path:
        return MONOREPO_ROOT

    @property
    def existing_models_dir(self) -> Path:
        return MONOREPO_ROOT / "frontend" / "public" / "assets" / "models"

    @property
    def resolved_generated_dir(self) -> Path:
        p = Path(self.generated_dir)
        if not p.is_absolute():
            p = (AGENT_ROOT / p).resolve()
        return p

    @property
    def resolved_ffmpeg_path(self) -> str:
        return _find_binary(self.ffmpeg_path, ["ffmpeg", "ffmpeg.exe"])

    @property
    def resolved_ffprobe_path(self) -> str:
        return _find_binary(self.ffprobe_path, ["ffprobe", "ffprobe.exe"])

    @property
    def resolved_blender_path(self) -> Optional[str]:
        candidates = [
            self.blender_executable_path,
            "blender",
            "blender.exe",
            "C:/Program Files/Blender Foundation/Blender 4.3/blender.exe",
            "C:/Program Files/Blender Foundation/Blender 4.2/blender.exe",
            "C:/Program Files/Blender Foundation/Blender 4.1/blender.exe",
        ]
        for c in candidates:
            if not c:
                continue
            p = Path(c)
            if p.is_file():
                return str(p)
            located = shutil.which(c)
            if located:
                return located
        return None

    def parsed_blender_mcp_args(self) -> List[str]:
        return shlex.split(self.blender_mcp_args) if self.blender_mcp_args else []

    def parsed_runway_mcp_args(self) -> List[str]:
        return shlex.split(self.runway_mcp_args) if self.runway_mcp_args else []

    def effective_llm_config(self) -> Dict[str, Optional[str]]:
        """Return effective LLM provider, model, and API key without exposing secrets."""
        provider = (self.llm_provider or "groq").lower()
        if provider == "gemini" or (not self.groq_api_key and self.gemini_api_key and not self.llm_api_key):
            return {
                "provider": "gemini",
                "api_key": self.llm_api_key or self.gemini_api_key,
                "model": self.llm_model or self.gemini_model,
                "fallback_model": self.llm_fallback_model,
            }
        return {
            "provider": provider,
            "api_key": self.llm_api_key or self.groq_api_key,
            "model": self.llm_model or self.groq_model,
            "fallback_model": self.llm_fallback_model or self.groq_fallback_model,
        }

    def capabilities_report(self) -> Dict[str, Any]:
        """Inspect live runtime availability of integrations (zero secrets leaked)."""
        ffmpeg_bin = self.resolved_ffmpeg_path
        ffprobe_bin = self.resolved_ffprobe_path
        blender_bin = self.resolved_blender_path
        llm_cfg = self.effective_llm_config()

        ffmpeg_ok = bool(shutil.which(ffmpeg_bin) or Path(ffmpeg_bin).is_file())
        ffprobe_ok = bool(shutil.which(ffprobe_bin) or Path(ffprobe_bin).is_file())
        blender_mcp_cmd_ok = bool(
            self.blender_mcp_command
            and (shutil.which(self.blender_mcp_command) or Path(self.blender_mcp_command).is_file())
        )
        runway_mcp_ok = bool(self.runway_mcp_url or self.runway_mcp_command)

        existing_models = []
        if self.existing_models_dir.is_dir():
            existing_models = sorted(p.name for p in self.existing_models_dir.glob("*.glb"))

        return {
            "llm": {
                "provider": llm_cfg["provider"],
                "model": llm_cfg["model"],
                "configured": bool(llm_cfg["api_key"]),
            },
            "blender_mcp": {
                "command": self.blender_mcp_command or None,
                "args": self.parsed_blender_mcp_args(),
                "configured": bool(self.blender_mcp_command),
                "executable_found": blender_mcp_cmd_ok,
            },
            "blender_cli": {
                "configured_path": self.blender_executable_path,
                "available": bool(blender_bin),
                "resolved_path": blender_bin,
            },
            "runway_mcp": {
                "configured": runway_mcp_ok,
                "url": self.runway_mcp_url,
                "command": self.runway_mcp_command,
            },
            "runway_api": {
                "configured": bool(self.runway_api_key),
                "base_url": self.runway_api_base_url,
                "version": self.runway_api_version,
                "model": self.runway_model,
            },
            "ffmpeg": {
                "available": ffmpeg_ok,
                "ffmpeg_path": ffmpeg_bin if ffmpeg_ok else None,
                "ffprobe_available": ffprobe_ok,
                "ffprobe_path": ffprobe_bin if ffprobe_ok else None,
            },
            "storage": {
                "provider": self.storage_provider,
                "supabase_configured": bool(self.supabase_url and self.supabase_service_role_key),
                "database_backend": "postgresql" if self.database_url else "sqlite",
            },
            "existing_assets": {
                "models_dir": str(self.existing_models_dir),
                "glb_count": len(existing_models),
                "models": existing_models,
            },
        }

    def ensure_directories(self) -> None:
        base = self.resolved_generated_dir
        for sub in ("scripts", "renders", "clips", "audio", "subtitles", "thumbnails", "storage", "tmp"):
            (base / sub).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings

