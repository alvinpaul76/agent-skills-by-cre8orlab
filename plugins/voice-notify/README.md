# voice-notify

Speaks aloud when Claude Code needs your approval or finishes, so you can step away from the terminal while it works.

It runs as **local hooks**: no LLM, no tokens, no network, no dependencies beyond Python 3 and your operating system's own voice.

## What it does

| Event | When Claude Code fires it | What you hear |
| --- | --- | --- |
| `Notification` | A permission prompt appears, or Claude has been waiting for your input | `<project>. <Claude Code's notification text>` |
| `Stop` | Claude finishes a turn (this includes turns that end by asking you a question in plain text) | `<project>. Claude has finished and is waiting for you.` |

The project name is the folder you launched Claude Code from, so you can tell sessions apart.

## Install

Inside Claude Code:

```
/plugin marketplace add alvinpaul76/agent-skills-by-cre8orlab
/plugin install voice-notify@agent-skills-by-cre8orlab
```

Or from a shell:

```
claude plugin marketplace add alvinpaul76/agent-skills-by-cre8orlab
claude plugin install voice-notify@agent-skills-by-cre8orlab
```

Restart Claude Code after installing so the hooks load.

## Requirements

- Python 3 (`python3` on macOS/Linux; `python` also works, the hook tries both)
- A speech engine:

| Platform | Engine |
| --- | --- |
| macOS | built-in `say` |
| Windows | built-in PowerShell speech (`System.Speech`) |
| WSL | uses the Windows voice through `powershell.exe` |
| Linux | `spd-say` (speech-dispatcher), `espeak-ng` or `espeak`. Install one, e.g. `sudo apt install espeak-ng` |

If no engine is found the script rings the terminal bell instead.

## Test it

Run the script directly. You should hear "Voice notify test":

```
python3 plugins/voice-notify/scripts/alert.py --test
```

Simulate a hook event:

```
echo '{"hook_event_name":"Notification","cwd":"/work/demo","message":"Claude needs your permission to use Bash"}' \
  | python3 plugins/voice-notify/scripts/alert.py
```

Then start Claude Code and ask it to run a command that needs approval.

## Configure

Set `CLAUDE_ALERT_EVENTS` to choose which events speak. Put it in the `env` block of `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_ALERT_EVENTS": "Notification"
  }
}
```

| Value | Effect |
| --- | --- |
| `Notification,Stop` (default) | Speak on prompts and after every finished turn |
| `Notification` | Speak only when Claude needs permission or has been idle |
| `none` | Disable the alert without uninstalling |

`Stop` fires after every turn, which gets chatty on long sessions. If that bothers you, use `Notification` only.

## Limits

- The alert tells you to look at the terminal. It cannot ask the question or take your answer, and it does not read Claude's question aloud.
- `Notification` can fire after a short idle delay rather than at the instant Claude stops. `Stop` covers that gap.
- Hooks run on your machine with your permissions. Read `scripts/alert.py` before installing; it is short and has no network access.

## Optional: MCP variant

`mcp/alert_server.py` exposes a `trigger_pending_alert` tool so Claude can say *what* it is asking about (for example "which database?"). It is **not** registered by the plugin because it is less reliable than the hooks:

- It only works when the model decides to call the tool, so it can be forgotten.
- Every call costs a few tokens, and the tool description is sent with every request.
- It cannot catch harness-level pauses such as permission prompts.

If you still want it:

```
claude mcp add voice-notify -- python3 /absolute/path/to/plugins/voice-notify/mcp/alert_server.py
```

Then add a line like this to your `CLAUDE.md`:

```
Before asking the user a question or requesting approval, call the
trigger_pending_alert tool with a short message describing what you need.
```

## Uninstall

```
/plugin uninstall voice-notify@agent-skills-by-cre8orlab
```

## License

MIT, see the repository `LICENSE`.
