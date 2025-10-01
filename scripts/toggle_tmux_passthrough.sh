#!/usr/bin/env bash
# Toggle tmux-aware keymaps (guarded by cmdline:tmux) via local include
set -euo pipefail

CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty
LOCAL_DIR="$CONFIG_DIR/local"
TOGGLE_FILE="$LOCAL_DIR/tmux-passthrough.conf"
SOCKET=${KITTY_LISTEN_ON:-unix:$HOME/.cache/kitty/kitty-$USER.sock}

mkdir -p "$LOCAL_DIR"

if [[ -f "$TOGGLE_FILE" ]]; then
  rm -f "$TOGGLE_FILE"
  state="disabled"
else
  cat >"$TOGGLE_FILE" <<'EOF'
# Tmux-aware keymaps (chord prefix: Ctrl+Shift+G)

# Tmux prefix and common operations (sent only to tmux windows)
map kitty_mod+g>p launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh prefix'
map kitty_mod+g>c launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh copy'
map kitty_mod+g>y launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh paste'

# Pane navigation (hjkl)
map kitty_mod+g>h launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh left'
map kitty_mod+g>j launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh down'
map kitty_mod+g>k launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh up'
map kitty_mod+g>l launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh right'

# Splits and pane management
map kitty_mod+g>v launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh vsplit'
map kitty_mod+g>s launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh hsplit'
map kitty_mod+g>x launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh kill'
map kitty_mod+g>o launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh other'

# Window management
map kitty_mod+g>n launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh new'
map kitty_mod+g>shift+n launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh next'
map kitty_mod+g>shift+p launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh prev'
map kitty_mod+g>d launch --type=background bash -lc '~/.config/kitty/scripts/tmux_send.sh detach'

# Status overlay
map kitty_mod+g>i launch --type=overlay --title="Tmux Status" bash -lc '~/.config/kitty/scripts/tmux_send.sh status; read -n 1 -r -s'
EOF
  state="enabled"
fi

if kitty @ --to "$SOCKET" load-config 2>/dev/null; then
  echo "Tmux passthrough $state and config reloaded"
else
  echo "Tmux passthrough $state; press your reload key (e.g., Ctrl+Shift+F5)"
fi
