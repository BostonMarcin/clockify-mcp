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

## Tech Stack

Python, FastMCP, httpx — runs via `uv` with no install needed.
