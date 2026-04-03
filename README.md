# Clockify MCP Server

MCP server for Claude Code that provides Clockify time tracking integration. Start/stop timers, auto-create tasks, and list projects — all from within Claude.

## Tools

- **`start_timer(project_name, task_name)`** — Start tracking time. Auto-stops any running timer. Creates the task if it doesn't exist.
- **`stop_timer()`** — Stop the currently running timer.
- **`list_projects()`** — List all available Clockify projects.
- **`status()`** — Check if a timer is running and show details.

## Setup

1. Get your Clockify API key from [Clockify Settings > API](https://app.clockify.me/user/preferences#advanced)

2. Copy the config:
```bash
cp .mcp.json.example .mcp.json
```

3. Edit `.mcp.json` and replace `your_api_key_here` with your actual key.

4. Start Claude Code from this directory:
```bash
claude
```

## Auto Time Tracking via CLAUDE.md

Add the following block to any project's `CLAUDE.md` to have Claude automatically check and manage Clockify at the start of every conversation:

```markdown
# Clockify Time Tracking

This project is covered by Clockify time tracking.

At the start of every conversation:
1. Check if any timer is currently running in Clockify (use the `status` tool)
2. If a timer IS running — tell me what's being tracked and ask if I want to continue with it or switch to something else
3. If NO timer is running — ask me explicitly what task we should track time against before proceeding with any work

Never skip this check. Always confirm before starting or stopping timers.
```

## Tech Stack

Python, FastMCP, httpx — runs via `uv` with no install needed.
