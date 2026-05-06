"""Agent API: list agents, run agents, stream agent responses."""

import json

from flask import Response, jsonify, request, stream_with_context

from app.agents.definitions import get_agent, list_agents
from app.api import api_bp


@api_bp.get("/agents")
def list_agents_endpoint():
    """List all registered specialized agents."""
    return jsonify({"success": True, "data": list_agents()})


@api_bp.post("/agents/<agent_name>/run")
def run_agent(agent_name: str):
    """Run an agent (non-streaming).

    Body:
        {
            "input": "user question or task",
            "context": {"course_id": "...", "chapter_id": "..."}  // optional
        }
    """
    body = request.get_json(silent=True) or {}
    user_input = body.get("input", "")
    if not isinstance(user_input, str) or not user_input.strip():
        return jsonify({"success": False, "error": "input is required"}), 400

    context = body.get("context") or {}
    if not isinstance(context, dict):
        return jsonify({"success": False, "error": "context must be an object"}), 400

    agent = get_agent(agent_name)
    if agent is None:
        return jsonify({"success": False, "error": f"unknown agent: {agent_name}"}), 404

    run = agent.run(user_input, context=context)
    return jsonify({
        "success": True,
        "data": {
            "answer": run.answer,
            "tool_calls": run.tool_calls,
            "citations": run.citations,
            "iterations": run.iterations,
            "finish_reason": run.finish_reason,
            "error": run.error,
        },
    })


@api_bp.post("/agents/<agent_name>/stream")
def stream_agent(agent_name: str):
    """Run an agent with SSE streaming.

    Each event is a JSON line: {"type": "tool_call|tool_result|answer|error", "content": ...}
    """
    body = request.get_json(silent=True) or {}
    user_input = body.get("input", "")
    if not isinstance(user_input, str) or not user_input.strip():
        return jsonify({"success": False, "error": "input is required"}), 400

    context = body.get("context") or {}
    if not isinstance(context, dict):
        return jsonify({"success": False, "error": "context must be an object"}), 400

    agent = get_agent(agent_name)
    if agent is None:
        return jsonify({"success": False, "error": f"unknown agent: {agent_name}"}), 404

    def generate():
        for event in agent.stream(user_input, context=context):
            yield event.to_sse()
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
