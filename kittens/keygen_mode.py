#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

def main():
    home = Path.home()
    session = home / '.config' / 'kitty' / 'sessions' / 'keygen.session'

    # Validate session file exists and is safe
    try:
        if not session.exists() or not session.is_file():
            print(f"Session file not found: {session}")
            return 1

        # Ensure it's actually under our config directory
        if not session.resolve().is_relative_to((home / '.config' / 'kitty').resolve()):
            print(f"Session file outside safe directory: {session}")
            return 1
    except (OSError, ValueError) as e:
        print(f"Invalid session path: {e}")
        return 1

    # Launch with safe resolved path (don't wait for completion)
    safe_session_path = os.fspath(session.resolve())
    try:
        subprocess.Popen(['kitty', '--single-instance', '--session', safe_session_path],
                        cwd=home,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True)
        print("Keygen mode launched!")
    except Exception as e:
        print(f"Failed to launch keygen mode: {e}")
        return 1
    return 0

if __name__ == '__main__':
    exit(main())
