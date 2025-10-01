#!/usr/bin/env python3
"""Layout Presets - Quick access to predefined window layouts.

Provides common development layouts like:
- Single: One full window
- VSplit: Two windows side-by-side
- HSplit: Two windows stacked
- Grid: Four windows in 2x2 grid
- Main+Side: Large main window with smaller sidebar
"""
from __future__ import annotations

import curses
from typing import Optional

from kitty.boss import Boss

# Layout definitions
LAYOUTS = {
    "Single": {
        "desc": "One full window",
        "layout": "tall",
        "commands": [],
    },
    "VSplit": {
        "desc": "Two windows side-by-side",
        "layout": "splits",
        "commands": [
            ("launch", "--location=vsplit", "--cwd=current"),
        ],
    },
    "HSplit": {
        "desc": "Two windows stacked",
        "layout": "splits",
        "commands": [
            ("launch", "--location=hsplit", "--cwd=current"),
        ],
    },
    "Grid 2x2": {
        "desc": "Four windows in 2x2 grid",
        "layout": "grid",
        "commands": [
            ("launch", "--cwd=current"),
            ("launch", "--cwd=current"),
            ("launch", "--cwd=current"),
        ],
    },
    "Main+Side": {
        "desc": "Large main window with sidebar",
        "layout": "fat",
        "commands": [
            ("launch", "--location=vsplit", "--cwd=current"),
        ],
    },
    "Triple Column": {
        "desc": "Three columns",
        "layout": "vertical",
        "commands": [
            ("launch", "--location=vsplit", "--cwd=current"),
            ("launch", "--location=vsplit", "--cwd=current"),
        ],
    },
}


def picker_ui(stdscr):
    """Interactive layout picker UI."""
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    layouts = list(LAYOUTS.keys())
    selected_idx = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Header
        stdscr.addnstr(
            0, 0,
            "Layout Presets — Arrow keys: navigate | Enter: apply | Esc/q: cancel",
            w - 1,
            curses.A_BOLD,
        )

        # Layout list
        for idx, name in enumerate(layouts):
            y_pos = 2 + idx * 2
            if y_pos >= h - 1:
                break

            layout_info = LAYOUTS[name]
            desc = layout_info["desc"]

            # Highlight selected
            attr = curses.A_REVERSE if idx == selected_idx else curses.A_NORMAL

            stdscr.addnstr(y_pos, 2, f"{name}", w - 3, attr | curses.A_BOLD)
            stdscr.addnstr(y_pos + 1, 4, desc, w - 5, attr | curses.A_DIM)

        stdscr.refresh()

        # Handle input
        ch = stdscr.getch()

        if ch in (ord("q"), 27):  # q or Esc
            return None
        elif ch in (curses.KEY_ENTER, 10, 13):  # Enter
            return layouts[selected_idx]
        elif ch in (curses.KEY_UP, ord("k")):
            selected_idx = max(0, selected_idx - 1)
        elif ch in (curses.KEY_DOWN, ord("j")):
            selected_idx = min(len(layouts) - 1, selected_idx + 1)
        elif ch in (curses.KEY_HOME,):
            selected_idx = 0
        elif ch in (curses.KEY_END,):
            selected_idx = len(layouts) - 1


def main(args: list[str]) -> str:
    """Entry point - returns selected layout name."""
    try:
        selected = curses.wrapper(picker_ui)
        return selected or ""
    except Exception as e:
        return f"ERROR: {e}"


def handle_result(
    args: list[str], answer: str, target_window_id: int, boss: Boss
) -> None:
    """Apply the selected layout preset."""
    if not answer or answer.startswith("ERROR:"):
        if answer.startswith("ERROR:"):
            print(answer)
        return

    if answer not in LAYOUTS:
        print(f"✗ Unknown layout: {answer}")
        return

    layout_config = LAYOUTS[answer]
    layout_name = layout_config["layout"]
    commands = layout_config["commands"]

    try:
        # First, close all windows except the current one
        active_tab = boss.active_tab
        if active_tab:
            windows = list(active_tab.windows)
            active_window = active_tab.active_window
            for window in windows:
                if window != active_window:
                    boss.close_window(window)

        # Set the layout
        if active_tab:
            active_tab.set_enabled_layouts([layout_name])
            active_tab.goto_layout(layout_name)

        # Execute layout-specific commands
        for cmd_args in commands:
            boss.call_remote_control(None, cmd_args)

        print(f"✓ Applied layout: {answer}")
    except Exception as e:
        print(f"✗ Failed to apply layout: {e}")


if __name__ == "__main__":
    import sys

    # Test standalone
    layout = main(sys.argv[1:])
    if layout:
        print(f"Selected: {layout}")
