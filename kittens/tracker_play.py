#!/usr/bin/env python3
"""Play tracker music (MOD/XM/S3M/IT) with playlist controls.

Usage:
  kitty +kitten tracker_play.py [--loop] [--build] [--shuffle] [--next|--prev] [path_or_dir]

Players tried in order:
  - openmpt123 (libopenmpt), command: openmpt123 -q <file>
  - xmp (libxmp), command: xmp -q <file>
  - mpv, command: mpv --no-video --really-quiet <file>
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

BASE_EXTS = {'.mod', '.xm', '.s3m', '.it'}
COMPRESSED_SUFFIXES = {'.gz', '.xz', '.bz2', '.zst'}


def which(cmd: str) -> bool:
    return subprocess.run(['bash', '-lc', f'command -v {cmd} >/dev/null 2>&1'], check=False).returncode == 0


def _is_module_file(path: Path) -> bool:
    sfx = [e.lower() for e in path.suffixes]
    if not sfx:
        return False
    # Plain module
    if sfx[-1] in BASE_EXTS:
        return True
    # Compressed module: mod.gz, it.gz, xm.gz, s3m.gz; or packed as .itgz/.xmz/.s3mz
    if len(sfx) >= 2 and sfx[-2] in BASE_EXTS and sfx[-1] in COMPRESSED_SUFFIXES:
        return True
    if sfx[-1] in {'.itgz', '.xmz', '.s3mz'}:
        return True
    return False


def scan_tracks(dirpath: Path):
    if not dirpath.exists():
        return []
    return [str(f) for f in sorted(dirpath.iterdir()) if f.is_file() and f.stat().st_size > 0 and _is_module_file(f)]


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
               _is_module_file(resolved) and \
               resolved.is_file() and resolved.stat().st_size > 0
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


def ffmpeg_supports(path: Path) -> bool:
    # Detect if local ffmpeg build can demux this file via ffprobe
    try:
        r = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=format_name',
            '-of', 'default=nw=1:nk=1', os.fspath(path)
        ], capture_output=True, text=True, cwd=HOME)
        return r.returncode == 0 and bool(r.stdout.strip())
    except Exception:
        return False


def play(track: Path) -> int:
    if track is None:
        print('No music files found in music directory.', file=sys.stderr)
        print('Drop some tracker modules (.mod, .xm, .s3m, .it) into ~/.config/kitty/music/', file=sys.stderr)
        try:
            input('Press Enter to close...')
        except Exception:
            pass
        return 1

    if not is_safe_track(track):
        print(f'Unsafe track path: {track}', file=sys.stderr)
        return 1

    safe_path = os.fspath(track.resolve())

    # Try players in order, skipping ffplay when ffmpeg lacks module support
    players = []
    if which('openmpt123'):
        players.append(('openmpt123', ['openmpt123', '-q', safe_path]))
    if which('xmp'):
        players.append(('xmp', ['xmp', '-q', safe_path]))
    if which('mpv'):
        players.append(('mpv', ['mpv', '--no-video', '--really-quiet', '--force-window=no', safe_path]))
    if which('ffplay') and ffmpeg_supports(track):
        players.append(('ffplay', ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'error', safe_path]))

    for name, cmd in players:
        rc = subprocess.run(cmd, cwd=HOME).returncode
        if rc == 0:
            return 0
    # If we got here, nothing worked
    print('No suitable tracker player succeeded.', file=sys.stderr)
    print('Install one of: openmpt123 (libopenmpt), xmp, or mpv with module support.', file=sys.stderr)
    print('Fedora example: sudo dnf install openmpt123 xmp mpv', file=sys.stderr)
    # Keep the tab visible long enough to read the message when launched via Kitty
    try:
        input('Press Enter to close...')
    except Exception:
        pass
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
                rc = play(t)
                if rc != 0:
                    return rc
        except KeyboardInterrupt:
            return 0
    else:
        t = pick_track(target)
        return play(t)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
