#!/usr/bin/env python3
"""
Kitty kitten: ansi viewer (ansilove integration) with optional background apply.

Usage:
  kitty +kitten ~/.config/kitty/kittens/ansiview.py <file.ans|.nfo|...> [--bg]

Behavior:
  - Converts ANSI/ASCII art to PNG via ansilove
  - Displays the image inline via kitty's icat kitten
  - With --bg, writes ~/.config/kitty/generated/background.conf and asks kitty to load it

ansilove binary resolution order:
  1) $ANSILOVE_BIN
  2) $HOME/src/ansilove/build/ansilove
  3) $HOME/dist/bin/ansilove
  4) ansilove (from PATH)
"""
import os
import sys
import hashlib
import subprocess
from pathlib import Path

HOME = Path.home()
ART_DIR = HOME / '.config' / 'kitty' / 'art'
SAFE_EXTS = {'.ans', '.nfo', '.txt', '.asc'}

def find_ansilove() -> str:
    cands = []
    env = os.environ.get('ANSILOVE_BIN')
    if env:
        cands.append(Path(env))
    cands.extend([
        HOME / 'src' / 'ansilove' / 'build' / 'ansilove',
        HOME / 'dist' / 'bin' / 'ansilove',
    ])
    cands.append('ansilove')
    for c in cands:
        try:
            if isinstance(c, Path):
                if c.exists() and os.access(str(c), os.X_OK):
                    return str(c)
            else:
                # PATH lookup
                r = subprocess.run(['bash', '-lc', f'command -v {c}'], capture_output=True, text=True)
                if r.returncode == 0:
                    return r.stdout.strip()
        except Exception:
            continue
    return ''

def ensure_cache_dir() -> Path:
    d = HOME / '.cache' / 'kitty' / 'ansilove'
    d.mkdir(parents=True, exist_ok=True)
    return d

def is_safe_art_file(filepath: Path) -> bool:
    """Validate art file is safe to process."""
    try:
        resolved = filepath.resolve()
        return (resolved.is_relative_to(ART_DIR.resolve()) or
                resolved.is_relative_to(HOME.resolve())) and \
               resolved.suffix.lower() in SAFE_EXTS and \
               resolved.is_file()
    except (OSError, ValueError):
        return False

def convert_to_png(ansilove_bin: str, infile: Path, outdir: Path) -> Path:
    if not is_safe_art_file(infile):
        raise ValueError(f"Unsafe art file: {infile}")

    key = f"{infile.resolve()}::{infile.stat().st_mtime_ns}"
    h = hashlib.sha1(key.encode()).hexdigest()[:16]
    outfile = outdir / f"{infile.stem}-{h}.png"
    if not outfile.exists():
        cmd = [ansilove_bin, os.fspath(infile.resolve()), '-o', os.fspath(outfile)]
        subprocess.run(cmd, check=True, cwd=HOME)
    return outfile

def icat_show(png: Path) -> None:
    # Clear any previous images and display using the kitten CLI
    subprocess.run(['kitten', 'icat', '--clear'], check=False)
    subprocess.run(['kitten', 'icat', str(png)], check=False)

def apply_background(png: Path) -> None:
    gen_dir = HOME / '.config' / 'kitty' / 'generated'
    gen_dir.mkdir(parents=True, exist_ok=True)
    bg_conf = gen_dir / 'background.conf'
    safe_png_path = os.fspath(png.resolve())
    with bg_conf.open('w') as f:
        f.write(f"background_image {safe_png_path}\n")
        f.write("dynamic_background_opacity yes\n")
    safe_conf_path = os.fspath(bg_conf.resolve())
    r = subprocess.run(['kitty', '@', 'action', 'load_config_file', safe_conf_path], check=False, cwd=HOME)
    if r.returncode != 0:
        subprocess.run(['kitten', '@', 'action', 'load_config_file', safe_conf_path], check=False, cwd=HOME)

def main(argv):
    if len(argv) < 2:
        print("Usage: kitty +kitten ansiview.py <file.ans|.nfo|...> [--bg]", file=sys.stderr)
        return 1
    try:
        infile = Path(argv[1]).expanduser().resolve()
        if not is_safe_art_file(infile):
            print(f"Error: unsafe or invalid art file: {infile}", file=sys.stderr)
            return 1
    except (OSError, ValueError) as e:
        print(f"Error: invalid file path: {e}", file=sys.stderr)
        return 1
    want_bg = '--bg' in argv[2:]
    al = find_ansilove()
    if not al:
        print("Error: ansilove binary not found. Build it or set $ANSILOVE_BIN.", file=sys.stderr)
        return 1
    try:
        outdir = ensure_cache_dir()
        png = convert_to_png(al, infile, outdir)
        icat_show(png)
        if want_bg:
            apply_background(png)
    except subprocess.CalledProcessError as e:
        print(f"Conversion/display failed: {e}", file=sys.stderr)
        return e.returncode or 1
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
