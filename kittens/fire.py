#!/usr/bin/env python3
"""DOS-style fire effect kitten (ANSI colors).

Usage: kitty +kitten fire.py [seconds]
"""
import random
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

def main(argv):
    dur = float(argv[1]) if len(argv) > 1 else 12.0
    cols, rows = get_size()
    rows = max(5, rows - 1)
    # Buffer of intensities
    buf = [[0]*cols for _ in range(rows)]
    palette = [196, 202, 208, 214, 220, 226, 229, 231]
    t0 = time.time()
    sys.stdout.write("\033[?25l")
    try:
        while time.time() - t0 < dur:
            # Heat source bottom row
            for x in range(cols):
                buf[-1][x] = random.randint(0, 7) * 32
            # Propagate upward with cooling
            for y in range(rows-2, -1, -1):
                for x in range(cols):
                    s = buf[y+1][x]
                    if x > 0: s += buf[y+1][x-1]
                    if x < cols-1: s += buf[y+1][x+1]
                    s //= 3
                    s = max(0, s - random.randint(0, 8))
                    buf[y][x] = s
            # Render
            for y in range(rows):
                for x in range(cols):
                    val = buf[y][x]
                    idx = min(len(palette)-1, val // 32)
                    sys.stdout.write(f"\033[{y+1};{x+1}H\033[48;5;{palette[idx]}m ")
            sys.stdout.flush()
            time.sleep(1/30)
        sys.stdout.write(RESET)
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

