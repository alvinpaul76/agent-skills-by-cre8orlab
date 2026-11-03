# Infisical agent skill: ship *.example config, gitignore real files, doc step

Status: resolved
Type: task

## Answer
`infisical-docker-agent` references renamed to `agent-config.example.yaml` and `app.example.tpl` (placeholder host, project ID, env). `SKILL.md` now says: commit only `*.example` files, gitignore the real `agent-config.yaml`, `templates/*.tpl` (with `!*.example.tpl` exception) and `.infisical.yaml`, check with `git check-ignore -v`. Added a Docs step (README/docs update checklist: prerequisites, copy step, restart, troubleshooting, grep for leftover secret names). Machine identity step renumbered to 7. Updated `docs/skills/infisical-docker-agent.md` file table.
