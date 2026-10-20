# fastapi-docker: require .env.example to cover compose and CMD variables

Status: resolved
Type: task

## Answer
The fastapi-docker skill only asked `.env.example` to document variables the app
reads, so `${VAR}` values interpolated by `docker-compose.yml` (published port,
`FORWARDED_ALLOW_IPS`) and variables used in the Dockerfile `CMD` could be missed.

- `skills/fastapi-docker/SKILL.md`: the compose review step now checks that every
  interpolated `${VAR}` and every `CMD` variable is in `.env.example`.
- `skills/fastapi-docker/references/compose.md`: `.env.example` must also list
  compose-interpolated variables, with a test that fails on drift, and secrets
  supplied via `secrets/` stay out unless the app has a non-Docker fallback
  (noted in a comment that Compose ignores it).
