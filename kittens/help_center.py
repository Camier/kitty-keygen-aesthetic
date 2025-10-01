#!/usr/bin/env python3
"""Compact help overlay for Kitty."""

from __future__ import annotations

import curses

HELP_TEXT = """
WINDOW / TAB BASICS
- New tab:             Ctrl+Shift+Enter
- New window:          Ctrl+Shift+N
- Horizontal split:    Ctrl+Shift+Alt+-
- Vertical split:      Ctrl+Shift+Alt+\
- Cycle windows:       Ctrl+Shift+[ / ]
- Cycle tabs:          Ctrl+Shift+Left / Right
- Toggle fullscreen:   Ctrl+Shift+F11
- Toggle maximize:     Ctrl+Shift+F10

NAVIGATION & HISTORY
- Scrollback viewer:   Ctrl+Shift+H
- Scroll to prompt:    Ctrl+Shift+Alt+Z / X
- Command output:      Right click selects entire command, F1 reopens it
- Broadcast input:      Ctrl+Shift+B (match current tab panes)

CONFIG & TOOLING
- Edit config:         Ctrl+Shift+F2
- Reload config:       Ctrl+Shift+F5
- Debug config:        Ctrl+Alt+F11
- Command palette:     Ctrl+Shift+P, C
- Help overlay:        Ctrl+Shift+F9 (this view)

PROFILES & TOGGLES (Ctrl+Shift+P, …)
- B: Battery saver        - writes local/battery.conf
- F: Font autoscale       - writes local/font-scale.conf
- T: Toggle tmux prefix   - writes local/tmux-prefix.conf
- W: Watch & auto reload  - toggles watch-reload.sh
- U: Transfer (download)  - `kitty @ remote-transfer` via helper
- Y: Transfer (upload)    - `kitty @ remote-transfer --direction=upload`
- M: Status panel         - htop panel via kitty +kitten panel
- H: SSH host picker      - wrapper around kitten ssh

SCRIPTS & PATHS
- Config root:        ~/.config/kitty
- Includes:           ~/.config/kitty/includes/*.conf
- Scripts:            ~/.config/kitty/scripts/
- Sessions:           ~/.config/kitty/sessions/
- Local overrides:    ~/.config/kitty/local/

TROUBLESHOOTING
- Minimal config:     kitty --config ~/.config/kitty/kitty-minimal.conf
- GPU-safe launcher:  ~/.config/kitty/run-kitty-safe.sh
- RC socket issues:   ensure ui.conf exports KITTY_LISTEN_ON
- File watch:         scripts/watch-reload.sh (requires inotifywait)
"""


def viewer(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    lines = HELP_TEXT.strip("\n").splitlines()
    top = 0
    cur = 0
    search = ""
    matches = []

    def redraw() -> None:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addnstr(0, 0, "Kitty Help — arrows to scroll | / to search | q to close", w-1, curses.A_BOLD)
        for idx in range(1, h):
            line_idx = top + idx - 1
            if line_idx >= len(lines):
                break
            attr = curses.A_REVERSE if line_idx == cur else curses.A_NORMAL
            stdscr.addnstr(idx, 0, lines[line_idx], w-1, attr)
        stdscr.refresh()

    redraw()

    while True:
        ch = stdscr.getch()
        if ch in (ord('q'), 27):
            return
        elif ch in (curses.KEY_DOWN, ord('j')):
            cur = min(len(lines) - 1, cur + 1)
        elif ch in (curses.KEY_UP, ord('k')):
            cur = max(0, cur - 1)
        elif ch in (curses.KEY_NPAGE, ord(' ')):
            cur = min(len(lines) - 1, cur + 10)
        elif ch in (curses.KEY_PPAGE, ord('b')):
            cur = max(0, cur - 10)
        elif ch == ord('/'):
            curses.echo()
            stdscr.addstr(curses.LINES - 1, 0, "/")
            query = stdscr.getstr().decode()
            curses.noecho()
            if query:
                matches[:] = [i for i, line in enumerate(lines) if query.lower() in line.lower()]
                if matches:
                    cur = matches[0]
        if cur < top:
            top = cur
        elif cur >= top + curses.LINES - 1:
            top = cur - curses.LINES + 2
        redraw()


def main():
    curses.wrapper(viewer)


if __name__ == "__main__":
    main()
