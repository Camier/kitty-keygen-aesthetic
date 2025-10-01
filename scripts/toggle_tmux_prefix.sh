#!/usr/bin/env bash
# Toggle tmux passthrough prefix between Ctrl+B (default) and Ctrl+A
set -euo pipefail

CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty
LOCAL_DIR="$CONFIG_DIR/local"
TOGGLE_FILE="$LOCAL_DIR/tmux-prefix.conf"
SOCKET=${KITTY_LISTEN_ON:-unix:$HOME/.cache/kitty/kitty-$USER.sock}

mkdir -p "$LOCAL_DIR"

if [[ -f "$TOGGLE_FILE" ]]; then
  rm -f "$TOGGLE_FILE"
  state="default (Ctrl+B)"
else
  # Presence of this file indicates Ctrl+A prefix for tmux_send.sh
  echo "prefix=Ctrl+A" >"$TOGGLE_FILE"
  state="Ctrl+A"
fi

if kitty @ --to "$SOCKET" load-config 2>/dev/null; then
  echo "Tmux prefix set to $state and config reloaded"
else
  echo "Tmux prefix set to $state; press your reload key (e.g., Ctrl+Shift+F5)"
fi
