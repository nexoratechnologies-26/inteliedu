"""Official MCP Python SDK client wrapper supporting stdio and Streamable HTTP transports."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import create_mcp_http_client

from app.mcp.tool_registry import MCPToolDescriptor, ToolRegistry
from app.utils.error_handler import MCPConnectionError, MCPToolValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for connecting to an external MCP server."""

    name: str
    transport: str = "stdio"  # "stdio" | "streamable_http"
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None
    url: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class MCPCallResult:
    """Normalized result from an MCP tool invocation."""

    server_name: str
    tool_name: str
    is_error: bool
    text_content: str
    structured_content: Optional[Any] = None
    raw_content: List[Dict[str, Any]] = field(default_factory=list)


def _extract_tool_output(result: Any) -> tuple[bool, str, Optional[Any], List[Dict[str, Any]]]:
    """Normalize mcp CallToolResult into plain text and structured JSON when present."""
    is_error = bool(
        getattr(result, "is_error", None)
        if getattr(result, "is_error", None) is not None
        else getattr(result, "isError", False)
    )
    structured = getattr(result, "structured_content", None)
    if structured is None:
        structured = getattr(result, "structuredContent", None)
    raw_blocks: List[Dict[str, Any]] = []
    text_parts: List[str] = []

    for item in getattr(result, "content", []) or []:
        block_type = getattr(item, "type", "unknown")
        if hasattr(item, "model_dump"):
            raw_blocks.append(item.model_dump())
        else:
            raw_blocks.append({"type": block_type, "value": str(item)})

        text_val = getattr(item, "text", None)
        if text_val is not None:
            text_parts.append(str(text_val))
        elif getattr(item, "data", None) is not None:
            text_parts.append(f"[{block_type} data: {len(str(item.data))} chars]")

    joined = "\n".join(text_parts).strip()
    if isinstance(structured, dict) and set(structured.keys()) == {"result"} and isinstance(structured["result"], str):
        try:
            unwrapped = json.loads(structured["result"])
            if isinstance(unwrapped, (dict, list)):
                structured = unwrapped
        except json.JSONDecodeError:
            pass
    if structured is None and joined:
        try:
            parsed = json.loads(joined)
            if isinstance(parsed, (dict, list)):
                structured = parsed
        except json.JSONDecodeError:
            pass

    return is_error, joined, structured, raw_blocks


class MCPClientManager:
    """Manages connections, tool discovery, validation, and safe retries against MCP servers."""

    def __init__(self, registry: Optional[ToolRegistry] = None) -> None:
        self.registry = registry or ToolRegistry()

    @asynccontextmanager
    async def session(self, config: MCPServerConfig) -> AsyncIterator[ClientSession]:
        """Open a live MCP ClientSession and perform protocol initialization."""
        if config.transport == "streamable_http":
            if not config.url:
                raise MCPConnectionError(config.name, "Streamable HTTP URL is not configured.")
            try:
                async with create_mcp_http_client(headers=config.headers or None) as http_client:
                    async with streamable_http_client(config.url, http_client=http_client) as streams:
                        read_stream, write_stream = streams[0], streams[1]
                        async with ClientSession(read_stream, write_stream) as session:
                            await session.initialize()
                            yield session
            except Exception as exc:
                raise MCPConnectionError(config.name, str(exc)) from exc
            return

        if not config.command:
            raise MCPConnectionError(config.name, "Stdio MCP command is not configured.")

        resolved_cmd = shutil.which(config.command) or config.command
        if not shutil.which(resolved_cmd) and not Path(resolved_cmd).is_file():
            raise MCPConnectionError(
                config.name, f"MCP executable '{config.command}' was not found on PATH or disk."
            )

        merged_env = os.environ.copy()
        if config.env:
            merged_env.update(config.env)

        params = StdioServerParameters(
            command=resolved_cmd,
            args=config.args,
            env=merged_env,
            cwd=config.cwd,
        )
        try:
            async with stdio_client(params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    yield session
        except Exception as exc:
            raise MCPConnectionError(config.name, str(exc)) from exc

    async def discover_tools(self, config: MCPServerConfig) -> List[MCPToolDescriptor]:
        """Connect to an MCP server, inspect real tools & schemas, and populate the registry."""
        async with self.session(config) as session:
            result = await session.list_tools()
            descriptors: List[MCPToolDescriptor] = []
            for tool in result.tools:
                input_schema = (
                    getattr(tool, "input_schema", None)
                    or getattr(tool, "inputSchema", None)
                    or {}
                )
                descriptors.append(
                    MCPToolDescriptor(
                        server_name=config.name,
                        name=tool.name,
                        description=getattr(tool, "description", "") or "",
                        input_schema=input_schema,
                    )
                )
            return self.registry.register_tools(config.name, descriptors)

    async def call_tool(
        self,
        config: MCPServerConfig,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        *,
        timeout_seconds: float = 120.0,
        retries: int = 1,
        retry_delay_seconds: float = 1.0,
    ) -> MCPCallResult:
        """Discover (if needed), validate arguments against JSON Schema, and invoke an MCP tool."""
        args = arguments or {}
        if not self.registry.get_tool(config.name, tool_name):
            await self.discover_tools(config)

        # Always validate against the real discovered tool schema before execution
        self.registry.validate_arguments(config.name, tool_name, args)

        last_exc: Optional[Exception] = None
        for attempt in range(retries + 1):
            try:
                async with self.session(config) as session:
                    raw_result = await asyncio.wait_for(
                        session.call_tool(
                            name=tool_name,
                            arguments=args,
                            read_timeout_seconds=timeout_seconds,
                        ),
                        timeout=timeout_seconds + 5.0,
                    )
                is_error, text_content, structured, raw_blocks = _extract_tool_output(raw_result)
                return MCPCallResult(
                    server_name=config.name,
                    tool_name=tool_name,
                    is_error=is_error,
                    text_content=text_content,
                    structured_content=structured,
                    raw_content=raw_blocks,
                )
            except MCPToolValidationError:
                raise
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "MCP tool call failed (%s/%s, attempt %s/%s): %s",
                    config.name,
                    tool_name,
                    attempt + 1,
                    retries + 1,
                    exc,
                )
                if attempt < retries:
                    await asyncio.sleep(retry_delay_seconds)

        raise MCPConnectionError(
            config.name,
            f"Tool '{tool_name}' failed after {retries + 1} attempt(s): {last_exc}",
        )
