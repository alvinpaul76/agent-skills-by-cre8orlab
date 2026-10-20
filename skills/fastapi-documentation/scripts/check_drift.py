#!/usr/bin/env python3
"""Checks that the docs still match the code of a FastAPI app.

Usage (run with the PROJECT's Python so the app can be imported):
    uv run python <skill-dir>/scripts/check_drift.py <repo-root> --app app.main:create_app

Fails (exit 1) when:
  - a route of the app is not mentioned in the docs, or an API page documents
    a `METHOD /path` the app no longer has;
  - a settings field is missing from docs/architecture.md, or the settings table
    lists a name that is no longer a field;
  - an error code defined in the source is missing from docs/troubleshooting.md,
    or troubleshooting lists a code the source no longer defines;
  - docker-compose.yml or .env.example sets a variable the app does not read.
Routes come from app.openapi(), so routes hidden from the schema are not checked.
Needs a Settings-style object at app.state.settings (pydantic-settings); other checks
still run without it. Prints nothing secret: it reads field names, never values.
"""
import argparse
import importlib
import re
import sys
from pathlib import Path

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
SKIP_PATHS = {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect", "/"}
# Variables read by the container or compose, not by the app's settings.
NON_SETTINGS = {"FORWARDED_ALLOW_IPS", "CRAFT_PORT", "PORT", "WEB_CONCURRENCY"}
CODE_DEFS = [
    re.compile(r"""^\s+code\s*=\s*["']([a-z][a-z0-9_]*)["']""", re.M),
    re.compile(r"""_problem\(\s*[^,]+,\s*["']([a-z][a-z0-9_]*)["']""", re.S),
]
ROUTE_DOC = re.compile(r"`(GET|POST|PUT|PATCH|DELETE) (/[^`\s]*)`")


def read(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def load_app(spec: str, root: Path):
    sys.path.insert(0, str(root))
    module_name, _, attr = spec.partition(":")
    target = getattr(importlib.import_module(module_name), attr or "app")
    return target() if callable(target) and attr else target


def app_routes(app) -> set[tuple[str, str]]:
    """Routes from the OpenAPI schema; newer FastAPI nests routers, so app.routes is not enough."""
    found = set()
    for path, operations in app.openapi().get("paths", {}).items():
        if path in SKIP_PATHS:
            continue
        found |= {(m.upper(), path) for m in operations if m in HTTP_METHODS}
    return found


def source_codes(root: Path) -> set[str]:
    codes = set()
    for path in (root / "app").rglob("*.py") if (root / "app").exists() else []:
        text = path.read_text()
        for pattern in CODE_DEFS:
            codes |= set(pattern.findall(text))
    codes.discard("domain_error")  # base class, never returned
    return codes


def table_first_column(text: str) -> set[str]:
    names = set()
    for line in text.splitlines():
        if line.startswith("|"):
            first = line.split("|")[1]
            names |= set(re.findall(r"`([A-Z][A-Z0-9_]+)`", first))
    return names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--app", required=True, help="module:factory, e.g. app.main:create_app")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []

    docs_text = "\n".join(p.read_text() for p in [root / "README.md", *sorted((root / "docs").rglob("*.md"))] if p.exists())
    api_text = "\n".join(p.read_text() for p in sorted((root / "docs" / "apis").glob("*.md")))
    architecture = read(root / "docs" / "architecture.md")
    troubleshooting = read(root / "docs" / "troubleshooting.md")

    app = load_app(args.app, root)

    # Routes
    routes = app_routes(app)
    for method, path in sorted(routes):
        if path not in docs_text:
            errors.append(f"route {method} {path} is not mentioned in the docs; add it to an API page")
    documented = set(ROUTE_DOC.findall(api_text))
    for method, path in sorted(documented - routes):
        errors.append(f"docs/apis documents `{method} {path}` but the app has no such route")

    # Settings
    settings = getattr(getattr(app, "state", None), "settings", None)
    fields = set(type(settings).model_fields) if settings is not None else set()
    for name in sorted(fields):
        if not re.search(rf"\b{name}\b", architecture):
            errors.append(f"setting {name} is missing from docs/architecture.md")
    for name in sorted(table_first_column(architecture) - fields):
        if fields:
            errors.append(f"docs/architecture.md lists setting {name} but the app has no such setting")
    if fields:
        for label, path in (("docker-compose.yml", root / "docker-compose.yml"), (".env.example", root / ".env.example")):
            for name in sorted(set(re.findall(r"^\s*#?\s*([A-Z][A-Z0-9_]+)\s*[:=]", read(path), re.M)) - fields - NON_SETTINGS):
                errors.append(f"{label} sets {name} but the app does not read it")

    # Error codes
    codes = source_codes(root)
    for code in sorted(codes):
        if f"`{code}`" not in troubleshooting:
            errors.append(f"error code {code} is missing from docs/troubleshooting.md")
    listed = set(re.findall(r"^\|\s*`([a-z][a-z0-9_]*)`\s*\|\s*\d{3}\s*\|", troubleshooting, re.M))
    for code in sorted(listed - codes):
        errors.append(f"docs/troubleshooting.md lists code {code} but the source no longer defines it")

    for message in errors:
        print("DRIFT  ", message)
    print(f"\n{len(routes)} routes, {len(fields)} settings, {len(codes)} error codes checked: {len(errors)} drifts")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
