"""Tests fuer DF-KPM-Portfolio-Tracker Core-Logic [CRUX-MK]."""

from __future__ import annotations

import os
from decimal import Decimal

import pytest

from src.portfolio_tracker_main import (
    AssetClass,
    AssetAllocation,
    PortfolioSnapshot,
    NavCalculator,
    DriftDetector,
    create_mock_snapshot,
    get_default_mode,
)


def test_asset_allocation_validation_target_weight():
    """target_weight muss zwischen 0 und 1 liegen."""
    with pytest.raises(ValueError, match="target_weight"):
        AssetAllocation(
            asset_class=AssetClass.EQUITIES_US,
            target_weight=Decimal("1.5"),
            current_weight=Decimal("0.5"),
            nav_eur=Decimal("100000"),
        )


def test_asset_allocation_validation_negative_nav():
    """nav_eur muss >= 0 sein."""
    with pytest.raises(ValueError, match="nav_eur"):
        AssetAllocation(
            asset_class=AssetClass.BONDS,
            target_weight=Decimal("0.4"),
            current_weight=Decimal("0.4"),
            nav_eur=Decimal("-1000"),
        )


def test_asset_allocation_drift_pct():
    """drift_pct = (current - target) * 100."""
    alloc = AssetAllocation(
        asset_class=AssetClass.EQUITIES_US,
        target_weight=Decimal("0.4"),
        current_weight=Decimal("0.45"),
        nav_eur=Decimal("450000"),
    )
    assert alloc.drift_pct == Decimal("5.00")


def test_portfolio_snapshot_real_api_requires_phronesis_ticket():
    """Real-API-Source MUSS phronesis_ticket haben."""
    allocs = (
        AssetAllocation(
            asset_class=AssetClass.CASH,
            target_weight=Decimal("1"),
            current_weight=Decimal("1"),
            nav_eur=Decimal("100000"),
        ),
    )
    with pytest.raises(ValueError, match="phronesis_ticket"):
        PortfolioSnapshot(
            snapshot_id="test",
            timestamp="2026-05-11T10:00:00+00:00",
            total_nav_eur=Decimal("100000"),
            allocations=allocs,
            source="real-api",
            phronesis_ticket=None,
        )


def test_portfolio_snapshot_allocations_must_sum_to_1():
    """Allocations-Sum muss 1.0 sein (innerhalb 1%-Tolerance)."""
    allocs = (
        AssetAllocation(
            asset_class=AssetClass.EQUITIES_US,
            target_weight=Decimal("0.5"),
            current_weight=Decimal("0.5"),
            nav_eur=Decimal("500000"),
        ),
        AssetAllocation(
            asset_class=AssetClass.BONDS,
            target_weight=Decimal("0.3"),
            current_weight=Decimal("0.3"),  # sum=0.8, should fail
            nav_eur=Decimal("300000"),
        ),
    )
    with pytest.raises(ValueError, match="sum to 1.0"):
        PortfolioSnapshot(
            snapshot_id="test",
            timestamp="2026-05-11T10:00:00+00:00",
            total_nav_eur=Decimal("800000"),
            allocations=allocs,
            source="mock",
        )


def test_nav_calculator_total():
    """Total-NAV ist Summe aller Asset-NAVs."""
    allocs = [
        AssetAllocation(
            asset_class=AssetClass.EQUITIES_US,
            target_weight=Decimal("0.5"),
            current_weight=Decimal("0.5"),
            nav_eur=Decimal("500000"),
        ),
        AssetAllocation(
            asset_class=AssetClass.BONDS,
            target_weight=Decimal("0.5"),
            current_weight=Decimal("0.5"),
            nav_eur=Decimal("500000"),
        ),
    ]
    assert NavCalculator.calculate_total_nav(allocs) == Decimal("1000000")


def test_drift_detector_warns_at_5pp():
    """5pp drift triggert 'warn'."""
    snapshot = PortfolioSnapshot(
        snapshot_id="test",
        timestamp="2026-05-11T10:00:00+00:00",
        total_nav_eur=Decimal("1000000"),
        allocations=(
            AssetAllocation(
                asset_class=AssetClass.EQUITIES_US,
                target_weight=Decimal("0.4"),
                current_weight=Decimal("0.46"),  # +6pp drift
                nav_eur=Decimal("460000"),
            ),
            AssetAllocation(
                asset_class=AssetClass.BONDS,
                target_weight=Decimal("0.6"),
                current_weight=Decimal("0.54"),
                nav_eur=Decimal("540000"),
            ),
        ),
        source="mock",
    )
    drifts = DriftDetector.detect_drifts(snapshot)
    assert drifts[AssetClass.EQUITIES_US] == "warn"


def test_drift_detector_rebalance_at_10pp():
    """10pp drift triggert 'rebalance_trigger'."""
    snapshot = PortfolioSnapshot(
        snapshot_id="test",
        timestamp="2026-05-11T10:00:00+00:00",
        total_nav_eur=Decimal("1000000"),
        allocations=(
            AssetAllocation(
                asset_class=AssetClass.EQUITIES_US,
                target_weight=Decimal("0.4"),
                current_weight=Decimal("0.51"),  # +11pp drift
                nav_eur=Decimal("510000"),
            ),
            AssetAllocation(
                asset_class=AssetClass.BONDS,
                target_weight=Decimal("0.6"),
                current_weight=Decimal("0.49"),
                nav_eur=Decimal("490000"),
            ),
        ),
        source="mock",
    )
    drifts = DriftDetector.detect_drifts(snapshot)
    assert drifts[AssetClass.EQUITIES_US] == "rebalance_trigger"


def test_get_default_mode_sandbox(monkeypatch):
    """Default-Mode ist 'mock' ohne ENV-Var."""
    monkeypatch.delenv("DF_KPM_PORTFOLIO_REAL_ENABLED", raising=False)
    assert get_default_mode() == "mock"


def test_get_default_mode_real_only_with_true(monkeypatch):
    """Nur 'true' aktiviert Real-Mode."""
    monkeypatch.setenv("DF_KPM_PORTFOLIO_REAL_ENABLED", "1")
    assert get_default_mode() == "mock"  # 1 ist nicht 'true'

    monkeypatch.setenv("DF_KPM_PORTFOLIO_REAL_ENABLED", "true")
    assert get_default_mode() == "real-api"


def test_create_mock_snapshot_valid():
    """Mock-Snapshot ist sauber konstruiert."""
    snap = create_mock_snapshot("test-mock")
    assert snap.source == "mock"
    assert snap.phronesis_ticket is None
    assert snap.total_nav_eur == Decimal("1000000")
    assert len(snap.allocations) == 3
