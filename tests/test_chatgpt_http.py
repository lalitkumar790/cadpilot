"""Contract checks for the local ChatGPT MCP HTTP entry point."""
from __future__ import annotations

import pytest

from freecad_mcp import chatgpt_http


def test_default_http_port(monkeypatch):
    monkeypatch.delenv("CADPILOT_MCP_HTTP_PORT", raising=False)
    assert chatgpt_http.get_port() == 8765


@pytest.mark.parametrize("value", ["0", "80", "65536", "oops"])
def test_http_port_rejects_invalid_values(monkeypatch, value):
    monkeypatch.setenv("CADPILOT_MCP_HTTP_PORT", value)
    with pytest.raises(ValueError):
        chatgpt_http.get_port()


def test_http_entry_point_is_local_and_uses_streamable_http(monkeypatch):
    monkeypatch.setenv("CADPILOT_MCP_HTTP_PORT", "8899")
    calls = {}

    def record_run(**kwargs):
        calls.update(kwargs)

    monkeypatch.setattr(chatgpt_http.mcp_server, "run", record_run)
    chatgpt_http.run()
    assert calls == {
        "transport": "streamable-http",
        "host": "127.0.0.1",
        "port": 8899,
        "streamable_http_path": "/mcp",
        "stateless_http": True,
        "json_response": True,
    }
