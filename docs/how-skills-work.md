# How skills work

What an agent skill is, how an agent finds and uses one, and how this repository is
organized.

New to a word? See the [word list](glossary.md).

## In plain words

A skill is a short instruction file that teaches a coding agent how to handle one
kind of task. The agent reads the skill only when the task matches it, so skills add
expertise without filling the agent's memory with rules it does not need.

```text
you describe a task
        │
        ▼
agent matches the task ──reads──▶ SKILL.md
        │                            │
        ▼                            ▼
agent follows the steps ◀──reads── references/ files (only when needed)
        │
        ▼
you get work that follows the skill's standards
```

## The life of a skill

1. **You write or install a skill folder** into a directory the agent watches. The
   folder holds a `SKILL.md` file and, optionally, `references/`, `scripts/`, and
   other supporting files.
2. **The agent lists the skill's name and description** at the start of a session.
   Only the name and description are loaded, not the whole file.
3. **You or the agent invoke the skill.** You can call it by name (for example as a
   slash command), or the agent invokes it on its own when your request matches the
   description.
4. **The agent reads `SKILL.md`** and follows its steps. When the file points to a
   `references/` document, the agent reads only that document, only when the task
   needs it. This keeps the agent's working memory small.
5. **The work follows the skill's rules.** A good `SKILL.md` says what "done" looks
   like, so the result is consistent every time.

## Where things live in this repo

```text
.
├── fastapi-standards/          architecture and code standards for FastAPI services
│   ├── SKILL.md                the file the agent reads first
│   └── references/             detailed standards, read on demand
├── fastapi-docker/             container and deployment standards for FastAPI
│   ├── SKILL.md
│   └── references/
├── fastapi-documentation/      plain-language documentation workflow
│   ├── SKILL.md
│   ├── references/
│   └── scripts/check_docs.py   a docs checker the skill runs
├── plugins/voice-notify/       a Claude Code plugin (not a skill): spoken alerts
├── .claude-plugin/             marketplace listing for the plugin
└── docs/                       these pages
```

## Anatomy of a skill folder

```text
my-skill/
├── SKILL.md          required: frontmatter (name, description) + instructions
├── references/       optional: detailed docs the agent reads on demand
├── scripts/          optional: helper scripts the skill tells the agent to run
└── agents/           optional: agent-specific metadata
```

Only `SKILL.md` is required. The `description` in its frontmatter decides when the
agent reaches for the skill, so it lists the tasks and phrases that should trigger
it. The details live in `references/` so `SKILL.md` stays short.

## Rules for new skills

The conventions the next skill must follow, each with its reason:

- **One skill, one job.** A skill that tries to cover everything triggers on
  everything and helps with nothing.
- **`description` lists trigger phrases.** The agent matches your request against
  it, so vague descriptions mean the skill never fires.
- **`SKILL.md` is the map, `references/` is the territory.** Put steps and pointers
  in `SKILL.md` and depth in `references/`, so the agent loads detail only when the
  task needs it.
- **Say what done looks like.** "Done when" lines let the agent check its own work.
- **Keep paths relative.** The same skill folder should work in any agent and any
  project.
- **No secrets, no machine-specific paths.** Skills get shared; anything private
  inside them gets shared too.

The full authoring walkthrough is in [creating a skill](creating-a-skill.md).

## A note on plugins

`plugins/voice-notify/` is a Claude Code plugin, not a skill. A skill is read by the
agent when a task matches; a plugin is installed once and acts on its own (here,
speaking aloud when the agent finishes). See
[the plugin page](plugins/voice-notify.md).
