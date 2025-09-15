#!/usr/bin/env python3
"""
Theme Gallery (overlay)

Navigate and preview themes, apply on selection.

Keys:
  Up/Down  - Move selection
  p        - Preview highlighted theme
  Enter    - Apply highlighted theme and exit
  r        - Revert to original theme
  q / ESC  - Quit (revert to original)

Runs inside Kitty as an overlay: mapped to Ctrl+Shift+F6
"""
import curses
import os
import subprocess
from pathlib import Path

HOME = Path.home()
CFG = HOME / ".config" / "kitty"
THEMES = CFG / "themes"
THEME_APPLY = CFG / "kittens" / "theme_apply.py"


def read_current_theme_name() -> str | None:
    cur = THEMES / "current-theme.conf"
    try:
        text = cur.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("include "):
            name = line.split(None, 1)[1].strip()
            # Return only basename
            return Path(name).name
    return None


def list_theme_names() -> list[str]:
    names = []
    if THEMES.exists():
        for p in sorted(THEMES.glob("*.conf")):
            if p.name == "current-theme.conf":
                continue
            names.append(p.name)
    return names


def apply_theme(name: str) -> None:
    # Call the existing safe applier (handles remote reload)
    try:
        subprocess.run([
            "python3",
            os.fspath(THEME_APPLY),
            name,
        ], check=False)
    except Exception:
        pass


def draw(stdscr, themes: list[str], idx: int, original: str | None, status: str = "") -> None:
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "Theme Gallery — Enter: Apply  p: Preview  r: Revert  q: Quit"
    stdscr.addnstr(0, 0, title, w - 1, curses.A_BOLD)
    if original:
        orig = f"Original: {original}"
        stdscr.addnstr(1, 0, orig, w - 1)
    if status:
        stdscr.addnstr(2, 0, status, w - 1, curses.A_DIM)
    start_row = 4
    for i, name in enumerate(themes):
        marker = "➤ " if i == idx else "  "
        attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
        stdscr.addnstr(start_row + i, 0, f"{marker}{name}", w - 1, attr)
    stdscr.refresh()


def run(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    themes = list_theme_names()
    if not themes:
        stdscr.addstr(0, 0, "No themes found in ~/.config/kitty/themes")
        stdscr.getch()
        return

    original = read_current_theme_name()
    try:
        idx = themes.index(original) if original in themes else 0
    except Exception:
        idx = 0

    draw(stdscr, themes, idx, original)

    while True:
        ch = stdscr.getch()
        if ch in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % len(themes)
            draw(stdscr, themes, idx, original)
        elif ch in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % len(themes)
            draw(stdscr, themes, idx, original)
        elif ch in (10, 13, curses.KEY_ENTER):  # Enter
            apply_theme(themes[idx])
            draw(stdscr, themes, idx, original, status=f"Applied: {themes[idx]}")
            break
        elif ch in (ord('p'), ord('P')):
            apply_theme(themes[idx])
            draw(stdscr, themes, idx, original, status=f"Preview: {themes[idx]}")
        elif ch in (ord('r'), ord('R')):
            if original:
                apply_theme(original)
                draw(stdscr, themes, idx, original, status=f"Reverted to: {original}")
        elif ch in (ord('q'), 27):  # q or ESC
            if original:
                apply_theme(original)
            break


def main():
    curses.wrapper(run)


if __name__ == "__main__":
    main()

