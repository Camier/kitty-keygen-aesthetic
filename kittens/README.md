# Kitty Kittens

Custom kittens for enhanced Kitty terminal functionality.

## Interactive Kittens

| Kitten | Description | Keybinding |
| --- | --- | --- |
| **command_palette.py** | Quick access to common window/tab actions and config utilities | `Ctrl+Shift+P, C` |
| **theme_picker.py** | Interactive theme browser with fuzzy search across all available themes | `Ctrl+Shift+P, T` |
| **layout_presets.py** | Quick window layout switching (Single, VSplit, HSplit, Grid, Main+Side, Triple Column) | `Ctrl+Shift+P, G` |
| **clipboard_history.py** | Browse and paste from clipboard history (integrates with clipman/copyq/clipster) | `Ctrl+Shift+Alt+V` |
| **help_center.py** | Searchable help center for Kitty configuration and features | `Ctrl+Shift+F9` |

## Utility Kittens

| Kitten | Description | Usage |
| --- | --- | --- |
| **long_task.py** | Wrap long-running commands with notifications on completion | `python3 long_task.py <threshold_seconds> -- <command>` |

## Features

### Command Palette (`command_palette.py`)
Provides quick access to:
- Window management (new tab/window, splits, fullscreen, maximize)
- Configuration tools (edit config, reload, debug)
- Help center access

**Usage**: Press `Ctrl+Shift+P, C`, type to filter, Enter to execute

### Theme Picker (`theme_picker.py`)
- Fuzzy search across 20+ available themes
- Live preview of current theme
- Vim-style navigation (j/k or arrow keys)
- Instant apply with config reload

**Usage**: Press `Ctrl+Shift+P, T`, type to filter, Enter to apply

### Layout Presets (`layout_presets.py`)
Quick layouts:
- **Single**: One full window
- **VSplit**: Two windows side-by-side
- **HSplit**: Two windows stacked
- **Grid 2x2**: Four windows in grid
- **Main+Side**: Large main window with sidebar
- **Triple Column**: Three columns

**Usage**: Press `Ctrl+Shift+P, G`, select layout, Enter to apply

### Clipboard History (`clipboard_history.py`)
- Integrates with system clipboard managers:
  - **clipman** (Wayland)
  - **CopyQ** (cross-platform)
  - **clipster** (X11)
- Falls back to Kitty's built-in clipboard
- Number shortcuts (1-9) for quick selection
- Truncates long entries for display

**Usage**: Press `Ctrl+Shift+Alt+V`, navigate, Enter to paste

### Long Task Wrapper (`long_task.py`)
- Monitors command execution time
- Marks tab with ⏳ when threshold exceeded
- Sends desktop notification on completion (success ✅ or failure ❌)
- Shows duration in notification

**Example**:
```bash
python3 ~/.config/kitty/kittens/long_task.py 10 -- make -j8
# Notifies if build takes longer than 10 seconds
```

## Architecture

All interactive kittens follow Kitty's kitten API:
- `main(args)` → Returns user selection
- `handle_result(args, answer, window_id, boss)` → Applies the selection

This ensures consistent behavior and proper integration with Kitty's event loop.
