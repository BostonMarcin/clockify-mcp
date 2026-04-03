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

This project is covered by Clockify time tracking (project: "<YOUR_PROJECT_NAME>").

At the start of every conversation:
1. Check if any timer is currently running in Clockify (use the `status` tool)
2. If a timer IS running — decide whether the running task fits the current session:
   - If it fits (same topic/area of work) — keep it running, no action needed
   - If it doesn't fit — stop the current timer and start a new one (see below)
3. If NO timer is running — start a new timer immediately (see below)

When starting a new timer:
- Decide on a short, descriptive task name based on what the user is asking to work on
- Use the project name configured above
- Start the timer without asking — just inform the user what you started

Never skip the initial status check.
```

## Tech Stack

Python, FastMCP, httpx — runs via `uv` with no install needed.
