#!/usr/bin/env python3
"""Minimal command palette for Kitty.

Provides quick access to common window/tab actions and config utilities.
"""
from __future__ import annotations

import curses
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

HOME = Path.home()
CFG = HOME / ".config" / "kitty"


def rc(*args: str) -> None:
    try:
        subprocess.run(["kitty", "@", *args], check=False)
    except Exception:
        pass


def launch(typ: str, title: str, *cmd: str) -> None:
    rc("launch", f"--type={typ}", f"--title={title}", *cmd)


@dataclass
class Action:
    label: str
    desc: str
    run: Callable[[], None]


def build_actions() -> List[Action]:
    actions: List[Action] = []
    A = actions.append

    # Windows/Tabs
    A(Action("New Tab", "Open a new tab in CWD", lambda: rc("launch", "--type=tab")))
    A(Action("New Window", "Open a new window in CWD", lambda: rc("launch", "--type=window")))
    A(Action("New OS Window", "Open a new OS window", lambda: rc("launch", "--type=os-window")))
    A(Action("Horizontal Split", "Split window horizontally", lambda: rc("launch", "--location=hsplit")))
    A(Action("Vertical Split", "Split window vertically", lambda: rc("launch", "--location=vsplit")))
    A(Action("Toggle Fullscreen", "Fullscreen the current window", lambda: rc("toggle-fullscreen")))
    A(Action("Toggle Maximized", "Maximize the current window", lambda: rc("toggle-maximized")))
    A(Action("Clear Terminal", "Reset the active terminal", lambda: rc("send-text", "reset\n")))

    # Config helpers
    A(Action("Edit Config", "Open kitty.conf in $EDITOR", lambda: launch(
        "overlay", "Edit Config", "sh", "-lc", f"${{EDITOR:-nvim}} {os.fspath(CFG/'kitty.conf')}"
    )))
    A(Action("Reload Config", "Reload configuration", lambda: rc("load-config")))
    A(Action("Debug Config", "Open debug view", lambda: rc("debug-config")))
    A(Action("Help Center", "Searchable help", lambda: launch(
        "overlay", "Help", "python3", os.fspath(CFG/"kittens"/"help_center.py")
    )))

    return actions


def match_score(q: str, label: str, desc: str) -> int:
    q = q.lower().strip()
    if not q:
        return 1
    s = 0
    target = f"{label} {desc}".lower()
    for part in q.split():
        if part in target:
            s += 2
        for token in label.lower().split():
            if token.startswith(part):
                s += 3
    return s


def palette(stdscr):
    curses.curs_set(1)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    actions = build_actions()
    query = ""
    sel = 0

    def current_list():
        scored = [(
            match_score(query, a.label, a.desc), a
        ) for a in actions]
        scored.sort(key=lambda t: (-t[0], t[1].label))
        return [a for sc, a in scored if sc > 0]

    items = current_list()

    def redraw():
        nonlocal items
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addnstr(0, 0, "Command Palette — type to filter | Enter: run | q: quit", w-1, curses.A_BOLD)
        stdscr.addnstr(1, 0, "> " + query, w-1)

        items = current_list()
        for idx, action in enumerate(items[: h - 3]):
            attr = curses.A_REVERSE if idx == sel else curses.A_NORMAL
            stdscr.addnstr(3 + idx, 0, action.label, w-1, attr)
            stdscr.addnstr(3 + idx, min(30, w - 1), " — " + action.desc, w-1, attr)
        stdscr.refresh()

    redraw()

    while True:
        ch = stdscr.getch()
        if ch in (ord('q'), 27):
            return
        elif ch in (curses.KEY_ENTER, 10, 13):
            if items:
                items[sel].run()
            return
        elif ch in (curses.KEY_UP,):
            sel = max(0, sel - 1)
        elif ch in (curses.KEY_DOWN,):
            sel = min(max(0, len(items) - 1), sel + 1)
        elif ch in (curses.KEY_BACKSPACE, 127):
            query = query[:-1]
            sel = 0
        elif ch >= 32 and ch <= 126:
            query += chr(ch)
            sel = 0
        redraw()


def main():
    curses.wrapper(palette)


if __name__ == "__main__":
    main()
