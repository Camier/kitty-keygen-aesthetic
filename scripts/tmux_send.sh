#!/usr/bin/env bash
# Send tmux-prefixed keys to the focused tmux window using kitty remote control
set -euo pipefail

SOCKET=${KITTY_LISTEN_ON:-unix:$HOME/.cache/kitty/kitty-$USER.sock}
CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty

prefix_byte='\x02' # Ctrl+B default
if [[ -f "$CONFIG_DIR/local/tmux-prefix.conf" ]]; then
  prefix_byte='\x01' # Ctrl+A when toggled
fi

cmd=${1:-}
if [[ -z "$cmd" ]]; then
  echo "Usage: tmux_send.sh <prefix|copy|paste|left|down|up|right|vsplit|hsplit|kill|other|status>" >&2
  exit 1
fi

send_bytes() {
  # $1: byte sequence with escapes for printf
  printf '%b' "$1" | kitty @ --to "$SOCKET" send-text --match 'cmdline:tmux' --stdin >/dev/null 2>&1 || true
}

case "$cmd" in
  status)
    # Enhanced status with session details
    if kitty @ --to "$SOCKET" ls 2>/dev/null | grep -q '"tmux"'; then
      echo "═══ Tmux Status ═══"
      echo "✓ Tmux detected in current window"
      if command -v tmux >/dev/null 2>&1; then
        echo ""
        echo "Active sessions:"
        tmux list-sessions 2>/dev/null || echo "(no sessions)"
        echo ""
        echo "Current prefix: $(printf '%s' "$prefix_byte" | od -An -tx1)"
      fi
    else
      echo "═══ Tmux Status ═══"
      echo "✗ No tmux detected in current window"
      if command -v tmux >/dev/null 2>&1; then
        echo ""
        echo "Available sessions:"
        tmux list-sessions 2>/dev/null || echo "(no sessions)"
      fi
    fi
    ;;
  prefix) send_bytes "${prefix_byte}" ;;
  copy)   send_bytes "${prefix_byte}[" ;;
  paste)  send_bytes "${prefix_byte}]" ;;
  left)   send_bytes "${prefix_byte}\e[D" ;;
  down)   send_bytes "${prefix_byte}\e[B" ;;
  up)     send_bytes "${prefix_byte}\e[A" ;;
  right)  send_bytes "${prefix_byte}\e[C" ;;
  vsplit) send_bytes "${prefix_byte}%" ;;
  hsplit) send_bytes "${prefix_byte}\"" ;;
  kill)   send_bytes "${prefix_byte}x" ;;
  other)  send_bytes "${prefix_byte}o" ;;
  new)    send_bytes "${prefix_byte}c" ;;     # Create new window
  next)   send_bytes "${prefix_byte}n" ;;     # Next window
  prev)   send_bytes "${prefix_byte}p" ;;     # Previous window
  detach) send_bytes "${prefix_byte}d" ;;     # Detach session
  *) echo "Unknown cmd: $cmd" >&2; exit 1 ;;
esac

