Local overrides
===============

Any `.conf` files here are loaded at the end of `kitty.conf` and override earlier settings.

Common toggles created by scripts:
- `perf-low.conf` — enables low-latency profile (sync_to_monitor no, repaint_delay 2)
- `focus-follows-mouse.conf` — toggles `focus_follows_mouse` yes/no (file absent means default `yes`)

These files are managed by:
- `scripts/toggle_perf_profile.sh`
- `scripts/toggle_focus_follows_mouse.sh`

You can add your own overrides here as needed.

