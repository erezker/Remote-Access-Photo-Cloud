#!/usr/bin/env bash
# Preflight only: never attempts backup or opens/modifies Apple Photos.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCAL="$ROOT/config/mac.env.local"
if [[ ! -f "$LOCAL" ]]; then
  echo 'Create ignored config/mac.env.local first.' >&2
  exit 1
fi
# shellcheck disable=SC1090
source "$LOCAL"
: "${PHOTOS_LIBRARY_PATH:?Set PHOTOS_LIBRARY_PATH in mac.env.local}"
if [[ ! -d "$PHOTOS_LIBRARY_PATH" ]]; then
  echo 'External Photos library is not mounted / not found. Do not run a scheduled backup.' >&2
  exit 2
fi
if [[ "$PHOTOS_LIBRARY_PATH" != *.photoslibrary ]]; then
  echo 'The selected path is not a .photoslibrary package.' >&2
  exit 2
fi
printf '%s\n' 'Photos library package found. ALSO verify the active library in Photos settings and open an original before backup.'
