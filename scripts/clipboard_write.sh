#!/usr/bin/env bash
set -euo pipefail
human_name="kitty clipboard helper"
password=""
use_primary="no"
cache_file="$HOME/.cache/kitty/clipboard.pass"
restore_password="no"

usage() {
  cat <<USAGE
Usage: clipboard_write.sh [--primary] [--password TEXT] [--cache yes|no] [files...]
Pipe data on stdin or pass files to copy them to the clipboard via kitty.
USAGE
}

args=( )
while [[ $# -gt 0 ]]; do
  case "$1" in
    --primary) use_primary="yes"; shift ;;
    --password) password=$2; shift 2 ;;
    --cache) restore_password=$2; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) args+=("$1"); shift ;;
  esac
done

if [[ $restore_password == yes && -f $cache_file && -z $password ]]; then
  password=$(<"$cache_file")
fi

cmd=("kitty" "+kitten" "clipboard")
[[ $use_primary == yes ]] && cmd+=("--use-primary")
if [[ -n $password ]]; then
  cmd+=("--password" "text:$password" "--human-name" "$human_name")
  mkdir -p "$(dirname "$cache_file")"
  printf '%s' "$password" > "$cache_file"
fi
if [[ ${#args[@]} -gt 0 ]]; then
  cmd+=("${args[@]}")
fi

if [[ ${#args[@]} -eq 0 ]]; then
  "${cmd[@]}" --wait-for-completion
else
  "${cmd[@]}"
fi
