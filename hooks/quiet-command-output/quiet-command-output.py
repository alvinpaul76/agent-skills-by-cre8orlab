#!/usr/bin/env python3
"""
Claude Code PreToolUse hook + quiet command runner.

Hook mode:
  Reads Claude Code hook JSON from stdin. For a conservative allowlist of
  simple, non-interactive Bash commands, returns updatedInput.command that
  invokes this same script in runner mode.

Runner mode:
  Runs the original command through the shell, captures combined output, and
  emits a concise success summary or bounded diagnostics on failure.

This deliberately does NOT attempt to rewrite arbitrary shell syntax.
"""
from __future__ import annotations

import base64
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

# Only these command families are eligible. Keep this list conservative.
ELIGIBLE_PREFIXES = (
    "npm install", "npm ci", "npm run build",
    "pnpm install", "pnpm i ", "pnpm build", "pnpm run build",
    "yarn install", "yarn build", "yarn run build",
    "pip install", "pip3 install", "uv pip install", "uv sync",
    "python -m pip install", "python3 -m pip install",
    "pytest", "python -m pytest", "python3 -m pytest",
    "npm test", "npm run test", "pnpm test", "pnpm run test",
    "yarn test", "yarn run test",
    "cargo build", "cargo test",
    "go build", "go test",
)

# Shell syntax that makes transparent wrapping too risky. Fail open instead.
UNSAFE_SYNTAX = re.compile(r"[\n\r|;&<>`]")
UNSAFE_SUBSHELL = re.compile(r"\$\s*\(")
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

ERROR_RE = re.compile(
    r"(^|\b)(error|errors|failed|failure|fatal|exception|traceback|"
    r"warning|warn:|assertionerror|test failures?|npm err!|"
    r"build failed|compilation failed|cannot find|not found)(\b|:)",
    re.IGNORECASE,
)
SUMMARY_RE = re.compile(
    r"(added \d+ packages?|audited \d+ packages?|up to date|"
    r"found \d+ vulnerabilities?|\d+ (passed|failed|skipped|errors?)|"
    r"\d+ (tests?|checks?|packages?|files?)|"
    r"test result:|tests? run:|build (succeeded|completed|finished)|"
    r"compiled successfully|successfully built|"
    r"finished (dev|release) \[|"
    r"finished in \d|"
    r"^ok(?:\s|$)|^--- PASS:|^--- FAIL:)",
    re.IGNORECASE,
)
MAX_FAILURE_LINES = 240
MAX_SUCCESS_LINES = 100


def eligible(command: str) -> bool:
    cmd = command.strip()
    if not cmd or len(cmd) > 5000:
        return False
    if UNSAFE_SYNTAX.search(cmd) or UNSAFE_SUBSHELL.search(cmd):
        return False
    # Avoid commands with redirection/expansion or leading environment wrappers.
    if "$" in cmd or cmd.startswith(("sudo ", "env ", "time ", "nohup ")):
        return False
    # Do not wrap likely interactive commands.
    if any(x in cmd.lower() for x in ("--interactive", " -i", "login", "watch ")):
        return False
    for prefix in ELIGIBLE_PREFIXES:
        normalized = prefix.rstrip()
        if cmd == normalized:
            return True
        if prefix.endswith(" "):
            if cmd.startswith(prefix):
                return True
        elif cmd.startswith(prefix + " "):
            return True
    return False


def hook_mode() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # Fail open: malformed hook input must not block the user's command.
        return 0

    if payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command")
    if not isinstance(command, str) or not eligible(command):
        return 0

    encoded = base64.b64encode(command.encode("utf-8")).decode("ascii")
    runner = str(Path(__file__).resolve())
    # The base64 payload prevents shell metacharacters in the original command
    # from being interpreted by the outer shell. The original command itself is
    # only passed to subprocess(shell=True) after conservative eligibility checks.
    replacement = (
        f"{shlex.quote(sys.executable)} {shlex.quote(runner)} --run-b64 {encoded}"
    )
    updated = dict(tool_input)
    updated["command"] = replacement
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": updated,
        }
    }
    sys.stdout.write(json.dumps(result))
    return 0


def clean(text: str) -> str:
    return ANSI.sub("", text).replace("\r", "")


def select_success_output(lines: list[str]) -> list[str]:
    if len(lines) <= 18:
        # If it was not actually noisy, keep all of it.
        return lines
    keep_indices = set()
    for i, line in enumerate(lines):
        if ERROR_RE.search(line) or SUMMARY_RE.search(line):
            keep_indices.add(i)
    # Keep a little trailing context, which often contains the final summary.
    for i in range(max(0, len(lines) - 8), len(lines)):
        if lines[i].strip():
            keep_indices.add(i)
    selected = sorted(keep_indices)
    result = [lines[i] for i in selected if lines[i].strip()]
    if not result:
        result = [line for line in lines[-8:] if line.strip()]
    return result[:MAX_SUCCESS_LINES]


def select_failure_output(lines: list[str]) -> tuple[list[str], bool]:
    if len(lines) <= MAX_FAILURE_LINES:
        return lines, False
    important = set()
    for i, line in enumerate(lines):
        if ERROR_RE.search(line) or SUMMARY_RE.search(line):
            important.update(range(max(0, i - 2), min(len(lines), i + 3)))
    # Always include the tail, where test runners usually print their summary.
    important.update(range(max(0, len(lines) - 60), len(lines)))
    chosen = sorted(important)
    truncated = len(chosen) > MAX_FAILURE_LINES
    if truncated:
        chosen = chosen[:MAX_FAILURE_LINES // 2] + chosen[-(MAX_FAILURE_LINES // 2):]
    return [lines[i] for i in chosen], truncated


def run_mode(encoded: str) -> int:
    try:
        command = base64.b64decode(encoded.encode("ascii"), validate=True).decode("utf-8")
    except Exception:
        print("quiet-command-output: invalid encoded command; refusing to run", file=sys.stderr)
        return 2

    # Revalidate even though hook mode performed the same check.
    if not eligible(command):
        print("quiet-command-output: command is not eligible for wrapping; refusing to run",
              file=sys.stderr)
        return 2

    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            env=os.environ.copy(),
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
        output = clean(proc.stdout or "")
    except KeyboardInterrupt:
        print("quiet-command-output: interrupted; command was stopped", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"quiet-command-output: runner error: {exc}", file=sys.stderr)
        return 127

    lines = output.splitlines()
    if proc.returncode == 0:
        chosen = select_success_output(lines)
        if len(lines) > 18:
            removed = max(0, len(lines) - len(chosen))
            print(f"[quiet-command-output] Success; reduced {len(lines)} output lines to "
                  f"{len(chosen)} ({removed} omitted).")
        for line in chosen:
            print(line)
    else:
        chosen, truncated = select_failure_output(lines)
        print(f"[quiet-command-output] Command failed with exit code {proc.returncode}. "
              f"Showing diagnostic output:")
        if truncated:
            print(f"[quiet-command-output] Diagnostics were bounded to {len(chosen)} lines.")
        for line in chosen:
            print(line)
    return proc.returncode


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--run-b64":
        return run_mode(sys.argv[2])
    if len(sys.argv) == 2 and sys.argv[1] == "--hook":
        return hook_mode()
    print("Usage: quiet-command-output.py --hook | --run-b64 BASE64", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
