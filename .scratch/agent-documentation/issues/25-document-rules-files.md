# Document the reusable rules files (AGENTS.md, CLAUDE.md)

Status: resolved
Type: task

## Answer
`docs/installation.md` gained a "Rules files" section: `AGENTS.md` and `CLAUDE.md`
are always-on instructions that can be copied per project (to the repo root) or
globally (`~/.config/devin/AGENTS.md` for Devin CLI, `~/.claude/CLAUDE.md` for
Claude Code). It also warns that only section 1 of this repo's `AGENTS.md` is
generic; section 2 is repo-specific. The repo map in `how-skills-work.md` now
includes `bin/`, `hooks/`, `test/`, `package.json`, and the rules files, and the
README points at the new section.

## Comments
