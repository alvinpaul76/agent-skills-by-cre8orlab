# Add context-audit skill

Status: resolved
Type: task

## Answer
Added the `context-audit` skill: a read-only audit of why a Claude Code setup uses
so many tokens. `context-audit/SKILL.md` checks instruction files, MCP servers and
tool deferral, model and effort settings, output-filtering hooks, subagent
definitions, scheduled jobs against cache lifetime, and the newest session log. It
reports one ranked table and a single highest-leverage change.
`context-audit/scripts/analyze_session.py` summarizes a session log's token usage,
and `context-audit/README.md` describes the folder.

Documented it in a new `docs/skills/context-audit.md` page, added a row to the
Skills table in `README.md`, added the folder to the layout tree in
`docs/how-skills-work.md`, and added "Prompt cache" and "Context" entries to
`docs/glossary.md`.

## Comments
