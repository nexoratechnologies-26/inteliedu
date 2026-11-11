"""Dynamic MCP tool registry with JSON Schema argument validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from jsonschema import Draft202012Validator, ValidationError as JSONSchemaError

from app.utils.error_handler import MCPToolValidationError


@dataclass(frozen=True)
class MCPToolDescriptor:
    """Metadata describing a real tool discovered from a connected MCP server."""

    server_name: str
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "server_name": self.server_name,
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    """Stores discovered MCP tools and validates tool arguments before invocation."""

    def __init__(self) -> None:
        self._tools: Dict[str, Dict[str, MCPToolDescriptor]] = {}

    def register_tools(self, server_name: str, tools: Iterable[MCPToolDescriptor]) -> List[MCPToolDescriptor]:
        server_map: Dict[str, MCPToolDescriptor] = {}
        for tool in tools:
            server_map[tool.name] = tool
        self._tools[server_name] = server_map
        return list(server_map.values())

    def clear_server(self, server_name: str) -> None:
        self._tools.pop(server_name, None)

    def list_tools(self, server_name: Optional[str] = None) -> List[MCPToolDescriptor]:
        if server_name:
            return list(self._tools.get(server_name, {}).values())
        all_tools: List[MCPToolDescriptor] = []
        for server_map in self._tools.values():
            all_tools.extend(server_map.values())
        return all_tools

    def get_tool(self, server_name: str, tool_name: str) -> Optional[MCPToolDescriptor]:
        return self._tools.get(server_name, {}).get(tool_name)

    def find_matching_tool(
        self,
        server_name: str,
        preferred_names: Iterable[str] = (),
        keyword_groups: Iterable[Iterable[str]] = (),
    ) -> Optional[MCPToolDescriptor]:
        """Select a discovered tool by exact name first, then by description/name keywords."""
        server_map = self._tools.get(server_name, {})
        for name in preferred_names:
            if name in server_map:
                return server_map[name]

        for keywords in keyword_groups:
            kw_lower = [k.lower() for k in keywords]
            for tool in server_map.values():
                haystack = f"{tool.name} {tool.description}".lower()
                if all(kw in haystack for kw in kw_lower):
                    return tool
        return None

    def validate_arguments(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Validate tool call arguments against the discovered MCP tool's inputSchema."""
        descriptor = self.get_tool(server_name, tool_name)
        if descriptor is None:
            raise MCPToolValidationError(
                tool_name,
                f"Tool '{tool_name}' was not discovered on MCP server '{server_name}'.",
            )
        schema = descriptor.input_schema
        if not schema:
            return
        try:
            validator = Draft202012Validator(schema)
            validator.validate(arguments)
        except JSONSchemaError as exc:
            raise MCPToolValidationError(tool_name, exc.message) from exc

