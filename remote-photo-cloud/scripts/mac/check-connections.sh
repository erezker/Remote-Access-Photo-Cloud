#!/usr/bin/env bash
# Harmless reachability checks; does not upload or modify data.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCAL="$ROOT/config/mac.env.local"
if [[ ! -f "$LOCAL" ]]; then
  echo 'Create config/mac.env.local from config/mac.env.example (locally, never in Git).' >&2
  exit 1
fi
# shellcheck disable=SC1090
source "$LOCAL"
: "${IMMICH_URL:?Set IMMICH_URL in config/mac.env.local}"
: "${RDP_HOST:?Set RDP_HOST in config/mac.env.local}"
[[ "$IMMICH_URL" == https://* ]] || { echo 'IMMICH_URL must be HTTPS.' >&2; exit 1; }

status=0
if curl --fail --silent --location --max-time 12 --output /dev/null "$IMMICH_URL"; then
  echo 'OK: Immich HTTPS endpoint reachable through Tailscale.'
else
  echo 'FAIL: Immich HTTPS endpoint unavailable. Check Tailscale, Serve, Docker and Windows.' >&2
  status=1
fi

if nc -z -G 5 "$RDP_HOST" 3389 >/dev/null 2>&1; then
  echo 'OK: Windows RDP port reachable through private network.'
else
  echo 'FAIL: RDP port not reachable. Check Windows power, RDP and Tailscale.' >&2
  status=1
fi

exit "$status"
