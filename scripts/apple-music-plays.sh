#!/usr/bin/env bash
# Sums the "played count" across every track in the local Music.app library.
# macOS-only, run manually to refresh APPLE_MUSIC_TOTAL_PLAYS in
# frontend/src/data/site.ts — Apple exposes no API for this, so there's no
# way to fetch it live from the deployed site. Large libraries can take a
# minute or two since Music.app scripting isn't fast.
set -euo pipefail

osascript -e 'tell application "Music" to get played count of every track of library playlist 1' \
  | tr ',' '\n' \
  | awk '{sum += $1} END {print sum}'
