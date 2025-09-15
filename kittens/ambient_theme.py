#!/usr/bin/env python3
"""
Ambient Theme

Apply a theme based on time-of-day (and optionally CPU temp).

Usage:
  python3 ambient_theme.py [apply]

Profiles:
  Morning/Day (08–18):   fairlight_cyan
  Evening (18–22):       neon_nights (if present) else reloaded_magenta
  Night (22–08):         fairlight_dark

If /sys/class/thermal/.../temp exists and is hot (>75C), prefer cooler theme.
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

HOME = Path.home()
CFG = HOME / ".config" / "kitty"


def theme_exists(name: str) -> bool:
    p = CFG / "themes" / name
    return p.exists()


def detect_cpu_hot() -> bool:
    # Best-effort read of CPU temp (Linux)
    for p in Path("/sys/class/thermal").glob("**/temp"):
        try:
            v = int(p.read_text().strip())
            c = v / 1000.0
            if c >= 75.0:
                return True
        except Exception:
            continue
    return False


def pick_theme_by_time() -> str:
    hr = time.localtime().tm_hour
    hot = detect_cpu_hot()
    if 8 <= hr < 18:
        # Daytime: cool cyan
        return "fairlight_cyan.conf"
    if 18 <= hr < 22:
        # Evening: neon or magenta
        return "neon_nights.conf" if theme_exists("neon_nights.conf") else "reloaded_magenta.conf"
    # Night: dark
    return "fairlight_dark.conf" if theme_exists("fairlight_dark.conf") else "default-dark.conf"


def apply_theme(theme: str) -> None:
    subprocess.run(["python3", os.fspath(CFG / "kittens" / "theme_apply.py"), theme], check=False)


def main():
    theme = pick_theme_by_time()
    apply_theme(theme)
    print(f"Applied ambient theme: {theme}")


if __name__ == "__main__":
    main()

