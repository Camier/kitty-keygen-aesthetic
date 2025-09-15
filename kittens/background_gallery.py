#!/usr/bin/env python3
"""
Background Gallery (overlay)

Pick, preview, and apply a background image for kitty.

Sources:
- ~/Pictures (recursive, common image formats)

Keys:
- Up/Down or j/k  : Move selection
- p               : Preview highlighted image
- Enter           : Apply highlighted image and exit
- r               : Revert to original background
- n               : Clear background (none)
- q or ESC        : Quit (revert to original)
"""
from __future__ import annotations

import curses
import os
import subprocess
from pathlib import Path
from typing import List

HOME = Path.home()
CFG = HOME / ".config" / "kitty"
GEN = CFG / "generated"
BG_CONF = GEN / "background.conf"

IMG_DIRS = [HOME / "Pictures"]
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".tif"}


def read_current_background() -> str | None:
    try:
        text = BG_CONF.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("background_image "):
            return line.split(None, 1)[1]
    return None


def persist_background(path: str | None) -> None:
    GEN.mkdir(parents=True, exist_ok=True)
    if path is None:
        # Clear file to remove any persisted image
        if BG_CONF.exists():
            BG_CONF.unlink(missing_ok=True)
        return
    BG_CONF.write_text(f"background_image {path}\n", encoding="utf-8")


def rc_set_background(path: str | None) -> None:
    cmd = ["kitty", "@", "set-background-image"]
    if path is None:
        cmd.append("none")
    else:
        cmd.append(path)
    # Apply to all windows to keep experience consistent
    cmd.insert(2, "--all")
    try:
        subprocess.run(cmd, check=False)
    except Exception:
        pass


def collect_images() -> List[Path]:
    images: List[Path] = []
    for base in IMG_DIRS:
        if not base.exists():
            continue
        # Recursive scan with a reasonable cap
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in IMG_EXTS:
                images.append(p)
                if len(images) >= 500:
                    break
    images.sort(key=lambda p: (p.parent.as_posix(), p.name.lower()))
    return images


def draw(stdscr, items: List[str], idx: int, original: str | None, status: str = "") -> None:
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "Background Gallery — Enter: Apply  p: Preview  r: Revert  n: None  q: Quit"
    stdscr.addnstr(0, 0, title, w - 1, curses.A_BOLD)
    orig = f"Original: {original or 'None'}"
    stdscr.addnstr(1, 0, orig, w - 1)
    if status:
        stdscr.addnstr(2, 0, status, w - 1, curses.A_DIM)
    start_row = 4
    for i, name in enumerate(items):
        marker = "➤ " if i == idx else "  "
        attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
        stdscr.addnstr(start_row + i, 0, f"{marker}{name}", w - 1, attr)
    stdscr.refresh()


def run(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    images = collect_images()
    items = ["<None>"] + [os.fspath(p) for p in images]
    original = read_current_background()

    # Determine initial index
    if original is None:
        idx = 0
    else:
        try:
            idx = items.index(original)
        except ValueError:
            idx = 0

    draw(stdscr, items, idx, original)

    while True:
        ch = stdscr.getch()
        if ch in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % len(items)
            draw(stdscr, items, idx, original)
        elif ch in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % len(items)
            draw(stdscr, items, idx, original)
        elif ch in (ord('p'), ord('P')):
            sel = None if idx == 0 else items[idx]
            rc_set_background(sel)
            draw(stdscr, items, idx, original, status=f"Preview: {sel or 'None'}")
        elif ch in (10, 13, curses.KEY_ENTER):
            sel = None if idx == 0 else items[idx]
            rc_set_background(sel)
            persist_background(sel)
            draw(stdscr, items, idx, original, status=f"Applied: {sel or 'None'}")
            break
        elif ch in (ord('r'), ord('R')):
            rc_set_background(original)
            persist_background(original)
            draw(stdscr, items, idx, original, status=f"Reverted to: {original or 'None'}")
        elif ch in (ord('n'), ord('N')):
            rc_set_background(None)
            persist_background(None)
            draw(stdscr, items, idx, original, status="Cleared background")
        elif ch in (ord('q'), 27):
            # Revert and exit
            rc_set_background(original)
            break


def main():
    curses.wrapper(run)


if __name__ == "__main__":
    main()

