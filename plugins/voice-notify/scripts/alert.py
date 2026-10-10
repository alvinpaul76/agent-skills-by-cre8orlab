#!/usr/bin/env python3
"""Spoken alert for Claude Code hooks.

Works on macOS, Windows, Linux and WSL using only the standard library and the
operating system's own speech engine. No LLM, no network, no tokens.

Hook usage (see hooks/hooks.json): Claude Code runs this script on the
Notification and Stop events and passes event details as JSON on stdin.

Manual test:
    python3 alert.py --test

Environment variables:
    CLAUDE_ALERT_EVENTS   Comma-separated events that should speak.
                          Default: "Notification,Stop".
                          Use "Notification" to stay quiet after every turn,
                          or "none" to disable the alert completely.
"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys

DEVNULL = subprocess.DEVNULL
MAX_CHARS = 140
DEFAULT_EVENTS = "Notification,Stop"
DEFAULT_MESSAGE = "Claude needs your attention."
FINISHED_MESSAGE = "Claude has finished and is waiting for you."
# PowerShell treats typographic single quotes as quote characters too.
PS_QUOTES = "'\u2018\u2019\u201a\u201b"


def clean(text, limit=MAX_CHARS):
    """Make text safe to hand to a speech engine."""
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", str(text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    text = text.lstrip("-").strip()  # never let text look like a CLI flag
    return text[:limit].rstrip()


def is_wsl():
    try:
        with open("/proc/version", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False


def _spawn(cmd):
    """Start a process without waiting for it, detached from the hook."""
    kwargs = {"stdin": DEVNULL, "stdout": DEVNULL, "stderr": DEVNULL}
    if os.name == "nt":
        # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        kwargs["creationflags"] = 0x00000008 | 0x00000200
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(cmd, **kwargs)


def _speak_powershell(text, powershell):
    safe = text
    for ch in PS_QUOTES:
        safe = safe.replace(ch, "''")
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "(New-Object System.Speech.Synthesis.SpeechSynthesizer)"
        f".Speak('{safe}')"
    )
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    _spawn([
        powershell, "-NoProfile", "-NonInteractive",
        "-WindowStyle", "Hidden", "-EncodedCommand", encoded,
    ])


def _bell():
    """Last resort: terminal bell on the controlling terminal."""
    try:
        with open("/dev/tty", "w") as tty:
            tty.write("\a")
            tty.flush()
    except OSError:
        pass


def speak(text):
    """Speak text. Returns True if a speech engine was started."""
    text = clean(text)
    if not text:
        return False
    try:
        if sys.platform == "darwin":
            _spawn(["say", text])
            return True

        if sys.platform == "win32":
            ps = shutil.which("powershell") or shutil.which("pwsh")
            if ps:
                _speak_powershell(text, ps)
                return True
            return False

        # Linux, with WSL borrowing the Windows voice
        if is_wsl():
            ps = shutil.which("powershell.exe")
            if ps:
                _speak_powershell(text, ps)
                return True

        for exe in ("spd-say", "espeak-ng", "espeak"):
            path = shutil.which(exe)
            if path:
                _spawn([path, text])
                return True
    except OSError:
        pass

    _bell()
    return False


def read_hook_input():
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    try:
        data = json.load(sys.stdin)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def build_message(data):
    event = data.get("hook_event_name") or ""
    cwd = data.get("cwd") or os.getcwd()
    project = os.path.basename(str(cwd).rstrip("/\\"))
    if event == "Stop":
        body = FINISHED_MESSAGE
    else:
        body = data.get("message") or DEFAULT_MESSAGE
    return event, (f"{project}. {body}" if project else body)


def enabled_events():
    raw = os.environ.get("CLAUDE_ALERT_EVENTS", DEFAULT_EVENTS)
    return {e.strip() for e in raw.split(",") if e.strip() and e.strip().lower() != "none"}


def main(argv):
    if "--test" in argv:
        ok = speak("Voice notify test. Claude needs your attention.")
        print("Speech engine started." if ok else "No speech engine found; rang the terminal bell.")
        return 0

    data = read_hook_input()
    event, message = build_message(data)
    if event and event not in enabled_events():
        return 0
    speak(message)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
