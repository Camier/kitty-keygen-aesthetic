#!/usr/bin/env bash
# Show a quick cheat sheet for the Ctrl+Shift+P chord
set -euo pipefail

cat <<'HELP'
P Chord — Quick Guide

Press Ctrl+Shift+P, then one of:

  C  Command Palette
  T  Toggle Tmux Prefix (Ctrl+B <-> Ctrl+A)
  S  Save Session Snapshot
  R  Restore Session Snapshot
  W  Watch & auto reload config (toggle)
  H  SSH Host Picker
  K  Keymap Check report
  D  Dependency Check summary
  B  Battery Saver (toggle)
  F  Auto-scale fonts for DPI
  U  Transfer download (kitty @ remote-transfer)
  Y  Transfer upload (kitty @ remote-transfer --direction=upload)
  M  Status Panel (htop overlay)
  O  (This) Overview

HELP

echo
read -n 1 -r -s -p "Press any key to close"
echo

