#!/usr/bin/env bash
# Restore saved SSH sessions
set -euo pipefail

SSH_SESSIONS_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty/sessions/ssh

if [[ ! -d "$SSH_SESSIONS_DIR" ]] || [[ -z "$(ls -A "$SSH_SESSIONS_DIR" 2>/dev/null)" ]]; then
  echo "No SSH sessions found in $SSH_SESSIONS_DIR" >&2
  exit 1
fi

# List available sessions
sessions=$(find "$SSH_SESSIONS_DIR" -name "*.session" -type f -printf "%f\n" | sed 's/.session$//' | sort)

if [[ -z "$sessions" ]]; then
  echo "No SSH sessions to restore" >&2
  exit 1
fi

# Pick a session
pick=""
if command -v fzf >/dev/null 2>&1; then
  pick=$(printf "%s\n" "$sessions" | fzf --prompt="Restore SSH session> " --height=40% --reverse --preview="cat $SSH_SESSIONS_DIR/{}.session")
else
  echo "Select session to restore:" >&2
  select s in $sessions; do
    pick="$s"; break
  done
fi

if [[ -z "${pick:-}" ]]; then
  echo "No selection"
  exit 1
fi

# Restore session
session_file="$SSH_SESSIONS_DIR/${pick}.session"
if [[ -f "$session_file" ]]; then
  echo "✓ Restoring SSH session: $pick"
  exec kitty @ launch --type=tab kitten ssh "$pick"
else
  echo "✗ Session file not found: $session_file" >&2
  exit 1
fi
