"""Tests fuer KPM-Variante-D Helpers [CRUX-MK]."""

from __future__ import annotations

from decimal import Decimal

import pytest

from src.kpm_variante_d_helpers import (
    TradingContext,
    DrawdownState,
    kelly_fraction_for_context,
    drawdown_cap_check,
    hive_leverage_gate,
    position_reduction_factor,
)


def test_kelly_fraction_per_context():
    """Kelly-Fraction-Matrix per kpm-sizing.md."""
    assert kelly_fraction_for_context(TradingContext.NORMALREGIME_HIGH_CONFIDENCE) == Decimal("0.40")
    assert kelly_fraction_for_context(TradingContext.NORMALREGIME_AVG_CONFIDENCE) == Decimal("0.30")
    assert kelly_fraction_for_context(TradingContext.HIGH_VOLATILITY) == Decimal("0.25")
    assert kelly_fraction_for_context(TradingContext.WITHDRAWAL_PHASE) == Decimal("0.20")
    assert kelly_fraction_for_context(TradingContext.REGIME_BREAK) == Decimal("0")


def test_drawdown_cap_check_normal():
    """< 15% drawdown = NORMAL."""
    assert drawdown_cap_check(Decimal("10")) == DrawdownState.NORMAL
    assert drawdown_cap_check(Decimal("14.99")) == DrawdownState.NORMAL


def test_drawdown_cap_check_soft_brake():
    """15-20% = SOFT_BRAKE."""
    assert drawdown_cap_check(Decimal("15")) == DrawdownState.SOFT_BRAKE
    assert drawdown_cap_check(Decimal("19.99")) == DrawdownState.SOFT_BRAKE


def test_drawdown_cap_check_hard_cap():
    """20-25% = HARD_CAP (Trading-Pause + Phronesis)."""
    assert drawdown_cap_check(Decimal("20")) == DrawdownState.HARD_CAP
    assert drawdown_cap_check(Decimal("24.99")) == DrawdownState.HARD_CAP


def test_drawdown_cap_check_absolute_no_go():
    """>= 25% = ABSOLUTE_NO_GO (Familien-Notfall)."""
    assert drawdown_cap_check(Decimal("25")) == DrawdownState.ABSOLUTE_NO_GO
    assert drawdown_cap_check(Decimal("30")) == DrawdownState.ABSOLUTE_NO_GO


def test_drawdown_cap_check_negative_raises():
    """Negative Drawdowns sind invalid."""
    with pytest.raises(ValueError):
        drawdown_cap_check(Decimal("-5"))


def test_hive_leverage_gate_states():
    """HIVE-Score-Schwellen per Variante-D."""
    assert hive_leverage_gate(Decimal("0.3")) == "auto_deleverage"
    assert hive_leverage_gate(Decimal("0.6")) == "no_leverage_increase"
    assert hive_leverage_gate(Decimal("0.7")) == "leverage_ok"
    assert hive_leverage_gate(Decimal("0.9")) == "leverage_ok"


def test_position_reduction_factor_per_state():
    """Position-Reduktion per Drawdown-State."""
    assert position_reduction_factor(DrawdownState.NORMAL) == Decimal("1.0")
    assert position_reduction_factor(DrawdownState.SOFT_BRAKE) == Decimal("0.5")
    assert position_reduction_factor(DrawdownState.HARD_CAP) == Decimal("0.0")
    assert position_reduction_factor(DrawdownState.ABSOLUTE_NO_GO) == Decimal("0.0")
