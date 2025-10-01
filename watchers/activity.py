"""Enhanced activity watcher using official Kitty API.

Provides:
- Automatic tab title updates based on running commands
- Window dimming for unfocused windows
- Auto-save sessions on last window close
"""
from __future__ import annotations

import shlex
import time
from pathlib import Path
from typing import Any, Dict

from kitty.boss import Boss
from kitty.window import Window

# State tracking
_STATE: Dict[int, Dict[str, Any]] = {}
_LAST_FOCUSED_WINDOW: int | None = None


def _short_command(cmdline: str) -> str:
    """Extract short command name from command line."""
    try:
        parts = shlex.split(cmdline)
    except ValueError:
        parts = cmdline.split()
    if not parts:
        return ""
    return Path(parts[0]).name[:32]


def _default_title(window: Window) -> str:
    """Generate default title from window context."""
    cwd = getattr(window, "cwd", None)
    if cwd:
        leaf = Path(cwd).name
        if leaf:
            return leaf
    tab = getattr(window, "tab", None)
    if tab is not None:
        title = getattr(tab, "title", None)
        if title:
            return title
    return "shell"


def on_cmd_startstop(boss: Boss, window: Window, data: Dict[str, Any]) -> None:
    """Handle command start/stop events (shell integration)."""
    if window is None:
        return

    wid = window.id
    entry = _STATE.setdefault(wid, {})
    is_start = bool(data.get("is_start"))

    if is_start:
        entry["started_at"] = time.monotonic()
        tab = getattr(window, "tab", None)
        if tab is not None:
            entry["original_title"] = getattr(tab, "title", None)
        short = _short_command(data.get("cmdline", ""))
        if short:
            try:
                boss.call_remote_control(window, (
                    "set-tab-title",
                    "--match",
                    "recent:0",
                    short,
                ))
            except Exception:
                pass
    else:
        # Command finished - restore original title
        original = entry.get("original_title")
        try:
            boss.call_remote_control(window, (
                "set-tab-title",
                "--match",
                "recent:0",
                original or _default_title(window),
            ))
        except Exception:
            pass
        _STATE.pop(wid, None)


def on_focus_change(boss: Boss, window: Window, data: Dict[str, Any]) -> None:
    """Handle window focus changes - dim unfocused windows."""
    global _LAST_FOCUSED_WINDOW

    if window is None:
        return

    focused = data.get("focused", False)

    if focused:
        # Window gained focus - restore full opacity
        _LAST_FOCUSED_WINDOW = window.id
        # Note: Changing colors dynamically can be jarring, so we keep it subtle
        # Users can uncomment these to enable dimming:
        # try:
        #     boss.call_remote_control(window, ("set-colors", "--reset"))
        # except Exception:
        #     pass
    else:
        # Window lost focus - could dim here
        # try:
        #     boss.call_remote_control(window, ("set-colors", "foreground=#a0a0a0"))
        # except Exception:
        #     pass
        pass


def on_resize(boss: Boss, window: Window, data: Dict[str, Any]) -> None:
    """Handle window resize events with optional dynamic font scaling."""
    if window is None:
        return

    old_geom = data.get("old_geometry")
    new_geom = data.get("new_geometry")

    # Detect first creation (old geometry is all zeros)
    if old_geom and hasattr(old_geom, 'xnum') and old_geom.xnum == 0 and old_geom.ynum == 0:
        # Window just created
        return

    # Dynamic font scaling based on window width
    # Uncomment below to enable automatic scaling
    # try:
    #     if new_geom and hasattr(new_geom, 'xpixel'):
    #         width = new_geom.xpixel
    #         if width > 0:
    #             # Scale font: 13pt for ~1600px, 15pt for ~2000px, 11pt for ~1200px
    #             base_size = 13.0
    #             scale_factor = width / 1600.0
    #             new_size = max(9.0, min(18.0, base_size * scale_factor))
    #             boss.call_remote_control(window, ("set-font-size", f"{new_size:.1f}"))
    # except Exception:
    #     pass


def on_close(boss: Boss, window: Window, data: Dict[str, Any]) -> None:
    """Handle window close - auto-save session if last window."""
    if window is None:
        return

    # Clean up state
    _STATE.pop(window.id, None)

    # Check if this is the last window
    try:
        window_count = len(boss.window_id_map)
        if window_count <= 1:
            # This is the last window - auto-save session
            # Note: This runs in background, won't block closing
            try:
                import subprocess
                session_script = Path.home() / ".config" / "kitty" / "scripts" / "session_snapshot.sh"
                if session_script.exists():
                    subprocess.Popen([str(session_script)],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
            except Exception:
                pass
    except Exception:
        pass


def on_load(boss: Boss, data: Dict[str, Any]) -> None:
    """Initialize watcher on load."""
    # This is called once when the watcher is first loaded
    # Can be used for one-time setup
    pass
