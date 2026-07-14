from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from portfolio_tracker_main import AssetClass, build_portfolio_report


def write_portfolio(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    path.write_text(
        "symbol,asset_class,quantity,price_eur\n"
        + "\n".join(
            f"{symbol},{asset_class},{quantity},{price_eur}"
            for symbol, asset_class, quantity, price_eur in rows
        )
        + "\n",
        encoding="utf-8",
    )


def max_abs_drift(report) -> object:
    return max(abs(allocation.drift_pct) for allocation in report.allocations)


def status_vector(report) -> tuple[str, ...]:
    return tuple(report.drift_status[allocation.asset_class] for allocation in report.allocations)


def test_tracker_discriminates_adversarial_counter_portfolio_from_policy_portfolio(tmp_path):
    policy_file = tmp_path / "policy_like_positions.csv"
    adversarial_file = tmp_path / "adversarial_positions.csv"

    write_portfolio(
        policy_file,
        [
            ("VTI", "equities_us", "40", "1000"),
            ("VEA", "equities_eu", "10", "1000"),
            ("VWO", "equities_em", "10", "1000"),
            ("AGG", "bonds", "25", "1000"),
            ("BTC", "crypto", "5", "1000"),
            ("EUR", "cash", "10", "1000"),
        ],
    )
    write_portfolio(
        adversarial_file,
        [
            ("VTI", "equities_us", "5", "1000"),
            ("VEA", "equities_eu", "5", "1000"),
            ("VWO", "equities_em", "5", "1000"),
            ("AGG", "bonds", "5", "1000"),
            ("BTC", "crypto", "75", "1000"),
            ("EUR", "cash", "5", "1000"),
        ],
    )

    policy_report = build_portfolio_report(policy_file)
    adversarial_report = build_portfolio_report(adversarial_file)

    assert policy_report.total_nav_eur == adversarial_report.total_nav_eur
    assert policy_report.risk_state != adversarial_report.risk_state
    assert status_vector(policy_report) != status_vector(adversarial_report)
    assert adversarial_report.actionable_assets != policy_report.actionable_assets
    assert max_abs_drift(adversarial_report) > max_abs_drift(policy_report)
    assert adversarial_report.drift_status[AssetClass.CRYPTO] != policy_report.drift_status[AssetClass.CRYPTO]
