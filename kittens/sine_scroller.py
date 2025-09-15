#!/usr/bin/env python3
"""Sine scroller kitten — prints a sine-wave scrolling banner.

Usage: kitty +kitten sine_scroller.py ["YOUR GREETINGS ..."] [duration_sec]

Defaults: message with classic greetings, duration 20s.
"""
import math
import os
import sys
import time

RESET = "\033[0m"

def get_size():
    try:
        import shutil
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except Exception:
        return 80, 24

def main(argv):
    msg = argv[1] if len(argv) > 1 else (
        "GREETINGS TO RAZOR1911 • FAiRLiGHT • DEViANCE • RELOADED • SKIDROW • CODEX • CPY • FUTURE CREW"
    )
    duration = float(argv[2]) if len(argv) > 2 else 20.0
    cols, rows = get_size()
    amplitude = max(1, min(rows//3, 6))
    period = 20.0
    speed = 30.0

    # Colors cycle (neon cyan/magenta/green)
    palette = [45, 201, 46, 51, 93, 226]

    start = time.time()
    phase = 0.0
    text = f"   {msg}   "
    text = text + " " * cols
    off = 0

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    try:
        while time.time() - start < duration:
            col = int(off) % len(text)
            line = [" "] * cols
            for i in range(cols):
                ch = text[(col + i) % len(text)]
                y = int((math.sin((i/period) + phase) * amplitude) + amplitude + 1)
                # Move cursor and print char with color
                color = palette[(i // 4) % len(palette)]
                sys.stdout.write(f"\033[{y};{i+1}H\033[38;5;{color}m{ch}{RESET}")
            sys.stdout.flush()
            time.sleep(1/60)
            phase += 0.2
            off += speed * (1/60)
        # Reset screen region
        sys.stdout.write(RESET)
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

