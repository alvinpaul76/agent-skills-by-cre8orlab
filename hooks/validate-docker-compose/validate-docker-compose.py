#!/usr/bin/env python3
"""
Validate Docker Compose files against the docker-compose-standards skill.

Every image pulled from a registry must be one `${VAR:?msg}` reference, VAR must
be declared in `.env.example` next to the Compose file, and its value must be
pinned (major.minor or more, or a digest). Services with `build:` are exempt.

CLI / CI:  validate-docker-compose.py [--json] [--no-docker] [PATH ...]
           PATH is a Compose file, a .env.example, or a directory (searched
           recursively). Default: the current directory. Exit 1 on any ERROR.
Hook:      validate-docker-compose.py --hook
           Claude Code PostToolUse hook. Reads the event JSON on stdin; after an
           edit to a Compose file or .env.example, validates that folder and, on
           errors, prints them to stderr and exits 2 so the agent fixes them.

Never modifies files. Prints variable names and image references only, never
other values from .env files. Needs PyYAML, or Docker Compose as a fallback parser.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

COMPOSE_NAME = re.compile(r"^(docker-)?compose(\.[\w.-]+)?\.ya?ml$")
BASE_NAMES = ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")
REQUIRED_REF = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*):\?[^}]*\}$")
ANY_VAR = re.compile(r"(?<!\$)\$(?:\{([A-Za-z_][A-Za-z0-9_]*)[^}]*\}|([A-Za-z_][A-Za-z0-9_]*))")
FLOATING_TAGS = {"latest", "stable", "main", "master", "edge", "lts", "nightly",
                 "dev", "develop", "current", "mainline", "rolling", "beta", "alpha"}
DIGEST = re.compile(r"@sha256:[0-9a-f]{64}$")
MINOR = re.compile(r"^v?\d+\.\d+")
PATCH = re.compile(r"^v?\d+\.\d+\.\d+")
DATED = re.compile(r"\d{4}-?\d{2}-?\d{2}")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}

try:
    import yaml  # PyYAML: safe_load resolves anchors, aliases and << merge keys
except ImportError:  # pragma: no cover - depends on the machine
    yaml = None


def finding(level, code, file, service, message):
    return {"level": level, "code": code, "file": str(file), "service": service, "message": message}


# ---- image references --------------------------------------------------------

def pin_problem(ref: str) -> tuple[str, str] | None:
    """Return (level, reason) when an image reference is not acceptably pinned."""
    if DIGEST.search(ref):
        return None
    name = ref.rsplit("/", 1)[-1]
    if ":" not in name:
        return "ERROR", "has no tag, so it floats to latest"
    tag = name.rsplit(":", 1)[1]
    if tag.lower() in FLOATING_TAGS:
        return "ERROR", f"tag '{tag}' is floating"
    if DATED.search(tag):
        return None  # date-stamped release tags (for example RELEASE.2024-01-01...) are fixed
    if not MINOR.match(tag):
        return "ERROR", f"tag '{tag}' needs at least major.minor (or a digest)"
    if not PATCH.match(tag):
        return "WARNING", f"tag '{tag}' has no patch version"
    return None


# ---- file reading -------------------------------------------------------------

def read_env(path: Path, only_images: bool = False) -> dict[str, str] | None:
    """Minimal dotenv reader. With only_images, keeps *_IMAGE keys and drops the rest unread."""
    if not path.is_file():
        return None
    values = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.removeprefix("export ").strip()
        if only_images and not key.endswith("_IMAGE"):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        else:
            value = value.split(" #", 1)[0].strip()
        values[key] = value
    return values


def load_compose(path: Path, use_docker: bool) -> tuple[dict | None, str | None]:
    """Parse one Compose file without interpolation. Returns (data, error)."""
    if yaml is not None:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            return None, f"invalid YAML: {str(exc).splitlines()[0]}"
        return (data if isinstance(data, dict) else {}), None
    if use_docker and docker_compose():
        # Fallback: Compose itself parses the file, keeping ${VAR} text intact.
        proc = subprocess.run(
            [*docker_compose(), "-f", str(path), "config", "--no-interpolate", "--format", "json"],
            capture_output=True, text=True, timeout=60, cwd=path.parent)
        if proc.returncode == 0:
            return json.loads(proc.stdout), None
        return None, "docker compose could not parse the file"
    return None, "cannot parse: install PyYAML (pip install pyyaml) or Docker Compose"


_DOCKER = None


def docker_compose() -> list[str] | None:
    global _DOCKER
    if _DOCKER is None:
        _DOCKER = []
        if shutil.which("docker"):
            ok = subprocess.run(["docker", "compose", "version"], capture_output=True).returncode == 0
            if ok:
                _DOCKER = ["docker", "compose"]
        if not _DOCKER and shutil.which("docker-compose"):
            _DOCKER = ["docker-compose"]
    return _DOCKER or None


# ---- validation ---------------------------------------------------------------

def validate_dir(folder: Path, files: list[Path], use_docker: bool) -> list[dict]:
    out: list[dict] = []
    example_path = folder / ".env.example"
    example = read_env(example_path)
    services: dict[str, dict] = {}  # name -> {"build": bool, "image": (value, file) | None}
    parsed: list[Path] = []

    for f in files:
        data, error = load_compose(f, use_docker)
        if error:
            out.append(finding("ERROR", "E5", f, None, error))
            continue
        parsed.append(f)
        if data.get("include"):
            out.append(finding("WARNING", "W4", f, None, "`include:` files are not followed; validate them separately"))
        for name, svc in (data.get("services") or {}).items():
            if not isinstance(svc, dict):
                continue
            entry = services.setdefault(name, {"build": False, "image": None})
            entry["build"] = entry["build"] or "build" in svc
            if "image" in svc and svc["image"] is not None:
                entry["image"] = (str(svc["image"]), f)
            if "extends" in svc and "image" not in svc:
                out.append(finding("WARNING", "W4", f, name, "`extends:` is not followed; the inherited image is not checked"))

    used_vars: set[str] = set()
    for name, entry in services.items():
        if entry["image"] is None or entry["build"]:
            continue  # nothing to pull, or a local build whose image: is only the output tag
        value, f = entry["image"]
        refs = [a or b for a, b in ANY_VAR.findall(value)]
        used_vars.update(refs)
        if not refs:
            out.append(finding("ERROR", "E1", f, name,
                               f"hardcoded image '{value}'; use ${{{name.upper().replace('-', '_')}_IMAGE:?...}} "
                               "and put the pinned value in .env.example"))
            continue
        match = REQUIRED_REF.match(value)
        if not match:
            out.append(finding("ERROR", "E2", f, name,
                               f"image '{value}' must be exactly one ${{VAR:?message}} reference "
                               "(no defaults, partial tags or bare $VAR)"))
            continue
        var = match.group(1)
        if example is None:
            out.append(finding("ERROR", "E3", f, name, f"{var} needs a .env.example next to the Compose file"))
            continue
        if not example.get(var):
            out.append(finding("ERROR", "E3", f, name, f"{var} is not declared in .env.example"))
            continue
        problem = pin_problem(example[var])
        if problem:
            level, reason = problem
            code = "E4" if level == "ERROR" else "W1"
            out.append(finding(level, code, example_path, name, f"{var}={example[var]}: {reason}"))

    if example is not None and parsed:
        for var in sorted(k for k in example if k.endswith("_IMAGE") and k not in used_vars):
            if not any(var in f.read_text(encoding="utf-8") for f in parsed):
                out.append(finding("WARNING", "W2", example_path, None, f"{var} is not used by any Compose file here"))
        local = read_env(folder / ".env", only_images=True) or {}
        for var, value in sorted(local.items()):
            if var in example and value != example[var]:
                out.append(finding("WARNING", "W3", folder / ".env", None,
                                   f"{var} differs from .env.example ({value} vs {example[var]})"))

    if use_docker and parsed:
        out.extend(docker_check(folder, parsed, example_path))
    return out


def docker_check(folder: Path, files: list[Path], example_path: Path) -> list[dict]:
    """`docker compose config -q` for the base file, and the base plus each other file."""
    cmd = docker_compose()
    if not cmd:
        return [finding("WARNING", "W4", folder, None, "Docker Compose not found; syntax check (E5) skipped")]
    base = next((f for f in files if f.name in BASE_NAMES), None)
    combos = [[f] for f in files] if base is None else \
        [[base]] + [[base, f] for f in files if f != base]
    env = ["--env-file", str(example_path)] if example_path.is_file() else []
    out = []
    for combo in combos:
        args = [*cmd, *env, *sum((["-f", str(f)] for f in combo), []), "config", "-q"]
        proc = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=folder)
        if proc.returncode != 0:
            detail = (proc.stderr.strip().splitlines() or ["unknown error"])[-1]
            out.append(finding("ERROR", "E5", combo[-1], None, f"docker compose config failed: {detail}"))
    return out


def collect(paths: list[str]) -> dict[Path, list[Path]]:
    """Group Compose files by folder. A .env.example or a folder selects its Compose files."""
    groups: dict[Path, set[Path]] = {}

    def add_folder(folder: Path, recursive: bool):
        walker = os.walk(folder) if recursive else [(folder, [], os.listdir(folder))]
        for root, dirs, names in walker:
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for n in names:
                if COMPOSE_NAME.match(n):
                    groups.setdefault(Path(root), set()).add(Path(root) / n)

    for p in map(Path, paths):
        p = p.resolve()
        if p.is_dir():
            add_folder(p, recursive=True)
        elif p.is_file() and (p.name == ".env.example" or COMPOSE_NAME.match(p.name)):
            add_folder(p.parent, recursive=False)
    return {k: sorted(v) for k, v in sorted(groups.items())}


def run(paths: list[str], use_docker: bool) -> list[dict]:
    findings = []
    for folder, files in collect(paths).items():
        findings.extend(validate_dir(folder, files, use_docker))
    return findings


def fmt(f: dict) -> str:
    where = f["file"] + (f":{f['service']}" if f["service"] else "")
    return f"{f['level']} {f['code']} {where}: {f['message']}"


def hook_main() -> int:
    try:
        event = json.load(sys.stdin)
        file_path = event.get("tool_input", {}).get("file_path", "")
    except (ValueError, AttributeError):
        return 0
    if yaml is None and not docker_compose():
        return 0  # no parser on this machine: stay quiet rather than block every edit
    name = Path(file_path).name
    if not file_path or not (name == ".env.example" or COMPOSE_NAME.match(name)) or not Path(file_path).is_file():
        return 0
    errors = [f for f in run([file_path], use_docker=True) if f["level"] == "ERROR"]
    if not errors:
        return 0
    print("Docker Compose standards violated (see the docker-compose-standards skill):", file=sys.stderr)
    print("\n".join(fmt(f) for f in errors), file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--hook", action="store_true", help="run as a Claude Code PostToolUse hook")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--no-docker", action="store_true", help="skip the docker compose config check")
    args = parser.parse_args(argv)
    if args.hook:
        return hook_main()
    findings = run(args.paths, use_docker=not args.no_docker)
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            print(fmt(f))
        errors = sum(f["level"] == "ERROR" for f in findings)
        print(f"{errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if any(f["level"] == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
