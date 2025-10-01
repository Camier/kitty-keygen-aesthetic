#!/usr/bin/env bash
# Toggle low-latency perf overrides via local include and reload config
set -euo pipefail

CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty
LOCAL_DIR="$CONFIG_DIR/local"
TOGGLE_FILE="$LOCAL_DIR/perf-low.conf"
SOCKET=${KITTY_LISTEN_ON:-unix:$HOME/.cache/kitty/kitty-$USER.sock}

mkdir -p "$LOCAL_DIR"

if [[ -f "$TOGGLE_FILE" ]]; then
  rm -f "$TOGGLE_FILE"
  state="disabled"
else
  cat >"$TOGGLE_FILE" <<EOF
# Low-latency overrides (toggle)
sync_to_monitor no
repaint_delay 2
input_delay 0
EOF
  state="enabled"
fi

if kitty @ --to "$SOCKET" load-config 2>/dev/null; then
  echo "Low-latency profile $state and config reloaded"
else
  echo "Low-latency profile $state; press your reload key (e.g. Ctrl+Shift+F5)"
fi

