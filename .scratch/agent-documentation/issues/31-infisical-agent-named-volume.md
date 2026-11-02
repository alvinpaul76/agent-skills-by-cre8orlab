# Infisical agent skill: named volume, umask scope, hardening

Status: resolved
Type: task

## Answer
Updated `infisical-docker-agent` skill. `shared_secrets` is now a plain Docker-managed named volume (no host dir, bind, or setup script); persists across reboots as offline fallback, so no tmpfs. Scoped `umask 077` to a subshell around credential files so consumers can read the rendered file. Added `cap_drop: [ALL]` and `no-new-privileges` to the agent reference compose. Added an offline-fallback verification section and gotchas to `SKILL.md`.
