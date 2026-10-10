# Agent Skills by Cre8or Lab

Reusable skills that give coding agents focused engineering guidance, workflows, and
reference material. Each skill is a self-contained folder that an agent loads when a
task calls for it.

## What is it for?

- Give any coding agent consistent standards for FastAPI work
- Share the same guidance across different agents and projects

## Skills

| Skill | What it does | Docs |
| --- | --- | --- |
| fastapi-standards | Layered-architecture standards for building, reviewing, and refactoring FastAPI services | [fastapi-standards](docs/skills/fastapi-standards.md) |
| fastapi-docker | Container, deployment, and image-scanning standards for FastAPI services | [fastapi-docker](docs/skills/fastapi-docker.md) |
| fastapi-documentation | Writes plain-language docs that non-developers can follow | [fastapi-documentation](docs/skills/fastapi-documentation.md) |

Each page explains when the skill triggers and what is inside it.
The repo also ships the [voice-notify](docs/plugins/voice-notify.md) plugin for
Claude Code.

## Get started

1. Clone the repository:

   ```bash
   git clone https://github.com/alvinpaul76/agent-skills-by-cre8orlab.git
   ```

2. Copy or symlink the skill folders you want into your agent's skills directory.
   Where that directory lives depends on the agent; see
   [installing skills](docs/installation.md).

## Docs

- [How skills work](docs/how-skills-work.md): what a skill is and how agents use one
- [Installing skills](docs/installation.md)
- [Creating a skill](docs/creating-a-skill.md)
- [Something not working?](docs/troubleshooting.md)
- [Word list](docs/glossary.md)

## License

Released under the [MIT License](./LICENSE).
