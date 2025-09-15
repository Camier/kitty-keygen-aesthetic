#!/bin/bash
# Safe Kitty launcher for dual GPU + Wayland systems

echo "🔧 Launching Kitty with GPU-safe settings..."

# Force Intel GPU (avoid NVIDIA conflicts)
export __GLX_VENDOR_LIBRARY_NAME=mesa
export DRI_PRIME=0

# Force X11 (avoid Wayland issues)
export QT_QPA_PLATFORM=xcb
export GDK_BACKEND=x11

# Launch with safe config
kitty --config="/home/miko/.config/kitty/kitty-gpu-safe.conf" "$@"
