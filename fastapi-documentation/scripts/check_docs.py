#!/usr/bin/env python3
"""Checks a repo's markdown docs. Usage: python check_docs.py [repo_root]

Fails (exit 1) on: broken relative links or heading anchors, a docs/apis page the README
does not link, a README without an '## APIs' section, unbalanced code fences, a page that does
not open with a title and a purpose line, and strings that look like real secrets.
Warns about: a long README and developer jargon to double-check.
"""
import re
import sys
from pathlib import Path

JARGON = [
    "adapter", "middleware", "lifespan", "dependency injection", "idempotent",
    "serializ", "mutex", "RFC 9457", "problem+json", "CORS", "ASGI", "DTO",
    "use case", "fail-closed", "fail closed", "payload", "schema", "port",
]
SECRET_PATTERNS = [
    re.compile(r"(?i)x-api-key:\s*(?!<)[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?i)bearer\s+(?!<)[A-Za-z0-9._\-]{20,}"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[=:]\s*['\"]?(?!<)[A-Za-z0-9_\-]{24,}"),
]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")


def slug(heading: str) -> str:
    """GitHub-style anchor for a heading."""
    text = re.sub(r"`", "", heading.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    found, in_code = set(), False
    for line in path.read_text().splitlines():
        if line.startswith("```"):
            in_code = not in_code
        elif not in_code and re.match(r"#{1,6} ", line):
            found.add(slug(line.lstrip("#")))
    return found


def pages(root: Path) -> list[Path]:
    found = [root / "README.md"] if (root / "README.md").exists() else []
    found += sorted((root / "docs").rglob("*.md")) if (root / "docs").exists() else []
    return found


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    files = pages(root)
    if not files:
        print("no README.md or docs/*.md found")
        return 1
    errors: list[str] = []
    warnings: list[str] = []
    glossary = (root / "docs" / "glossary.md")
    glossary_text = glossary.read_text().lower() if glossary.exists() else ""

    for path in files:
        rel = path.relative_to(root)
        lines = path.read_text().splitlines()
        if sum(l.startswith("```") for l in lines) % 2:
            errors.append(f"{rel}: unbalanced code fence")
        body = [l for l in lines if l.strip()]
        if not body or not body[0].startswith("# "):
            errors.append(f"{rel}: first line should be a '# Title'")
        elif len(body) < 2 or body[1].startswith("#"):
            errors.append(f"{rel}: add a one-line purpose right after the title")
        if rel.name == "README.md" and len(lines) > 60:
            warnings.append(f"{rel}: {len(lines)} lines; keep the landing page near 50")
        in_code = False
        for n, line in enumerate(lines, 1):
            if line.startswith("```"):
                in_code = not in_code
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                errors.append(f"{rel}:{n}: looks like a real secret; use a <placeholder>")
            if in_code:
                continue
            for target in LINK.findall(line):
                if re.match(r"^(https?:|mailto:)", target):
                    continue
                file_part, _, anchor = target.partition("#")
                linked = (path.parent / file_part).resolve() if file_part else path
                if not linked.exists():
                    errors.append(f"{rel}:{n}: broken link -> {target}")
                elif anchor and linked.suffix == ".md" and anchor not in anchors(linked):
                    errors.append(f"{rel}:{n}: no heading '#{anchor}' in {linked.name}")
            prose = re.sub(r"`[^`]*`", "", line)  # exact code names are not prose
            for term in JARGON:
                if re.search(rf"(?i)\b{re.escape(term)}", prose) and term.lower() not in glossary_text:
                    warnings.append(f"{rel}:{n}: '{term}' - explain it or add it to the glossary")

    readme = root / "README.md"
    if readme.exists():
        readme_text = readme.read_text()
        for api_page in sorted((root / "docs" / "apis").glob("*.md")):
            if f"docs/apis/{api_page.name}" not in readme_text:
                errors.append(f"README.md: add a row to the APIs table linking docs/apis/{api_page.name}")
        if "## APIs" not in readme_text and (root / "docs" / "apis").exists():
            errors.append("README.md: missing an '## APIs' section")
        for n, line in enumerate(readme_text.splitlines(), 1):
            if re.search(r"curl .*(/api/|-X POST)|\"results\"\s*:", line):
                warnings.append(f"README.md:{n}: API request or answer example; move it to the API page")

    for message in errors:
        print("ERROR  ", message)
    for message in warnings:
        print("WARNING", message)
    print(f"\n{len(files)} pages checked: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
