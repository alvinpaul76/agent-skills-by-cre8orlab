# docker-compose-standards

Shared rules for every Docker Compose file: how files are named, how images are
pinned, and how `.env.example` stays complete. The other Docker skills follow it
instead of repeating it.

New to a word? See the [word list](../glossary.md). · skill folder:
[`docker-compose-standards/`](../../skills/docker-compose-standards/)

## When does the agent use it?

Whenever you create, change, review, or debug a `docker-compose*.yml`, `.env`, or
`.env.example` file, including when [fastapi-docker](fastapi-docker.md) or
[infisical-docker-agent](infisical-docker-agent.md) is also in use.

## What is inside?

| File | What it holds |
| --- | --- |
| `SKILL.md` | File naming, image pinning through variables, `.env` and `.env.example` rules, the validation command |

## How does it work inside?

1. Every image downloaded from a registry is written as one variable, such as
   `${POSTGRES_IMAGE:?POSTGRES_IMAGE is required}`. The version lives in
   `.env.example`, so it is reviewed in one place, and Compose refuses to start
   when it is missing instead of downloading something unexpected.
2. The version must be exact enough not to change on the next download: at least
   `major.minor` such as `postgres:18.6`, or a fixed fingerprint (`@sha256:…`).
   Tags like `latest`, `stable`, or `postgres:18` are rejected.
3. Images built from your own code (`build:`) are exempt.
4. `.env.example` lists every variable the Compose files and the app use. The agent
   never edits your `.env`; it tells you which lines to add. It updates
   `.env.example` in the same change as any Compose edit, then runs a short shell
   check that prints variables missing from it and stale ones.
5. Before calling the work done, the agent checks the files with the
   [validate-docker-compose](../hooks/validate-docker-compose.md) hook's script, or
   with `docker compose --env-file .env.example config -q` when the hook is not
   installed.

## What it deliberately avoids

- Changing an image version you did not ask to change. When it adds or upgrades
  one, it first confirms that the version exists for your machine type.
- Inventing a version. When it suggests or pins one, it looks up the current stable
  release first, uses that exact `major.minor.patch`, and tells you which it found.
- Renaming an existing project's `compose.yaml`, because scripts and CI refer to it.
- Hardening, health checks, and secrets handling; those belong to the domain skills.

Back to [how skills work](../how-skills-work.md).
