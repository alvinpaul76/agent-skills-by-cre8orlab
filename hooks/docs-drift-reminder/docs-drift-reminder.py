#!/usr/bin/env python3
"""
Claude Code PostToolUse hook: remind the agent to update the docs.

After an Edit or Write to a .py file under <project>/app/, runs the
fastapi-documentation skill's check_drift.py. If the docs no longer match the
code, prints the DRIFT lines to stderr and exits 2, which Claude Code passes back
to the agent. Stays silent (exit 0) when nothing drifted, when the edited file is
elsewhere, or when the project or the skill does not fit.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_CHECK = Path.home() / ".claude/skills/fastapi-documentation/scripts/check_drift.py"
DEFAULT_APP = "app.main:create_app"


def is_app_source(file_path: str, root: Path) -> bool:
    path = Path(file_path)
    return path.suffix == ".py" and (root / "app") in path.parents


def run_check(root: Path) -> subprocess.CompletedProcess[str]:
    # The check imports the app, so it must run with the project's Python.
    python = ["uv", "run", "python"] if shutil.which("uv") else [sys.executable]
    app = os.environ.get("DOCS_DRIFT_APP", DEFAULT_APP)
    return subprocess.run(
        [*python, "-I", str(SKILL_CHECK), ".", "--app", app],
        cwd=root, capture_output=True, text=True, timeout=60,
    )


def main() -> int:
    try:
        file_path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
    except (ValueError, AttributeError):
        return 0
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if not file_path or not is_app_source(file_path, root):
        return 0
    if not SKILL_CHECK.is_file() or not (root / "docs").is_dir():
        return 0
    try:
        result = run_check(root)
    except (OSError, subprocess.TimeoutExpired):
        return 0
    if result.returncode == 0:
        return 0
    drift = [line for line in result.stdout.splitlines() if line.startswith("DRIFT")]
    if not drift:
        return 0  # the check itself failed to run; do not nag about docs
    edited = Path(file_path).relative_to(root)
    print(f"The docs no longer match the code after editing {edited}:", file=sys.stderr)
    print("\n".join(drift), file=sys.stderr)
    print("Update the pages named above (see 'Updating docs after a code change' "
          "in the fastapi-documentation skill).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
