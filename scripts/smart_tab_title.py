#!/usr/bin/env python3
"""Derive an informative tab title based on the focused window."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Iterable, Optional

DEFAULT_SOCKET = f"unix:{Path.home()}/.cache/kitty/kitty-{os.environ.get('USER', '')}.sock"
SOCKET = os.environ.get("KITTY_LISTEN_ON", DEFAULT_SOCKET)
SHELLS = {"bash", "zsh", "fish", "sh", "nu", "dash"}
EDITOR_LAUNCHERS = {"nvim", "vim", "nano", "emacs", "hx", "code"}


def kitty_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    base = ["kitty", "@", "--to", SOCKET]
    return subprocess.run(base + list(args), check=False, capture_output=True, text=True)


def load_ls() -> Optional[dict]:
    result = kitty_cmd("ls")
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def first(seq: Iterable, predicate) -> Optional:
    for item in seq:
        if predicate(item):
            return item
    return None


def describe_command(cmdline: list[str], cwd: Path) -> Optional[str]:
    if not cmdline:
        return None
    exe = Path(cmdline[0]).name
    # Editors -- show filename when possible
    if exe in EDITOR_LAUNCHERS:
        path = next((arg for arg in reversed(cmdline[1:]) if not arg.startswith("-")), None)
        if path:
            return f"{exe} {Path(path).name}"
        return exe
    # SSH targets
    if exe in {"ssh", "mosh"}:
        host = next((arg for arg in cmdline[1:] if not arg.startswith("-")), None)
        if host:
            return f"ssh {host}"
        return exe
    if exe in SHELLS:
        return None
    return exe


def detect_project_type(cwd: Path) -> Optional[str]:
    """Detect project type based on marker files."""
    markers = {
        "pyproject.toml": "🐍",
        "setup.py": "🐍",
        "requirements.txt": "🐍",
        "Pipfile": "🐍",
        "package.json": "⬢",
        "Cargo.toml": "🦀",
        "go.mod": "🐹",
        "Makefile": "🔨",
        "CMakeLists.txt": "⚙️",
        "docker-compose.yml": "🐳",
        "Dockerfile": "🐳",
    }
    for marker, icon in markers.items():
        if (cwd / marker).exists():
            return icon
    return None


def git_context(cwd: Path) -> Optional[str]:
    try:
        toplevel = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    repo = Path(toplevel).name
    project_icon = detect_project_type(Path(toplevel))
    prefix = f"{project_icon} " if project_icon else ""
    if branch == "HEAD":
        return f"{prefix}{repo}"
    return f"{prefix}{repo}:{branch}"


def fallback_title(cwd: Path) -> str:
    git = git_context(cwd)
    if git:
        return git
    if cwd == Path.home():
        return "home"
    # Try to detect project type for non-git directories
    project_icon = detect_project_type(cwd)
    if project_icon:
        return f"{project_icon} {cwd.name}"
    return cwd.name or str(cwd)


def main() -> None:
    data = load_ls()
    if not data:
        return
    os_window = first(data.get("os_windows", []), lambda w: w.get("is_focused"))
    if not os_window:
        return
    tab = first(os_window.get("tabs", []), lambda t: t.get("is_focused"))
    if not tab:
        return
    window = first(tab.get("windows", []), lambda w: w.get("is_focused"))
    if not window:
        return

    cwd_str = window.get("cwd") or window.get("child", {}).get("cwd")
    cwd = Path(cwd_str) if cwd_str else Path.cwd()
    child = window.get("cmdline") or window.get("child", {}).get("cmdline") or []

    current_title = tab.get('title') or ''
    title = describe_command(child, cwd) or fallback_title(cwd)
    title = title.strip()
    if len(title) > 42:
        title = title[:41] + "…"
    # Only set if changed to avoid needless events
    if title != current_title:
        kitty_cmd("set-tab-title", "--match", f"id:{tab['id']}", title)


if __name__ == "__main__":
    main()
