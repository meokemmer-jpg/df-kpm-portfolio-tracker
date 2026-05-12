"""HMAC-SHA256 Audit-Logger fuer K_0-relevante Events [CRUX-MK].

Pflicht per K12-K13 Akzeptanz-Kriterien.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_LOG_PATH = Path.home() / ".df-kpm-portfolio-tracker" / "audit.jsonl"
AUDIT_SECRET_KEY_PATH = Path.home() / ".df-kpm-portfolio-tracker" / "audit-secret.key"


def _ensure_secret_key() -> bytes:
    """Generiert oder liest HMAC-Secret-Key."""
    AUDIT_SECRET_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_SECRET_KEY_PATH.exists():
        secret = os.urandom(32)
        AUDIT_SECRET_KEY_PATH.write_bytes(secret)
        os.chmod(AUDIT_SECRET_KEY_PATH, 0o600)  # Owner-only
    return AUDIT_SECRET_KEY_PATH.read_bytes()


def _compute_hmac(payload: str, key: bytes) -> str:
    """Berechnet HMAC-SHA256 fuer Payload."""
    return hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def log_audit_event(
    event: str,
    df_id: str,
    details: dict[str, Any] | None = None,
) -> str:
    """Schreibt Audit-Event mit HMAC-SHA256-Signatur.

    Args:
        event: Event-Name (z.B. 'snapshot_created')
        df_id: DF-ID (z.B. 'df-kpm-portfolio-tracker')
        details: Event-Details (frei strukturiert)

    Returns:
        HMAC-Signatur als hex-String
    """
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "df_id": df_id,
        "details": details or {},
    }

    payload = json.dumps(entry, sort_keys=True)
    secret = _ensure_secret_key()
    signature = _compute_hmac(payload, secret)
    entry["hmac_sha256"] = signature

    # Append-only
    with AUDIT_LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    return signature


def verify_audit_event(entry: dict[str, Any]) -> bool:
    """Verifiziert HMAC-Signatur eines Audit-Events.

    Returns:
        True if signature valid, False otherwise
    """
    if "hmac_sha256" not in entry:
        return False
    expected_sig = entry.pop("hmac_sha256")
    payload = json.dumps(entry, sort_keys=True)
    secret = _ensure_secret_key()
    actual_sig = _compute_hmac(payload, secret)
    entry["hmac_sha256"] = expected_sig  # Restore
    return hmac.compare_digest(expected_sig, actual_sig)
