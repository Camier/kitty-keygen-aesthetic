#!/usr/bin/env bash
# Show a quick cheat sheet for the Ctrl+Shift+E chord (Hints & Utilities)
set -euo pipefail

cat <<'HELP'
E Chord — Hints & Utilities

Press Ctrl+Shift+E, then one of:

  (E alone)  URL Hints (open links)
  F          File paths (select/copy paths)
  L          Lines (select whole lines)
  W          Words (select single words)
  H          Hashes (git SHAs, checksums)
  E          Open path in editor (VS Code)
  N          Open file at line (file:line)
  C          Copy selected path into cwd
  I          View image from path (icat)
  T          Intelligent Tab Rename
  O          (This) Overview

Tip: Quick image preview: Ctrl+Shift+I (hints picker)
HELP

echo
read -n 1 -r -s -p "Press any key to close"
echo

