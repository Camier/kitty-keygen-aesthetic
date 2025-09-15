Kitty Keygen Aesthetic — Quick Guide

Assets
- ANSI/NFO/TXT artwork: ~/.config/kitty/art
- Tracker modules (MOD/XM/S3M/IT): ~/.config/kitty/music

Themes
- Active theme: themes/current-theme.conf (auto-included by kitty.conf)
- Theme Gallery (overlay): Ctrl+Shift+F6 → browse, preview, apply
- Theme Cycle: Ctrl+Shift+F1 (next), Ctrl+Shift+Shift+F1 (prev)
- Quick switch:
  - Ctrl+Shift+Ctrl+1 → fairlight_cyan
  - Ctrl+Shift+Ctrl+2 → skidrow_green
  - Ctrl+Shift+Ctrl+3 → reloaded_magenta
  - Ctrl+Shift+Ctrl+4 → razor_amber
- Safe apply script: kittens/theme_apply.py (updates current-theme and reloads)
 - Wal bridge: builds themes/wal-current.conf from wal and sets current-theme

Effects and Tools
- Ctrl+Shift+P/O/S → Plasma/Fire/Scroller
- Ctrl+Shift+M → Play a random module
- Ctrl+Shift+Alt+M → Loop random modules
  - Requires player: openmpt123 (recommended), xmp, or mpv
  - Fedora: sudo dnf install openmpt123 xmp mpv
  - Note: Some ffmpeg/ffplay builds cannot decode .it/.xm/.s3m/.mod
  - Sample file: ~/.config/kitty/music/demo.it (placeholder, may be empty)
Music controls
- Ctrl+Shift+Shift+M → Music Picker (overlay)
- Ctrl+Shift+Ctrl+Alt+., Ctrl+Shift+Ctrl+Alt+, → Next/Prev track
- Ctrl+Shift+Ctrl+Alt+S → Toggle shuffle

Layout & Navigation
- Ctrl+Shift+Space → cycle layouts
- Ctrl+Shift+Ctrl+H/J/K/L → focus left/down/up/right
- Ctrl+Shift+Ctrl+Shift+H/J/K/L → swap windows left/down/up/right
- Ctrl+Shift+Shift+T → toggle tab bar

Backgrounds
- Background Gallery (overlay): Ctrl+Shift+F7 → browse/preview/apply images from ~/Pictures
- Clear background: press 'n' inside the gallery or remove generated/background.conf
 - Wal theme from wallpaper: Ctrl+Shift+Alt+W (apply), Ctrl+Shift+Alt+Shift+W (restore)
   - Requires pywal (pip install --user pywal); uses current background image when run without args

Help
- Help Center (overlay): Ctrl+Shift+F9 → searchable, scrollable help for all features

Kitten Menu
- Ctrl+Shift+F8 → command palette for local kittens (Theme/Background galleries, Plasma, Fire, Scroller, ANSI, Tracker, etc.)

Command Palette
- Ctrl+Shift+P then P → global command palette (search actions: windows/tabs/splits, themes, backgrounds, sessions, modes, effects)

Ambient Theme
- Ctrl+Shift+P then A → apply ambient theme (time-of-day)

Long Tasks
- Wrapper kitten: python3 ~/.config/kitty/kittens/long_task.py 10 -- <cmd>
  - Marks tab while running; bell on completion; prints duration
  - Tip: combine with notify_on_cmd_finish (enabled) for desktop notifications

Notes
- Theme browser, font picker, and ANSI viewer hotkeys are disabled by default for stability.
- For presentations: start Demo/Keygen modes (see modes/*.conf) which use low-latency performance.
