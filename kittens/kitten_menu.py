#!/usr/bin/env python3
"""
Kitten Menu (overlay)

A simple command palette to launch common local kittens and effects.

Keys:
- Up/Down or j/k: Move selection
- Enter: Launch selected item
- q or ESC: Quit
"""
from __future__ import annotations

import os
import curses
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

HOME = Path.home()
CFG = HOME / ".config" / "kitty"
KITTENS = CFG / "kittens"


@dataclass
class MenuItem:
    title: str
    desc: str
    launch_type: str  # overlay|tab|window
    cmd: List[str]

    def available(self) -> bool:
        return True


def script_path(name: str) -> str:
    return os.fspath(KITTENS / name)


def build_items() -> List[MenuItem]:
    items: List[MenuItem] = []

    def add_if_exists(title: str, desc: str, launch_type: str, script: str, args: List[str] | None = None):
        p = KITTENS / script
        if p.exists():
            items.append(MenuItem(
                title,
                desc,
                launch_type,
                ["python3", os.fspath(p)] + (args or []),
            ))

    # Visual galleries
    add_if_exists("Theme Gallery", "Browse, preview, apply themes", "overlay", "theme_gallery.py")
    add_if_exists("Background Gallery", "Pick background image from ~/Pictures", "overlay", "background_gallery.py")
    add_if_exists("Help Center", "Searchable, scrollable help", "overlay", "help_center.py")

    # Effects
    add_if_exists("Plasma", "Plasma effect (tab)", "tab", "plasma.py", ["180"])  # shorter default
    add_if_exists("Fire", "Fire effect (tab)", "tab", "fire.py", ["20"])  # gentle default
    add_if_exists("Sine Scroller", "Sine-wave text scroller (tab)", "tab", "sine_scroller.py")
    add_if_exists("ANSI Gallery", "ANSI/NFO art viewer (tab)", "tab", "ansiview.py")
    add_if_exists("Random Art", "Show random ANSI/ASCII art (overlay)", "overlay", "random_art.py")
    add_if_exists("Tracker Player", "Play tracker modules (tab)", "tab", "tracker_play.py")
    add_if_exists("Theme Cycle", "Cycle themes every few seconds (window)", "window", "theme_cycle.py")

    return items


def launch(item: MenuItem):
    args = [
        "kitty", "@", "launch",
        f"--type={item.launch_type}",
        f"--title={item.title}",
    ] + item.cmd
    try:
        subprocess.run(args, check=False)
    except Exception:
        pass


def draw(stdscr, items: List[MenuItem], idx: int, status: str = "") -> None:
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "Kitten Menu — Enter: Launch  q: Quit"
    stdscr.addnstr(0, 0, title, w - 1, curses.A_BOLD)
    if status:
        stdscr.addnstr(1, 0, status, w - 1, curses.A_DIM)
    start = 3
    for i, it in enumerate(items):
        marker = "➤ " if i == idx else "  "
        attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
        stdscr.addnstr(start + i * 2, 0, f"{marker}{it.title}", w - 1, attr)
        stdscr.addnstr(start + i * 2 + 1, 2, it.desc, w - 3, curses.A_DIM)
    stdscr.refresh()


def run(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    items = build_items()
    if not items:
        stdscr.addstr(0, 0, "No local kittens found. Add scripts to ~/.config/kitty/kittens/")
        stdscr.getch()
        return

    idx = 0
    draw(stdscr, items, idx)
    while True:
        ch = stdscr.getch()
        if ch in (ord('q'), 27):
            break
        elif ch in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % len(items)
            draw(stdscr, items, idx)
        elif ch in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % len(items)
            draw(stdscr, items, idx)
        elif ch in (10, 13, curses.KEY_ENTER):
            launch(items[idx])
            break


def main():
    curses.wrapper(run)


if __name__ == "__main__":
    main()

