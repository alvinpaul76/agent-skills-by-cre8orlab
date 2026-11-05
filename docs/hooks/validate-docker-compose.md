# validate-docker-compose (hook)

A Claude Code hook that checks every Docker Compose change against the
[docker-compose-standards](../skills/docker-compose-standards.md) skill and sends
the agent back to fix any image that is not pinned through a variable.

New to a word? See the [word list](../glossary.md). · hook folder:
[`hooks/validate-docker-compose/`](../../hooks/validate-docker-compose/)

This is a hook, not a skill. It runs on its own after edits, and the same script
runs by hand or in CI.

## Install

Needs Node.js, Python 3, and PyYAML (`pip install pyyaml`). Docker Compose is
optional; with it, the hook also checks the file's syntax.

```bash
npx --allow-git=all github:alvinpaul76/agent-skills-by-cre8orlab install validate-docker-compose
npx --allow-git=all github:alvinpaul76/agent-skills-by-cre8orlab status validate-docker-compose
npx --allow-git=all github:alvinpaul76/agent-skills-by-cre8orlab uninstall validate-docker-compose
```

Then restart Claude Code and check `/hooks`. The installer works the same way as for
[quiet-command-output](quiet-command-output.md#install): it merges one entry into
`~/.claude/settings.json`, backs the file up first, and leaves your other hooks alone.

## What does it do?

After the agent edits or writes a `docker-compose*.yml`, `compose*.yml`, or
`.env.example` file, the hook checks every Compose file in that folder.

- **Everything follows the rules:** the hook says nothing.
- **Something breaks a rule:** the hook sends the errors back to the agent, such as
  `ERROR E4 .env.example:db: POSTGRES_IMAGE=postgres:latest: tag 'latest' is floating`,
  and the agent fixes them before carrying on.

## Run it by hand or in CI

```bash
python3 hooks/validate-docker-compose/validate-docker-compose.py            # this folder and below
python3 hooks/validate-docker-compose/validate-docker-compose.py deploy/   # one folder
python3 hooks/validate-docker-compose/validate-docker-compose.py --json --no-docker .
```

It exits with 1 when there is any error, so a CI step fails. Warnings never fail it.

## What the codes mean

| Code | Level | Meaning | What to do |
| --- | --- | --- | --- |
| E1 | error | An image is written directly in the Compose file | Replace it with `${NAME_IMAGE:?NAME_IMAGE is required}` and put the version in `.env.example` |
| E2 | error | The image uses a variable in the wrong form: a default (`:-`), only the tag (`postgres:${TAG}`), or no `:?` | Use exactly one `${NAME_IMAGE:?message}` |
| E3 | error | The variable is missing from `.env.example`, or there is no `.env.example` | Add `NAME_IMAGE=<image>:<version>` to `.env.example` |
| E4 | error | The version in `.env.example` can change on the next download: no tag, `latest`, `stable`, or only a major version such as `postgres:18` | Use at least `major.minor` (`postgres:18.6`) or a digest (`@sha256:…`) |
| E5 | error | The file is not valid YAML, or `docker compose config` rejects it | Fix the file; the message shows Compose's own error |
| W1 | warning | The version has no patch number (`3.14` rather than `3.14.0`) | Add it if the image publishes one; some, like Postgres, don't |
| W2 | warning | `.env.example` has an `_IMAGE` variable no Compose file here uses | Remove it, or it is used somewhere the hook can't see |
| W3 | warning | Your `.env` has a different image than `.env.example` | Usually an upgrade not yet copied across; decide which is right |
| W4 | warning | Something was not checked: Docker Compose missing, or `include:` / `extends:` in use | Run with Docker Compose, or check those files separately |

Services with `build:` are skipped, because their image is built from your code.

## Things to know

- **It never changes your files.** It only reports. It never prints values from
  `.env` other than image names.
- **Errors reach the agent; warnings don't.** In hook mode only errors are sent back.
  Run the script by hand to see warnings.
- **No PyYAML and no Docker:** the hook stays quiet rather than blocking every edit.
  The hand-run command reports that it cannot check.
- **It runs after the edit.** The file is already changed when the hook speaks; the
  agent then fixes it. Edits you make yourself are only caught by the hand-run
  command or CI.
- **Date-stamped tags** such as `RELEASE.2024-01-16T16-07-38Z` count as pinned. Other
  unusual tags may be flagged; pin those by digest.
- **Not Windows.** The settings entry calls `python3`.

## Back to

[Installing skills](../installation.md) · [how skills work](../how-skills-work.md)
