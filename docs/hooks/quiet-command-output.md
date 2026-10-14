# quiet-command-output (hook)

A Claude Code hook that shrinks noisy install, build, and test output before it
reaches the agent, so it spends fewer tokens reading progress bars and lines of
passing tests.

New to a word? See the [word list](../glossary.md). · hook folder:
[`hooks/quiet-command-output/`](../../hooks/quiet-command-output/)

This is a hook, not a skill. A skill is read by the agent when a task matches; a
hook is installed once and runs on its own around every command.

## Install

Needs Node.js and Python 3 (macOS or Linux). No clone, no npm account:

```bash
npx github:alvinpaul76/agent-skills-by-cre8orlab install quiet-command-output
npx github:alvinpaul76/agent-skills-by-cre8orlab status quiet-command-output
npx github:alvinpaul76/agent-skills-by-cre8orlab uninstall quiet-command-output
```

Then restart Claude Code and check `/hooks`. To try a branch first, add
`#branch-name` after the repo name.

The installer copies the script to `~/.claude/hooks/` and adds one entry to
`~/.claude/settings.json`. It merges instead of replacing, backs up settings
before changing them, and leaves your other hooks alone. `uninstall` removes only
the entry the installer wrote (matched by its exact command, whatever its
matcher) and the script.

## What does it do?

Before a Bash command runs, the hook checks it against a short list of commands:
`npm`/`pnpm`/`yarn` install, build and test, `pip install`, `uv sync`, `pytest`,
`cargo build`/`test`, and `go build`/`test`. For a match it runs the command for
you and prints a short result:

- **Success:** errors, warnings, and the final summary. A command with 18 lines or
  fewer prints in full.
- **Failure:** the error lines with some context and the end of the output, so test
  failures and stack traces stay. Very long output is cut to a set limit, and it
  says so.
- The exit code is kept either way.

Anything else is left alone: `git`, file reads, commands with pipes, `;`, `&&`,
redirects, `$` variables, `sudo`, or interactive words (`--interactive`, `-i`, `--watch`, `watch`, `login`).

## Things to know

- **Permission prompts.** Claude Code checks permission rules against the changed
  command, not the one the agent wrote. A rule like `Bash(npm install:*)` will not
  match, so you may be asked to approve. To skip that, add
  `Bash(<python> *quiet-command-output.py --run-b64 *)` to your `allow` rules,
  where `<python>` is the path printed by `which python3` (the hook uses the
  Python it was started with). The script only runs listed command families.
- **No live output.** Output appears when the command finishes, so a long build
  shows nothing meanwhile.
- **Rough matching.** The error and summary patterns are heuristics. If a tool uses
  unusual wording, edit the patterns in the script.
- **Not Windows.** The settings entry calls `python3`.

## Back to

[Installing skills](../installation.md) · [how skills work](../how-skills-work.md)
