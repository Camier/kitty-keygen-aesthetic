#!/usr/bin/env bash
# Toggle smart window dimming on/off
set -euo pipefail

CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty
WATCHER_FILE="$CONFIG_DIR/watchers/activity.py"
STATE_FILE="$CONFIG_DIR/.dimming_enabled"

# Check if dimming is currently enabled
if [[ -f "$STATE_FILE" ]]; then
    # Currently enabled - disable it
    sed -i 's/^        boss.call_remote_control/        # boss.call_remote_control/' "$WATCHER_FILE"
    rm "$STATE_FILE"
    echo "✓ Window dimming disabled"
    echo "  Restart kitty or reload config to apply"
else
    # Currently disabled - enable it
    sed -i 's/^        # boss.call_remote_control/        boss.call_remote_control/' "$WATCHER_FILE"
    touch "$STATE_FILE"
    echo "✓ Window dimming enabled"
    echo "  Restart kitty or reload config to apply"
fi
