# docker-compose-standards: actually update and check .env.example

Status: resolved
Type: bug

## Answer
The skill described `.env.example` rules but had no step that enforced them, and the validator only checks image variables. Added a rule to update `.env.example` in the same change as any Compose variable edit, and a copy-paste shell check in "Validate" that prints `${VAR}`s missing from `.env.example` and stale entries, plus a reminder to check app-read variables. Docs page updated.
