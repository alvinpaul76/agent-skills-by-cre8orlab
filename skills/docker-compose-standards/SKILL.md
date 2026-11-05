---
name: docker-compose-standards
description: Shared rules for every Docker Compose file - file naming, version-pinned images supplied through env vars, and keeping .env.example in sync. Use whenever creating, editing, reviewing or debugging a docker-compose*.yml, .env or .env.example, including alongside another Docker skill such as fastapi-docker or infisical-docker-agent.
---

# Docker Compose standards

Rules every Docker skill shares. Domain skills own the rest (hardening, healthchecks, how secrets are delivered) and point here instead of repeating these.

## File names

Base file `docker-compose.yml`; additional files `docker-compose.<purpose>.yml` (`override`, `dev`, `prod`). Use `.yml`. In an existing project that already uses `compose.yaml`, keep its name: renaming breaks the scripts and CI that reference it.

## Images (blocking)

1. Every image pulled from a registry comes from one variable:
   `image: ${POSTGRES_IMAGE:?POSTGRES_IMAGE is required}`.
   The version then lives in one reviewed place, and Compose refuses to start when it is unset instead of pulling something unexpected. No literal, no `:-` default (a default is a hidden literal), no partial `postgres:${TAG}`.
2. The value is pinned: at least `major.minor`, preferably `major.minor.patch`, optionally with a variant (`postgres:18.6-trixie`), or a digest (`@sha256:…`). Floating references change on the next pull: no tag, `latest`, `stable`, `main`, `edge`, `lts`, a bare variant (`alpine`), major-only (`postgres:18`).
3. Name it `<SERVICE>_IMAGE` in upper snake case. Keep a project's existing names (such as `INFISICAL_CLI_IMAGE`) rather than renaming them.
4. Services with `build:` are local and exempt; an `image:` next to `build:` is only the output tag (`myapi:local`).
5. Never change a version the user did not ask to change. When adding or bumping one, confirm the tag exists for the target architecture (`docker buildx imagetools inspect <ref>`) and say that you did.

## .env and .env.example

- `.env` is git-ignored and belongs to the user. Never edit or overwrite an existing one; tell the user which lines to add.
- `.env.example` is committed and lists every `${VAR}` the Compose files interpolate, plus every variable the app reads. Image variables carry their real pinned values (versions are not secrets); secrets get placeholders. A secret Compose supplies through `secrets:` files stays out unless the app also reads it without Docker, with a comment saying Compose ignores it.
- `${VAR:?msg}` only for values that are always required. Use `${VAR:-default}` for settings the app validates itself or that a feature switch can make optional, since `:?` would block the switch.
- Define each variable once: with duplicates the last line wins silently.
- Containers keep the values they were created with. `docker compose restart` does not re-read `.env`; use `docker compose up -d` (add `--force-recreate` if it reports nothing changed). Compare values without printing them: `printf %s "$v" | sha256sum | cut -c1-8`.

## Validate

Before calling Compose work done, run the `validate-docker-compose` hook script if it is installed. Otherwise run at least `docker compose --env-file .env.example config -q`, which checks syntax and confirms `.env.example` declares every required variable without needing the user's `.env`.
