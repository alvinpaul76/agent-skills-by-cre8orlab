# Page templates

Fill the angle-bracket parts from the code. Keep the section order: the reader meets
the purpose first, the details last. Every "Done when" line is a check you can make.

## README.md (project summary, about 50 lines)

The README describes the project, not any one API. A reader should learn what the
project is for, which APIs it offers, how to get it running, and where the docs are.

```markdown
# <Project name>

<Two sentences: what the project is for, and how it is organized. Name the purpose
the owner gave it (for example "a playground for testing X and building X-powered
APIs"), not just the one API that exists today.>

## What is it for?
- <Purpose 1 in plain words>
- <Purpose 2>

## APIs
| API | What it does | Docs |
|---|---|---|
| <Name> | <One plain sentence> | [<Name> API](docs/apis/<feature>.md) |

<One line: each page has a step-by-step first request; how to add an API.>

## Get it running
1. <Copy the settings file and create a key: commands>
2. <Start the service: command>
3. <Check it is ready: command, then the answer you should see>
4. <Where to explore it (interactive docs), and a pointer to the API pages for a first request>

## Run the tests
<command>

## Run it in Docker
<command>

## Docs
- [How it works](docs/architecture.md): the big picture in plain words
- [Something went wrong?](docs/troubleshooting.md)
- [Running it for real](docs/deployment.md)
- [Word list](docs/glossary.md)
```

Done when: every `docs/apis/*.md` page has a row in the APIs table, a newcomer can get a
running, ready service from this page alone, and the page holds no endpoint paths and no
request or response examples (those belong to the API pages). If you do not know the
project's purpose, ask the owner in one question instead of guessing.

## docs/architecture.md (shared design)

1. **In plain words**: two or three sentences, then one small diagram of a request's
   journey with a verb on each arrow.
2. **The journey of a request**: numbered list, one line per stop (tracing ID, key
   check, size and validation checks, the business rule, the model or outside
   service, the answer). Say what each stop protects against.
3. **Where things live**: directory map, one plain sentence per folder.
4. **Errors**: only the shape every error shares and the rule that clients rely on `code`.
   The list of codes lives in `troubleshooting.md` (one owner); link to it.
5. **Settings**: table of variable, default, what it changes. Name the file the defaults
   come from. The safe-versus-risky values live in `deployment.md`.
6. **Starting, health and tests**: how to tell it is running and ready.
7. **Rules for new APIs**: the conventions the next feature must follow, each with
   its reason.

Done when: no sentence is true of only one endpoint, and a term used here is
explained or links to the glossary. Put "New to a word? See the [word list](glossary.md)."
under the purpose line of every page.

## docs/apis/<feature>.md (one per feature)

```markdown
# <Feature name>

<One sentence: what this API does and when you would use it.>

`<METHOD> <path>` · needs an API key: <yes/no> · code: `<source dir>`

## How do I use it?
<Numbered steps with a real request (placeholders for secrets) and the real answer.>

## What do I send?
| Field | Required? | What it means | Limits |
|---|---|---|---|
(Limits come from the code; cite the file, for example `domain/entities.py`.)

## What do I get back?
<Real example answer, then a table: field, what it means, how to read it
(for example "confidence: 0 to 1, higher means more certain").>

## How does it work inside?
<A few plain sentences: what the service does with each item, in what order, and
anything that affects speed or results.>

## What can go wrong?
| Code | Meaning for this API | What to do |
|---|---|---|
(Only errors this API adds. Shared ones: link to troubleshooting.)

Back to [how it works](../architecture.md).
```

Done when: every route on the router is covered, every limit exists in the code, and
the example was produced by a real run.

## docs/deployment.md (only when running it needs more than one command)

Add a table "Which settings matter for production?" (setting, safe value, risk of the
other value). Sections as tasks: "How do I create and rotate API keys?", "How do I choose the
backend?", "How do I run it in Docker?", "How do I turn docs or the key check on or
off?". For each setting: what it does, the safe value for production, the risk of
the other value. Keep all real secrets out; show `<your-api-key>`.

## docs/troubleshooting.md (always)

Start from symptoms the reader sees: "I get 401", "The first request is slow",
"The service will not start". For each: likely cause, how to check (with a command),
fix. Include the status-code table from `plain-language.md` with a column for the
exact `code` string of every error the API returns, and one real error body. This
page owns the error list and the conditions that stop the service from starting; other
pages link here.

## docs/glossary.md (always)

Only terms the docs use, alphabetical, each in one plain sentence. Link a term's
first use on each page to its entry when the term is not obvious.
