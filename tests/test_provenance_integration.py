"""W50-A Batch-2: K12+K13+K16 Tests fuer df-kpm-portfolio provenance_integration [CRUX-MK]."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.provenance_integration import (
    PortfolioProvenanceRecorder,
    W48_FOUNDATION,
    DEFAULT_K16_LOCK_PATH,
)


@pytest.mark.skipif(not W48_FOUNDATION, reason="W48 foundation modules not installed")
def test_k12_portfolio_snapshot_envelope(tmp_path: Path):
    """K12: portfolio-snapshot gets signed envelope (K_0-DIRECT)."""
    rec = PortfolioProvenanceRecorder(audit_dir=tmp_path)
    result = rec.record_portfolio_snapshot(
        snapshot_id="kpm-snap-001",
        snapshot_payload={
            "total_nav_eur": "1000000",
            "allocations": [
                {"asset_class": "equities_us", "current_weight": "0.42"},
                {"asset_class": "bonds", "current_weight": "0.38"},
                {"asset_class": "cash", "current_weight": "0.20"},
            ],
            "source": "mock",
        },
        tenant_id="kpm-family",
    )
    assert result is not None
    assert "envelope_path" in result
    env_file = Path(result["envelope_path"])
    assert env_file.exists()
    with open(env_file) as f:
        env = json.load(f)
    assert env["operation_type"] == "df-kpm-portfolio-snapshot"
    assert env["issuer"] == "df-kpm-portfolio-tracker"
    assert env["tenant_id"] == "kpm-family"
    assert "signature" in env


@pytest.mark.skipif(not W48_FOUNDATION, reason="W48 foundation modules not installed")
def test_k12_chain_linkage_kpm(tmp_path: Path):
    """K12: 2 consecutive snapshots are chain-linked."""
    rec = PortfolioProvenanceRecorder(audit_dir=tmp_path)
    r1 = rec.record_portfolio_snapshot("s1", {"a": 1})
    r2 = rec.record_portfolio_snapshot("s2", {"a": 2})
    with open(r2["envelope_path"]) as f:
        env2 = json.load(f)
    # Schema-Feldname laut full_provenance_envelope.py: chain_predecessor_hash
    assert env2.get("chain_predecessor_hash") == r1["payload_hash"]


@pytest.mark.skipif(not W48_FOUNDATION, reason="W48 foundation modules not installed")
def test_k13_anchor_per_snapshot(tmp_path: Path):
    """K13: rfc3161-anchors.jsonl appended per snapshot (K_0-DIRECT pflicht)."""
    rec = PortfolioProvenanceRecorder(audit_dir=tmp_path)
    rec.record_portfolio_snapshot("kpm-anchor-1", {"nav": 1000000})
    rec.record_portfolio_snapshot("kpm-anchor-2", {"nav": 1010000})
    anchor_file = tmp_path / "anchors" / "rfc3161-anchors.jsonl"
    assert anchor_file.exists()
    lines = anchor_file.read_text().strip().split("\n")
    assert len(lines) == 2


def test_k16_default_lock_path():
    assert "df-kpm-portfolio" in str(DEFAULT_K16_LOCK_PATH)
    assert DEFAULT_K16_LOCK_PATH.name.endswith(".lockfile")
