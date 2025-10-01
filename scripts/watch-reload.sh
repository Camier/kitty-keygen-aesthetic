#!/usr/bin/env bash
# Toggle a background watcher to auto-reload kitty config on file changes
set -euo pipefail

CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty
SOCKET=${KITTY_LISTEN_ON:-unix:$HOME/.cache/kitty/kitty-$USER.sock}
PIDFILE=/tmp/kitty-watch-reload-${USER}.pid

start() {
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Watcher already running (pid $(cat "$PIDFILE"))"
    exit 0
  fi
  (
    echo $$ >"$PIDFILE"
    trap 'rm -f "$PIDFILE"' EXIT
    if command -v inotifywait >/dev/null 2>&1; then
      while :; do
        inotifywait -qq -e close_write,move,create,delete \
          "$CONFIG_DIR/kitty.conf" \
          "$CONFIG_DIR"/includes "$CONFIG_DIR"/themes "$CONFIG_DIR"/local "$CONFIG_DIR"/generated \
          --recursive
        kitty @ --to "$SOCKET" load-config >/dev/null 2>&1 || true
      done
    else
      # Fallback: poll and only reload on change
      prev=$(find "$CONFIG_DIR" -type f -name '*.conf' -print0 | sort -z | xargs -0 sha1sum 2>/dev/null | sha1sum | awk '{print $1}')
      while :; do
        sleep 1
        cur=$(find "$CONFIG_DIR" -type f -name '*.conf' -print0 | sort -z | xargs -0 sha1sum 2>/dev/null | sha1sum | awk '{print $1}')
        if [[ "$cur" != "$prev" ]]; then
          prev="$cur"
          kitty @ --to "$SOCKET" load-config >/dev/null 2>&1 || true
        fi
      done
    fi
  ) &
  disown || true
  echo "Started watcher (pid $(cat "$PIDFILE"))"
}

stop() {
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    kill "$(cat "$PIDFILE")" 2>/dev/null || true
    rm -f "$PIDFILE"
    echo "Stopped watcher"
  else
    echo "Watcher not running"
  fi
}

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  toggle|"")
    if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      stop
    else
      start
    fi
    ;;
  status)
    if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "running (pid $(cat "$PIDFILE"))"
    else
      echo "stopped"
    fi
    ;;
  *) echo "Usage: watch-reload.sh [start|stop|toggle|status]" >&2; exit 1 ;;
esac
