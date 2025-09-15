#!/usr/bin/env python3
"""Apply a theme safely by updating themes/current-theme.conf and reloading kitty.conf.

Usage:
  kitty +kitten theme_apply.py themes/neon_nights.conf

This preserves all other settings by reloading the main kitty.conf.
"""
import os
import sys
from pathlib import Path
import subprocess

HOME = Path.home()
CFG = HOME / '.config' / 'kitty'

def main(argv):
    if len(argv) < 2:
        print('Usage: kitty +kitten theme_apply.py <file>.conf | themes/<file>.conf', file=sys.stderr)
        return 1

    theme_arg = argv[1]

    # Accept either 'file.conf' or 'themes/file.conf'
    if not theme_arg.endswith('.conf') or '..' in theme_arg:
        print(f'Invalid theme name: {theme_arg}', file=sys.stderr)
        return 1

    if theme_arg.startswith('themes/'):
        theme_path = (CFG / theme_arg).resolve()
    else:
        theme_path = (CFG / 'themes' / theme_arg).resolve()

    try:
        themes_root = (CFG / 'themes').resolve()
        # Ensure resolved path is still under CFG/themes/
        if not theme_path.is_relative_to(themes_root):
            print(f'Theme path outside safe directory: {theme_path}', file=sys.stderr)
            return 1
        if not theme_path.exists():
            print(f'Theme not found: {theme_path}', file=sys.stderr)
            return 1
    except (OSError, ValueError) as e:
        print(f'Invalid theme path: {e}', file=sys.stderr)
        return 1

    # Write include relative to the themes directory so it works regardless of include location
    current = CFG / 'themes' / 'current-theme.conf'
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text(f'include {theme_path.name}\n')

    # Reload main config so includes take effect
    main_conf = CFG / 'kitty.conf'
    safe_conf_path = os.fspath(main_conf.resolve())
    r = subprocess.run(['kitty', '@', 'action', 'load_config_file', safe_conf_path], check=False, cwd=HOME)
    if r.returncode != 0:
        # Remote control may be disabled. Config will apply on next launch.
        print('Theme updated; enable remote control to live-reload (see includes/ui.conf).')
    print(f'Applied theme: {theme_path.name}')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
