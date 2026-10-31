#!/data/data/com.termux/files/usr/bin/sh
# Run on the Android relay only. Secrets stay in the phone's private config.
set -eu
CONFIG="$HOME/.config/remote-photo-cloud/wol.env"
if [ ! -f "$CONFIG" ]; then
  printf '%s\n' 'Missing private phone config: ~/.config/remote-photo-cloud/wol.env' >&2
  exit 1
fi
set -a
# File is created and controlled only by the operator on their own device.
. "$CONFIG"
set +a
if [ -z "${TARGET_MAC:-}" ]; then
  printf '%s\n' 'TARGET_MAC is not configured.' >&2
  exit 1
fi
exec python "$HOME/wake_pc.py"
