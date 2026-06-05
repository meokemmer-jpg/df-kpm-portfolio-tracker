
# K12+K13+K16 Trinity-CONTRARIAN 2026-05-17 (Cross-LLM-validated)
def k12_provenance(payload: bytes, key: bytes = b"df-trinity-contrarian-v1") -> dict:
    import hashlib, hmac
    return {
        "payload_hash": hashlib.sha256(payload).hexdigest(),
        "hmac_sha256": hmac.new(key, payload, hashlib.sha256).hexdigest(),
    }

def k13_anchor(payload_hash: str) -> dict:
    from datetime import datetime, timezone
    return {
        "anchor_type": "rfc3161-mock",
        "iso_ts": datetime.now(timezone.utc).isoformat(),
        "payload_hash": payload_hash,
    }

def k16_lock_or_exit(df_name: str):
    import fcntl, os, sys
    lock_path = f"/tmp/df-trinity-{df_name}.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_WRONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except BlockingIOError:
        sys.exit(3)

"""Tests fuer Adapter-Orchestrator [CRUX-MK]."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.adapter_orchestrator import main


def test_main_returns_0_in_mock_mode(monkeypatch, tmp_path):
    """Default-Mock-Mode -> exit 0."""
    monkeypatch.delenv("DF_KPM_PORTFOLIO_REAL_ENABLED", raising=False)
    # Stop-Flag im tmp_path platzieren (existiert nicht)
    monkeypatch.setattr("src.adapter_orchestrator.Path", lambda p: tmp_path / "no-stop-flag")
    # Audit-Log auch im tmp_path
    with patch("src.adapter_orchestrator.log_audit_event"):
        rc = main([])
    assert rc == 0


def test_main_returns_1_real_without_phronesis(monkeypatch):
    """Real-Mode ohne PHRONESIS_TICKET -> exit 1."""
    monkeypatch.setenv("DF_KPM_PORTFOLIO_REAL_ENABLED", "true")
    monkeypatch.delenv("PHRONESIS_TICKET", raising=False)
    # Stop-Flag existiert nicht
    with patch("src.adapter_orchestrator.Path") as mock_path:
        mock_path.return_value.exists.return_value = False
        with patch("src.adapter_orchestrator.log_audit_event"):
            rc = main([])
    assert rc == 1


def test_main_returns_2_when_stop_flag(monkeypatch, tmp_path):
    """STOP.flag existiert -> exit 2."""
    stop_flag = tmp_path / "stop.flag"
    stop_flag.write_text("stop")
    with patch("src.adapter_orchestrator.Path", return_value=stop_flag):
        rc = main([])
    assert rc == 2


def test_main_works_with_real_and_phronesis(monkeypatch):
    """Real-Mode + PHRONESIS_TICKET -> exit 0."""
    monkeypatch.setenv("DF_KPM_PORTFOLIO_REAL_ENABLED", "true")
    monkeypatch.setenv("PHRONESIS_TICKET", "PT-2026-05-11-001")
    with patch("src.adapter_orchestrator.Path") as mock_path:
        mock_path.return_value.exists.return_value = False
        with patch("src.adapter_orchestrator.log_audit_event"):
            with patch("src.adapter_orchestrator.create_mock_snapshot") as mock_snap:
                mock_snap.return_value.snapshot_id = "test"
                mock_snap.return_value.timestamp = "2026-05-11T10:00:00+00:00"
                from decimal import Decimal
                mock_snap.return_value.total_nav_eur = Decimal("1000000")
                mock_snap.return_value.source = "mock"  # main uses mock-default in Phase-1
                mock_snap.return_value.allocations = ()
                rc = main([])
    assert rc == 0
