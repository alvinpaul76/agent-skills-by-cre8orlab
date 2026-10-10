#!/usr/bin/env python3
"""OPTIONAL: minimal MCP server exposing one tool, trigger_pending_alert.

The hooks in this plugin are the recommended way to get alerts because they
fire deterministically. This server only helps if you want Claude to say WHAT
it is asking about (it can pass a short message), and it only works when the
model chooses to call the tool, so it can be forgotten. Calls cost a few tokens.

Register it (use an absolute path):
    claude mcp add voice-notify -- python3 /abs/path/to/plugins/voice-notify/mcp/alert_server.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from alert import DEFAULT_MESSAGE, speak  # noqa: E402

SERVER_INFO = {"name": "voice-notify", "version": "1.0.0"}
TOOL = {
    "name": "trigger_pending_alert",
    "description": (
        "Speak a local audio alert. Call right before asking the user a "
        "question or requesting approval."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Optional short spoken message, e.g. 'which database?'",
            }
        },
    },
}


def send(req_id, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle(req):
    method, req_id = req.get("method"), req.get("id")
    if req_id is None:  # notifications never get a reply
        return
    if method == "initialize":
        params = req.get("params") or {}
        send(req_id, {
            "protocolVersion": params.get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })
    elif method == "ping":
        send(req_id, {})
    elif method == "tools/list":
        send(req_id, {"tools": [TOOL]})
    elif method == "tools/call":
        params = req.get("params") or {}
        if params.get("name") != TOOL["name"]:
            send(req_id, error={"code": -32602, "message": "Unknown tool"})
            return
        args = params.get("arguments") or {}
        speak(args.get("message") or DEFAULT_MESSAGE)
        send(req_id, {"content": [{"type": "text", "text": "Alert played."}]})
    else:
        send(req_id, error={"code": -32601, "message": f"Method not found: {method}"})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(req, dict):
            continue
        try:
            handle(req)
        except Exception as exc:  # always answer requests that have an id
            if req.get("id") is not None:
                send(req["id"], error={"code": -32603, "message": str(exc)})


if __name__ == "__main__":
    main()
