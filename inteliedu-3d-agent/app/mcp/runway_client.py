"""Runway MCP client for inspecting and calling official/configured Runway MCP servers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.config import Settings, get_settings
from app.mcp.client import MCPCallResult, MCPClientManager, MCPServerConfig
from app.mcp.tool_registry import MCPToolDescriptor, ToolRegistry
from app.utils.error_handler import MCPConnectionError


class RunwayMCPClient:
    """Connects to Runway MCP if configured; otherwise signals fallback to Runway REST API."""

    SERVER_NAME = "runway_mcp"

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
        if self.settings.runway_mcp_url:
            headers: Dict[str, str] = {}
            if self.settings.runway_mcp_token:
                headers["Authorization"] = f"Bearer {self.settings.runway_mcp_token}"
            return MCPServerConfig(
                name=self.SERVER_NAME,
                transport="streamable_http",
                url=self.settings.runway_mcp_url,
                headers=headers,
            )
        if self.settings.runway_mcp_command:
            env: Dict[str, str] = {}
            if self.settings.runway_api_key:
                env["RUNWAY_API_KEY"] = self.settings.runway_api_key
            return MCPServerConfig(
                name=self.SERVER_NAME,
                transport="stdio",
                command=self.settings.runway_mcp_command,
                args=self.settings.parsed_runway_mcp_args(),
                env=env,
            )
        return None

    async def discover_tools(self) -> List[MCPToolDescriptor]:
        cfg = self.build_server_config()
        if not cfg:
            raise MCPConnectionError(
                self.SERVER_NAME,
                "Neither RUNWAY_MCP_URL nor RUNWAY_MCP_COMMAND is configured.",
            )
        return await self.mcp_manager.discover_tools(cfg)

    async def generate_video(
        self,
        prompt_text: str,
        duration: int = 5,
        ratio: str = "1280:720",
        prompt_image: Optional[str] = None,
    ) -> MCPCallResult:
        """Discover Runway MCP video tool dynamically and invoke with validated schema args."""
        cfg = self.build_server_config()
        if not cfg:
            raise MCPConnectionError(self.SERVER_NAME, "Runway MCP is not configured.")

        await self.discover_tools()
        tool = self.registry.find_matching_tool(
            self.SERVER_NAME,
            preferred_names=("runway_generateVideo", "generate_video", "text_to_video"),
            keyword_groups=(("generate", "video"), ("text", "video")),
        )
        if not tool:
            available = [t.name for t in self.registry.list_tools(self.SERVER_NAME)]
            raise MCPConnectionError(
                self.SERVER_NAME,
                f"No video generation tool discovered on Runway MCP. Available: {available}",
            )

        props = tool.input_schema.get("properties", {})
        args: Dict[str, Any] = {}
        for key in ("promptText", "prompt", "text", "description"):
            if key in props:
                args[key] = prompt_text
                break
        for key in ("duration", "seconds"):
            if key in props:
                args[key] = duration
                break
        if "ratio" in props:
            args["ratio"] = ratio
        if prompt_image:
            for key in ("promptImage", "image_url", "image"):
                if key in props:
                    args[key] = prompt_image
                    break

        return await self.mcp_manager.call_tool(
            cfg,
            tool.name,
            args,
            timeout_seconds=float(self.settings.runway_timeout_seconds),
            retries=0,
        )

