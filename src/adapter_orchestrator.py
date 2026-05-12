"""DF-KPM-Portfolio-Tracker LaunchAgent-Entry [CRUX-MK]."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from .portfolio_tracker_main import (
    create_mock_snapshot,
    get_default_mode,
    DriftDetector,
)
from .audit_logger import log_audit_event


def main(argv: list[str] | None = None) -> int:
    """LaunchAgent-Entry-Point.

    Returns:
        0 = success
        1 = error (real-mode without phronesis-ticket etc.)
        2 = STOP.flag detected
        3 = K16-VETO (concurrent spawn)
    """
    stop_flag = Path("/tmp/df-kpm-portfolio-tracker.stop")
    if stop_flag.exists():
        print(f"STOP.flag detected at {stop_flag}, exiting", file=sys.stderr)
        return 2

    mode = get_default_mode()
    if mode == "real-api" and not os.environ.get("PHRONESIS_TICKET"):
        print("Real-API-Mode requires PHRONESIS_TICKET env-var", file=sys.stderr)
        log_audit_event(
            event="real_mode_rejected_no_phronesis",
            df_id="df-kpm-portfolio-tracker",
            details={"reason": "PHRONESIS_TICKET missing"},
        )
        return 1

    # Phase-1: Mock-Default
    snapshot = create_mock_snapshot(snapshot_id=f"daily-{os.environ.get('DATE', 'today')}")
    drifts = DriftDetector.detect_drifts(snapshot)

    # Audit-Log
    log_audit_event(
        event="snapshot_created",
        df_id="df-kpm-portfolio-tracker",
        details={
            "snapshot_id": snapshot.snapshot_id,
            "total_nav_eur": str(snapshot.total_nav_eur),
            "source": snapshot.source,
            "drifts": {ac.value: status for ac, status in drifts.items()},
        },
    )

    # Health-File
    health_data = {
        "status": "ok",
        "timestamp": snapshot.timestamp,
        "total_nav_eur": str(snapshot.total_nav_eur),
        "source": snapshot.source,
        "drift_count_warn": sum(1 for s in drifts.values() if s == "warn"),
        "drift_count_rebalance": sum(1 for s in drifts.values() if s == "rebalance_trigger"),
    }
    health_path = Path("/tmp/df-kpm-portfolio-tracker-health.json")
    try:
        health_path.write_text(json.dumps(health_data, indent=2))
    except Exception as e:
        print(f"Could not write health file: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
