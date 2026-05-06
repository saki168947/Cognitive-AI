"""Base Agent class with tool-calling loop.

Pattern:
1. Build messages from system prompt + history + user input
2. Call LLM with tools
3. If tool calls returned, execute them, append results, loop
4. If text response returned, that's the final answer
5. Repeat until max iterations or text response
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from flask import current_app

from app.agents.registry import Tool, registry
from app.llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for a specialized agent."""

    name: str
    description: str
    system_prompt: str
    tools: list[str]  # Tool names this agent can use
    model: str | None = None  # Override LLM_MODEL_NAME
    temperature: float = 0.7
    max_iterations: int = 8  # Max tool-calling rounds before giving up


@dataclass
class AgentEvent:
    """Event emitted during agent execution (for streaming/observability)."""

    type: str  # "thinking" | "tool_call" | "tool_result" | "token" | "answer" | "error"
    content: dict | str

    def to_sse(self) -> str:
        """Format as SSE event."""
        payload = {"type": self.type, "content": self.content}
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@dataclass
class AgentRun:
    """Result of an agent run."""

    answer: str = ""
    tool_calls: list[dict] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
    iterations: int = 0
    finish_reason: str = "stop"  # "stop" | "max_iterations" | "error"
    error: str | None = None


def _llm_client_from_config(model: str | None = None) -> LLMClient:
    cfg = current_app.config
    return LLMClient(
        base_url=cfg["LLM_BASE_URL"],
        api_key=cfg["LLM_API_KEY"],
        model=model or cfg["LLM_MODEL_NAME"],
    )


class Agent:
    """Tool-calling agent that loops until it produces a text answer."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    def _execute_tool(self, name: str, arguments: dict) -> dict:
        """Execute a tool and return its result as a dict."""
        tool: Tool | None = registry.get(name)
        if tool is None:
            return {"error": f"unknown tool: {name}"}
        try:
            return tool.handler(**arguments)
        except TypeError as exc:
            return {"error": f"invalid arguments for {name}: {exc}"}
        except Exception as exc:
            logger.exception("Tool %s failed", name)
            return {"error": f"tool {name} raised: {exc}"}

    def run(self, user_input: str, context: dict | None = None) -> AgentRun:
        """Run the agent to completion (non-streaming)."""
        result = AgentRun()
        for event in self._iterate(user_input, context):
            if event.type == "answer":
                result.answer = event.content if isinstance(event.content, str) else event.content.get("text", "")
            elif event.type == "tool_call":
                result.tool_calls.append(event.content)
            elif event.type == "error":
                result.error = event.content if isinstance(event.content, str) else event.content.get("message", "")
                result.finish_reason = "error"
        return result

    def stream(self, user_input: str, context: dict | None = None):
        """Run the agent with streaming events."""
        yield from self._iterate(user_input, context, stream_tokens=True)

    def _iterate(self, user_input: str, context: dict | None = None, stream_tokens: bool = False):
        """Main agent loop. Yields AgentEvents."""
        cfg = current_app.config
        if not cfg.get("LLM_API_KEY"):
            yield AgentEvent("error", "LLM_API_KEY not configured")
            return

        llm = _llm_client_from_config(self.config.model)
        tool_schemas = registry.schemas_for(self.config.tools)

        # Build system prompt with optional context
        system_content = self.config.system_prompt
        if context:
            ctx_lines = [f"{k}: {v}" for k, v in context.items() if v]
            if ctx_lines:
                system_content += "\n\n## 当前上下文\n" + "\n".join(ctx_lines)

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input},
        ]

        for iteration in range(self.config.max_iterations):
            try:
                if tool_schemas:
                    response = llm.client.chat.completions.create(
                        model=llm.model,
                        messages=messages,
                        temperature=self.config.temperature,
                        tools=tool_schemas,
                        tool_choice="auto",
                    )
                else:
                    response = llm.client.chat.completions.create(
                        model=llm.model,
                        messages=messages,
                        temperature=self.config.temperature,
                    )
            except Exception as exc:
                logger.exception("LLM call failed")
                yield AgentEvent("error", f"LLM call failed: {exc}")
                return

            choice = response.choices[0]
            message = choice.message

            # Tool calls?
            if message.tool_calls:
                # Append assistant message (with tool calls) to history
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ],
                })

                for tc in message.tool_calls:
                    tool_name = tc.function.name
                    try:
                        arguments = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        arguments = {}

                    yield AgentEvent("tool_call", {
                        "name": tool_name,
                        "arguments": arguments,
                    })

                    result = self._execute_tool(tool_name, arguments)

                    yield AgentEvent("tool_result", {
                        "name": tool_name,
                        "result_preview": str(result)[:300],
                    })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    })

                continue  # Loop again to let LLM see tool results

            # No tool calls — final answer
            answer = message.content or ""

            if stream_tokens and answer:
                # Stream the final answer token by token via a second call
                # (Simpler: just yield as one event since we already have the full text)
                # Future: if we want true token streaming, refactor to use chat_stream from start.
                yield AgentEvent("answer", answer)
            else:
                yield AgentEvent("answer", answer)

            return

        yield AgentEvent("error", f"max iterations ({self.config.max_iterations}) reached")
