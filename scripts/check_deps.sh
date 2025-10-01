#!/usr/bin/env bash
set -euo pipefail

ok() { printf "\e[32m✓\e[0m %s\n" "$1"; }
miss() { printf "\e[31m✗\e[0m %s\n" "$1"; }

have() { command -v "$1" >/dev/null 2>&1; }

heading() { printf "\n\e[1m%s\e[0m\n" "$1"; }

reqlist=( kitty python3 )
heading "Required"
for c in "${reqlist[@]}"; do
  if have "$c"; then ok "$c"; else miss "$c"; fi
done

heading "Recommended (improves features)"
rec_msgs=(
  "fzf (profile/ssh pickers)"
  "inotifywait (config watcher)"
  "git (smart titles, git-aware prompts)"
  "htop (sessions/dev tab)"
  "journalctl (logs mapping)"
)
recs=( fzf inotifywait git htop journalctl )
for i in "${!recs[@]}"; do
  c=${recs[$i]}
  m=${rec_msgs[$i]}
  if have "$c"; then ok "$m"; else miss "$m"; fi
done

heading "Alternatives (any one is fine)"
# editors
if have nvim || have vim || have code; then ok "editor (nvim/vim/code)"; else miss "editor (nvim|vim|code)"; fi
# git UIs
if have gitui || have lazygit || have tig; then ok "git UI (gitui/lazygit/tig)"; else miss "git UI (gitui|lazygit|tig)"; fi
# music
if have openmpt123 || have xmp || have mpv; then ok "music player (openmpt123/xmp/mpv)"; else miss "music player (openmpt123|xmp|mpv)"; fi

heading "Install Hints"
cat <<'HINTS'
Fedora:
  sudo dnf install fzf inotify-tools git htop systemd
  # optional:
  sudo dnf install neovim gitui lazygit tig mpv openmpt123 xmp

Debian/Ubuntu:
  sudo apt update && sudo apt install fzf inotify-tools git htop systemd
  # optional:
  sudo apt install neovim gitui tig mpv libopenmpt0 xmp

Arch:
  sudo pacman -S --needed fzf inotify-tools git htop systemd
  # optional:
  sudo pacman -S --needed neovim gitui lazygit tig mpv openmpt xmp

openSUSE:
  sudo zypper install fzf inotify-tools git htop systemd
  # optional:
  sudo zypper install neovim gitui lazygit tig mpv libopenmpt-tools xmp

Notes:
  - journalctl is provided by systemd (already present on most systems)
  - 'code' (VS Code) install varies by distro; use your preferred method
HINTS

