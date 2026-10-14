# context-audit

A read-only Claude Code skill that audits why a session costs what it does. It checks
instruction-file size, MCP/tool deferral, model and effort settings, hooks, subagents,
scheduled work, and prompt-cache behavior, then returns one ranked table and one
highest-leverage change. It never modifies your configuration.

## Install

```bash
mkdir -p ~/.claude/skills
cp -R context-audit ~/.claude/skills/
```

Run this from the `skills/` folder of the repository. If you extracted this bundle elsewhere, replace `context-audit` with its actual path.
Restart Claude Code if needed, then run:

```text
/context-audit
```

It also starts on its own when you ask why Claude Code is expensive, burning tokens, or
hitting context limits. If `/context` or `/usage` are not available to the skill, it
asks you to paste their output and marks anything it cannot measure `UNKNOWN`.

## Output

A ranked Markdown table (`# | Severity | Finding | Evidence | What it is costing me`) sorted by
cost impact, with 🔴 RED / 🟡 AMBER / 🟢 GREEN markers, then a bold
`Highest-leverage change: ...` line.

## Session usage helper

Dependency-free and read-only:

```bash
# newest session log under ~/.claude/projects
python3 ~/.claude/skills/context-audit/scripts/analyze_session.py --latest

# a specific log, last 50 turns only
python3 ~/.claude/skills/context-audit/scripts/analyze_session.py \
  --input "/path/to/session.jsonl" --max-rows 50
```

It prints Markdown tables and reports:

- aggregate cache read / cache creation / input / output tokens and percentages
- cache hit rate (cache read divided by prompt tokens)
- models seen (a model switch can break the cache) and subagent message count
- context growth: first, last, and peak (cache read + creation + input)
- cache-creation spikes: turns where over half the prompt was freshly cached
- per-message rows

Claude Code logs one line per content block, so one response can repeat its usage over
several lines. The helper merges them by message id and prints how many it merged.
Percentages use cache read + creation + input + output as the denominator: token
volume, not billed cost. The newest log is often the audit session itself; use
`--input` to audit an earlier one.
