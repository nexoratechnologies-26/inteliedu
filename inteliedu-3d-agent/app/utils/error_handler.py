"""Custom domain errors and FastAPI error envelope handlers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AgentError(Exception):
    """Base error for the 3D Generation Agent."""

    def __init__(
        self,
        message: str,
        code: str = "AGENT_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ValidationError(AgentError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR", status_code=422, details=details)


class DependencyUnavailableError(AgentError):
    """Raised when a required external renderer/API/MCP server is missing or unreachable."""

    def __init__(
        self,
        message: str,
        missing_dependencies: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        merged = dict(details or {})
        if missing_dependencies:
            merged["missing_dependencies"] = missing_dependencies
        super().__init__(
            message,
            code="DEPENDENCY_UNAVAILABLE",
            status_code=503,
            details=merged,
        )
        self.missing_dependencies = missing_dependencies or []


class MCPConnectionError(DependencyUnavailableError):
    def __init__(self, server_name: str, message: str) -> None:
        super().__init__(
            f"MCP server '{server_name}' unavailable: {message}",
            missing_dependencies=[server_name],
            details={"server": server_name},
        )


class MCPToolValidationError(AgentError):
    def __init__(self, tool_name: str, message: str) -> None:
        super().__init__(
            f"Invalid arguments for MCP tool '{tool_name}': {message}",
            code="MCP_TOOL_VALIDATION_ERROR",
            status_code=400,
            details={"tool_name": tool_name},
        )


class RunwayAPIError(AgentError):
    def __init__(self, message: str, status_code: int = 502, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code="RUNWAY_API_ERROR", status_code=status_code, details=details)


class VideoProcessingError(AgentError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code="VIDEO_PROCESSING_ERROR", status_code=500, details=details)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach INTELIEDU-consistent JSON error envelope handlers to FastAPI."""

    @app.exception_handler(AgentError)
    async def handle_agent_error(_: Request, exc: AgentError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "code": exc.code,
                "errors": [exc.details] if exc.details else [],
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Request payload validation failed.",
                "code": "REQUEST_VALIDATION_ERROR",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "code": "HTTP_ERROR",
                "errors": [],
            },
        )

