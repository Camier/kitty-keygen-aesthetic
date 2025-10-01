# LAB Kitty Configuration

Lean-by-default terminal profile with optional scene-inspired extras. The base `kitty.conf` loads only core UI, key bindings, and performance tuning. Additional modules live under `includes/` and can be opt-in when you need them.

## Quick Facts
- Config root: `~/.config/kitty`
- Main entrypoint: `kitty.conf`
- Reload: press `Ctrl+Shift+F5` or run `kitty @ load-config`
- Remote control socket: `unix:$HOME/.cache/kitty/kitty-$USER.sock` (exported to child shells)
- Automation watcher: `watchers/activity.py` keeps tab titles in sync with running commands
- Local overrides: drop `.conf` files in `local/`; they load last

## Everyday Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+Enter` | New window in current working dir |
| `Ctrl+Shift+T` | New tab |
| `Ctrl+Shift+[` / `]` | Previous / next window |
| `Ctrl+Shift+Left` / `Right` | Previous / next tab |
| `Ctrl+Shift+F5` | Reload configuration |
| `Right Click` | Select entire command output (shell integration) |
| `F1` | Show last command output |
| `Ctrl+Shift+F2` | Open config file in editor |

Full bindings live in `includes/keymaps.conf` (grouped by feature area).

## Profiles & Toggles
Trigger these from the command palette (`Ctrl+Shift+P`) or the dedicated keys:
- Low-latency mode: `Ctrl+Shift+F2` → writes `local/perf-low.conf`
- Focus follows mouse: `Ctrl+Shift+F3` → toggles `local/focus-follows-mouse.conf`
- Tmux passthrough: `Ctrl+Shift+F4` → toggles `local/tmux-passthrough.conf`
- Battery saver: `Ctrl+Shift+P`, `B` → toggles `local/battery.conf`
- Font autoscale: `Ctrl+Shift+P`, `F`
- Watch + auto reload: `Ctrl+Shift+P`, `W` (uses `scripts/watch-reload.sh`)
- Transfer helpers: `Ctrl+Shift+P`, `U` downloads, `Y` uploads via `kitty @ remote-transfer`
- Status panel: `Ctrl+Shift+P`, `M` toggles the htop panel
- Broadcast input: `Ctrl+Shift+B` targets all panes in the current tab

`local/README.md` documents every generated override. Removing a file restores the upstream default.

## Directory Map
```
~/.config/kitty/
├── kitty.conf                # Main orchestrator
├── includes/                 # Modular configuration blocks
│   ├── core.conf             # Shared shell + socket settings
│   ├── ui.conf               # Fonts, window chrome, URL handling
│   ├── keymaps.conf          # Primary key bindings
│   └── perf.conf             # Balanced performance defaults
├── themes/                   # Color schemes
├── kittens/                  # Local helper kittens (palette, help center, utilities)
├── scripts/                  # Utility scripts (toggles, remote control helpers)
├── modes/                    # Standalone profiles for work/demo/etc
├── sessions/                 # Prebuilt session layouts
└── local/                    # Auto-generated overrides (gitignored)
```

## Maintenance Tips
- Use `kitty +kitten diff-conf` to inspect live settings versus files.
- `scripts/watch-reload.sh` relies on `inotifywait`; install `inotify-tools` for best results.
- Keep `kitty --version` at ≥ `0.42.2` to ensure `shell_integration enabled` stays compatible.

## Troubleshooting
| Symptom | Check |
|---------|-------|
| Remote control failures | Socket value: `echo $KITTY_LISTEN_ON`; should be `unix:$HOME/.cache/kitty/kitty-$USER.sock` |
| Config reload prints errors | Run `kitty +kitten debug-config` to locate parse issues |
| Watcher doesn’t reload | Ensure `inotifywait` is installed or rerun `watch-reload.sh start` |

Enjoy the clean base setup, and opt into the flashy bits only when you need them.
