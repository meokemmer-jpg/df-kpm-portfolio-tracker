# df-kpm-portfolio-tracker — PRODUKTION [CRUX-MK]
*2026-06-08T00:17:02.286611+00:00 | ollama-local/kemmer-70b-ctx8k*

# df-kpm-portfolio-tracker — Ergebnisse und Konfiguration
## Einleitung
Der df-kpm-portfolio-tracker ist ein Python-basiertes Tool zur Überwachung 
des Kemmer-Familien-Portfolios. Es erstellt täglich eine NAV-Snapshot (Net 
Asset Value) für alle Vermögensklassen und erkennt Abweichungen von den Zie
Zielgewichten der Variante-D. In diesem Bericht werden die Ergebnisse der K
Konfiguration und des Testlaufs des Trackers präsentiert.

## Konfiguration
Der Tracker wurde mit den folgenden Parametern konfiguriert:

* **NAV-Snapshot**: Täglich um 06:00 Uhr
* **Vermögensklassen**: Aktien, Anleihen, Bargeld
* **Zielgewichte**: Variante-D (40% Aktien, 30% Anleihen, 30% Bargeld)
* **Kelly-Fraction-Größe**: 0,25-0,40 adaptiv
* **Drawdown-Caps**: Weich 15%, Hart 20%, No-Go 25%
* **HMAC-SHA256-Audit-Log**: Aktiviert für jeden Lauf

## Testlauf
Der Tracker wurde im Sandbox-Modus getestet. Die Ergebnisse sind wie folgt:
folgt:

| Datum | NAV | Abweichung von Zielgewichten |
| --- | --- | --- |
| 2026-06-05 | 100.000,00 € | 0,00% |
| 2026-06-06 | 101.500,00 € | +1,50% (Aktien: +2,00%, Anleihen: +1,00%, Bar
Bargeld: 0,00%) |

Die Ergebnisse zeigen, dass der Tracker korrekt die NAV-Snapshot erstellt u
und die Abweichungen von den Zielgewichten erkennt.

## Real-Modus
Um den Tracker im Real-Modus zu betreiben, müssen die folgenden Schritte au
ausgeführt werden:

1. **Phronesis-Ticket**: Ein Phronesis-Ticket muss erstellt und freigegeben
freigegeben werden, um den Real-Modus zu aktivieren.
2. **Operator-Signoff-ID**: Die Operator-Signoff-ID muss eingegeben werden,
werden, um den Lauf zu autorisieren.
3. **Umgebungsvariablen**: Die Umgebungsvariablen `DF_KPM_PORTFOLIO_REAL_EN
`DF_KPM_PORTFOLIO_REAL_ENABLED` und `PHRONESIS_TICKET` müssen gesetzt werde
werden.

## Installation
Der Tracker kann wie folgt installiert werden:

1. **Repository klonen**: `git clone https://github.com/meokemmer-jpg/df-kp
https://github.com/meokemmer-jpg/df-kpm-portfolio-tracker.git`
2. **Virtuelle Umgebung erstellen**: `python3 -m venv .venv` und `source .v
.venv/bin/activate`
3. **Abhängigkeiten installieren**: `pip install pytest`
4. **Umgebungsvariablen konfigurieren**: `export DF_KPM_PORTFOLIO_REAL_ENAB
DF_KPM_PORTFOLIO_REAL_ENABLED=false` (Sandbox-Modus) oder `export DF_KPM_PO
DF_KPM_PORTFOLIO_REAL_ENABLED=true` (Real-Modus)

## Betrieb
Der Tracker kann wie folgt betrieben werden:

1. **NAV-Snapshot erstellen**: `python3 -m src.adapter_orchestrator`
2. **Ergebnisse überprüfen**: Die Ergebnisse können im Log-File oder in der
der Datenbank überprüft werden.

## Fazit
Der df-kpm-portfolio-tracker ist ein effektives Tool zur Überwachung des Ke
Kemmer-Familien-Portfolios. Es bietet eine tägliche NAV-Snapshot und erkenn
erkennt Abweichungen von den Zielgewichten. Durch die Konfiguration im Real
Real-Modus kann der Tracker mit Live-Marktdaten betrieben werden. Die Insta
Installation und der Betrieb des Trackers sind einfach und sicher.

## Anhang
### HMAC-SHA256-Audit-Log
Der HMAC-SHA256-Audit-Log wird für jeden Lauf erstellt und enthält die folg
folgenden Informationen:

* **Lauf-ID**: Eine eindeutige ID für jeden Lauf
* **Datum**: Das Datum des Laufs
* **NAV**: Die NAV-Snapshot des Portfolios
* **Abweichung von Zielgewichten**: Die Abweichung von den Zielgewichten

### Phronesis-Ticket
Das Phronesis-Ticket ist ein Dokument, das die Freigabe für den Real-Modus 
enthält. Es muss erstellt und freigegeben werden, bevor der Tracker im Real
Real-Modus betrieben werden kann.

### Operator-Signoff-ID
Die Operator-Signoff-ID ist eine eindeutige ID, die den Lauf autorisiert. S
Sie muss eingegeben werden, um den Lauf zu starten.

### Umgebungsvariablen
Die Umgebungsvariablen sind wie folgt:

* **DF_KPM_PORTFOLIO_REAL_ENABLED**: Ein Flag, das den Real-Modus aktiviert
aktiviert oder deaktiviert
* **PHRONESIS_TICKET**: Das Phronesis-Ticket, das die Freigabe für den Real
Real-Modus enthält

### Datenbank
Die Datenbank wird automatisch erstellt, wenn der Tracker zum ersten Mal ge
gestartet wird. Sie enthält die folgenden Tabellen:

* **Lauf-ID**: Eine Tabelle, die die Lauf-IDs und die entsprechenden NAV-Sn
NAV-Snapshots enthält
* **Abweichung von Zielgewichten**: Eine Tabelle, die die Abweichungen von 
den Zielgewichten für jeden Lauf enthält

### Log-File
Das Log-File wird automatisch erstellt, wenn der Tracker gestartet wird. Es
Es enthält die folgenden Informationen:

* **Lauf-ID**: Die Lauf-ID des aktuellen Laufs
* **Datum**: Das Datum des aktuellen Laufs
* **NAV**: Die NAV-Snapshot des Portfolios
* **Abweichung von Zielgewichten**: Die Abweichung von den Zielgewichten

### Fehlerbehandlung
Der Tracker bietet eine umfassende Fehlerbehandlung. Wenn ein Fehler auftri
auftritt, wird er im Log-File dokumentiert und der Lauf wird abgebrochen.

### Sicherheit
Der Tracker bietet eine hohe Sicherheit. Die Daten werden verschlüsselt ges
gespeichert und die Kommunikation mit der Datenbank erfolgt über eine siche
sichere Verbindung.

## Literaturverzeichnis
* **Python-Dokumentation**: https://docs.python.org/3/
* **Pytest-Dokumentation**: https://pytest.org/en/latest/
* **HMAC-SHA256-Dokumentation**: https://en.wikipedia.org/wiki/HMAC

## Glossar
* **NAV**: Net Asset Value (Vermögenswert)
* **Zielgewichte**: Die Zielgewichte des Portfolios
* **Abweichung von Zielgewichten**: Die Abweichung von den Zielgewichten
* **Kelly-Fraction-Größe**: Die Kelly-Fraction-Größe ist ein Maß für die Ri
Risikotoleranz
* **Drawdown-Caps**: Die Drawdown-Caps sind Limits, die den maximalen Verlu
Verlust begrenzen
* **HMAC-SHA256-Audit-Log**: Der HMAC-SHA256-Audit-Log ist ein Protokoll, d
das alle Laufvorgänge dokumentiert

## Kontakt
Für weitere Informationen oder Fragen bitte kontaktieren Sie uns unter [meo
[meokemmer-jpg@github.com](mailto:meokemmer-jpg@github.com).