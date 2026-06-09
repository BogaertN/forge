#!/usr/bin/env bash
set -euo pipefail
SRC="/home/nic/forge/desktop_entries/aiweb-os-operator-console.desktop"
APP_DST="/home/nic/.local/share/applications/aiweb-os-operator-console.desktop"
DESK_DST="/home/nic/Desktop/AI.Web OS Operator Console.desktop"
if [ ! -f "$SRC" ]; then
  echo "Missing desktop entry source: $SRC" >&2
  exit 1
fi
mkdir -p /home/nic/.local/share/applications /home/nic/Desktop
cp "$SRC" "$APP_DST"
cp "$SRC" "$DESK_DST"
chmod +x "$APP_DST" "$DESK_DST"
if command -v gio >/dev/null 2>&1; then
  gio set "$DESK_DST" metadata::trusted true >/dev/null 2>&1 || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database /home/nic/.local/share/applications >/dev/null 2>&1 || true
fi
echo "Installed: $APP_DST"
echo "Installed: $DESK_DST"
