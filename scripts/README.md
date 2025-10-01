# Kitty Scripts

## Core Utilities

| Script | Description | Keybinding |
| --- | --- | --- |
| kitty-rc.sh | Unified remote control helper (`launch`, `pipe`, `focus`) | - |
| kitty-profile | Launch Kitty with named profiles (`default`, `work`, `demo`, `stable`, `gpu-safe`, `minimal`) | - |
| smart_tab_title.py | Intelligent tab renaming with project context detection (Python 🐍, Node ⬢, Rust 🦀, etc.) | `Ctrl+Shift+E, T` |
| check-keymaps.sh | Report duplicate/overlapping keymaps across global and mode profiles | `Ctrl+Shift+P, K` |
| check_deps.sh | Check required/recommended tools and suggest install commands | `Ctrl+Shift+P, D` |

## Session Management

| Script | Description | Keybinding |
| --- | --- | --- |
| session_snapshot.sh | Save/restore sessions with `--startup`, `--output`, `--restore` flags | `Ctrl+Shift+P, S` (save)<br>`Ctrl+Shift+P, R` (restore)<br>`Ctrl+Shift+P, L` (save as startup) |
| watch-reload.sh | Watch config for changes and auto-reload (toggle/start/stop) | `Ctrl+Shift+P, W` |

## SSH Integration

| Script | Description | Keybinding |
| --- | --- | --- |
| ssh_picker.sh | Fuzzy-pick SSH host from `~/.ssh/config` and run `kitten ssh` with session tracking | `Ctrl+Shift+P, H` |
| ssh_restore.sh | Restore previously saved SSH sessions from `sessions/ssh/` | `Ctrl+Shift+P, Shift+H` |

## Clipboard

| Script | Description | Keybinding |
| --- | --- | --- |
| clipboard_write.sh | Copy stdin or files to system clipboard (OSC 52 / 22) | - |
| clipboard_read.sh | Read clipboard MIME contents | - |

## Toggle Scripts

| Script | Description | Keybinding |
| --- | --- | --- |
| toggle_perf_profile.sh | Toggle low-latency performance overrides | `Ctrl+Shift+F2` |
| toggle_focus_follows_mouse.sh | Toggle `focus_follows_mouse` | `Ctrl+Shift+F3` |
| toggle_tmux_passthrough.sh | Toggle tmux-aware chord keymaps (`Ctrl+Shift+G`) | `Ctrl+Shift+F4` |
| toggle_tmux_prefix.sh | Toggle tmux prefix between Ctrl+B and Ctrl+A | - |
| toggle_battery_saver.sh | Toggle battery-saver overrides | `Ctrl+Shift+P, B` |
| toggle_window_dimming.sh | Toggle smart window dimming for unfocused windows | `Ctrl+Shift+F6` |
| toggle_font_scaling.sh | Toggle dynamic font scaling based on window width | `Ctrl+Shift+P, Shift+F` |

## Tmux Integration

| Script | Description | Commands |
| --- | --- | --- |
| tmux_send.sh | Send tmux commands with enhanced status display | `prefix`, `copy`, `paste`, `left/down/up/right`, `vsplit`, `hsplit`, `kill`, `other`, `new`, `next`, `prev`, `detach`, `status` |

## Utility Scripts

| Script | Description | Keybinding |
| --- | --- | --- |
| auto_scale.sh | Auto-scale font/line-height based on DPI/scale | `Ctrl+Shift+P, F` |
| transfer_helper.sh | Interactive wrapper around `kitty @ remote-transfer` | `Ctrl+Shift+P, U` (download)<br>`Ctrl+Shift+P, Y` (upload) |
| p_chord_cheatsheet.sh | Overlay cheatsheet summarising `Ctrl+Shift+P` bindings | `Ctrl+Shift+P, O` |
| e_chord_cheatsheet.sh | Overlay cheatsheet summarising `Ctrl+Shift+E` bindings | `Ctrl+Shift+E, O` |

## New Features (2025)

### Enhanced Project Context Detection
- **smart_tab_title.py** now detects project types via marker files
- Shows visual icons: 🐍 (Python), ⬢ (Node.js), 🦀 (Rust), 🐹 (Go), 🔨 (Make), ⚙️ (CMake), 🐳 (Docker)
- Works in both git and non-git directories

### Session Persistence
- **Startup session** support via `startup_session ~/.config/kitty/sessions/last.session`
- Auto-saves on last window close via activity watcher
- Manual save as startup: `session_snapshot.sh --startup`

### SSH Session Restoration
- Automatically tracks SSH connections in `sessions/ssh/`
- Restore previous SSH sessions with `ssh_restore.sh`
- Integrates with fuzzy finder (fzf) for quick selection
