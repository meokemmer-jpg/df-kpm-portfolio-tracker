#!/bin/bash
# DF-KPM-Portfolio-Tracker Wrapper [CRUX-MK]
# K16 Concurrent-Spawn-Mutex + status=partial -> exit 0

set -e

LOCK_DIR="/tmp/df-kpm-portfolio-tracker.lock"
LOCK_AGE_LIMIT_S=21600  # 6h Stale-Lock-Schwelle

# K16 Stale-Lock-Auto-Claim
if [ -d "$LOCK_DIR" ]; then
  LOCK_AGE_S=$(( $(date +%s) - $(stat -f %m "$LOCK_DIR" 2>/dev/null || echo 0) ))
  if [ "$LOCK_AGE_S" -gt "$LOCK_AGE_LIMIT_S" ]; then
    echo "Stale lock detected (${LOCK_AGE_S}s old), removing"
    rm -rf "$LOCK_DIR"
  fi
fi

# K16 Atomic-Mutex via mkdir
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Another instance running (lock at $LOCK_DIR)"
  exit 3
fi

echo "$$" > "$LOCK_DIR/pid"
trap 'rm -rf "$LOCK_DIR"' EXIT INT TERM

# Run DF
cd /Users/make/Projects/dark-factories/df-kpm-portfolio-tracker

# Status partial (K_0-Schutz: keine Hard-Failures, mock-fallback default)
if /usr/bin/python3 -m src.adapter_orchestrator; then
  echo "DF-KPM-Portfolio-Tracker run completed successfully"
  exit 0
else
  RC=$?
  if [ "$RC" = "2" ]; then
    echo "STOP.flag detected, graceful exit"
    exit 0  # status=partial -> exit 0
  fi
  echo "DF-KPM-Portfolio-Tracker exited with code $RC"
  exit 0  # K_0-Schutz: kein Hard-Failure
fi
