#!/usr/bin/env python3
"""
Command Palette (overlay)

Fuzzy-find and launch common actions: windows/tabs/splits, themes,
backgrounds, modes, sessions, effects, and utilities.

Type to filter. Enter to execute. ESC/q to quit.
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


def apply_theme(name: str) -> None:
    # Use existing safe applier
    subprocess.run(["python3", os.fspath(CFG / "kittens" / "theme_apply.py"), name], check=False)


def set_opacity(delta: float | None = None, absolute: float | None = None) -> None:
    if absolute is not None:
        rc("set-background-opacity", str(absolute))
    elif delta is not None:
        rc("set-background-opacity", "+" + str(delta))


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
    A(Action("HSplit", "Horizontal split", lambda: rc("launch", "--location=hsplit")))
    A(Action("VSplit", "Vertical split", lambda: rc("launch", "--location=vsplit")))
    A(Action("Toggle Fullscreen", "Fullscreen current window", lambda: rc("toggle-fullscreen")))
    A(Action("Toggle Maximized", "Maximize current window", lambda: rc("toggle-maximized")))
    A(Action("Clear Terminal", "Reset active terminal", lambda: rc("send-text", "reset\r")))

    # Config
    A(Action("Edit Config", "Open kitty.conf in $EDITOR", lambda: launch("overlay", "Edit Config", "sh", "-lc", f"${{EDITOR:-nvim}} {os.fspath(CFG/'kitty.conf')}")))
    A(Action("Reload Config", "Reload configuration", lambda: rc("load-config")))
    A(Action("Debug Config", "Open debug view", lambda: rc("debug-config")))

    # Galleries / Menus
    A(Action("Theme Gallery", "Browse, preview, apply themes", lambda: launch("overlay", "Themes", "python3", os.fspath(CFG/"kittens"/"theme_gallery.py"))))
    A(Action("Background Gallery", "Browse/preview/apply backgrounds", lambda: launch("overlay", "Backgrounds", "python3", os.fspath(CFG/"kittens"/"background_gallery.py"))))
    A(Action("Kitten Menu", "Menu of local kittens", lambda: launch("overlay", "Kittens", "python3", os.fspath(CFG/"kittens"/"kitten_menu.py"))))
    A(Action("Help Center", "Searchable help", lambda: launch("overlay", "Help", "python3", os.fspath(CFG/"kittens"/"help_center.py"))))

    # Themes
    for theme in ("fairlight_cyan.conf", "skidrow_green.conf", "reloaded_magenta.conf", "razor_amber.conf", "default-dark.conf", "neon_nights.conf"):
        A(Action(f"Theme: {theme.replace('.conf','').replace('_',' ').title()}", "Apply theme", lambda t=theme: apply_theme(t)))

    # Background
    A(Action("Clear Background", "Remove background image", lambda: rc("set-background-image", "--all", "none")))

    # Effects
    A(Action("Plasma", "Plasma effect (tab)", lambda: launch("tab", "Plasma", "python3", os.fspath(CFG/"kittens"/"plasma.py"), "120")))
    A(Action("Fire", "Fire effect (tab)", lambda: launch("tab", "Fire", "python3", os.fspath(CFG/"kittens"/"fire.py"), "20")))
    A(Action("Scroller", "Sine scroller (tab)", lambda: launch("tab", "Scroller", "python3", os.fspath(CFG/"kittens"/"sine_scroller.py"))))
    A(Action("ANSI Gallery", "ANSI/NFO viewer (tab)", lambda: launch("tab", "ANSI", "python3", os.fspath(CFG/"kittens"/"ansiview.py"))))
    A(Action("Tracker Player", "Play tracker modules (tab)", lambda: launch("tab", "Tracker", "python3", os.fspath(CFG/"kittens"/"tracker_play.py"))))

    # Sessions / Modes
    A(Action("Session: Default", "Open default session", lambda: rc("launch", "--type=os-window", "kitty", "--session", os.fspath(CFG/"sessions"/"default.session"))))
    A(Action("Session: Dev", "Open dev session", lambda: rc("launch", "--type=os-window", "kitty", "--session", os.fspath(CFG/"sessions"/"dev.session"))))
    A(Action("Session: Keygen", "Open keygen session", lambda: rc("launch", "--type=os-window", "kitty", "--session", os.fspath(CFG/"sessions"/"keygen.session"))))
    A(Action("Mode: Work", "Open Work mode", lambda: rc("launch", "--type=os-window", "kitty", "--config", os.fspath(CFG/"modes"/"work.conf"))))
    A(Action("Mode: Demo", "Open Demo mode", lambda: rc("launch", "--type=os-window", "kitty", "--config", os.fspath(CFG/"modes"/"demo.conf"))))
    A(Action("Mode: Keygen", "Open Keygen mode", lambda: rc("launch", "--type=os-window", "kitty", "--config", os.fspath(CFG/"modes"/"keygen.conf"))))

    # Opacity
    A(Action("Opacity +0.1", "Increase background opacity", lambda: set_opacity(delta=0.1)))
    A(Action("Opacity -0.1", "Decrease background opacity", lambda: set_opacity(delta=-0.1)))
    A(Action("Opacity 1.0", "Set background opacity to 1", lambda: set_opacity(absolute=1.0)))

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
        start = 3
        for i, it in enumerate(items[: h - start - 1]):
            marker = "➤ " if i == sel else "  "
            attr = curses.A_REVERSE if i == sel else curses.A_NORMAL
            stdscr.addnstr(start + i*2, 0, f"{marker}{it.label}", w-1, attr)
            stdscr.addnstr(start + i*2 + 1, 2, it.desc, w-3, curses.A_DIM)
        stdscr.refresh()

    redraw()
    while True:
        ch = stdscr.getch()
        if ch in (27, ord('q')):
            break
        elif ch in (curses.KEY_UP, ord('k')):
            sel = max(0, sel - 1)
            redraw()
        elif ch in (curses.KEY_DOWN, ord('j')):
            sel = min(max(0, len(items)-1), sel + 1)
            redraw()
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if query:
                query = query[:-1]
                sel = 0
                redraw()
        elif ch in (10, 13, curses.KEY_ENTER):
            if items:
                items[sel].run()
            break
        elif 32 <= ch < 127:
            query += chr(ch)
            sel = 0
            redraw()


def main():
    curses.wrapper(palette)


if __name__ == "__main__":
    main()

