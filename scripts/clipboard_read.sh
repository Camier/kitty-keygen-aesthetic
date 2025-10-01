#!/usr/bin/env bash
set -euo pipefail
use_primary="no"
mime='text/*'

usage() {
  cat <<USAGE
Usage: clipboard_read.sh [--primary] [--mime TYPE]
Outputs clipboard contents (default text/*) to STDOUT via kitty clipboard kitten.
USAGE
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --primary) use_primary="yes"; shift ;;
    --mime) mime=$2; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option $1" >&2; usage; exit 1 ;;
  esac
done

cmd=("kitty" "+kitten" "clipboard" "--get-clipboard" "--mime" "$mime")
if [[ $use_primary == yes ]]; then
  cmd+=("--use-primary")
fi
"${cmd[@]}"
