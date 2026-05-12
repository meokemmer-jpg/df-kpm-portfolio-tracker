"""KPM-Variante-D Helpers [CRUX-MK].

Per ~/.claude/rules/kpm-sizing.md:
- Kelly-Fraction 0.25-0.40 kontext-adaptiv
- Drawdown-Caps Soft-Brake 15% / Hard-Cap 20% / Absolute-No-Go 25%
- HIVE-Score-Gate fuer Leverage-Erhoehung
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum


class TradingContext(Enum):
    """Kontext-Klassen fuer Kelly-Fraction-Wahl."""
    NORMALREGIME_HIGH_CONFIDENCE = "normal_high"
    NORMALREGIME_AVG_CONFIDENCE = "normal_avg"
    HIGH_VOLATILITY = "high_vol"
    WITHDRAWAL_PHASE = "withdrawal"
    REGIME_BREAK = "regime_break"


class DrawdownState(Enum):
    """Drawdown-Cap-Stufen per Variante-D."""
    NORMAL = "normal"        # < 15%
    SOFT_BRAKE = "soft_brake"  # 15-20%
    HARD_CAP = "hard_cap"      # 20-25%
    ABSOLUTE_NO_GO = "absolute_no_go"  # >= 25%


# Kelly-Fraction-Matrix per kpm-sizing.md
KELLY_FRACTION_MATRIX: dict[TradingContext, Decimal] = {
    TradingContext.NORMALREGIME_HIGH_CONFIDENCE: Decimal("0.40"),
    TradingContext.NORMALREGIME_AVG_CONFIDENCE: Decimal("0.30"),
    TradingContext.HIGH_VOLATILITY: Decimal("0.25"),
    TradingContext.WITHDRAWAL_PHASE: Decimal("0.20"),
    TradingContext.REGIME_BREAK: Decimal("0"),  # Pause
}

# Drawdown-Schwellen per Variante-D
DRAWDOWN_SOFT_BRAKE_PCT = Decimal("15")   # Position-Reduktion 50%
DRAWDOWN_HARD_CAP_PCT = Decimal("20")     # Trading-Pause + Phronesis
DRAWDOWN_ABSOLUTE_NO_GO_PCT = Decimal("25")  # Familien-Notfall-Protokoll

# HIVE-Score-Schwellen
HIVE_LEVERAGE_GATE = Decimal("0.7")   # >=0.7 = Leverage-OK
HIVE_AUTO_DELEVERAGE = Decimal("0.5")  # <0.5 = auto-deleverage


def kelly_fraction_for_context(context: TradingContext) -> Decimal:
    """Returns Kelly-Fraction fuer gegebenen Trading-Kontext."""
    if context not in KELLY_FRACTION_MATRIX:
        raise ValueError(f"Unknown context: {context}")
    return KELLY_FRACTION_MATRIX[context]


def drawdown_cap_check(current_drawdown_pct: Decimal) -> DrawdownState:
    """Returns Drawdown-State per Variante-D-Schwellen.

    Args:
        current_drawdown_pct: Akkumulierter Drawdown in Prozent (z.B. 15.5 fuer 15.5%)

    Returns:
        DrawdownState: NORMAL | SOFT_BRAKE | HARD_CAP | ABSOLUTE_NO_GO
    """
    if current_drawdown_pct < Decimal("0"):
        raise ValueError(f"Drawdown must be >=0, got {current_drawdown_pct}")

    if current_drawdown_pct >= DRAWDOWN_ABSOLUTE_NO_GO_PCT:
        return DrawdownState.ABSOLUTE_NO_GO
    if current_drawdown_pct >= DRAWDOWN_HARD_CAP_PCT:
        return DrawdownState.HARD_CAP
    if current_drawdown_pct >= DRAWDOWN_SOFT_BRAKE_PCT:
        return DrawdownState.SOFT_BRAKE
    return DrawdownState.NORMAL


def hive_leverage_gate(hive_score: Decimal) -> str:
    """Returns Leverage-Gate-Decision basierend auf HIVE-Score.

    Returns:
        'leverage_ok' | 'no_leverage_increase' | 'auto_deleverage'
    """
    if hive_score < Decimal("0") or hive_score > Decimal("1"):
        raise ValueError(f"HIVE-Score must be 0-1, got {hive_score}")

    if hive_score < HIVE_AUTO_DELEVERAGE:
        return "auto_deleverage"
    if hive_score < HIVE_LEVERAGE_GATE:
        return "no_leverage_increase"
    return "leverage_ok"


def position_reduction_factor(state: DrawdownState) -> Decimal:
    """Returns Position-Size-Multiplier basierend auf Drawdown-State.

    1.0 = volle Position, 0.5 = halbe Position, 0.0 = keine Position
    """
    if state == DrawdownState.NORMAL:
        return Decimal("1.0")
    if state == DrawdownState.SOFT_BRAKE:
        return Decimal("0.5")  # 50% Reduktion
    if state == DrawdownState.HARD_CAP:
        return Decimal("0.0")  # Trading-Pause
    if state == DrawdownState.ABSOLUTE_NO_GO:
        return Decimal("0.0")  # Familien-Notfall, keine Position
    raise ValueError(f"Unknown DrawdownState: {state}")
