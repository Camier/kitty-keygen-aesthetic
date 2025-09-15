#!/usr/bin/env python3
"""
Long Task Wrapper

Run a command; if it exceeds a threshold, mark the tab and notify on finish.

Usage:
  python3 long_task.py <seconds-threshold> -- <command> [args...]

Example:
  python3 long_task.py 10 -- make -j

Notes:
- Uses bell to trigger window/tab alerts per your config.
- Prints duration summary on completion.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
import time


def rc(*args: str) -> None:
    try:
        subprocess.run(["kitty", "@", *args], check=False)
    except Exception:
        pass


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] == "--":
        print("Usage: long_task.py <seconds-threshold> -- <command> [args...]", file=sys.stderr)
        return 2
    try:
        threshold = float(argv[1])
    except ValueError:
        print("Invalid threshold", file=sys.stderr)
        return 2
    if argv[2] != "--":
        print("Missing -- separator", file=sys.stderr)
        return 2
    cmd = argv[3:]
    if not cmd:
        print("Missing command", file=sys.stderr)
        return 2

    title_prefix = "⏳ "
    start = time.time()
    proc = subprocess.Popen(cmd)
    shown = False
    try:
        while True:
            ret = proc.poll()
            if ret is not None:
                break
            elapsed = time.time() - start
            if not shown and elapsed >= threshold:
                # Mark tab by prefixing title (best-effort)
                rc("set-tab-title", title_prefix + "Long task")
                shown = True
            time.sleep(0.2)
    finally:
        proc.wait()
    elapsed = time.time() - start
    # Clear title marker and ring bell for attention
    if shown:
        rc("set-tab-title", "")
    # Ring bell to trigger visual/audio/tab activity per config
    sys.stdout.write("\a")
    sys.stdout.flush()
    print(f"\n✅ Task finished in {elapsed:.1f}s: {shlex.join(cmd)}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

