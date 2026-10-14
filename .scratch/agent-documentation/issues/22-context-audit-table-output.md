# Make context-audit output a table

Status: resolved
Type: task

The helper script printed key/value lines and tab-separated rows, so the audit was
hard to read. Show it as tables and make the final report easier to scan.

## Answer
`skills/context-audit/scripts/analyze_session.py` now prints Markdown tables under
headings: session log, aggregate tokens, models seen, context growth, cache-creation
spikes, and per-message usage. Numbers are right-aligned with thousands separators
and the cache hit rate is bold. Checked by running it with `--latest --max-rows 3`.

`skills/context-audit/SKILL.md` now specifies a numbered report table (`#`,
Severity, Finding, Evidence, What it is costing me) with 🔴 RED, 🟡 AMBER, 🟢 GREEN
and ⚪ UNKNOWN markers, bold finding names, paths in backticks, and a bold
"Highest-leverage change" line. The plain severity words stay beside the markers.
It includes a one-row example. `skills/context-audit/README.md` describes the new
output. Not tested: a full audit run end to end with the new report format.

## Comments
