#!/bin/bash
# Debug script for Kitty crashes

echo "Kitty Debug Information"
echo "======================"
echo "Date: $(date)"
echo "Kitty version: $(kitty --version)"
echo "System: $(uname -a)"
echo

echo "Testing minimal configuration..."
echo "Command: kitty --config=/home/miko/.config/kitty/kitty-minimal.conf --debug-input --detach"
echo

# Try to run kitty with minimal config and debugging
if kitty --config=/home/miko/.config/kitty/kitty-minimal.conf --debug-input --detach 2>&1; then
    echo "✓ Minimal config works"
else
    echo "✗ Minimal config failed"
fi

echo
echo "Checking for core dumps..."
find /tmp /var/crash ~ -name "*kitty*core*" -o -name "core.*kitty*" 2>/dev/null | head -5

echo
echo "Checking system logs..."
journalctl --user -u kitty* --since "1 hour ago" --no-pager -n 20 2>/dev/null || echo "No systemd logs found"

echo
echo "Memory and resource usage:"
ps aux | grep kitty | head -5

echo
echo "GPU information (if relevant):"
lspci | grep -i vga || echo "No VGA info"