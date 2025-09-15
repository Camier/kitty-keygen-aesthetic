#!/usr/bin/env python3
"""Play tracker music (MOD/XM/S3M/IT) with playlist controls.

Usage:
  kitty +kitten tracker_play.py [--loop] [--build] [--shuffle] [--next|--prev] [path_or_dir]

Players tried in order:
  - xmp (libxmp), command: xmp -q <file>
  - ffplay (ffmpeg), command: ffplay -nodisp -autoexit -loglevel error <file>

Default source directory: ~/.config/kitty/music
Playlist state: ~/.cache/kitty/playlist.json
"""
import json
import os
import random
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
MUSIC_DIR = HOME / '.config' / 'kitty' / 'music'
PLAYLIST = HOME / '.cache' / 'kitty' / 'playlist.json'

EXTS = {'.mod', '.xm', '.s3m', '.it', '.itgz', '.xmz', '.s3mz', '.mod.gz'}


def which(cmd: str) -> bool:
    return subprocess.run(['bash', '-lc', f'command -v {cmd} >/dev/null 2>&1'], check=False).returncode == 0


def scan_tracks(dirpath: Path):
    if not dirpath.exists():
        return []
    return [str(f) for f in sorted(dirpath.iterdir()) if f.is_file() and f.suffix.lower() in EXTS]


def load_playlist():
    try:
        return json.loads(PLAYLIST.read_text())
    except Exception:
        return {'tracks': scan_tracks(MUSIC_DIR), 'index': 0, 'shuffle': False}


def save_playlist(pl):
    PLAYLIST.parent.mkdir(parents=True, exist_ok=True)
    PLAYLIST.write_text(json.dumps(pl))


def is_safe_track(track_path: Path) -> bool:
    """Validate track file is safe to play."""
    try:
        resolved = track_path.resolve()
        return (resolved.is_relative_to(MUSIC_DIR.resolve()) or
                resolved.is_relative_to(HOME.resolve())) and \
               resolved.suffix.lower() in EXTS and \
               resolved.is_file()
    except (OSError, ValueError):
        return False

def pick_track(p: Path) -> Path:
    if p.is_file() and is_safe_track(p):
        return p
    if p.is_dir():
        try:
            files = [f for f in p.iterdir() if f.is_file() and is_safe_track(f)]
            if files:
                return random.choice(files)
        except (OSError, PermissionError):
            pass
    # fallback: return None if no valid tracks found
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    return None


def play(track: Path) -> int:
    if track is None:
        print('No music files found in music directory.', file=sys.stderr)
        print('Drop some tracker modules (.mod, .xm, .s3m, .it) into ~/.config/kitty/music/', file=sys.stderr)
        return 1

    if not is_safe_track(track):
        print(f'Unsafe track path: {track}', file=sys.stderr)
        return 1

    safe_path = os.fspath(track.resolve())

    if which('xmp'):
        return subprocess.run(['xmp', '-q', safe_path], cwd=HOME).returncode
    if which('ffplay'):
        return subprocess.run(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'error', safe_path], cwd=HOME).returncode
    print('No suitable player found (install xmp or ffmpeg).', file=sys.stderr)
    return 127


def main(argv):
    loop = '--loop' in argv
    build = '--build' in argv
    do_next = '--next' in argv
    do_prev = '--prev' in argv
    do_shuffle = '--shuffle' in argv
    args = [a for a in argv[1:] if not a.startswith('--')]
    target = MUSIC_DIR
    if args:
        try:
            candidate = Path(args[0]).expanduser().resolve()
            if candidate.is_relative_to(MUSIC_DIR.resolve()) or candidate.is_relative_to(HOME.resolve()):
                target = candidate
        except (OSError, ValueError):
            pass

    if build:
        pl = {'tracks': scan_tracks(MUSIC_DIR), 'index': 0, 'shuffle': False}
        save_playlist(pl)
        print(f'Playlist: {len(pl["tracks"])} tracks')
        return 0

    if do_shuffle:
        pl = load_playlist()
        pl['shuffle'] = not pl.get('shuffle', False)
        save_playlist(pl)
        print(f'Shuffle: {pl["shuffle"]}')
        return 0

    if do_next or do_prev:
        pl = load_playlist()
        tracks = pl.get('tracks') or scan_tracks(MUSIC_DIR)
        if not tracks:
            print('No tracks found in music directory.', file=sys.stderr)
            return 1
        if do_next:
            if pl.get('shuffle'):
                pl['index'] = random.randrange(len(tracks))
            else:
                pl['index'] = (pl.get('index', 0) + 1) % len(tracks)
        else:
            pl['index'] = (pl.get('index', 0) - 1) % len(tracks)
        save_playlist(pl)
        return play(Path(tracks[pl['index']]))

    if loop:
        try:
            while True:
                t = pick_track(target)
                play(t)
        except KeyboardInterrupt:
            return 0
    else:
        t = pick_track(target)
        return play(t)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
