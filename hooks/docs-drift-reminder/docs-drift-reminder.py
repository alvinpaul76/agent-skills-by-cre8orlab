#!/usr/bin/env python3
"""
Claude Code PostToolUse hook: remind the agent to update the docs.

FastAPI project (a .py file under <project>/app/, a docs/ folder, and the
fastapi-documentation skill installed): runs the skill's check_drift.py. If the
docs no longer match the code, prints the DRIFT lines to stderr and exits 2, which
Claude Code passes back to the agent. Silent when nothing drifted.

Any other project: after an edit to a source file, if the project has a docs/
folder or README.md, reminds the agent once per session to check the docs.
Docs files and non-source files never trigger it.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_CHECK = Path.home() / ".claude/skills/fastapi-documentation/scripts/check_drift.py"
DEFAULT_APP = "app.main:create_app"
SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt",
                   ".rb", ".php", ".cs", ".swift", ".sh"}


def is_app_source(file_path: str, root: Path) -> bool:
    path = Path(file_path)
    return path.suffix == ".py" and (root / "app") in path.parents


def has_docs(root: Path) -> bool:
    return (root / "docs").is_dir() or (root / "README.md").is_file()


def is_source(file_path: str, root: Path) -> bool:
    path = Path(file_path)
    if path.suffix not in SOURCE_SUFFIXES or root not in path.parents:
        return False
    return (root / "docs") not in path.parents


def first_time_this_session(session_id: str) -> bool:
    marker = Path(tempfile.gettempdir()) / f"docs-drift-reminder-{session_id or 'none'}"
    if marker.exists():
        return False
    try:
        marker.touch()
    except OSError:
        pass
    return True


def run_check(root: Path) -> subprocess.CompletedProcess[str]:
    # The check imports the app, so it must run with the project's Python.
    python = ["uv", "run", "python"] if shutil.which("uv") else [sys.executable]
    app = os.environ.get("DOCS_DRIFT_APP", DEFAULT_APP)
    return subprocess.run(
        [*python, "-I", str(SKILL_CHECK), ".", "--app", app],
        cwd=root, capture_output=True, text=True, timeout=60,
    )


def fastapi_check(file_path: str, root: Path) -> int | None:
    """Exit code for a FastAPI project, or None when the project does not fit."""
    if not (is_app_source(file_path, root) and SKILL_CHECK.is_file()
            and (root / "docs").is_dir()):
        return None
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


def main() -> int:
    try:
        data = json.load(sys.stdin)
        file_path = data.get("tool_input", {}).get("file_path", "")
        session_id = str(data.get("session_id", ""))
    except (ValueError, AttributeError):
        return 0
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if not file_path:
        return 0
    code = fastapi_check(file_path, root)
    if code is not None:
        return code
    if is_source(file_path, root) and has_docs(root) and first_time_this_session(session_id):
        edited = Path(file_path).relative_to(root)
        print(f"You edited {edited}. If this changes behavior, update the docs "
              "(README.md or docs/) in the same change. Reminder shown once per session.",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
