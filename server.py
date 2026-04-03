"""Clockify MCP server — start/stop time tracking from Claude."""

import os
from datetime import datetime, timezone

import httpx
from fastmcp import FastMCP

API_KEY = os.environ.get("CLOCKIFY_API_KEY", "")
BASE_URL = "https://api.clockify.me/api/v1"

mcp = FastMCP("clockify")

# --- HTTP helpers ---


def _headers() -> dict[str, str]:
    return {"X-Api-Key": API_KEY, "Content-Type": "application/json"}


async def _get(path: str, params: dict | None = None) -> dict | list:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}{path}", headers=_headers(), params=params)
        resp.raise_for_status()
        return resp.json()


async def _post(path: str, body: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BASE_URL}{path}", headers=_headers(), json=body)
        resp.raise_for_status()
        return resp.json()


async def _patch(path: str, body: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.patch(f"{BASE_URL}{path}", headers=_headers(), json=body)
        resp.raise_for_status()
        return resp.json()


# --- Resolve helpers ---


async def _get_workspace_id() -> str:
    workspaces = await _get("/workspaces")
    if not workspaces:
        raise Exception("No workspaces found in your Clockify account.")
    return workspaces[0]["id"]


async def _get_user_id() -> str:
    user = await _get("/user")
    return user["id"]


async def _find_project(workspace_id: str, project_name: str) -> dict | None:
    projects = await _get(f"/workspaces/{workspace_id}/projects", params={"name": project_name})
    for p in projects:
        if p["name"].lower() == project_name.lower():
            return p
    return None


async def _find_task(workspace_id: str, project_id: str, task_name: str) -> dict | None:
    tasks = await _get(f"/workspaces/{workspace_id}/projects/{project_id}/tasks", params={"name": task_name})
    for t in tasks:
        if t["name"].lower() == task_name.lower():
            return t
    return None


async def _create_task(workspace_id: str, project_id: str, task_name: str) -> dict:
    return await _post(
        f"/workspaces/{workspace_id}/projects/{project_id}/tasks",
        {"name": task_name},
    )


async def _get_running_entry(workspace_id: str, user_id: str) -> dict | None:
    entries = await _get(
        f"/workspaces/{workspace_id}/user/{user_id}/time-entries",
        params={"in-progress": "true"},
    )
    if entries:
        return entries[0]
    return None


async def _stop_entry(workspace_id: str, user_id: str) -> dict:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return await _patch(
        f"/workspaces/{workspace_id}/user/{user_id}/time-entries",
        {"end": now},
    )


# --- Tools ---


@mcp.tool()
async def start_timer(project_name: str, task_name: str) -> str:
    """Start tracking time on a task. If a timer is already running, it will be stopped first.
    If the task doesn't exist under the project, it will be created automatically.

    Args:
        project_name: Name of the Clockify project
        task_name: Name of the task to track time on
    """
    workspace_id = await _get_workspace_id()
    user_id = await _get_user_id()

    # Stop any running timer first
    running = await _get_running_entry(workspace_id, user_id)
    stopped_msg = ""
    if running:
        await _stop_entry(workspace_id, user_id)
        stopped_msg = f"Stopped previous timer (was tracking: {running.get('description', 'unnamed')}). "

    # Find project
    project = await _find_project(workspace_id, project_name)
    if not project:
        raise Exception(
            f"Project '{project_name}' not found. Available projects can be listed with list_projects."
        )

    # Find or create task
    task = await _find_task(workspace_id, project["id"], task_name)
    created_msg = ""
    if not task:
        task = await _create_task(workspace_id, project["id"], task_name)
        created_msg = f"Created new task '{task_name}'. "

    # Start timer
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    await _post(
        f"/workspaces/{workspace_id}/time-entries",
        {
            "start": now,
            "projectId": project["id"],
            "taskId": task["id"],
            "description": task_name,
        },
    )

    return f"{stopped_msg}{created_msg}Timer started on '{task_name}' in project '{project_name}'."


@mcp.tool()
async def stop_timer() -> str:
    """Stop the currently running timer."""
    workspace_id = await _get_workspace_id()
    user_id = await _get_user_id()

    running = await _get_running_entry(workspace_id, user_id)
    if not running:
        return "No timer is currently running."

    await _stop_entry(workspace_id, user_id)

    description = running.get("description", "unnamed")
    start = running.get("timeInterval", {}).get("start", "?")
    return f"Timer stopped. Was tracking: '{description}' (started at {start})."


@mcp.tool()
async def list_projects() -> str:
    """List all available Clockify projects."""
    workspace_id = await _get_workspace_id()
    projects = await _get(f"/workspaces/{workspace_id}/projects")
    if not projects:
        return "No projects found."
    lines = [f"- {p['name']}" for p in projects]
    return "Projects:\n" + "\n".join(lines)


@mcp.tool()
async def status() -> str:
    """Check if a timer is currently running and show its details."""
    workspace_id = await _get_workspace_id()
    user_id = await _get_user_id()

    running = await _get_running_entry(workspace_id, user_id)
    if not running:
        return "No timer is currently running."

    description = running.get("description", "unnamed")
    start = running.get("timeInterval", {}).get("start", "?")
    project_id = running.get("projectId", "")

    project_name = "unknown"
    if project_id:
        try:
            project = await _get(f"/workspaces/{workspace_id}/projects/{project_id}")
            project_name = project.get("name", "unknown")
        except Exception:
            pass

    return f"Timer running: '{description}' in project '{project_name}' (started at {start})."
