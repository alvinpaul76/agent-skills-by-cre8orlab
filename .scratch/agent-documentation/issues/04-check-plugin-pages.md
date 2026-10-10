# Teach check_docs.py to check plugin pages too

Status: needs-triage
Type: task

`agent-documentation/scripts/check_docs.py` verifies files in a skill page's "What is inside?" table exist, but does nothing equivalent for plugins.

## To do
- Check every hook event in `hooks/hooks.json` appears in the plugin page's events table
- Check script paths named on the page exist

## Comments
