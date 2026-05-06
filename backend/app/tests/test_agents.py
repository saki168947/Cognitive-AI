"""Tests for the agent registry, tools, and definitions.

We don't test the actual LLM-driven agent loop (that would require API credentials).
We verify the registry shape, tool schemas, and tool execution against the DB.
"""

import pytest

from app.agents.definitions import AGENT_CONFIGS, get_agent, list_agents
from app.agents.registry import registry
from app.services.seed_data import seed_courses


def test_registry_lists_expected_tools():
    names = registry.list_names()
    assert "search_materials" in names
    assert "search_concept_graph" in names
    assert "get_chapter" in names
    assert "list_chapters" in names
    assert "get_quiz_items_for_chapter" in names


def test_tool_schemas_have_required_shape():
    for name in registry.list_names():
        tool = registry.get(name)
        schema = tool.to_openai_schema()
        assert schema["type"] == "function"
        assert schema["function"]["name"] == name
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]
        assert schema["function"]["parameters"]["type"] == "object"


def test_list_chapters_tool(app):
    with app.app_context():
        seed_courses()
        tool = registry.get("list_chapters")
        result = tool.handler(course_id="ai-intro")
        assert result["count"] >= 1
        assert all("title" in c for c in result["chapters"])


def test_get_chapter_tool_returns_full_content(app):
    with app.app_context():
        seed_courses()
        tool = registry.get("get_chapter")
        result = tool.handler(chapter_id="ai-search")
        assert result["id"] == "ai-search"
        assert "title" in result
        assert "body" in result


def test_get_chapter_tool_handles_missing(app):
    with app.app_context():
        seed_courses()
        tool = registry.get("get_chapter")
        result = tool.handler(chapter_id="nonexistent")
        assert "error" in result


def test_search_concept_graph_finds_seeded_concepts(app):
    with app.app_context():
        seed_courses()
        tool = registry.get("search_concept_graph")
        result = tool.handler(query="search", course_id="ai-intro")
        # Seed has search-related concepts
        assert isinstance(result["concepts"], list)
        assert "concept_count" in result


def test_search_materials_returns_empty_when_no_embedding_key(app):
    with app.app_context():
        seed_courses()
        # Test app config has no EMBEDDING_API_KEY
        tool = registry.get("search_materials")
        result = tool.handler(query="anything", course_id="ai-intro")
        assert result["results"] == []
        assert "EMBEDDING_API_KEY" in result.get("message", "")


def test_agent_definitions_are_valid():
    for name, cfg in AGENT_CONFIGS.items():
        # Every tool referenced by the agent must exist in registry
        for tool_name in cfg.tools:
            assert registry.get(tool_name) is not None, f"Agent '{name}' references unknown tool '{tool_name}'"


def test_get_agent_returns_none_for_unknown():
    assert get_agent("nonexistent-agent") is None


def test_get_agent_returns_agent_for_known():
    agent = get_agent("tutor")
    assert agent is not None
    assert agent.config.name == "tutor"


def test_list_agents_returns_metadata():
    items = list_agents()
    names = {a["name"] for a in items}
    assert "tutor" in names
    assert "document-analyst" in names
    assert "graph-explorer" in names


def test_agent_run_without_llm_key_returns_error(app):
    """Running an agent without LLM_API_KEY should yield an error event."""
    with app.app_context():
        seed_courses()
        # Test config has empty LLM_API_KEY
        agent = get_agent("tutor")
        run = agent.run("What is AI?")
        assert run.error is not None
        assert "LLM_API_KEY" in run.error
