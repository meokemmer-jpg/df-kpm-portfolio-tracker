# DF-KPM-Portfolio-Tracker [CRUX-MK]

**Welle-42 Foundation-DF für KPM (Kemmer-Portfolio-Management)**
**Per `~/.claude/rules/kpm-sizing.md` Variante-D-Hybrid**

## Zweck

Real-Portfolio-State-Monitoring für Kemmer-Familien-Vermoegen.
Tagesschluss-NAV + Position-Drift vs Target-Allocation pro Asset-Klasse.

## K_0-MAX-Berührung

Diese DF berührt das Kemmer-Familien-Vermoegen direkt. Strict-Conditions:
- KEINE Real-Trade-Execution (read-only Portfolio-State)
- KEIN Auto-Rebalance (nur Drift-Detection)
- Sandbox-Mode-Default mit Mock-3-Asset-Portfolio
- Phronesis-Pflicht Martin vor jedem Real-Mode-Aktivieren

## KPM-Sizing-Variante-D-Pattern

Per `rules/kpm-sizing.md`:
- Kelly-Fraction 0.25-0.40 kontext-adaptiv
- Drawdown-Caps Soft-Brake 15% / Hard-Cap 20% / Absolute-No-Go 25%
- HIVE-Score-Gate fuer Leverage-Erhoehung (>=0.7)

## Asset-Universum (Mock-Default)

- Equities US (z.B. SPY, QQQ)
- Equities EU (z.B. EXSA)
- Equities EM (z.B. EEM)
- Bonds (z.B. AGG, BNDX)
- Crypto (BTC, ETH)
- Cash (USD, EUR)

## ENV-Var-Aktivierung

```bash
export DF_KPM_PORTFOLIO_REAL_ENABLED=false  # Default-Disabled
export PHRONESIS_TICKET="PT-2026-XX-XX-001"  # Pflicht bei Real-Mode
```

## Architektur

- `src/portfolio_tracker_main.py` - Core-Logic (NAV-Calc + Drift-Detection)
- `src/kpm_variante_d_helpers.py` - Kelly-Fraction + Drawdown-Cap-Calc
- `src/adapter_orchestrator.py` - LaunchAgent-Entry mit main()
- `src/audit_logger.py` - HMAC-SHA256 Audit-Pflicht (K_0)

## CRUX-Bindung

- **K_0:** Read-only Tracking schuetzt vor Auto-Trade-Risiko
- **Q_0:** Familien-Vermoegens-Transparenz erhoeht
- **I_min:** Strukturiertes Variante-D-Compliance-Tracking
- **W_0:** Martin-Bandbreite minimiert via Daily-Tracking

## Tests

- `tests/test_portfolio_tracker_main.py` - >=8 Tests
- `tests/test_kpm_variante_d.py` - >=4 Tests
- `tests/test_adapter_orchestrator.py` - >=4 Tests

[CRUX-MK]
