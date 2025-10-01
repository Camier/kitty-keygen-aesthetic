#!/usr/bin/env bash
# Interactive wrapper around kitty @ remote-transfer for the focused SSH tab
set -euo pipefail

if [[ ${1:-} =~ ^(-h|--help)$ ]]; then
  cat <<'HELP'
Usage: transfer_helper.sh [download|upload]

Selects the previously focused window (usually your SSH session) via
`--match recent:1` and drives `kitty @ remote-transfer` for you.
HELP
  exit 0
fi

choice=${1:-}
if [[ -z $choice ]]; then
  read -rp "Direction ([d]ownload remote->local, [u]pload local->remote): " choice
fi

case ${choice,,} in
  d|download)
    read -rp "Remote source path: " remote_path
    if [[ -z $remote_path ]]; then
      echo "Remote path is required" >&2
      exit 1
    fi
    default_local="$HOME/Downloads/$(basename "$remote_path")"
    read -rp "Local destination [${default_local}]: " local_path
    local_path=${local_path:-$default_local}
    mkdir -p "$(dirname "$local_path")"
    exec kitty @ remote-transfer --match recent:1 "$remote_path" "$local_path"
    ;;
  u|upload)
    read -rp "Local source path: " local_path
    if [[ -z $local_path ]]; then
      echo "Local path is required" >&2
      exit 1
    fi
    read -rp "Remote destination path: " remote_path
    if [[ -z $remote_path ]]; then
      echo "Remote destination is required" >&2
      exit 1
    fi
    exec kitty @ remote-transfer --match recent:1 --direction=upload "$local_path" "$remote_path"
    ;;
  *)
    echo "Unknown choice: $choice" >&2
    exit 1
    ;;
esac
