## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

**Log every change.** When you change anything in this repo, add or update a ticket under `.scratch/` in the same commit: new work starts as `Status: needs-triage`; completed work gets a resolved ticket describing what changed (not commit hashes or PR numbers). The pattern is one ticket per shipped change — see `.scratch/agent-documentation/issues/`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
