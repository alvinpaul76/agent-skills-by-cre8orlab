# Writing for people who are not developers

Read this before writing any page. The reader is smart but has never opened the repo:
a manager choosing tools, a teammate installing a plugin, someone new to coding agents.
If they have to ask a developer what a word means, the page has failed.

## Rules

1. **Start with the purpose.** The first lines of every page say what this is for and
   who would use it.
2. **Say what it does, then what it is called.** "A folder of instructions the agent reads
   for one kind of task (called a *skill*)". Add each term to `docs/glossary.md`.
3. **Short sentences.** Aim for 20 words or fewer. One idea per sentence.
4. **Talk to the reader.** Use "you" and active verbs: "Copy the folder into your skills
   directory", not "The folder should be copied".
5. **Headings are questions or tasks.** "When does the agent use it?" beats "Triggering".
6. **One action per step.** Number the steps; put each command in a code block and
   show what the reader should see afterwards.
7. **Explain why.** "It only reads the reference file when needed, which keeps the
   agent's memory small" is remembered and trusted.
8. **Say what it costs and touches.** Does it use the network, spend tokens, run
   commands, read files? Say so in plain words.
9. **Real examples only.** Quote the real trigger phrases, commands, and output.
10. **Avoid filler.** Skip "simply", "just", "obviously". Avoid a bare "it" or "this"
    when two things could be meant.
11. **Tables for lookups, prose for reasons.**

## Before and after

| Developer wording | Plain wording |
|---|---|
| "Registers a Stop hook that shells out to a TTS script." | "When the agent finishes, a small script speaks a short message so you know to come back." |
| "Progressive disclosure via references/." | "The agent reads the short main file first and opens the longer files only when the task needs them." |
| "Frontmatter description is the invocation trigger." | "The agent compares your request to the skill's description. The closer they match, the more likely it uses the skill." |
| "Ships an MCP server exposing a tool." | "Includes a small helper program the agent can call. Off by default because every call costs tokens." |

## Plain-language glossary starter

Copy only the terms the docs actually use into `docs/glossary.md`.

| Term | In plain words |
|---|---|
| Agent / coding agent | A program that reads your instructions and writes or changes code for you. |
| Skill | A folder of instructions that teaches an agent how to handle one kind of task. |
| `SKILL.md` | The one required file in a skill folder: a short header plus the steps to follow. |
| Frontmatter | The `---` block at the top of `SKILL.md` with the skill's `name` and `description`. |
| Description | The text that tells the agent when to use the skill. |
| Plugin | An add-on installed once that acts on its own, unlike a skill, which the agent reads per task. |
| Hook | A small action the editor runs automatically when something happens, such as the agent finishing. |
| MCP server | A helper program that gives the agent extra tools it can call. |
| Marketplace | A list of plugins that the agent's plugin command can install from. |
| Symlink | A shortcut file pointing at another folder, so one copy serves many agents. |
| Skills directory | The folder an agent scans for skills. Its location depends on the agent. |
| Token | The unit an AI model is billed and limited by; roughly a few characters of text. |
| Trigger | The moment a skill starts being used, because you named it or your request matched its description. |
