#!/usr/bin/env bash
# Toggle battery saver overrides
set -euo pipefail

CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty
LOCAL_DIR="$CONFIG_DIR/local"
TOGGLE_FILE="$LOCAL_DIR/battery.conf"
SOCKET=${KITTY_LISTEN_ON:-unix:$HOME/.cache/kitty/kitty-$USER.sock}

mkdir -p "$LOCAL_DIR"

if [[ -f "$TOGGLE_FILE" ]]; then
  rm -f "$TOGGLE_FILE"
  state="disabled"
else
  cat >"$TOGGLE_FILE" <<'EOF'
# Battery saver: reduce GPU/CPU work and memory footprint
background_opacity 1.0
sync_to_monitor yes
repaint_delay 5
scrollback_lines 3000
window_padding_width 4
EOF
  state="enabled"
fi

if kitty @ --to "$SOCKET" load-config 2>/dev/null; then
  echo "Battery saver $state and config reloaded"
else
  echo "Battery saver $state; press your reload key (e.g., Ctrl+Shift+F5)"
fi

