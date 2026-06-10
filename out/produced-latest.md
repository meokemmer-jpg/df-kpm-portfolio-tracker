# df-kpm-portfolio-tracker — PRODUKTION [CRUX-MK]
*2026-06-09T16:03:23.886972+00:00 | ollama-local/kemmer-14b-ctx8k*

# df-kpm-portfolio-tracker

## Übersicht

**df-kpm-portfolio-tracker** ist ein Python-basierter Portfolioüberwachungs-Tool, das täglich am Schluss des Handelstages eine NAV (Net Asset Value) Aufnahme erstellt und Allocation-Drifts im Vergleich zu den Variante-D Zielgewichten erkennt. Das Tool implementiert Kelly-Fraktion Sizing (0.25–0.40 adaptiv), drei-Tier-Drawdown-Grenzwerte (weiche 15 % / harte 20 % / verbotene 25 %) und HMAC-SHA256-Auditlogging für jede Ausführung. Der Tracker betreibt standardmäßig in **Sandbox-Modus** unter Verwendung eines simulierten Dreikomponenten-Portfolios (Aktien / Anleihen / Bargeld), es wird jedoch nur auf echte Marktdaten geschaltet, wenn explizit durch ein genehmigtes Phronesis-Ticket aktiviert wird.

## Installation

### Voraussetzungen

- Python 3.9+
- macOS (für LaunchAgent-Ablaufplanung) oder beliebige Unix-like-Betriebssysteme

### Schritte zur Installation und Konfiguration

1. **Klonen des Repositorys**

   ```bash
   git clone https://github.com/meokemmer-jpg/df-kpm-portfolio-tracker.git
   cd df-kpm-portfolio-tracker
   ```

2. **Erstellen und Aktivieren einer virtuellen Umgebung**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Installation der Abhängigkeiten**

   ```bash
   pip install pytest
   ```

4. **Konfiguration der Umgebungsvariablen** (Sandbox-Modus erfordert keine zusätzliche Einstellung)

   - **Standard — Sandbox-Modus**
     ```bash
     export DF_KPM_PORTFOLIO_REAL_ENABLED=false
     ```
   
   - **Echte-Daten-Modus — wird explizit durch Phronesis-Kennung aktiviert**
     ```bash
     export DF_KPM_PORTFOLIO_REAL_ENABLED=true
     export PHRONESIS_TICKET="PT-YYYY-MM-DD-001"
     export OPERATOR_SIGNOFF_ID="your-signoff-id"
     ```

5. **Ausführen des Trackers** (SQLite-State-Datenbank wird bei der ersten Ausführung automatisch erstellt)

   ```bash
   python3 -m src.adapter_orchestrator
   ```

6. **(Optional) Installieren des macOS LaunchAgents für tägliche 06:00 Uhr Ablaufplanung**

   ```bash
   cp scripts/com.kemmer.df-kpm-portfolio-tracker.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.kemmer.df-kpm-portfolio-tracker.plist
   ```

## Verwendung

### 1 — Sandbox NAV-Aufnahme (Standardmodus)

Keine Umgebungsvariablenkonfiguration erforderlich. Führen Sie das Programm aus, um eine tägliche NAV-Snapshot auf Basis des simulierten Portfolios zu erstellen und zu analysieren.

### 2 — Echte Daten-Modus

Um den Tracker mit echten Marktdaten zu nutzen, muss der Modus explizit durch die Phronesis-Kennung aktiviert werden. Diese Prozedur sorgt für zusätzliche Sicherheit und Präzision bei der Handhabung echter Finanzdaten.

### 3 — Analyse der Ergebnisse

Die Ergebnisse des täglichen Betriebs werden in einer SQLite-Datenbank gespeichert, die automatisch beim ersten Start erstellt wird. Der Tracker generiert HMAC-SHA256-Auditlogs für jede Ausführung, um eine vollständige Überwachung und Sicherheit zu gewährleisten.

## Technische Details

### Teststruktur

- **Unit-Tests**: `tests/test_hmac_approval_gate.py` — 15 Tests
- **Integration-Tests**: `tests/test_integration_approval.py` — 10 Tests
- **Adversarial-Tests**: `tests/test_adversarial_approval.py` — 5 Tests (spezifisch für Codex)
- **Replay-Tests**: `tests/test_replay_approval.py` — 3 Tests
- **OS-Security-Tests**: `tests/test_os_acl_setup.py` — 2 Manuelle Überprüfungen

## Lizenzinformationen

Dieses Projekt unterliegt der MIT-Lizenz, welche den Benutzern freie Hand gibt, das Softwareprojekt zu nutzen, modifizieren und weiterzugeben. Weitere Informationen finden Sie in der Datei `LICENSE`.

Diese Dokumentation ist Teil des fortlaufenden Entwicklungs- und Überwachungsprozesses für die Portfolioüberwachungssysteme der Familie Kemmer und soll als einsetzbare Anleitung dienen, um den Tracker in verschiedenen Szenarien effektiv zu nutzen.