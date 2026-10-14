# Add the quiet-command-output hook with an npx installer

Status: resolved
Type: task

## Answer
Turned the supplied `quiet-command-output-npx` package into a hook in this repo,
installable with `npx github:alvinpaul76/agent-skills-by-cre8orlab install quiet-command-output`.

- `hooks/quiet-command-output/`: the Python hook plus `hook.json` (event, matcher,
  script). Fixed the success filter keeping every `PASSED` line, quoted the
  interpreter and script paths in the rewritten command, and removed an unused
  pattern.
- `bin/cli.js` and a root `package.json`: zero-dependency `install`, `status`, and
  `uninstall` for any folder under `hooks/`. Merges `~/.claude/settings.json`, backs
  it up only when it changes, and is safe to run twice.
- `docs/hooks/quiet-command-output.md`, plus pointers in `README.md`.
- The `AGENTS.md`/`CLAUDE.md` restructure that shipped alongside is logged
  separately in ticket 26. Review fixes are in ticket 27.
- Dropped the bundled `SKILL.md` (it told the agent to build a hook the installer
  already ships) and the npm-publish flow.

Tested in a throwaway HOME: install, repeat install, status, uninstall, with
existing settings kept. A 60-test pytest run went from 68 to 7 lines, and a failing
run kept its diagnostics and exit code. Not yet tested inside a live Claude Code
session or via the GitHub URL (needs a push).

## Comments
