"""DF-KPM-Portfolio-Tracker Core-Logic [CRUX-MK].

K_0-MAX-Berührung. Read-only NAV-Tracking + Drift-Detection.
KEINE Trade-Execution. Sandbox-Default mit Mock-Portfolio.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional


class AssetClass(Enum):
    """Asset-Klassen fuer KPM-Portfolio."""
    EQUITIES_US = "equities_us"
    EQUITIES_EU = "equities_eu"
    EQUITIES_EM = "equities_em"
    BONDS = "bonds"
    CRYPTO = "crypto"
    CASH = "cash"


@dataclass(frozen=True)
class AssetAllocation:
    """Target-Allocation pro Asset-Klasse (frozen, immutable)."""
    asset_class: AssetClass
    target_weight: Decimal  # 0.0 - 1.0
    current_weight: Decimal
    nav_eur: Decimal

    def __post_init__(self):
        if self.target_weight < Decimal("0") or self.target_weight > Decimal("1"):
            raise ValueError(f"target_weight must be 0-1, got {self.target_weight}")
        if self.current_weight < Decimal("0") or self.current_weight > Decimal("1"):
            raise ValueError(f"current_weight must be 0-1, got {self.current_weight}")
        if self.nav_eur < Decimal("0"):
            raise ValueError(f"nav_eur must be >=0, got {self.nav_eur}")

    @property
    def drift_pct(self) -> Decimal:
        """Drift in Prozent-Punkten (current - target)."""
        return (self.current_weight - self.target_weight) * Decimal("100")


@dataclass(frozen=True)
class PortfolioSnapshot:
    """Tagesschluss-NAV-Snapshot des Portfolios."""
    snapshot_id: str
    timestamp: str  # ISO 8601
    total_nav_eur: Decimal
    allocations: tuple[AssetAllocation, ...]  # frozen tuple
    source: str  # "mock" | "real-api"
    phronesis_ticket: Optional[str] = None

    def __post_init__(self):
        if self.source == "real-api" and not self.phronesis_ticket:
            raise ValueError("Real-API-Source requires phronesis_ticket")
        # Allocation-Sum-Check
        total_weight = sum(a.current_weight for a in self.allocations)
        if abs(total_weight - Decimal("1")) > Decimal("0.01"):
            raise ValueError(f"Allocations must sum to 1.0, got {total_weight}")


class NavCalculator:
    """Berechnet Total-NAV aus Asset-Allocations."""

    @staticmethod
    def calculate_total_nav(allocations: list[AssetAllocation]) -> Decimal:
        """Summiert NAV pro Asset-Klasse zu Total-NAV (EUR)."""
        return sum((a.nav_eur for a in allocations), start=Decimal("0"))

    @staticmethod
    def calculate_weights(allocations: list[AssetAllocation]) -> dict[AssetClass, Decimal]:
        """Berechnet aktuelle Gewichte aus NAV-Werten."""
        total = NavCalculator.calculate_total_nav(allocations)
        if total == Decimal("0"):
            return {a.asset_class: Decimal("0") for a in allocations}
        return {a.asset_class: a.nav_eur / total for a in allocations}


class DriftDetector:
    """Detektiert Allocation-Drift zwischen Target und Current."""

    DRIFT_WARN_THRESHOLD = Decimal("5")   # 5pp drift = warning
    DRIFT_REBALANCE_THRESHOLD = Decimal("10")  # 10pp drift = rebalance-trigger

    @staticmethod
    def detect_drifts(
        snapshot: PortfolioSnapshot,
    ) -> dict[AssetClass, str]:
        """Returns dict mit drift-status pro Asset-Klasse.

        Status: 'ok' | 'warn' | 'rebalance_trigger'
        """
        result = {}
        for alloc in snapshot.allocations:
            abs_drift = abs(alloc.drift_pct)
            if abs_drift >= DriftDetector.DRIFT_REBALANCE_THRESHOLD:
                result[alloc.asset_class] = "rebalance_trigger"
            elif abs_drift >= DriftDetector.DRIFT_WARN_THRESHOLD:
                result[alloc.asset_class] = "warn"
            else:
                result[alloc.asset_class] = "ok"
        return result


def get_default_mode() -> str:
    """Returns 'mock' (default) or 'real-api' based on ENV-Var."""
    if os.environ.get("DF_KPM_PORTFOLIO_REAL_ENABLED") == "true":
        return "real-api"
    return "mock"


def create_mock_snapshot(snapshot_id: str = "mock-default") -> PortfolioSnapshot:
    """Erzeugt Mock-3-Asset-Portfolio-Snapshot (Sandbox-Default)."""
    allocations = (
        AssetAllocation(
            asset_class=AssetClass.EQUITIES_US,
            target_weight=Decimal("0.4"),
            current_weight=Decimal("0.42"),
            nav_eur=Decimal("420000"),
        ),
        AssetAllocation(
            asset_class=AssetClass.BONDS,
            target_weight=Decimal("0.4"),
            current_weight=Decimal("0.38"),
            nav_eur=Decimal("380000"),
        ),
        AssetAllocation(
            asset_class=AssetClass.CASH,
            target_weight=Decimal("0.2"),
            current_weight=Decimal("0.20"),
            nav_eur=Decimal("200000"),
        ),
    )
    return PortfolioSnapshot(
        snapshot_id=snapshot_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_nav_eur=Decimal("1000000"),
        allocations=allocations,
        source="mock",
        phronesis_ticket=None,
    )
