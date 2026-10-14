# Writing for people who are not developers

Read this before writing any page. The reader is smart but has never seen the code:
a product owner, a support agent, a tester, a new teammate. If they have to ask
a developer what a word means, the page has failed.

## Rules

1. **Start with the purpose.** The first lines of every page say what this is for and
   who would use it, before any detail.
2. **Say what it does, then what it is called.** Write "the check that makes sure the
   caller has a valid key (called *authentication*)" the first time, and the short
   name afterwards. Add each such term to `docs/glossary.md`.
3. **Short sentences.** Aim for 20 words or fewer. One idea per sentence.
4. **Talk to the reader.** Use "you" and active verbs: "Send the key in the
   `X-API-Key` header", not "The key should be provided".
5. **Headings are questions or tasks.** "How do I send my first request?" beats
   "Request format".
6. **One action per step.** Number the steps. Put each command in a code block and
   show what the reader should see afterwards.
7. **Explain why.** A rule with a reason ("Batches are capped at 20 so one request
   cannot tie up the model for minutes") is remembered and trusted.
8. **Numbers carry units and meaning.** Write "2 MiB (about 2 megabytes)", not
   "2097152".
9. **Real examples only.** Every example is copied from a real run of the code.
   Never invent output. Never paste a real key: use `<your-api-key>`.
10. **Avoid filler and shortcuts.** Skip "simply", "just", "obviously", and
    "as you know". Avoid a bare "it" or "this" when two things could be meant.
11. **Tables for lookups, prose for reasons.** Error codes, settings and fields go in
    tables with a plain "what it means" column.
12. **A picture for the flow.** One small diagram per architecture page (a Mermaid
    block or ASCII arrows), with a verb on each arrow.

## Before and after

| Developer wording | Plain wording |
|---|---|
| "Requests traverse the middleware stack, then the auth dependency." | "Each request first gets an ID for tracing, then the service checks the API key. Only then does it look at what you sent." |
| "Returns 422 with RFC 9457 problem details on schema violation." | "If something in your request is not valid (for example an empty title), the service answers with status 422 and lists which fields to fix." |
| "Adapter serializes inference via a mutex." | "The service handles one ticket at a time on the local model, so a large batch takes a few seconds." |
| "Fail-closed at startup." | "If no API keys are configured, the service refuses to start. This prevents it from running open by accident." |

## Plain-language glossary starter

Copy only the terms the docs actually use into `docs/glossary.md`, and adjust to the
project.

| Term | In plain words |
|---|---|
| API | A way for one program to ask another program to do something. |
| Endpoint | One specific address of the API that does one job, like `/api/v1/ticket-analyses`. |
| Request / response | What a program sends, and what it gets back. |
| JSON | A text format for structured data: names and values in `{ }`. |
| Header | Extra information sent with a request, such as the API key. |
| API key | A long secret string that proves the caller is allowed to use the service. Treat it like a password. |
| Status code | A number in every response: 2xx worked, 4xx the request has a problem, 5xx the service has a problem. |
| Batch | Several items sent in one request. |
| Validation | Checking that what was sent is complete and within limits before doing any work. |
| Environment variable | A setting given to the program from outside, such as `JEV_BACKEND=jev`. |
| `.env` file | A private text file on your machine that holds those settings. It is never shared or committed. |
| Docker / container | A sealed package that runs the service the same way on any computer. |
| Health check | A tiny address that tells you whether the service is running and ready. |
| Rate limit | A cap on how many requests a caller may send in a period of time. |
| Request ID | A short code attached to each request, used to find it in the logs. |

## Status codes in plain words

Use this table (trimmed to the codes the API really returns) in `docs/troubleshooting.md`.

| Code | What it means | What to do |
|---|---|---|
| 200 | It worked. | Nothing. |
| 401 | The API key is missing or wrong. | Send the key in the `X-API-Key` header. Check for typos and extra spaces. |
| 413 | The request is too big. | Send fewer items or shorter text. The limit is in the API page. |
| 422 | Something in the request is not valid. | Read the `errors` list in the answer: it names each field to fix. |
| 429 | Too many requests. | Wait and retry. |
| 500 | The service had an unexpected problem. | Send the `request_id` from the answer to the team. |
| 503 | The service cannot do the work right now (for example, the model is still loading). | Wait a minute and retry. |
