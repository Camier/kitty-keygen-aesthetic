#!/usr/bin/env bash
# Unified helper for kitty remote control commands.
set -euo pipefail

socket=${KITTY_LISTEN_ON:-unix:$HOME/.cache/kitty/kitty-$USER.sock}
cmd=${1:-}
shift || true

usage() {
  cat <<USAGE
Usage: kitty-rc.sh <command> [options]
Commands:
  launch   Launch/focus windows or tabs
  pipe     Pipe stdin text into a matched window
  focus    Focus a window/tab via match
  reload   Reload kitty configuration
  profile  Launch a new kitty instance with a named profile
USAGE
}

launch() {
  local title="" match="" launch_type="window" cwd="" keep_focus="yes" command=""
  while [[ $# -gt 0 ]]; do
    case $1 in
      --title) title=$2; shift 2 ;;
      --match) match=$2; shift 2 ;;
      --type) launch_type=$2; shift 2 ;;
      --cwd) cwd=$2; shift 2 ;;
      --keep-focus) keep_focus=$2; shift 2 ;;
      --command) command=$2; shift 2 ;;
      -h|--help)
        cat <<HELP
kitty-rc launch [options]
  --title TITLE
  --match REGEX
  --type window|tab|os-window|overlay
  --cwd PATH
  --keep-focus yes|no (default yes)
  --command "shell command" (required)
HELP
        return 0 ;;
      *) echo "kitty-rc launch: unknown option $1" >&2; return 1 ;;
    esac
  done
  if [[ -z $command ]]; then
    echo "kitty-rc launch: --command is required" >&2
    return 1
  fi
  if [[ -n $match ]]; then
    kitty @ --to "$socket" focus-window --match "$match" >/dev/null 2>&1 || true
  fi
  launch_cmd=(kitty @ --to "$socket" launch --type="$launch_type")
  [[ -n $title ]] && launch_cmd+=(--title "$title")
  [[ $keep_focus == no ]] && launch_cmd+=(--keep-focus=no)
  [[ -n $cwd ]] && launch_cmd+=(--cwd "$cwd")
  launch_cmd+=(bash -lc "$command")
  "${launch_cmd[@]}"
}

pipe() {
  local match="" paste_mode="disable"
  while [[ $# -gt 0 ]]; do
    case $1 in
      --match) match=$2; shift 2 ;;
      --bracketed) paste_mode=$2; shift 2 ;;
      -h|--help)
        cat <<HELP
kitty-rc pipe --match 'title:^Output' [--bracketed disable|auto|enable]
Reads stdin and sends to matched window.
HELP
        return 0 ;;
      *) echo "kitty-rc pipe: unknown option $1" >&2; return 1 ;;
    esac
  done
  if [[ -z $match ]]; then
    echo "kitty-rc pipe: --match is required" >&2
    return 1
  fi
  kitty @ --to "$socket" send-text --match "$match" --stdin --bracketed-paste="$paste_mode"
}

focus() {
  if [[ $# -lt 1 ]]; then
    echo "kitty-rc focus 'title:^Logs'" >&2
    return 1
  fi
  kitty @ --to "$socket" focus-window --match "$1"
}

case $cmd in
  launch) launch "$@" ;;
  pipe) pipe "$@" ;;
  focus) focus "$@" ;;
  reload)
    # Try remote reload; fall back to message
    if kitty @ --to "$socket" load-config 2>/dev/null; then
      echo "Config reloaded via kitty @ load-config"
    else
      echo "Could not reload via remote; press your reload key (e.g. Ctrl+Shift+F5)"
    fi
    ;;
  profile)
    if [[ $# -lt 1 ]]; then
      echo "Usage: kitty-rc profile <default|work|demo|stable|gpu-safe|minimal> [-- kitty-args]" >&2
      exit 1
    fi
    exec "$(dirname "$0")/kitty-profile" "$@"
    ;;
  -h|--help|"") usage ;;
  *) echo "Unknown kitty-rc command: $cmd" >&2; usage; exit 1 ;;
esac
