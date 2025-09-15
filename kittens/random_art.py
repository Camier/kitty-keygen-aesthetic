#!/usr/bin/env python3
"""Pick a random ANSI/NFO/TXT art from ~/.config/kitty/art and display.

Usage: kitten random_art.py [--bg]
"""
import os
import random
import subprocess
from pathlib import Path
import sys

HOME = Path.home()
ART_DIR = HOME / '.config' / 'kitty' / 'art'
ANSIVIEW = HOME / '.config' / 'kitty' / 'kittens' / 'ansiview.py'

def choose_file() -> Path:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    cand = []
    exts = {'.ans', '.nfo', '.txt', '.asc'}
    for p in ART_DIR.iterdir():
        if p.is_file() and p.suffix.lower() in exts:
            cand.append(p)
    if not cand:
        # seed a minimal piece if none exists
        p = ART_DIR / 'welcome.ans'
        if not p.exists():
            p.write_text('\x1b[38;5;46mWELCOME TO KEYGEN MODE\x1b[0m\n')
        return p
    return random.choice(cand)

def main(argv):
    want_bg = '--bg' in argv[1:]
    art = choose_file()
    # Use the standalone kitten CLI to run ansiview in the current kitty instance
    args = ['kitten', str(ANSIVIEW), str(art)]
    if want_bg:
        args.append('--bg')
    subprocess.run(args, check=False)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
