#!/usr/bin/env python3
"""
Wal → Kitty theme bridge.

Usage:
  kitty +kitten wal_theme.py            # Use current background image (generated/background.conf)
  kitty +kitten wal_theme.py /path/img  # Use specific image
  kitty +kitten wal_theme.py --restore  # wal -R and re-apply last palette

Effect:
  - Runs wal to derive a palette
  - Builds ~/.config/kitty/themes/wal-current.conf from wal's colors-kitty.conf
  - Writes themes/current-theme.conf to include wal-current.conf
  - Reloads Kitty config via RC
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
CFG = HOME / ".config" / "kitty"
GEN = CFG / "generated"
THEMES = CFG / "themes"
CURRENT = THEMES / "current-theme.conf"
WAL_KITTY = HOME / ".cache" / "wal" / "colors-kitty.conf"
WAL_OUT = THEMES / "wal-current.conf"
BG_CONF = GEN / "background.conf"


def read_background_image() -> str | None:
    try:
        txt = BG_CONF.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("background_image "):
            return line.split(None, 1)[1]
    return None


def run_wal(img: str | None, restore: bool = False) -> int:
    if restore:
        return subprocess.run(["wal", "-R"], cwd=HOME).returncode
    if not img:
        return 2
    return subprocess.run(["wal", "-n", "-i", img], cwd=HOME).returncode


def build_kitty_from_wal() -> bool:
    if not WAL_KITTY.exists():
        return False
    THEMES.mkdir(parents=True, exist_ok=True)
    # Copy wal kitty colors, then append a few UI hints
    base = WAL_KITTY.read_text(encoding="utf-8")
    # Pick active/inactive tab colors from foreground/background and a bright accent
    # Wal defines: foreground, background, color0..15
    accent = "#00e676"  # fallback accent if not overridden by wal
    fg = "#c0c0c0"
    bg = "#121212"
    for line in base.splitlines():
        if line.startswith("foreground "):
            fg = line.split()[1]
        elif line.startswith("background "):
            bg = line.split()[1]
        elif line.startswith("color10 ") or line.startswith("color2 "):
            accent = line.split()[1]
    ui = f"\n# UI extras from wal_theme.py\n" \
         f"tab_bar_background    {bg}\n" \
         f"active_tab_foreground {bg}\n" \
         f"active_tab_background {accent}\n" \
         f"inactive_tab_foreground {fg}\n" \
         f"inactive_tab_background {bg}\n" \
         f"active_border_color   {accent}\n" \
         f"inactive_border_color {bg}\n" \
         f"selection_foreground  {bg}\n" \
         f"selection_background  {accent}\n"
    WAL_OUT.write_text(base + "\n" + ui, encoding="utf-8")
    CURRENT.write_text(f"include {WAL_OUT.name}\n", encoding="utf-8")
    return True


def rc_reload() -> None:
    try:
        subprocess.run(["kitty", "@", "--to", f"unix:/tmp/kitty-{os.environ.get('USER','')}",
                        "action", "load_config_file", os.fspath((CFG / "kitty.conf").resolve())], check=False)
    except Exception:
        subprocess.run(["kitty", "@", "action", "load_config_file", os.fspath((CFG / "kitty.conf").resolve())], check=False)


def main(argv: list[str]) -> int:
    restore = "--restore" in argv[1:]
    explicit = None
    args = [a for a in argv[1:] if not a.startswith("-")]
    if args:
        explicit = os.fspath(Path(args[0]).expanduser())
    img = explicit or read_background_image()
    rc = run_wal(img, restore=restore)
    if rc not in (0, 2):
        print("wal failed; ensure 'wal' is installed.")
        return rc
    if rc == 2 and not restore:
        print("No background image found; pass an image path or set one via Background Gallery.")
        return 2
    if not build_kitty_from_wal():
        print("Could not locate wal colors for Kitty (colors-kitty.conf).")
        return 3
    rc_reload()
    print("Applied wal-derived Kitty theme.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

