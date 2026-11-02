from __future__ import annotations

import json
import socket
import threading

import pytest

from freecad_mcp.config import SocketConfig
from freecad_mcp.transport.socket_client import (
    FreeCADConnectionError,
    _receive_response,
    send_command,
)


def test_receive_newline_delimited_response_in_fragments():
    client, peer = socket.socketpair()
    config = SocketConfig(recv_buffer_size=4)

    def writer():
        peer.sendall(b'{"ok":')
        peer.sendall(b'true}\n')
        peer.close()

    thread = threading.Thread(target=writer)
    thread.start()
    try:
        assert _receive_response(client, config) == {"ok": True}
    finally:
        client.close()
        thread.join(timeout=1)


def test_receive_legacy_json_without_newline():
    client, peer = socket.socketpair()
    config = SocketConfig()

    def writer():
        peer.sendall(b'{"legacy":true}')
        # Keep the connection open: the client must recognize complete JSON.
        threading.Event().wait(0.05)
        peer.close()

    thread = threading.Thread(target=writer)
    thread.start()
    try:
        assert _receive_response(client, config) == {"legacy": True}
    finally:
        client.close()
        thread.join(timeout=1)


def test_receive_response_enforces_size_limit():
    client, peer = socket.socketpair()
    config = SocketConfig(max_message_bytes=5)

    def writer():
        peer.sendall(b'{"long":true}\n')
        peer.close()

    thread = threading.Thread(target=writer)
    thread.start()
    try:
        with pytest.raises(FreeCADConnectionError, match="exceeded"):
            _receive_response(client, config)
    finally:
        client.close()
        thread.join(timeout=1)


def test_send_command_rejects_invalid_tool_name():
    with pytest.raises(ValueError, match="tool_name"):
        send_command("")


def test_send_command_rejects_non_dict_args():
    with pytest.raises(TypeError, match="args"):
        send_command("create_box", ["not", "a", "dict"])


def test_send_command_rejects_oversized_payload():
    config = SocketConfig(max_message_bytes=10)
    with pytest.raises(ValueError, match="message limit"):
        send_command("create_box", {"label": "this is too large"}, config=config)


def test_send_command_writes_newline_delimited_json(monkeypatch):
    client, peer = socket.socketpair()
    config = SocketConfig()

    def fake_open_socket(_config):
        return client

    def server():
        request = bytearray()
        while b"\n" not in request:
            request.extend(peer.recv(1024))
        peer.sendall(json.dumps({"accepted": True}).encode() + b"\n")
        peer.close()

    thread = threading.Thread(target=server)
    thread.start()
    monkeypatch.setattr(
        "freecad_mcp.transport.socket_client._open_socket", fake_open_socket
    )
    try:
        assert send_command("ping", {"x": 1}, config=config) == {"accepted": True}
    finally:
        thread.join(timeout=1)
