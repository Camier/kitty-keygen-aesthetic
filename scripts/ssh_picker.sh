#!/usr/bin/env bash
# SSH host picker using fzf (if available) and kitten ssh
# Supports session restoration via SSH connection tracking
set -euo pipefail

SSH_DIR=${SSH_CONFIG_DIR:-$HOME/.ssh}
CFG_A=$SSH_DIR/config
CFG_B=${XDG_CONFIG_HOME:-$HOME/.config}/ssh/config
SSH_SESSIONS_DIR=${XDG_CONFIG_HOME:-$HOME/.config}/kitty/sessions/ssh

gather_hosts() {
  awk '/^\s*Host\s+/{for(i=2;i<=NF;i++){h=$i; if(h!~/[\*\?]/){print h}}}' "$@" 2>/dev/null |
    sort -u
}

hosts=$(gather_hosts "$CFG_A" "$CFG_B")

if [[ -z "$hosts" ]]; then
  echo "No hosts found in $CFG_A or $CFG_B" >&2
  exit 1
fi

pick=""
if command -v fzf >/dev/null 2>&1; then
  pick=$(printf "%s\n" "$hosts" | fzf --prompt="ssh host> " --height=40% --reverse)
else
  echo "Select host:" >&2
  select h in $hosts; do
    pick="$h"; break
  done
fi

if [[ -z "${pick:-}" ]]; then
  echo "No selection"
  exit 1
fi

# Save SSH session metadata for restoration
mkdir -p "$SSH_SESSIONS_DIR"
cat > "$SSH_SESSIONS_DIR/${pick}.session" <<EOF
# SSH Session: $pick
# Created: $(date +%Y-%m-%d\ %H:%M:%S)
new_tab SSH: $pick
launch kitten ssh $pick
EOF

exec kitten ssh "$pick"

