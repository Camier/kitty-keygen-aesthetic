#!/usr/bin/env bash
# Test chord bindings by showing active keymaps
set -euo pipefail

echo "═══════════════════════════════════════════"
echo "  Kitty Chord Binding Diagnostic"
echo "═══════════════════════════════════════════"
echo ""
echo "Checking configuration..."
echo ""

# Check kitty_mod definition
KITTY_MOD=$(grep -E "^kitty_mod " ~/.config/kitty/includes/keymaps.conf 2>/dev/null | awk '{print $2}')
echo "✓ kitty_mod is set to: $KITTY_MOD"
echo ""

# Count P chord bindings
P_CHORD_COUNT=$(grep -cE "^map kitty_mod\+p>" ~/.config/kitty/includes/keymaps.conf 2>/dev/null || echo "0")
echo "✓ Found $P_CHORD_COUNT 'Ctrl+Shift+P' chord bindings"
echo ""

# Count E chord bindings
E_CHORD_COUNT=$(grep -cE "^map kitty_mod\+e>" ~/.config/kitty/includes/keymaps.conf 2>/dev/null || echo "0")
echo "✓ Found $E_CHORD_COUNT 'Ctrl+Shift+E' chord bindings"
echo ""

echo "═══════════════════════════════════════════"
echo "  How to Use Chord Bindings"
echo "═══════════════════════════════════════════"
echo ""
echo "Chord bindings require TWO sequential key presses:"
echo ""
echo "1. Press and release: Ctrl+Shift+P"
echo "2. Then press: T (for theme picker)"
echo ""
echo "⚠️  Common Issues:"
echo ""
echo "• Config not reloaded"
echo "  → Press: Ctrl+Shift+F5"
echo "  → Or restart Kitty"
echo ""
echo "• Pressing keys simultaneously"
echo "  → Must be SEQUENTIAL, not simultaneous"
echo "  → Press Ctrl+Shift+P, RELEASE, then press T"
echo ""
echo "• Wrong terminal"
echo "  → These bindings only work in Kitty terminal"
echo "  → Not in tmux, not in nested terminals"
echo ""
echo "═══════════════════════════════════════════"
echo "  Available Ctrl+Shift+P Chords"
echo "═══════════════════════════════════════════"
echo ""
grep -E "^map kitty_mod\+p>" ~/.config/kitty/includes/keymaps.conf 2>/dev/null | \
  sed 's/map kitty_mod+p>//; s/launch.*title="\([^"]*\)".*/→ \1/' | \
  awk '{key=$1; $1=""; printf "  P, %-10s %s\n", toupper(key), $0}'
echo ""
echo "═══════════════════════════════════════════"
echo "  Test Steps"
echo "═══════════════════════════════════════════"
echo ""
echo "1. Reload config: Ctrl+Shift+F5"
echo "2. Try theme picker: Ctrl+Shift+P, then T"
echo "3. If still fails, restart Kitty completely"
echo ""
echo "Press any key to exit..."
read -n 1 -r -s
