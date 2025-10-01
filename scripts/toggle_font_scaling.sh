#!/usr/bin/env bash
# Toggle dynamic font scaling on/off
set -euo pipefail

CONFIG_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty
WATCHER_FILE="$CONFIG_DIR/watchers/activity.py"
STATE_FILE="$CONFIG_DIR/.font_scaling_enabled"

# Check if font scaling is currently enabled
if [[ -f "$STATE_FILE" ]]; then
    # Currently enabled - disable it
    sed -i '131,140s/^    #/    # #/' "$WATCHER_FILE"
    sed -i '131,140s/^    \([^#]\)/    # \1/' "$WATCHER_FILE"
    rm "$STATE_FILE"
    echo "✓ Dynamic font scaling disabled"
    echo "  Restart kitty or reload config to apply"
else
    # Currently disabled - enable it
    sed -i '131,140s/^    # #/    #/' "$WATCHER_FILE"
    sed -i '131,140s/^    # \([^#]\)/    \1/' "$WATCHER_FILE"
    touch "$STATE_FILE"
    echo "✓ Dynamic font scaling enabled"
    echo "  Restart kitty or reload config to apply"
fi
