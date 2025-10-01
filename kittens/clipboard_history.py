#!/usr/bin/env python3
"""Clipboard History - Browse and paste from clipboard history.

Integrates with system clipboard managers:
- clipman (Wayland)
- clipster (X11)
- copyq (Cross-platform)

Falls back to kitty's built-in clipboard if no manager is detected.
"""
from __future__ import annotations

import curses
import subprocess
from typing import List, Optional, Tuple


def get_clipman_history() -> Optional[List[str]]:
    """Get clipboard history from clipman (Wayland)."""
    try:
        result = subprocess.run(
            ["clipman", "show-history"],
            capture_output=True,
            text=True,
            check=True,
        )
        items = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return items if items else None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def get_copyq_history() -> Optional[List[str]]:
    """Get clipboard history from CopyQ."""
    try:
        result = subprocess.run(
            ["copyq", "eval", "for(i=0;i<20;i++)print(str(read(i))+'\\n---\\n')"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2,
        )
        items = [
            item.strip()
            for item in result.stdout.split("---")
            if item.strip()
        ]
        return items if items else None
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def get_clipster_history() -> Optional[List[str]]:
    """Get clipboard history from clipster (X11)."""
    try:
        result = subprocess.run(
            ["clipster", "-o", "-n", "20"],
            capture_output=True,
            text=True,
            check=True,
        )
        items = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return items if items else None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def get_clipboard_history() -> Tuple[List[str], str]:
    """Get clipboard history from available manager."""
    # Try different clipboard managers
    history = get_clipman_history()
    if history:
        return history, "clipman"

    history = get_copyq_history()
    if history:
        return history, "copyq"

    history = get_clipster_history()
    if history:
        return history, "clipster"

    # Fallback: just return current clipboard
    try:
        result = subprocess.run(
            ["kitty", "@", "get-text", "clipboard"],
            capture_output=True,
            text=True,
            check=True,
        )
        current = result.stdout.strip()
        return [current] if current else ["(empty)"], "kitty"
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ["(no clipboard access)"], "none"


def set_clipboard(text: str) -> None:
    """Set clipboard content."""
    try:
        subprocess.run(
            ["kitty", "@", "set-clipboard", text],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass


def truncate_display(text: str, max_len: int = 80) -> str:
    """Truncate text for display, replacing newlines."""
    text = text.replace("\n", " ⏎ ").replace("\r", "")
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text


def picker_ui(stdscr, items: List[str], manager: str):
    """Interactive clipboard history picker."""
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    selected_idx = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Header
        title = f"Clipboard History ({manager}) — Arrow keys: navigate | Enter: paste | Esc/q: cancel"
        stdscr.addnstr(0, 0, title, w - 1, curses.A_BOLD)

        # Item list
        visible_lines = h - 3
        scroll_offset = max(0, selected_idx - visible_lines + 1)

        for idx in range(scroll_offset, min(scroll_offset + visible_lines, len(items))):
            y_pos = 2 + (idx - scroll_offset)
            if y_pos >= h:
                break

            item = items[idx]
            display = truncate_display(item, w - 5)

            # Highlight selected
            attr = curses.A_REVERSE if idx == selected_idx else curses.A_NORMAL

            # Number prefix
            prefix = f"{idx + 1}. "
            stdscr.addnstr(y_pos, 2, prefix, w - 3, attr)
            stdscr.addnstr(y_pos, 2 + len(prefix), display, w - 3 - len(prefix), attr)

        stdscr.refresh()

        # Handle input
        ch = stdscr.getch()

        if ch in (ord("q"), 27):  # q or Esc
            return None
        elif ch in (curses.KEY_ENTER, 10, 13):  # Enter
            return items[selected_idx]
        elif ch in (curses.KEY_UP, ord("k")):
            selected_idx = max(0, selected_idx - 1)
        elif ch in (curses.KEY_DOWN, ord("j")):
            selected_idx = min(len(items) - 1, selected_idx + 1)
        elif ch in (curses.KEY_PPAGE,):  # Page Up
            selected_idx = max(0, selected_idx - 10)
        elif ch in (curses.KEY_NPAGE,):  # Page Down
            selected_idx = min(len(items) - 1, selected_idx + 10)
        elif ch in (curses.KEY_HOME,):
            selected_idx = 0
        elif ch in (curses.KEY_END,):
            selected_idx = len(items) - 1
        elif ord("1") <= ch <= ord("9"):  # Number shortcuts
            num = ch - ord("1")
            if num < len(items):
                return items[num]


def main(args: list[str]) -> str:
    """Entry point - returns selected clipboard item."""
    items, manager = get_clipboard_history()

    if not items:
        return "ERROR: No clipboard history available"

    try:
        selected = curses.wrapper(picker_ui, items, manager)
        return selected or ""
    except Exception as e:
        return f"ERROR: {e}"


def handle_result(args: list[str], answer: str, target_window_id: int, boss) -> None:
    """Paste the selected clipboard item."""
    if not answer or answer.startswith("ERROR:"):
        if answer.startswith("ERROR:"):
            print(answer)
        return

    # Set clipboard and paste
    set_clipboard(answer)

    # Send paste command
    try:
        boss.call_remote_control(None, ("paste-from-clipboard",))
        print(f"✓ Pasted {len(answer)} characters")
    except Exception as e:
        print(f"✗ Failed to paste: {e}")


if __name__ == "__main__":
    import sys

    # Test standalone
    item = main(sys.argv[1:])
    if item and not item.startswith("ERROR:"):
        print(f"Selected: {truncate_display(item, 60)}")
    elif item:
        print(item)
