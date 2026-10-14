# context-audit

Checks why a Claude Code setup is using so many tokens, without changing anything.
It looks at the places cost usually hides and gives you one ranked table plus a
single change worth making first.

New to a word? See the [word list](../glossary.md). · skill folder:
[`context-audit/`](../../context-audit/)

## When does the agent use it?

Whenever you ask why Claude Code is expensive, using up your limits quickly,
hitting the context limit, compacting too often, or getting poor prompt-cache reuse,
or when you ask for a context, token, or cost audit. You can also call it directly
with `/context-audit`.

## What it produces

One table with the columns `FINDING`, `SEVERITY`, `EVIDENCE`, and
`WHAT IT IS COSTING ME`, sorted from biggest cost to smallest. Severity is `RED`,
`AMBER`, or `GREEN`. Below the table is one line: `Highest-leverage change: ...`.
Anything it cannot measure is marked `UNKNOWN` rather than guessed.

## What does it check?

1. Instruction files (`CLAUDE.md` and anything they import): size and token count.
2. MCP servers, tool deferral, and custom endpoint or proxy variables (names and
   whether they are set; never the values).
3. Model and effort settings, and where each one is set.
4. Hooks that filter noisy command output.
5. Subagent definitions and whether they pick a model.
6. Scheduled work (cron, systemd timers, launchd) compared with cache lifetime.
7. The newest session log: cache hit rate, context growth, and cache-creation spikes.

## Does it change anything?

No. It never edits files or settings, never installs anything, and never runs your
hook scripts. It does read local files under your project and `~/.claude/`, and it
redacts secrets. If it cannot run `/context` or `/usage` itself, it asks you to paste
the output.

## What is inside?

| File | What it holds |
| --- | --- |
| `SKILL.md` | The checks, the output format, and the evidence rules |
| `README.md` | Install steps and helper usage |
| `scripts/analyze_session.py` | Summarizes a session log: totals, cache hit rate, models, context growth, cache spikes |

## The session helper

```bash
python3 ~/.claude/skills/context-audit/scripts/analyze_session.py --latest
```

`--latest` picks the newest log under `~/.claude/projects/`. Use `--input <file>` for a
specific log and `--max-rows N` to show only the last N turns. The newest log is often
the audit session itself, so pass `--input` to audit an earlier session.

The helper merges log lines that belong to the same model response, so tokens are not
counted twice. Its percentages describe token volume, not what you were billed.

Back to [how skills work](../how-skills-work.md).
