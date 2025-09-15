# KEYGEN AESTHETIC SYSTEM
*Authentic demoscene terminal experience for Kitty*

## 🎯 Overview
Complete keygen/demoscene aesthetic implementation with authentic scene group themes, CRT visual effects, and operational modes. Built from extensive research on keygen culture, demo scene aesthetics, and retro computing visuals.

## 🎨 Scene Group Themes
Located in `themes/` directory:

- **Fairlight Cyan** (`fairlight_cyan.conf`) - Classic cyan/blue from Amiga era
- **Skidrow Green** (`skidrow_green.conf`) - Neon green matrix-style
- **Reloaded Magenta** (`reloaded_magenta.conf`) - Hot magenta elite aesthetic
- **Razor Amber** (`razor_amber.conf`) - Warm amber CRT monitor feel

## 🖥️ CRT Visual Effects
Configured in `includes/keygen_visuals.conf`:

- Scanline simulation via background opacity
- Phosphor glow effect with window padding
- Authentic cursor blinking and shape
- Retro typography with font features
- Classic system bell sounds

## ⚡ Effect System
Safe keybinding system in `includes/keygen_effects.conf`:

| Shortcut | Effect |
|----------|--------|
| `Kitty+P` | Plasma effect in new tab |
| `Kitty+A` | ANSI art gallery |
| `Kitty+M` | Tracker music player |
| `Kitty+X` | Matrix scrolling effect |
| `Kitty+C` | Color test patterns |
| `Kitty+1-4` | Quick theme switching |

## 🎮 Operational Modes
Mode switching via `includes/keygen_modes.conf`:

- **F1 - Work Mode**: Professional, subdued aesthetic
- **F2 - Demo Mode**: High-contrast presentation setup
- **F3 - Keygen Mode**: Full demoscene experience

## 🚀 Usage

### Quick Start
```bash
# Launch with keygen mode
kitty --session ~/.config/kitty/sessions/keygen.session

# Switch themes instantly
Kitty+1  # Fairlight cyan
Kitty+2  # Skidrow green
Kitty+3  # Reloaded magenta
Kitty+4  # Razor amber
```

### Effect Controls
```bash
# Plasma effects
Kitty+P         # New tab with plasma
Kitty+Shift+P   # Overlay plasma

# Music & Art
Kitty+M         # Tracker music overlay
Kitty+A         # ANSI art viewer

# Visual tests
Kitty+C         # Color patterns
Kitty+X         # Matrix effect
```

### Mode Switching
```bash
# Quick mode changes
Kitty+F1        # Switch to work mode
Kitty+F2        # Switch to demo mode
Kitty+F3        # Switch to keygen mode

# New windows with modes
Kitty+Shift+F1  # New work session
Kitty+Shift+F2  # New demo session
Kitty+Shift+F3  # New keygen session
```

## 🔧 Architecture
Modular design following Kitty's include system:

```
~/.config/kitty/
├── kitty.conf              # Main config with includes
├── themes/                 # Scene group color schemes
│   ├── fairlight_cyan.conf
│   ├── skidrow_green.conf
│   ├── reloaded_magenta.conf
│   └── razor_amber.conf
├── includes/               # Modular configurations
│   ├── keygen_visuals.conf # CRT effects & styling
│   ├── keygen_effects.conf # Effect keybindings
│   └── keygen_modes.conf   # Mode switching
├── modes/                  # Operational configurations
│   ├── work.conf          # Professional mode
│   ├── demo.conf          # Presentation mode
│   └── keygen.conf        # Full aesthetic mode
├── kittens/               # Custom effect scripts
│   ├── plasma.py          # Plasma effects
│   ├── ansiview.py        # ANSI art viewer
│   └── tracker_play.py    # Music player
└── sessions/              # Preconfigured sessions
    ├── work.session
    ├── demo.session
    └── keygen.session
```

## 🛡️ Security Features
All custom kittens include security validation:
- Path traversal protection
- Input sanitization
- Safe file type checking
- No arbitrary command execution

## 🎵 Audio Support
Tracker music support for authentic keygen experience:
- MOD, XM, S3M, IT format support
- Background music during effects
- Scene music integration

Built with authentic demoscene research and respect for keygen culture.