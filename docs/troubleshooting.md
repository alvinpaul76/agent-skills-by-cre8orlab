# Troubleshooting

What to do when a skill does not work the way you expect.

New to a word? See the [word list](glossary.md).

## The agent does not see my skill

| Check | How |
| --- | --- |
| The folder is in a directory the agent scans | Compare your path against the table in [installation](installation.md). The skill must sit at `<skills-dir>/<name>/SKILL.md`, not a level deeper or shallower. |
| The folder is named after the skill | The directory name should match the `name` in the frontmatter. |
| The agent was restarted | Many agents scan for skills when a session starts. Open a new session. |
| A symlink resolves | Run `ls <skills-dir>/<name>/SKILL.md`. If it fails, the link target moved — recreate the link. |

## The skill exists but never triggers

- **The description is too vague.** The agent matches your request against the
  `description` in `SKILL.md`. List concrete tasks and phrases, not "helps with
  FastAPI". Look at the three skills in this repo for the level of detail to aim
  for.
- **You can still invoke it by name.** Most agents let you call a skill directly
  (for example `/fastapi-standards`). If a direct call works, only the trigger
  description needs work.
- **The agent may have skipped it on purpose.** Ask it to explain why, then
  tighten the description or say the skill's name in your request.

## The skill triggers but behaves oddly

- **`SKILL.md` is too long.** An over-long instruction file dilutes the steps.
  Move detail into `references/` and leave pointers behind.
- **A referenced file is missing.** Re-read the skill and check every path it
  mentions exists and is relative.
- **Two skills fight.** If two skills claim the same task, the agent may pick the
  wrong one. Narrow each description so the trigger situations do not overlap.

## The docs checker reports an error

`check_docs.py` (from the fastapi-documentation skill) fails on these:

| Message | Fix |
| --- | --- |
| Broken relative link or heading anchor | The linked file or `#section` does not exist. Fix the path or the heading. |
| API page the README does not link | Add a row for it in the README's table. |
| Unbalanced code fences | A ` ``` ` block was opened and never closed. |
| Page without a title and purpose line | Start the page with `# Title`, then one sentence saying what the page is for. |
| Looks like a real secret | Replace the value with a placeholder such as `<your-api-key>`. |

Warnings about jargon are not failures: explain the word in place or add it to
the [word list](glossary.md).

## Still stuck?

Re-read [how skills work](how-skills-work.md) to check the mental model, then
compare your skill folder against one of the three in this repository — the
difference is usually the bug.
