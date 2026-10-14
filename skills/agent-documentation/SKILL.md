---
name: agent-documentation
description: "Write or update documentation for a repository of agent skills and plugins (Claude Code plugins, SKILL.md folders, hooks, MCP servers) so that people who are not developers can understand, install, and use them. Produces a short README with Skills and Plugins tables, one page per skill, one page per plugin, an installation page, a how-it-works page, a troubleshooting page, and a glossary. Use whenever the user asks to document a skill or plugin, write a README for a skills repo, explain what a skill or plugin does to non-technical people, add docs for a new skill or plugin, or refresh the docs after a skill or plugin changed, even if they never say 'documentation skill'."
---

# Agent documentation

Write docs for skills and plugins that someone who has never opened the folder can
follow. A skill is a set of instructions an agent reads; a plugin is an add-on that
runs on its own. Readers need to know what each one does, when it fires, how to install
it, and what to do when it misbehaves, without reading its source.

Before writing, read `references/plain-language.md` (word rules, before/after examples,
glossary starter). Take page layouts from `references/templates.md`.

## What gets produced

```
README.md                  project summary: purpose, Skills table, Plugins table, install, links
docs/
├── how-it-works.md        what a skill / plugin is, how the agent uses one, repo map
├── installation.md        where each agent looks for skills; how to install a plugin
├── skills/<name>.md       one page per skill
├── plugins/<name>.md      one page per plugin
├── troubleshooting.md     symptoms, causes, fixes
└── glossary.md            only the terms the docs use
```

Match the size to the repo. One skill and no plugins needs the README, one skill page,
and a short troubleshooting page. Add the rest only when there is something to say.
Skip a table in the README when the repo has no skills (or no plugins).

## Steps

### 1. Learn each skill and plugin from its files

Find them with search, not guesswork: every folder with a `SKILL.md`, and every folder
with `.claude-plugin/plugin.json` (plus the marketplace file at the repo root, if any).

- **Skills:** read `SKILL.md` fully (frontmatter `description` = when it fires, body =
  what it does), list `references/`, `scripts/`, `assets/`, and `agents/`, and skim each
  reference for what it holds. Run scripts with `--help` or on a sample.
- **Plugins:** read `plugin.json`, `hooks/hooks.json`, `.mcp.json` if present, and each
  script the hooks call. Note which events fire, what each script does, what it needs
  (Python, a speech engine, an API key) and whether it uses the network or tokens.
- Read existing README and docs so you extend them instead of replacing them. If the
  project's purpose is unclear, ask the owner one question.

Done when: you have a table of `{name, kind (skill/plugin), when it fires, what it
produces or does, files inside}` for every skill and plugin, and you have run or traced
anything you plan to describe as behavior.

### 2. Write one page per skill, one per plugin

Follow the templates. A skill page says when the agent uses it, what it produces, what
is inside, how it works, and what it avoids. A plugin page says what it does, what
events it reacts to, what it needs, how it works inside, and how to turn it off.

Done when: every file listed in "What is inside" exists, every trigger phrase comes from
the real `description`, and every claim about behavior was checked in the code.

### 3. Write the shared pages

`docs/how-it-works.md` (concept, lifecycle, repo map, rules for new skills),
`docs/installation.md` (one section per agent, one for plugins),
`docs/troubleshooting.md` (skill not firing, wrong skill fires, plugin silent, hook errors),
`docs/glossary.md` (terms the docs use). Each fact lives on one page; others link to it.

Done when: every term is explained where it first appears or linked to the glossary, and
the repo map in `how-it-works.md` matches the real folder tree.

### 4. Rewrite README.md as the project summary

Purpose, a **Skills** table and a **Plugins** table (name, one plain sentence, link to
its page), how to install, and links to the shared pages. No step-by-step usage here: it
lives on the skill and plugin pages. Follow the template.

Done when: every skill and plugin has a row, and a newcomer knows what the repo is for
and where to start.

### 5. Check

```bash
python <skill-dir>/scripts/check_docs.py <repo-root>
```

It fails on a skill or plugin without a docs page or README row, a skill whose folder
and frontmatter `name` differ, files named in a "What is inside" table that do not
exist, broken links or heading anchors, unbalanced code fences, pages without a title and
purpose line, machine-specific paths, and text that looks like a real secret. It warns
about jargon: explain each term in place or add it to the glossary.

Then do the reading test, as a newcomer:
- Can I tell in the first three lines of each page what it is for?
- Is there a word I would have to ask a developer about?
- Do I know what to type to make the skill or plugin start (or stop)?
- Does every claim match what the files really do?

## Rules

- **Facts live once.** An install command, setting, or requirement is written on the one
  page that owns it; other pages link. For a plugin, its own README may own install
  details: link to it instead of copying.
- **Describe real behavior.** Read the code or run it. Never describe what a skill or
  plugin should do from its name alone.
- **Quote the trigger.** The skill page's "When does the agent use it?" paraphrases the
  frontmatter `description`; if it drifts from the description, the docs mislead.
- **Say what it costs.** For plugins: network, tokens, permissions, and what it can read
  or run. Readers deciding to install need this most.
- **Secrets stay out.** Use `<your-api-key>` placeholders; no machine-specific paths.
- **Update, do not rewrite.** When docs exist, extend the affected page and keep links working.
- **Explain why.** A rule with its reason is easier to trust and remember.
