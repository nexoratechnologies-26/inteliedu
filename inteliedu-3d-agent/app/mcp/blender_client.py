"""Blender MCP client with dynamic tool discovery and controlled Blender CLI fallback."""

from __future__ import annotations

import asyncio
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import Settings, get_settings
from app.mcp.client import MCPClientManager, MCPServerConfig
from app.mcp.tool_registry import MCPToolDescriptor, ToolRegistry
from app.utils.error_handler import DependencyUnavailableError, MCPConnectionError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BlenderExecutionResult:
    """Outcome of executing a Blender scene build & render task."""

    success: bool
    engine_used: str  # "blender_mcp" | "blender_cli"
    output_path: Optional[str] = None
    scene_info: Optional[Dict[str, Any]] = None
    stdout: str = ""
    stderr: str = ""
    discovered_tools: List[str] = field(default_factory=list)


class BlenderMCPClient:
    """Orchestrates Blender via MCP first, or headless Blender CLI when available locally."""

    SERVER_NAME = "blender_mcp"

    def __init__(
        self,
        settings: Optional[Settings] = None,
        mcp_manager: Optional[MCPClientManager] = None,
        registry: Optional[ToolRegistry] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.registry = registry or ToolRegistry()
        self.mcp_manager = mcp_manager or MCPClientManager(registry=self.registry)

    def build_server_config(self) -> Optional[MCPServerConfig]:
        if not self.settings.blender_mcp_command:
            return None
        return MCPServerConfig(
            name=self.SERVER_NAME,
            transport="stdio",
            command=self.settings.blender_mcp_command,
            args=self.settings.parsed_blender_mcp_args(),
            env={
                "BLENDER_HOST": self.settings.blender_mcp_host,
                "BLENDER_PORT": str(self.settings.blender_mcp_port),
            },
        )

    async def discover_tools(self) -> List[MCPToolDescriptor]:
        """Inspect actual tools exposed by the configured Blender MCP server."""
        cfg = self.build_server_config()
        if not cfg:
            raise MCPConnectionError(
                self.SERVER_NAME,
                "BLENDER_MCP_COMMAND is not configured in environment.",
            )
        return await self.mcp_manager.discover_tools(cfg)

    def _select_code_execution_tool(self) -> Optional[MCPToolDescriptor]:
        return self.registry.find_matching_tool(
            self.SERVER_NAME,
            preferred_names=("execute_blender_code", "execute_code", "run_python", "run_script"),
            keyword_groups=(("execute", "blender"), ("execute", "code"), ("python", "script")),
        )

    def _select_scene_info_tool(self) -> Optional[MCPToolDescriptor]:
        return self.registry.find_matching_tool(
            self.SERVER_NAME,
            preferred_names=("get_scene_info", "scene_info", "inspect_scene"),
            keyword_groups=(("scene", "info"), ("get", "scene")),
        )

    @staticmethod
    def _build_code_payload(tool: MCPToolDescriptor, script_code: str) -> Dict[str, Any]:
        """Populate arguments strictly according to the discovered tool's inputSchema."""
        properties = tool.input_schema.get("properties", {})
        for key in ("code", "script", "python_code", "source"):
            if key in properties:
                return {key: script_code}
        required = tool.input_schema.get("required", [])
        if required:
            return {required[0]: script_code}
        return {"code": script_code}

    async def execute_scene_script(
        self,
        script_path: Path,
        expected_output_path: Path,
        timeout_seconds: Optional[int] = None,
    ) -> BlenderExecutionResult:
        """
        Execute a generated Blender Python scene & render script.

        Priority:
        1. Connected Blender MCP server (discovering real tools + validating schema).
        2. Local headless Blender CLI if `blender.exe` / `blender` actually exists.
        3. Raise DependencyUnavailableError with exact missing tools (never fake output).
        """
        timeout = float(timeout_seconds or self.settings.blender_render_timeout_seconds)
        script_code = script_path.read_text(encoding="utf-8")
        mcp_error_message: Optional[str] = None

        cfg = self.build_server_config()
        if cfg:
            try:
                tools = await self.discover_tools()
                tool_names = [t.name for t in tools]
                code_tool = self._select_code_execution_tool()
                if not code_tool:
                    raise MCPConnectionError(
                        self.SERVER_NAME,
                        f"No Blender code-execution tool discovered. Available tools: {tool_names}",
                    )

                scene_info: Optional[Dict[str, Any]] = None
                info_tool = self._select_scene_info_tool()
                if info_tool and not info_tool.input_schema.get("required"):
                    info_res = await self.mcp_manager.call_tool(
                        cfg, info_tool.name, {}, timeout_seconds=30.0, retries=1
                    )
                    if not info_res.is_error:
                        scene_info = (
                            info_res.structured_content
                            if isinstance(info_res.structured_content, dict)
                            else {"raw": info_res.text_content}
                        )

                payload = self._build_code_payload(code_tool, script_code)
                exec_res = await self.mcp_manager.call_tool(
                    cfg,
                    code_tool.name,
                    payload,
                    timeout_seconds=timeout,
                    retries=0,
                )
                if exec_res.is_error:
                    raise RuntimeError(f"Blender MCP returned tool error: {exec_res.text_content}")

                if expected_output_path.is_file() and expected_output_path.stat().st_size > 0:
                    return BlenderExecutionResult(
                        success=True,
                        engine_used="blender_mcp",
                        output_path=str(expected_output_path),
                        scene_info=scene_info,
                        stdout=exec_res.text_content,
                        discovered_tools=tool_names,
                    )

                raise RuntimeError(
                    f"Blender MCP tool '{code_tool.name}' completed, but output file was not produced at {expected_output_path}."
                )
            except Exception as exc:
                mcp_error_message = str(exc)
                logger.warning("Blender MCP execution failed (%s); checking local Blender CLI fallback.", exc)

        # Controlled Fallback: Local headless Blender CLI (only if binary really exists)
        blender_bin = self.settings.resolved_blender_path
        if blender_bin and Path(blender_bin).is_file():
            logger.info("Executing Blender script via headless CLI fallback: %s", blender_bin)
            proc = await asyncio.to_thread(
                subprocess.run,
                [blender_bin, "--background", "--python", str(script_path)],
                capture_output=True,
                text=True,
                timeout=int(timeout),
                check=False,
            )
            if proc.returncode == 0 and expected_output_path.is_file() and expected_output_path.stat().st_size > 0:
                return BlenderExecutionResult(
                    success=True,
                    engine_used="blender_cli",
                    output_path=str(expected_output_path),
                    stdout=proc.stdout[-4000:],
                    stderr=proc.stderr[-4000:],
                )
            raise RuntimeError(
                json.dumps(
                    {
                        "message": "Headless Blender CLI execution failed.",
                        "returncode": proc.returncode,
                        "mcp_error": mcp_error_message,
                        "stderr": proc.stderr[-1500:],
                    }
                )
            )

        missing = []
        if not cfg:
            missing.append("BLENDER_MCP_COMMAND (not configured)")
        elif mcp_error_message:
            missing.append(f"Blender MCP server ({mcp_error_message})")
        missing.append(
            f"Blender executable (not found at '{self.settings.blender_executable_path}' or PATH)"
        )

        raise DependencyUnavailableError(
            "Cannot render 3D scenes: neither Blender MCP nor a local Blender installation is available. "
            "Generated bpy script was saved for inspection.",
            missing_dependencies=missing,
            details={
                "script_path": str(script_path),
                "expected_output_path": str(expected_output_path),
            },
        )

