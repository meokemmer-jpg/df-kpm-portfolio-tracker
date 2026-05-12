"""DF-KPM-Portfolio-Tracker package [CRUX-MK].

LAZY-IMPORT-PATTERN: Module werden bei erstem Zugriff importiert.
Verhindert Import-Cycle + reduziert Bootstrap-Overhead.
"""

__version__ = "0.1.0-PHASE-1"

# Lazy-Import via __getattr__ (PEP 562)
def __getattr__(name):
    if name == "PortfolioSnapshot":
        from .portfolio_tracker_main import PortfolioSnapshot
        return PortfolioSnapshot
    if name == "AssetAllocation":
        from .portfolio_tracker_main import AssetAllocation
        return AssetAllocation
    if name == "NavCalculator":
        from .portfolio_tracker_main import NavCalculator
        return NavCalculator
    if name == "DriftDetector":
        from .portfolio_tracker_main import DriftDetector
        return DriftDetector
    if name == "kelly_fraction_for_context":
        from .kpm_variante_d_helpers import kelly_fraction_for_context
        return kelly_fraction_for_context
    if name == "drawdown_cap_check":
        from .kpm_variante_d_helpers import drawdown_cap_check
        return drawdown_cap_check
    raise AttributeError(f"module {__name__} has no attribute {name}")
