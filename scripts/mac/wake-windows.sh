#!/usr/bin/env bash
# Trigger the Android relay via a private SSH host alias; no device details here.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCAL="$ROOT/config/mac.env.local"
if [[ -f "$LOCAL" ]]; then
  # Local, Git-ignored values only.
  # shellcheck disable=SC1090
  source "$LOCAL"
fi
SSH_ALIAS="${WOL_SSH_ALIAS:-android-wol}"
if ! command -v ssh >/dev/null 2>&1; then
  echo 'OpenSSH client is required.' >&2
  exit 1
fi
printf 'Contacting Android WoL relay via SSH alias "%s"...\n' "$SSH_ALIAS"
ssh -o ConnectTimeout=12 -- "$SSH_ALIAS" '~/wake_pc.sh'
echo 'Wake command submitted. Boot and Windows availability must be checked separately.'
