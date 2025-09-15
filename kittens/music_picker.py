#!/usr/bin/env python3
"""
Music Picker (overlay)

Browse and launch tracker modules from ~/.config/kitty/music.

Keys:
- Up/Down or j/k : Move selection
- Enter          : Play highlighted track in a new tab
- n / p          : Next / Previous track (uses playlist state)
- s              : Toggle shuffle
- r              : Rebuild playlist from folder
- q / ESC        : Quit

Launches playback via kitty remote control into a new tab using
the existing tracker_play.py for consistent player selection.
Falls back to spawning the player directly if RC is unavailable.
"""
from __future__ import annotations

import curses
import os
import subprocess
from pathlib import Path

HOME = Path.home()
CFG = HOME / ".config" / "kitty"
MUSIC = CFG / "music"
TRACKER = CFG / "kittens" / "tracker_play.py"

BASE_EXTS = {".mod", ".xm", ".s3m", ".it"}
COMPRESSED_SUFFIXES = {".gz", ".xz", ".bz2", ".zst"}


def is_module_file(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size <= 0:
        return False
    sfx = [e.lower() for e in path.suffixes]
    if not sfx:
        return False
    if sfx[-1] in BASE_EXTS:
        return True
    if len(sfx) >= 2 and sfx[-2] in BASE_EXTS and sfx[-1] in COMPRESSED_SUFFIXES:
        return True
    if sfx[-1] in {".itgz", ".xmz", ".s3mz"}:
        return True
    return False


def list_tracks() -> list[Path]:
    MUSIC.mkdir(parents=True, exist_ok=True)
    try:
        return sorted([p for p in MUSIC.iterdir() if is_module_file(p)], key=lambda p: p.name.lower())
    except Exception:
        return []


def rc_launch_play(path: Path) -> bool:
    # Try to launch a new tab to run the tracker kitten on this track
    to = f"unix:/tmp/kitty-{os.environ.get('USER','')}"
    cmd = [
        "kitty", "@", "--to", to,
        "launch", "--type=tab", "--title", f"Music: {path.name}",
        "python3", os.fspath(TRACKER), os.fspath(path),
    ]
    r = subprocess.run(cmd, cwd=HOME)
    if r.returncode == 0:
        return True
    # Fallback without explicit --to
    r = subprocess.run([
        "kitty", "@", "launch", "--type=tab", "--title", f"Music: {path.name}",
        "python3", os.fspath(TRACKER), os.fspath(path),
    ], cwd=HOME)
    return r.returncode == 0


def rc_simple(action: list[str]) -> None:
    to = f"unix:/tmp/kitty-{os.environ.get('USER','')}"
    base = ["kitty", "@", "--to", to]
    subprocess.run(base + action, check=False)


def draw(stdscr, tracks: list[Path], idx: int, status: str = "") -> None:
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "Music Picker — Enter: Play  n/p: Next/Prev  s: Shuffle  r: Rebuild  q: Quit"
    stdscr.addnstr(0, 0, title, w - 1, curses.A_BOLD)
    if status:
        stdscr.addnstr(1, 0, status, w - 1, curses.A_DIM)
    start = 3
    if not tracks:
        stdscr.addnstr(start, 0, "No modules found in ~/.config/kitty/music", w - 1)
    else:
        for i, p in enumerate(tracks):
            marker = "➤ " if i == idx else "  "
            attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addnstr(start + i, 0, f"{marker}{p.name}", w - 1, attr)
    stdscr.refresh()


def run(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    tracks = list_tracks()
    idx = 0
    draw(stdscr, tracks, idx)

    while True:
        ch = stdscr.getch()
        if ch in (curses.KEY_UP, ord('k')):
            if tracks:
                idx = (idx - 1) % len(tracks)
            draw(stdscr, tracks, idx)
        elif ch in (curses.KEY_DOWN, ord('j')):
            if tracks:
                idx = (idx + 1) % len(tracks)
            draw(stdscr, tracks, idx)
        elif ch in (10, 13, curses.KEY_ENTER):  # Enter
            if tracks:
                ok = rc_launch_play(tracks[idx])
                draw(stdscr, tracks, idx, status=("Launched" if ok else "Failed to launch"))
        elif ch in (ord('n'), ord('N')):
            rc_simple(["launch", "--type=overlay", "python3", os.fspath(TRACKER), "--next"]) 
            draw(stdscr, tracks, idx, status="Next track")
        elif ch in (ord('p'), ord('P')):
            rc_simple(["launch", "--type=overlay", "python3", os.fspath(TRACKER), "--prev"]) 
            draw(stdscr, tracks, idx, status="Previous track")
        elif ch in (ord('s'), ord('S')):
            rc_simple(["launch", "--type=overlay", "python3", os.fspath(TRACKER), "--shuffle"]) 
            draw(stdscr, tracks, idx, status="Toggled shuffle")
        elif ch in (ord('r'), ord('R')):
            rc_simple(["launch", "--type=overlay", "python3", os.fspath(TRACKER), "--build"]) 
            tracks = list_tracks()
            if tracks:
                idx = min(idx, len(tracks) - 1)
            draw(stdscr, tracks, idx, status="Rebuilt playlist")
        elif ch in (ord('q'), 27):  # q or ESC
            break


def main():
    curses.wrapper(run)


if __name__ == "__main__":
    main()

