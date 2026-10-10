# Word list

The terms these docs use, in plain words.

| Term | In plain words |
| --- | --- |
| Agent / coding agent | A program that reads your instructions and writes or changes code for you, such as Devin or Claude Code. |
| Skill | A folder of instructions that teaches an agent how to handle one kind of task. |
| `SKILL.md` | The one required file inside a skill folder: its frontmatter plus the steps the agent follows. |
| Frontmatter | The `---` block at the top of `SKILL.md` holding `name` and `description`. The description decides when the skill fires. |
| `references/` | Extra documents inside a skill folder. The agent reads them only when the task needs them. |
| Trigger / invoke | To start using a skill — either you call it by name, or the agent starts it because your request matches its description. |
| Symlink | A shortcut file that points at another folder, so one copy of the skill serves every agent. |
| Skills directory | The folder an agent scans for skills. Its location depends on the agent; see [installation](installation.md). |
| Plugin | A packaged add-on an agent or editor installs once and runs on its own — unlike a skill, it is not invoked per task. |
| Layered architecture | Splitting code into routes, use cases, domain, and infrastructure so business rules stay independent of the framework. |
| Schema | A description of the shape some data must have — which fields exist and what type each is. |
| Dependency injection | Giving a piece of code the things it needs (a database session, a client) from outside instead of letting it build them itself, so tests can swap in fakes. |
| Multi-stage build | A Dockerfile technique that builds in one stage and copies only the result into the final, smaller image. |
| API | A way for one program to ask another program to do something. |
| FastAPI | A Python framework for building APIs. |
