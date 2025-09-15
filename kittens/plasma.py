#!/usr/bin/env python3
"""Plasma effect kitten — lightweight ANSI color plasma.

Usage: kitty +kitten plasma.py [seconds]
"""
import math
import sys
import time

RESET = "\033[0m"

def get_size():
    try:
        import shutil
        sz = shutil.get_terminal_size()
        return sz.columns, sz.lines
    except Exception:
        return 80, 24

def color_index(v: float) -> int:
    # Map 0..1 to a 256-color cyan/magenta/blue ramp
    ramps = [45, 51, 39, 33, 93, 201]
    return ramps[int(v * (len(ramps)-1))]

def main(argv):
    dur = float(argv[1]) if len(argv) > 1 else 15.0
    cols, rows = get_size()
    # Leave last line for prompt
    rows = max(5, rows - 1)
    t0 = time.time()
    # Hide cursor
    sys.stdout.write("\033[?25l")
    try:
        while time.time() - t0 < dur:
            t = time.time() - t0
            for y in range(rows):
                for x in range(cols):
                    v = 0.5 + 0.5*math.sin(x*0.08 + t)
                    v += 0.5 + 0.5*math.sin((x*0.08 + y*0.08)*2 + t*1.6)
                    v += 0.5 + 0.5*math.sin(math.hypot(x, y)*0.08)
                    v /= 3.0
                    c = color_index(v)
                    sys.stdout.write(f"\033[{y+1};{x+1}H\033[48;5;{c}m ")
            sys.stdout.flush()
            time.sleep(1/30)
        sys.stdout.write(RESET)
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

