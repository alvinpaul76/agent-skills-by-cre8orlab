# Page templates

Fill the angle-bracket parts from the files. Keep the section order: the reader meets
the purpose first, the details last. Put "New to a word? See the [word list](../glossary.md)."
under the purpose line of every page (fix the relative path per page).

## README.md (project summary, about 50 lines)

```markdown
# <Project name>

<Two sentences: what the repo is for and how it is organized.>

## What is it for?
- <Purpose 1 in plain words>

## Skills
| Skill | What it does | Docs |
|---|---|---|
| <name> | <One plain sentence> | [<name>](docs/skills/<name>.md) |

## Plugins
| Plugin | What it does | Docs |
|---|---|---|
| <name> | <One plain sentence> | [<name>](docs/plugins/<name>.md) |

## Get started
1. <Clone command>
2. <Install a skill: copy or symlink; link to installation.md>
3. <Install a plugin: command; link to the plugin page>

## Docs
- [How it works](docs/how-it-works.md)
- [Installing](docs/installation.md)
- [Something not working?](docs/troubleshooting.md)
- [Word list](docs/glossary.md)

## License
```

Done when: every skill folder and plugin has a row linking its page, and the README
holds no step-by-step usage.

## docs/skills/<name>.md

Keep the heading text; the checker reads "What is inside?".

```markdown
# <name>

<One sentence: what the skill does and for whom.>

New to a word? See the [word list](../glossary.md). · skill folder: [`<name>/`](../../<name>/)

## When does the agent use it?
<Paraphrase the frontmatter description: the tasks and phrases that trigger it.>

## What does it produce?
<Bullets: the files or results you get.>

## What is inside?
| File | What it holds |
|---|---|
| `SKILL.md` | <workflow> |
| `references/<file>.md` | <what it holds> |
| `scripts/<file>` | <what it does and when the agent runs it> |

## How does it work inside?
<Numbered, 3 to 5 plain steps: what the agent reads, does, and checks.>

## What it deliberately avoids
<Bullets, each with the reason.>

Back to [how it works](../how-it-works.md).
```

Done when: every file in the table exists in the skill folder, and the trigger section
matches the real `description`.

## docs/plugins/<name>.md

```markdown
# <name> (plugin)

<One sentence: what the plugin does for you.>

New to a word? See the [word list](../glossary.md). · plugin folder: [`plugins/<name>/`](../../plugins/<name>/)

<Two lines: this is a plugin, not a skill, and what that means for the reader.>

## What does it do?
| Event | When it fires | What happens |
|---|---|---|

## What does it need and cost?
<Requirements (Python, speech engine, keys). Network? Tokens? Files it reads or commands it runs?>

## How do I install and remove it?
<Numbered steps with the real commands, or a link to the plugin's own README if that owns them.>

## How does it work inside?
<Plain sentences: which script runs on which event, what it does.>

## Where is the detail?
<Link to the plugin README as the source of truth for settings and limits.>

Back to [how it works](../how-it-works.md).
```

Done when: every hook event in `hooks.json` appears in the table, and requirements and
costs were checked in the scripts.

## docs/how-it-works.md

1. **In plain words:** what a skill and a plugin are; one diagram of how the agent finds
   and uses a skill.
2. **The life of a skill:** numbered, from installing to the work following the rules.
3. **Where things live:** the real folder tree, one plain line per entry.
4. **Anatomy of a skill folder** and **of a plugin folder.**
5. **Rules for new skills and plugins**, each with its reason.

## docs/installation.md

One section per supported agent: where its skills directory is, the copy or symlink
command, how to confirm it loaded. A section for plugins: the marketplace add and
install commands, and "restart the agent".

## docs/troubleshooting.md

Symptoms the reader sees: "The agent ignores my skill", "The wrong skill fires", "The
plugin installs but does nothing", "A hook errors". Each: likely cause, a check
(command), fix. This page owns the list of symptoms; other pages link here.

## docs/glossary.md

Only terms the docs use, each in one plain sentence. Link a term's first use on a page.
