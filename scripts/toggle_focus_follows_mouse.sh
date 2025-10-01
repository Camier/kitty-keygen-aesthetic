#!/usr/bin/env bash
# Toggle focus_follows_mouse via local include and reload config
set -euo pipefail

CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty
LOCAL_DIR="$CONFIG_DIR/local"
TOGGLE_FILE="$LOCAL_DIR/focus-follows-mouse.conf"
SOCKET=${KITTY_LISTEN_ON:-unix:$HOME/.cache/kitty/kitty-$USER.sock}

mkdir -p "$LOCAL_DIR"

current=""
if [[ -f "$TOGGLE_FILE" ]]; then
  if grep -qiE '^\s*focus_follows_mouse\s+yes' "$TOGGLE_FILE"; then
    current="yes"
  elif grep -qiE '^\s*focus_follows_mouse\s+no' "$TOGGLE_FILE"; then
    current="no"
  fi
fi

if [[ "$current" == "yes" ]]; then
  echo "focus_follows_mouse no" >"$TOGGLE_FILE"
  state="disabled"
elif [[ "$current" == "no" ]]; then
  echo "focus_follows_mouse yes" >"$TOGGLE_FILE"
  state="enabled"
else
  # Default in ui.conf is 'yes'; first toggle disables it
  echo "focus_follows_mouse no" >"$TOGGLE_FILE"
  state="disabled"
fi

if kitty @ --to "$SOCKET" load-config 2>/dev/null; then
  echo "Focus-follows-mouse $state and config reloaded"
else
  echo "Focus-follows-mouse $state; press your reload key (e.g. Ctrl+Shift+F5)"
fi

