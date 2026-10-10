# Creating a skill

How to author a new skill for this repository, step by step.

New to a word? See the [word list](glossary.md).

## Steps

1. **Create a folder named after the skill**, using lowercase with hyphens, for
   example `postgres-migrations/`.

2. **Write `SKILL.md`** inside it. Start with the frontmatter — the metadata the
   agent reads to decide when the skill applies:

   ```markdown
   ---
   name: example-skill
   description: Explain what the skill does and list the phrases and tasks that should trigger it.
   ---
   ```

   The description is the trigger. Write it for matching: name the situations,
   file types, and user phrases that should invoke the skill. A vague description
   means the skill never fires.

3. **Write the instructions** below the frontmatter. Tell the agent when to use
   the skill, the steps to follow, and what successful completion looks like.
   "Done when" lines let the agent check its own work.

4. **Move detail into `references/`** and link to it from `SKILL.md`. The agent
   loads `SKILL.md` every time the skill fires but reads a reference file only
   when the task needs it, so deep material belongs there.

5. **Add helper scripts to `scripts/`** when the workflow includes a repeatable
   check or transformation. `fastapi-documentation`'s `check_docs.py` is the
   pattern: the skill names the command, the agent runs it.

6. **Keep paths relative** inside the skill so the folder works under any agent
   and any install location. Never include secrets, tokens, or paths that only
   exist on your machine.

7. **Add the skill to the README's Skills table** and give it a page under
   `docs/skills/` following the layout of the existing pages.

8. **Install and trigger it** the way [installation](installation.md) describes,
   and confirm the agent fires on the phrases from your description — and stays
   quiet on unrelated tasks.

## Done when

- The frontmatter parses and the description names concrete trigger situations.
- `SKILL.md` fits on a screen or two; the depth lives in `references/`.
- Every file the skill references exists, and every path is relative.
- The skill appears in the README table and has a `docs/skills/` page.
- A fresh session invokes it on a matching request.

## Contributing

Contributions are welcome. Keep each skill focused and self-contained, and
follow the rules for new skills in [how skills work](how-skills-work.md#rules-for-new-skills).
