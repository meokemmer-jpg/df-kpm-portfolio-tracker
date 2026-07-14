from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Iterable


class AssetClass(Enum):
    EQUITIES_US = "equities_us"
    EQUITIES_EU = "equities_eu"
    EQUITIES_EM = "equities_em"
    BONDS = "bonds"
    CRYPTO = "crypto"
    CASH = "cash"


@dataclass(frozen=True)
class Position:
    symbol: str
    asset_class: AssetClass
    quantity: Decimal
    price_eur: Decimal

    @property
    def nav_eur(self) -> Decimal:
        return money(self.quantity * self.price_eur)


@dataclass(frozen=True)
class AssetAllocation:
    asset_class: AssetClass
    target_weight: Decimal
    current_weight: Decimal
    nav_eur: Decimal

    @property
    def drift_pct(self) -> Decimal:
        return pct((self.current_weight - self.target_weight) * Decimal("100"))


@dataclass(frozen=True)
class PortfolioReport:
    total_nav_eur: Decimal
    allocations: tuple[AssetAllocation, ...]
    drift_status: dict[AssetClass, str]
    risk_state: str

    @property
    def actionable_assets(self) -> tuple[AssetClass, ...]:
        return tuple(
            asset for asset, status in self.drift_status.items()
            if status == "rebalance_trigger"
        )


TARGET_WEIGHTS: dict[AssetClass, Decimal] = {
    AssetClass.EQUITIES_US: Decimal("0.40"),
    AssetClass.EQUITIES_EU: Decimal("0.10"),
    AssetClass.EQUITIES_EM: Decimal("0.10"),
    AssetClass.BONDS: Decimal("0.25"),
    AssetClass.CRYPTO: Decimal("0.05"),
    AssetClass.CASH: Decimal("0.10"),
}

WARN_DRIFT_PCT = Decimal("5.00")
REBALANCE_DRIFT_PCT = Decimal("10.00")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def pct(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def parse_decimal(raw: str, field_name: str) -> Decimal:
    try:
        value = Decimal(raw.strip())
    except Exception as exc:
        raise ValueError(f"invalid decimal for {field_name}: {raw!r}") from exc
    if value < 0:
        raise ValueError(f"{field_name} must be >= 0, got {value}")
    return value


def load_positions_csv(path: str | Path) -> tuple[Position, ...]:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"symbol", "asset_class", "quantity", "price_eur"}
        if set(reader.fieldnames or ()) != required:
            raise ValueError(f"CSV header must be exactly {sorted(required)}")

        positions: list[Position] = []
        for row_number, row in enumerate(reader, start=2):
            try:
                asset_class = AssetClass(row["asset_class"].strip())
            except ValueError as exc:
                raise ValueError(f"row {row_number}: unknown asset_class {row['asset_class']!r}") from exc
            positions.append(
                Position(
                    symbol=row["symbol"].strip(),
                    asset_class=asset_class,
                    quantity=parse_decimal(row["quantity"], "quantity"),
                    price_eur=parse_decimal(row["price_eur"], "price_eur"),
                )
            )

    if not positions:
        raise ValueError("portfolio CSV contains no positions")
    return tuple(positions)


def calculate_total_nav(positions: Iterable[Position]) -> Decimal:
    return money(sum((position.nav_eur for position in positions), Decimal("0")))


def build_allocations(positions: Iterable[Position]) -> tuple[AssetAllocation, ...]:
    positions = tuple(positions)
    total_nav = calculate_total_nav(positions)
    if total_nav <= 0:
        raise ValueError("total NAV must be greater than zero")

    nav_by_asset = {asset: Decimal("0.00") for asset in TARGET_WEIGHTS}
    for position in positions:
        nav_by_asset[position.asset_class] = money(
            nav_by_asset[position.asset_class] + position.nav_eur
        )

    return tuple(
        AssetAllocation(
            asset_class=asset,
            target_weight=target,
            current_weight=(nav_by_asset[asset] / total_nav).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            ),
            nav_eur=nav_by_asset[asset],
        )
        for asset, target in TARGET_WEIGHTS.items()
    )


def classify_drift(allocation: AssetAllocation) -> str:
    absolute_drift = abs(allocation.drift_pct)
    if absolute_drift >= REBALANCE_DRIFT_PCT:
        return "rebalance_trigger"
    if absolute_drift >= WARN_DRIFT_PCT:
        return "warn"
    return "ok"


def build_portfolio_report(csv_path: str | Path) -> PortfolioReport:
    positions = load_positions_csv(csv_path)
    allocations = build_allocations(positions)
    drift_status = {
        allocation.asset_class: classify_drift(allocation)
        for allocation in allocations
    }
    if "rebalance_trigger" in drift_status.values():
        risk_state = "rebalance_required"
    elif "warn" in drift_status.values():
        risk_state = "watch"
    else:
        risk_state = "within_policy"
    return PortfolioReport(
        total_nav_eur=calculate_total_nav(positions),
        allocations=allocations,
        drift_status=drift_status,
        risk_state=risk_state,
    )


def main(argv: list[str] | None = None) -> int:
    argv = argv or []
    if len(argv) != 1:
        return 64
    report = build_portfolio_report(argv[0])
    return 2 if report.risk_state == "rebalance_required" else 0
