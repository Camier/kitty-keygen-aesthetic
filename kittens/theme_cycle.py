#!/usr/bin/env python3
"""Cycle through curated scene themes by loading config fragments."""
import json
import os
import subprocess
from pathlib import Path

HOME = Path.home()
THEMES = [
    'themes/razor1911_green.conf',
    'themes/fairlight_cyan_magenta.conf',
    'themes/deviance_purple_gold.conf',
    'themes/reloaded_matrix.conf',
    'themes/skidrow_red_black.conf',
    'themes/codex_gold_purple.conf',
    'themes/cpy_italian.conf',
    'themes/neon_nights.conf',
    'themes/razors_edge.conf',
    'themes/fairlight_dark.conf',
    'themes/codex_purple.conf',
    'themes/skidrow_green.conf',
    'themes/reloaded_cyan.conf',
]

STATE = HOME / '.cache' / 'kitty' / 'theme_cycle.json'

def load_state():
    try:
        with STATE.open('r') as f:
            return json.load(f)
    except Exception:
        return {'index': -1}

def save_state(st):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    with STATE.open('w') as f:
        json.dump(st, f)

def main():
    st = load_state()
    idx = (st.get('index', -1) + 1) % len(THEMES)
    st['index'] = idx
    save_state(st)
    theme = THEMES[idx]
    # Write current-theme.conf include and reload full config
    cfg = HOME / '.config' / 'kitty'
    current = cfg / 'themes' / 'current-theme.conf'
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text(f'include {theme}\n')
    main_conf = cfg / 'kitty.conf'
    r = subprocess.run(['kitty', '@', 'action', 'load_config_file', str(main_conf)], check=False)
    if r.returncode != 0:
        subprocess.run(['kitten', '@', 'action', 'load_config_file', str(main_conf)], check=False)
    print(f"Applied theme: {theme}")

if __name__ == '__main__':
    main()
