[![CI](https://github.com/meokemmer-jpg/df-kpm-portfolio-tracker/actions/workflows/test.yml/badge.svg)](https://github.com/meokemmer-jpg/df-kpm-portfolio-tracker/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0--PHASE--1-blue.svg)](config.yaml)

# df-kpm-portfolio-tracker

> Daily NAV tracking and position-drift detection for the Kemmer family portfolio — read-only, audit-logged, sandbox-first.

## Overview

**df-kpm-portfolio-tracker** is a Python-based portfolio monitoring tool that takes a daily end-of-day NAV (Net Asset Value) snapshot across all asset classes and detects allocation drift against the Variante-D target weights. It implements Kelly-fraction sizing (0.25–0.40 adaptive), three-tier drawdown caps (soft 15 % / hard 20 % / no-go 25 %), and HMAC-SHA256 audit logging for every run. The tracker operates in **sandbox mode by default** using a mock three-asset portfolio (Equities / Bonds / Cash), and only connects to live market data when explicitly enabled with a reviewed Phronesis sign-off ticket.

## Installation

### Prerequisites

- Python 3.9+
- macOS (for LaunchAgent scheduling) or any Unix-like OS

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/meokemmer-jpg/df-kpm-portfolio-tracker.git
   cd df-kpm-portfolio-tracker
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install pytest
   ```

4. **Configure environment variables** (sandbox mode requires no additional setup)

   ```bash
   # Default — sandbox mock portfolio, no real market data
   export DF_KPM_PORTFOLIO_REAL_ENABLED=false

   # Real-mode — requires explicit Phronesis sign-off
   export DF_KPM_PORTFOLIO_REAL_ENABLED=true
   export PHRONESIS_TICKET="PT-YYYY-MM-DD-001"
   export OPERATOR_SIGNOFF_ID="your-signoff-id"
   ```

5. **Run the tracker** (SQLite state database is created automatically on first run)

   ```bash
   python3 -m src.adapter_orchestrator
   ```

6. **(Optional) Install the macOS LaunchAgent for daily 06:00 scheduling**

   ```bash
   cp scripts/com.kemmer.df-kpm-portfolio-tracker.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.kemmer.df-kpm-portfolio-tracker.plist
   ```

## Usage

### 1 — Sandbox NAV snapshot (default)

No environment configuration needed. Runs against the built-in mock three-asset portfolio and writes results to the local SQLite database at `~/.df-kpm-portfolio-tracker/portfolio-state.db`.

```bash
python3 -m src.adapter_orchestrator
```

### 2 — Real market data mode

Requires a valid `PHRONESIS_TICKET` and `OPERATOR_SIGNOFF_ID`. **Never enable real mode without a reviewed sign-off ticket.**

```bash
export DF_KPM_PORTFOLIO_REAL_ENABLED=true
export PHRONESIS_TICKET="PT-2026-06-07-001"
export OPERATOR_SIGNOFF_ID="martin-signoff-001"
python3 -m src.adapter_orchestrator
```

### 3 — Shell-script wrapper with K16 mutex (macOS)

The wrapper enforces a filesystem mutex, auto-recovers stale locks older than 6 hours, and exits cleanly on a stop-flag. Use this for manual invocations or for testing outside the LaunchAgent.

```bash
bash scripts/run-df-kpm-portfolio-tracker-mac.sh
```

### 4 — Run the full test suite

```bash
pytest tests/ -v
```

### 5 — Inspect the HMAC-signed audit log

Every NAV snapshot is signed and appended to the JSONL audit trail.

```bash
tail -f branch-hub/audit/df-kpm-portfolio-tracker.jsonl | python3 -m json.tool
```

## Project Structure

```
df-kpm-portfolio-tracker/
├── src/
│   ├── adapter_orchestrator.py          # Entry-point & run orchestration
│   ├── portfolio_tracker_main.py        # NAV calculation + drift detection
│   ├── kpm_variante_d_helpers.py        # Kelly-fraction & drawdown-cap logic
│   ├── audit_logger.py                  # HMAC-SHA256 audit logging
│   └── provenance_integration.py        # Provenance envelope & chain linkage
├── scripts/
│   ├── run-df-kpm-portfolio-tracker-mac.sh        # Shell wrapper (K16 mutex)
│   └── com.kemmer.df-kpm-portfolio-tracker.plist  # macOS LaunchAgent
├── tests/
│   ├── test_portfolio_tracker_main.py
│   ├── test_kpm_variante_d.py
│   ├── test_adapter_orchestrator.py
│   └── test_provenance_integration.py
├── config.yaml       # DF metadata, gate configuration, env-var spec
└── genealogy.json
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. This project follows a strict safety model: any change touching NAV calculation, drawdown-cap logic, or the audit logger requires a passing test suite (>=90 % coverage target) and a reviewer sign-off. Feature branches should be named `feature/<short-description>`; bug fixes `fix/<short-description>`. Open an issue first for significant changes so the approach can be discussed before implementation begins.

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.