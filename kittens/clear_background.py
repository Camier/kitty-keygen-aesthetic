#!/usr/bin/env python3
"""
Clear any persistent background image and reset all Kitty windows.

Actions:
- Remove ~/.config/kitty/generated/background.conf (if present)
- kitty @ --all set-background-image none
"""
import os
import subprocess
from pathlib import Path

HOME = Path.home()
CFG = HOME / ".config" / "kitty"
GEN = CFG / "generated"
BG_CONF = GEN / "background.conf"


def main() -> int:
    try:
        if BG_CONF.exists():
            BG_CONF.unlink(missing_ok=True)
    except Exception:
        pass
    # Reset background across all windows; ignore failure if RC disabled
    try:
        subprocess.run(["kitty", "@", "--to", f"unix:/tmp/kitty-{os.environ.get('USER','')}", "--all", "set-background-image", "none"], check=False)
    except Exception:
        # Fallback to default address resolution
        subprocess.run(["kitty", "@", "--all", "set-background-image", "none"], check=False)
    print("Background cleared.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

