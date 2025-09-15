#!/usr/bin/env python3
"""
Help Center (overlay)

Scrollable, searchable help for your Kitty setup.

Keys:
- Up/Down, PgUp/PgDn, Home/End  : Scroll
- / to search, n/N               : Next/Prev match
- q or ESC                       : Quit
"""
from __future__ import annotations

import curses
from pathlib import Path

HELP_TEXT = f"""
KITTY HELP CENTER — Shortcuts, Modes, Galleries, Troubleshooting

GLOBAL KEYS
- New window/tab: Ctrl+Shift+Enter | Ctrl+Shift+T
- New OS window:  Ctrl+Shift+N
- Close:          Ctrl+Shift+W (window) | Ctrl+Shift+Q (tab)
- Switch window:  Ctrl+Shift+] / [
- Switch tab:     Ctrl+Shift+Right / Left
- Move tab:       Ctrl+Shift+Period / Comma
- Set tab title:  Ctrl+Shift+Alt+E

SPLITS & RESIZE
- Create split:   Ctrl+Shift+Alt+- (hsplit) | Ctrl+Shift+Alt+\ (vsplit)
- Resize split:   Ctrl+Shift+Alt+Arrows | Reset: Ctrl+Shift+Alt+Backspace
- Resize mode:    Ctrl+Shift+R (keyboard-driven resize mode)
- Focus numbered: Ctrl+Shift+1..0

SCROLLBACK & PROMPTS
- Scroll lines:   Ctrl+Shift+K / J
- Page/Home/End:  Ctrl+Shift+PageUp/PageDown | Home/End
- Show scrollback:Ctrl+Shift+H
- To prev/next prompt: Ctrl+Shift+Alt+Z / X

FONTS & OPACITY
- Font size:      Ctrl+Shift+= / - / Backspace
- Background opacity: Ctrl+Shift+Shift+= / - / Backspace

CONFIG & TOOLS
- Edit config:    Ctrl+Shift+F12
- Reload config:  Ctrl+Shift+F5
- Debug config:   Ctrl+Shift+F11
- Kitty shell:    Ctrl+Shift+Escape
- URL hints:      Ctrl+Shift+E
- Unicode input:  Ctrl+Shift+U

THEMES & BACKGROUNDS
- Theme Gallery:  Ctrl+Shift+F6 (browse, preview, apply)
- Quick themes:   Ctrl+Shift+Ctrl+1..4 (Fairlight, Skidrow, Reloaded, Razor)
- Background Gallery: Ctrl+Shift+F7 (browse/preview/apply images from ~/Pictures)

EFFECTS & DEMOSCENE
- Plasma:         Ctrl+Shift+P (tab)
- Fire:           Ctrl+Shift+O (tab)
- Scroller:       Ctrl+Shift+S (tab)
- Music:          Ctrl+Shift+M (tab) | Loop: Ctrl+Shift+Alt+M
- Colors test:    Ctrl+Shift+Alt+C
- Stars overlay:  Ctrl+Shift+Shift+Z
- Matrix (if installed): Ctrl+Shift+X
- Keygen mode:    Ctrl+Shift+G

MODES (open in new OS window)
- Work:           Ctrl+Shift+F1
- Demo:           Ctrl+Shift+F2
- Keygen:         Ctrl+Shift+F3

PROFILES
- Default:        Balanced perf (vsync on, repaint_delay 7)
- Demo/Keygen:    Low-latency perf (vsync off, repaint_delay 2)

THEME/BACKGROUND UNDER THE HOOD
- Theme active:   ~/.config/kitty/themes/current-theme.conf (overrides default)
- Background:     ~/.config/kitty/generated/background.conf (if present)
- Live reload:    kitty @ action load_config_file ~/.config/kitty/kitty.conf

FILES & PATHS
- Main config:    ~/.config/kitty/kitty.conf
- Includes:       ~/.config/kitty/includes/*.conf
- Themes:         ~/.config/kitty/themes/*.conf
- Kittens:        ~/.config/kitty/kittens/*.py
- Modes:          ~/.config/kitty/modes/*.conf
- Sessions:       ~/.config/kitty/sessions/*.session

TROUBLESHOOTING
- Minimal run:    kitty --config ~/.config/kitty/kitty-minimal.conf
- GPU-safe run:   ~/.config/kitty/run-kitty-safe.sh
- Debug script:   ~/.config/kitty/debug-kitty.sh
- RC socket off?  Restart Kitty or ensure ui.conf is included.

TIP
- Use Theme and Background galleries for quick visual changes.
- Host-specific overrides: drop files into ~/.config/kitty/includes/host/ or ~/.config/kitty/local/
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
    match_idx = -1

    def redraw(status: str = ""):
        nonlocal top, cur
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        vis = lines[top: top + h - 1]
        for i, ln in enumerate(vis):
            attr = curses.A_BOLD if ln and ln == ln.upper() and len(ln) < 60 else curses.A_NORMAL
            stdscr.addnstr(i, 0, ln, w - 1, attr)
        footer = f" Arrows/PgUp/PgDn/Home/End  / search  n/N next/prev  q quit {status}"
        stdscr.addnstr(h - 1, 0, footer[: w - 1], w - 1, curses.A_REVERSE)
        stdscr.refresh()

    def do_search(q: str):
        nonlocal matches, match_idx, top
        matches = []
        match_idx = -1
        if not q:
            return
        for i, ln in enumerate(lines):
            if q.lower() in ln.lower():
                matches.append(i)
        if matches:
            match_idx = 0
            top = max(0, matches[0] - 2)

    redraw()
    while True:
        ch = stdscr.getch()
        h, w = stdscr.getmaxyx()
        page = h - 2
        if ch in (ord('q'), 27):
            break
        elif ch in (curses.KEY_DOWN, ord('j')):
            top = min(max(0, len(lines) - page), top + 1)
            redraw()
        elif ch in (curses.KEY_UP, ord('k')):
            top = max(0, top - 1)
            redraw()
        elif ch in (curses.KEY_NPAGE,):
            top = min(max(0, len(lines) - page), top + page)
            redraw()
        elif ch in (curses.KEY_PPAGE,):
            top = max(0, top - page)
            redraw()
        elif ch in (curses.KEY_HOME,):
            top = 0
            redraw()
        elif ch in (curses.KEY_END,):
            top = max(0, len(lines) - page)
            redraw()
        elif ch == ord('/'):
            curses.echo()
            stdscr.addstr(h - 1, 0, "/ ")
            q = stdscr.getstr(h - 1, 2).decode('utf-8', 'ignore')
            curses.noecho()
            do_search(q)
            redraw(f" {len(matches)} matches for '{q}'" if matches else " no matches")
        elif ch in (ord('n'), ord('N')):
            if matches:
                if ch == ord('n'):
                    match_idx = (match_idx + 1) % len(matches)
                else:
                    match_idx = (match_idx - 1) % len(matches)
                top = max(0, min(matches[match_idx], len(lines) - page))
                redraw(f" match {match_idx + 1}/{len(matches)} at line {matches[match_idx] + 1}")


def main():
    curses.wrapper(viewer)


if __name__ == "__main__":
    main()

