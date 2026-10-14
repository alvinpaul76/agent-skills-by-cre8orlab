# Move behavioral guidelines from CLAUDE.md into AGENTS.md

Status: resolved
Type: task

## Answer
Moved the behavioral guidelines (think before coding, simplicity first, surgical
changes, goal-driven execution) out of `CLAUDE.md` and into `AGENTS.md`, so every
agent reads the same rules. `CLAUDE.md` now imports `AGENTS.md` and points at
`package.json` for npm commands.

The condensed version dropped the "These guidelines are working if" footer, the
plan template, and the "every changed line should trace to the request" line.
Removed the empty "Claude-Specific Rules" placeholder section from `CLAUDE.md`.

## Comments
