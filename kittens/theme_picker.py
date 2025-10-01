#!/usr/bin/env python3
"""Interactive theme picker for Kitty terminal.

Allows browsing and selecting from all available themes with fuzzy search.
"""
from __future__ import annotations

import curses
import os
from pathlib import Path
from typing import Optional

from kitty.boss import Boss

# Paths
HOME = Path.home()
THEMES_DIR = HOME / ".config" / "kitty" / "themes"
CURRENT_THEME_FILE = THEMES_DIR / "current-theme.conf"


def get_themes() -> list[tuple[str, Path]]:
    """Get list of available theme files."""
    if not THEMES_DIR.exists():
        return []

    themes = []
    for theme_file in sorted(THEMES_DIR.glob("*.conf")):
        # Skip meta files
        if theme_file.name in ("current-theme.conf", "default-dark.conf"):
            continue
        themes.append((theme_file.stem, theme_file))

    return themes


def get_current_theme() -> Optional[str]:
    """Read currently active theme name."""
    if not CURRENT_THEME_FILE.exists():
        return None

    try:
        content = CURRENT_THEME_FILE.read_text()
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("include ") and line.endswith(".conf"):
                # Extract theme name from "include themename.conf"
                theme_file = line.split()[1]
                return theme_file.replace(".conf", "")
    except Exception:
        pass

    return None


def match_score(query: str, theme_name: str) -> int:
    """Calculate fuzzy match score for theme name."""
    if not query:
        return 1

    query = query.lower()
    name = theme_name.lower()
    score = 0

    # Exact match
    if query == name:
        return 1000

    # Starts with
    if name.startswith(query):
        return 500

    # Contains whole query
    if query in name:
        score += 100

    # Individual character matches
    for char in query:
        if char in name:
            score += 10

    return score


def picker_ui(stdscr):
    """Main picker UI loop."""
    curses.curs_set(1)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    # Get themes
    all_themes = get_themes()
    if not all_themes:
        stdscr.addstr(0, 0, "No themes found!")
        stdscr.getch()
        return None

    current_theme = get_current_theme()
    query = ""
    selected_idx = 0

    # Find current theme in list
    if current_theme:
        for idx, (name, _) in enumerate(all_themes):
            if name == current_theme:
                selected_idx = idx
                break

    def filtered_themes():
        """Get themes matching query."""
        if not query:
            return all_themes

        scored = [(match_score(query, name), name, path)
                  for name, path in all_themes]
        scored = [(s, n, p) for s, n, p in scored if s > 0]
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [(n, p) for _, n, p in scored]

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Header
        stdscr.addnstr(0, 0, "Theme Picker — type to filter | Enter: apply | Esc/q: cancel",
                      w-1, curses.A_BOLD)

        # Search query
        stdscr.addnstr(1, 0, f"Search> {query}", w-1)

        # Current theme indicator
        if current_theme:
            stdscr.addnstr(2, 0, f"Current: {current_theme}", w-1, curses.A_DIM)

        # Theme list
        themes = filtered_themes()
        if not themes:
            stdscr.addnstr(4, 0, "No matching themes", w-1)
        else:
            # Adjust selected index if needed
            selected_idx = min(selected_idx, len(themes) - 1)
            selected_idx = max(0, selected_idx)

            # Calculate scroll offset
            visible_lines = h - 5
            scroll_offset = 0
            if selected_idx >= visible_lines:
                scroll_offset = selected_idx - visible_lines + 1

            for idx in range(scroll_offset, min(scroll_offset + visible_lines, len(themes))):
                theme_name, _ = themes[idx]
                y_pos = 4 + (idx - scroll_offset)

                if y_pos >= h:
                    break

                # Highlight selected
                attr = curses.A_REVERSE if idx == selected_idx else curses.A_NORMAL

                # Mark current theme
                prefix = "→ " if theme_name == current_theme else "  "

                display_name = f"{prefix}{theme_name}"
                stdscr.addnstr(y_pos, 0, display_name, w-1, attr)

        stdscr.refresh()

        # Handle input
        ch = stdscr.getch()

        if ch in (ord('q'), 27):  # q or Esc
            return None
        elif ch in (curses.KEY_ENTER, 10, 13):  # Enter
            if themes:
                selected_theme, _ = themes[selected_idx]
                return selected_theme
            return None
        elif ch in (curses.KEY_UP, ord('k')):
            selected_idx = max(0, selected_idx - 1)
        elif ch in (curses.KEY_DOWN, ord('j')):
            if themes:
                selected_idx = min(len(themes) - 1, selected_idx + 1)
        elif ch in (curses.KEY_PPAGE,):  # Page Up
            selected_idx = max(0, selected_idx - 10)
        elif ch in (curses.KEY_NPAGE,):  # Page Down
            if themes:
                selected_idx = min(len(themes) - 1, selected_idx + 10)
        elif ch in (curses.KEY_HOME,):
            selected_idx = 0
        elif ch in (curses.KEY_END,):
            if themes:
                selected_idx = len(themes) - 1
        elif ch in (curses.KEY_BACKSPACE, 127):
            query = query[:-1]
            selected_idx = 0
        elif 32 <= ch <= 126:  # Printable characters
            query += chr(ch)
            selected_idx = 0


def main(args: list[str]) -> str:
    """Entry point - returns selected theme name."""
    try:
        selected = curses.wrapper(picker_ui)
        return selected or ""
    except Exception as e:
        return f"ERROR: {e}"


def handle_result(args: list[str], answer: str, target_window_id: int, boss: Boss) -> None:
    """Apply the selected theme."""
    if not answer or answer.startswith("ERROR:"):
        if answer.startswith("ERROR:"):
            print(answer)
        return

    # Write to current-theme.conf
    try:
        CURRENT_THEME_FILE.write_text(f"include {answer}.conf\n")

        # Reload kitty configuration
        boss.call_remote_control(None, ("load-config",))

        print(f"✓ Applied theme: {answer}")
    except Exception as e:
        print(f"✗ Failed to apply theme: {e}")


if __name__ == "__main__":
    import sys
    # Test standalone
    theme = main(sys.argv[1:])
    if theme:
        print(f"Selected: {theme}")
