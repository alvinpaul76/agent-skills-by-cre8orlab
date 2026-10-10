#!/usr/bin/env python3
"""Checks the docs of a skills-and-plugins repo. Usage: python check_docs.py [repo_root]

Fails (exit 1) on: a skill (folder with SKILL.md) or plugin (folder with
.claude-plugin/plugin.json) that has no docs page or README link, a skill whose folder
and frontmatter name differ, files named in a 'What is inside?' table that do not exist,
broken relative links or heading anchors, unbalanced code fences, a page that does not
open with a title and a purpose line, machine-specific paths, and strings that look like
real secrets.
Warns about: a long README, docs pages for skills/plugins that no longer exist, and
developer jargon to double-check.
"""
import json
import re
import sys
from pathlib import Path

JARGON = [
    "frontmatter", "hook", "mcp", "symlink", "marketplace", "manifest", "invoke",
    "token", "llm", "slash command", "progressive disclosure", "stdin", "payload",
]
SKIP_DIRS = {".git", "node_modules", "docs", ".venv", "venv", "__pycache__"}
SECRET_PATTERNS = [
    re.compile(r"(?i)x-api-key:\s*(?!<)[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?i)bearer\s+(?!<)[A-Za-z0-9._\-]{20,}"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[=:]\s*['\"]?(?!<)[A-Za-z0-9_\-]{24,}"),
]
LOCAL_PATH = re.compile(r"(?<![\w.~])(/home/\w+|/Users/\w+|C:\\Users\\)")
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


def visible(root: Path, path: Path) -> bool:
    return not any(part in SKIP_DIRS or part.startswith(".") for part in path.relative_to(root).parts[:-1])


def skills(root: Path) -> dict[str, Path]:
    return {p.parent.name: p.parent for p in sorted(root.rglob("SKILL.md")) if visible(root, p)}


def plugins(root: Path) -> dict[str, Path]:
    found = {}
    for manifest in sorted(root.rglob(".claude-plugin/plugin.json")):
        folder = manifest.parent.parent
        if folder == root or any(part in SKIP_DIRS for part in folder.relative_to(root).parts):
            continue
        try:
            found[json.loads(manifest.read_text()).get("name", folder.name)] = folder
        except json.JSONDecodeError:
            found[folder.name] = folder
    return found


def frontmatter_name(skill_md: Path) -> str | None:
    match = re.match(r"---\n(.*?)\n---", skill_md.read_text(), re.S)
    name = re.search(r"(?m)^name:\s*(.+)$", match.group(1)) if match else None
    return name.group(1).strip().strip("\"'") if name else None


def inside_files(page: Path) -> list[str]:
    """Backticked first-column entries in the table under '## What is inside?'."""
    names, active = [], False
    for line in page.read_text().splitlines():
        if line.startswith("#"):
            active = line.lstrip("#").strip().lower().startswith("what is inside")
        elif active and (m := re.match(r"\|\s*`([^`]+)`\s*\|", line)):
            names.append(m.group(1))
    return names


def check_inventory(root: Path, errors: list[str], warnings: list[str]) -> None:
    readme = (root / "README.md").read_text() if (root / "README.md").exists() else ""
    for kind, found in (("skills", skills(root)), ("plugins", plugins(root))):
        for name, folder in found.items():
            page = root / "docs" / kind / f"{name}.md"
            if not page.exists():
                errors.append(f"docs/{kind}/{name}.md: missing page for {kind[:-1]} '{name}'")
                continue
            if f"docs/{kind}/{name}.md" not in readme:
                errors.append(f"README.md: add a row linking docs/{kind}/{name}.md")
            if kind == "skills":
                declared = frontmatter_name(folder / "SKILL.md")
                if declared != name:
                    errors.append(f"{folder.relative_to(root)}/SKILL.md: name '{declared}' differs from folder '{name}'")
                for ref in inside_files(page):
                    if not (folder / ref).exists():
                        errors.append(f"docs/{kind}/{name}.md: '{ref}' is listed but not in {name}/")
        for page in sorted((root / "docs" / kind).glob("*.md")) if (root / "docs" / kind).exists() else []:
            if page.stem not in found:
                warnings.append(f"docs/{kind}/{page.name}: no matching {kind[:-1]} folder; remove or rename?")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    files = pages(root)
    if not files:
        print("no README.md or docs/*.md found")
        return 1
    errors: list[str] = []
    warnings: list[str] = []
    glossary = root / "docs" / "glossary.md"
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
            if LOCAL_PATH.search(line):
                errors.append(f"{rel}:{n}: machine-specific path; use a relative path or a placeholder")
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
                if re.search(rf"(?i)\b{re.escape(term)}", prose) and term not in glossary_text:
                    warnings.append(f"{rel}:{n}: '{term}' - explain it or add it to the glossary")

    check_inventory(root, errors, warnings)

    for message in errors:
        print("ERROR  ", message)
    for message in warnings:
        print("WARNING", message)
    print(f"\n{len(files)} pages checked: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
