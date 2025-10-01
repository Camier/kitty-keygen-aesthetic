# Kitty Configuration Troubleshooting

## Issue: Ctrl+Shift+P Chord Bindings Not Working

### Understanding Chord Bindings

Chord bindings are **two-step key sequences**, NOT simultaneous key presses.

#### ✅ Correct Usage:
```
1. Press and hold: Ctrl+Shift+P
2. Release all keys
3. Press: T (for theme picker)
```

#### ❌ Incorrect Usage:
```
1. Press and hold: Ctrl+Shift+P+T (all at once)
   → This won't work!
```

---

## Quick Diagnostics

### Step 1: Check Configuration Status

Press `Ctrl+Shift+P`, then press `?` (question mark)

This runs the diagnostic script showing:
- How many chord bindings are defined
- Common issues
- Available shortcuts

### Step 2: Reload Configuration

**Option A**: Live reload
```
Press: Ctrl+Shift+F5
```

**Option B**: Restart Kitty
```bash
# Close all Kitty windows and restart
```

### Step 3: Test Basic Chord

Try the simplest chord first:

```
1. Press: Ctrl+Shift+P
2. Release
3. Press: O (letter O for "cheatsheet")
```

This should open the P chord cheatsheet overlay.

---

## Common Issues

### 1. "Nothing happens when I press Ctrl+Shift+P"

**Diagnosis**: Config not loaded

**Solution**:
```bash
# Reload configuration
Press: Ctrl+Shift+F5

# Or restart Kitty completely
```

**Verification**:
```bash
# Run diagnostic
Ctrl+Shift+P, then ?
```

### 2. "I press Ctrl+Shift+P+T but nothing happens"

**Diagnosis**: Pressing keys simultaneously instead of sequentially

**Solution**:
1. Press `Ctrl+Shift+P`
2. **Release all keys**
3. Press `T` alone

**Think of it like**: "Ctrl+Shift+P *THEN* T" (not "AND")

### 3. "Works in some tabs but not others"

**Diagnosis**: Running inside nested terminal (tmux/screen)

**Solution**:
- Tmux users: Enable tmux passthrough with `Ctrl+Shift+F4`
- Screen users: These bindings won't work inside screen
- SSH sessions: Should work fine with `kitten ssh`

### 4. "Chord bindings work but specific actions fail"

**Diagnosis**: Script or kitten has an error

**Solution**:
```bash
# Check for Python errors
python3 ~/.config/kitty/kittens/theme_picker.py

# Check for shell script errors
bash ~/.config/kitty/scripts/session_snapshot.sh --help
```

---

## Environment Checks

### Check 1: Are you in Kitty?

```bash
echo $TERM
# Should output: xterm-kitty
```

If not `xterm-kitty`, you're not in Kitty terminal.

### Check 2: Is remote control enabled?

```bash
# Check if socket exists
ls -la ~/.cache/kitty/kitty-$USER.sock
```

Should show a socket file. If missing, check `includes/ui.conf`:
```conf
allow_remote_control  socket-only
listen_on             unix:$HOME/.cache/kitty/kitty-$USER.sock
```

### Check 3: Config file syntax

```bash
# Check for syntax errors in keymaps
grep -E "^map kitty_mod\+p>" ~/.config/kitty/includes/keymaps.conf
```

Should show multiple lines starting with `map kitty_mod+p>`

---

## Manual Testing

### Test Theme Picker Directly

```bash
# Run the theme picker kitten manually
python3 ~/.config/kitty/kittens/theme_picker.py
```

**Expected**: Interactive theme browser opens
**If error**: Check Python syntax and imports

### Test Command Palette Directly

```bash
# Run command palette manually
python3 ~/.config/kitty/kittens/command_palette.py
```

**Expected**: Command palette opens
**If error**: Fix Python errors first

### Test Layout Presets Directly

```bash
# Run layout presets manually
python3 ~/.config/kitty/kittens/layout_presets.py
```

**Expected**: Layout picker opens
**If error**: Verify Kitty Boss import works

---

## Keybinding Reference

### Working Chord Bindings

All bindings are **sequential**, not simultaneous:

| First Press | Then Press | Action |
|-------------|------------|--------|
| `Ctrl+Shift+P` | `C` | Command palette |
| `Ctrl+Shift+P` | `T` | Theme picker |
| `Ctrl+Shift+P` | `G` | Layout presets |
| `Ctrl+Shift+P` | `S` | Save session |
| `Ctrl+Shift+P` | `R` | Restore session |
| `Ctrl+Shift+P` | `L` | Save startup session |
| `Ctrl+Shift+P` | `H` | SSH host picker |
| `Ctrl+Shift+P` | `O` | Cheatsheet |
| `Ctrl+Shift+P` | `?` | Diagnostic tool |

### Alternative Access Methods

If chord bindings aren't working, you can run features directly:

#### Theme Picker
```bash
kitty @ launch --type=overlay --title="Theme Picker" \
  python3 ~/.config/kitty/kittens/theme_picker.py
```

#### Layout Presets
```bash
kitty @ launch --type=overlay --title="Layout Presets" \
  python3 ~/.config/kitty/kittens/layout_presets.py
```

#### Session Save
```bash
~/.config/kitty/scripts/session_snapshot.sh
```

---

## Advanced Debugging

### Enable Debug Output

```bash
# Run Kitty with debug output
kitty --debug-keyboard
```

This shows all key events. Press `Ctrl+Shift+P` and watch for:
```
key_event: ctrl+shift+p pressed
key_event: t pressed
```

### Check Loaded Config

```bash
# Dump effective configuration
kitty @ load-config --help
```

### Verify Python Environment

```bash
# Check Python version (needs 3.7+)
python3 --version

# Test imports
python3 -c "from kitty.boss import Boss; print('OK')"
```

---

## Still Not Working?

### Reset to Defaults

1. **Backup current config**:
```bash
cp -r ~/.config/kitty ~/.config/kitty.backup.$(date +%Y%m%d)
```

2. **Test minimal config**:
```bash
# Create test file
cat > /tmp/test-kitty.conf <<'EOF'
kitty_mod ctrl+shift
map kitty_mod+p>t launch --type=overlay python3 -c "print('Chord works!')"
EOF

# Test with minimal config
kitty --config /tmp/test-kitty.conf
```

3. **If test works**: Issue is in your main config
4. **If test fails**: Check Kitty version/installation

### Check Kitty Version

```bash
kitty --version
```

Minimum version for all features: **0.26.0**

---

## Getting Help

### Diagnostic Information

When asking for help, provide:

```bash
# 1. Kitty version
kitty --version

# 2. OS/Distribution
uname -a
cat /etc/os-release | grep PRETTY_NAME

# 3. Config check
grep -E "^kitty_mod |^map kitty_mod\+p>" ~/.config/kitty/includes/keymaps.conf | head -5

# 4. Error output
python3 ~/.config/kitty/kittens/theme_picker.py 2>&1
```

### Support Resources

- **Official Docs**: https://sw.kovidgoyal.net/kitty/
- **GitHub Issues**: https://github.com/kovidgoyal/kitty/issues
- **Config Docs**: `~/.config/kitty/scripts/README.md`

---

## Quick Fixes Summary

| Problem | Quick Fix | Verification |
|---------|-----------|--------------|
| No response | `Ctrl+Shift+F5` | Try `Ctrl+Shift+P, O` |
| Simultaneous press | Press sequentially | Watch your key timing |
| Inside tmux | `Ctrl+Shift+F4` | Check tmux passthrough |
| Python error | `python3 -m py_compile kittens/*.py` | No output = OK |
| Script error | `bash -n scripts/*.sh` | No output = OK |

---

*Last updated: 2025-10-01*
