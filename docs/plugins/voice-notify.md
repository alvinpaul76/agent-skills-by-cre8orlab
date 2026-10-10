# voice-notify (plugin)

A Claude Code plugin that speaks aloud when the agent needs your approval or
finishes a turn, so you can step away from the terminal while it works.

New to a word? See the [word list](../glossary.md). · plugin folder:
[`plugins/voice-notify/`](../../plugins/voice-notify/)

This is a plugin, not a skill. A skill is read by the agent when a task matches;
a plugin is installed once and then acts on its own through editor hooks.

## What does it do?

| Event | When Claude Code fires it | What you hear |
| --- | --- | --- |
| `Notification` | A permission prompt appears, or the agent has been waiting for your input | The project name and the notification text |
| `Stop` | The agent finishes a turn | The project name and "Claude has finished and is waiting for you" |

The project name is the folder you launched Claude Code from, so you can tell
sessions apart. Which events speak is configurable, and `Notification` alone is
the quieter option.

## How does it work inside?

Claude Code runs `scripts/alert.py` on each event. The script reads the event
details, picks your operating system's built-in speech engine (`say` on macOS,
PowerShell speech on Windows, `spd-say` or `espeak-ng` on Linux), and speaks —
no LLM, no tokens, no network. Without a speech engine it falls back to the
terminal bell.

An optional MCP server (`mcp/alert_server.py`) can announce *what* the agent is
asking about, but it is not registered by default because the model can forget
to call it and every call costs tokens.

## Where is the detail?

The plugin's own [README](../../plugins/voice-notify/README.md) is the source of
truth for installation, speech-engine requirements, testing, the
`CLAUDE_ALERT_EVENTS` setting, limitations, and uninstalling.

Back to [how skills work](../how-skills-work.md).
