"""Tool registry for agent tool calling.

Tools self-register at import time. Each tool has:
- name: unique identifier
- description: what it does (shown to LLM)
- parameters: JSONSchema for arguments
- handler: callable that executes the tool

The registry is global and immutable after import.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Tool:
    """A tool that an agent can call."""

    name: str
    description: str
    parameters: dict  # JSONSchema for tool arguments
    handler: Callable[..., dict]
    requires_app_context: bool = True

    def to_openai_schema(self) -> dict:
        """Convert to OpenAI function/tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class ToolRegistry:
    """Global registry of available tools."""

    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_names(self) -> list[str]:
        return sorted(self._tools.keys())

    def schemas_for(self, names: list[str]) -> list[dict]:
        """Get OpenAI schemas for a subset of tools."""
        return [self._tools[n].to_openai_schema() for n in names if n in self._tools]

    def all_schemas(self) -> list[dict]:
        return [t.to_openai_schema() for t in self._tools.values()]


# Global registry instance
registry = ToolRegistry()


def register_tool(name: str, description: str, parameters: dict, requires_app_context: bool = True):
    """Decorator to register a function as a tool."""

    def decorator(func: Callable[..., dict]) -> Callable[..., dict]:
        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
            handler=func,
            requires_app_context=requires_app_context,
        )
        registry.register(tool)
        return func

    return decorator
