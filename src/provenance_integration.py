"""K12+K13+K16 Provenance-Integration fuer df-kpm-portfolio-tracker [CRUX-MK].

W50-A Batch-2 Pattern (replicated from df-9os-next/loop_orchestrator.py W48).

Adressiert:
- K12: FullProvenanceEnvelope pro Portfolio-Snapshot (HMAC-signed, chain-linked)
- K13: RFC3161 External-Anchor (per-snapshot pflicht fuer Familien-Kapital)
- K16: AtomicLock fuer Concurrent-Spawn-Mutex

K_0-RELEVANZ: K_0-DIRECT (Familien-Vermoegen + KPM-Trading).

[CRUX-MK]
"""

from __future__ import annotations

import json
import logging
import os as _bootstrap_os
import sys as _sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

_DF_ROOT = Path(__file__).resolve().parent.parent.parent
_sys.path.insert(0, str(_DF_ROOT))

try:
    from _df_common.full_provenance_envelope import (  # type: ignore
        build_full_envelope,
        FullProvenanceEnvelope,
    )
    from _df_common.rfc3161_anchor import (  # type: ignore
        rfc3161_timestamp,
        AnchorRecord,
    )
    from _df_common.atomic_lock import AtomicLock  # type: ignore
    W48_FOUNDATION = True
except ImportError:
    W48_FOUNDATION = False

logger = logging.getLogger(__name__)

_K12_HMAC_SECRET = _bootstrap_os.environ.get(
    "DF_KPM_PORTFOLIO_HMAC_SECRET", "df-kpm-portfolio-dev-hmac-secret-v1"
)
_K12_ENVELOPE_TTL_S = int(_bootstrap_os.environ.get("DF_KPM_PORTFOLIO_ENVELOPE_TTL_S", "86400"))

DEFAULT_K16_LOCK_PATH = Path("/tmp/df-kpm-portfolio-tracker.lock.lockfile")


class PortfolioProvenanceRecorder:
    """K_0-DIRECT provenance recorder for portfolio NAV-snapshots.

    K11 try/except per record-call.
    K12 FullProvenanceEnvelope per snapshot (chain-linked).
    K13 RFC3161-Anchor (per-snapshot pflicht fuer Familien-Kapital).
    K16 Optional AtomicLock for K_0-DIRECT-mutation protection.
    """

    def __init__(self,
                 audit_dir: Path | str = "branch-hub/audit/df-kpm-portfolio/",
                 k16_lock_path: Optional[Path] = None,
                 k16_lock_ttl_s: float = 600.0):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.provenance_full_dir = self.audit_dir / "provenance-full"
        self.provenance_full_dir.mkdir(parents=True, exist_ok=True)
        self.anchors_dir = self.audit_dir / "anchors"
        self.anchors_dir.mkdir(parents=True, exist_ok=True)
        self._k16_lock_path = k16_lock_path
        self._k16_lock_ttl_s = k16_lock_ttl_s

    def _read_predecessor_hash(self) -> Optional[str]:
        if not W48_FOUNDATION:
            return None
        try:
            files = sorted(
                self.provenance_full_dir.glob("*.envelope.json"),
                key=lambda p: p.stat().st_mtime,
            )
            if not files:
                return None
            with open(files[-1], "r", encoding="utf-8") as f:
                env = json.load(f)
            return env.get("payload_hash")
        except Exception as e:
            logger.warning(f"K12 predecessor read failed: {e}")
            return None

    def record_portfolio_snapshot(self,
                                  snapshot_id: str,
                                  snapshot_payload: dict[str, Any],
                                  tenant_id: str = "kpm-family") -> Optional[dict]:
        """K12 envelope + K13 anchor per Portfolio-Snapshot.

        K_0-DIRECT: jeder NAV-Snapshot MUSS provenance haben (Familien-Vermoegen).
        """
        if not W48_FOUNDATION:
            logger.warning("W48 foundation unavailable")
            return None

        k16_lock = None
        if self._k16_lock_path is not None:
            k16_lock = AtomicLock(self._k16_lock_path, ttl_s=self._k16_lock_ttl_s)
            if not k16_lock.acquire():
                raise RuntimeError(
                    f"K16 Concurrent-Spawn-Mutex: another df-kpm-portfolio recorder running. "
                    f"Lock: {self._k16_lock_path}"
                )

        try:
            return self._record_internal(snapshot_id, snapshot_payload, tenant_id)
        finally:
            if k16_lock is not None:
                k16_lock.release()

    def _record_internal(self, snapshot_id: str, payload: dict, tenant_id: str) -> dict:
        result: dict[str, Any] = {}
        try:
            predecessor_hash = self._read_predecessor_hash()
            envelope = build_full_envelope(
                operation_id=snapshot_id,
                operation_type="df-kpm-portfolio-snapshot",
                issuer="df-kpm-portfolio-tracker",
                payload_dict=payload,
                secret=_K12_HMAC_SECRET,
                predecessor_hash=predecessor_hash,
                tenant_id=tenant_id,
                ttl_seconds=_K12_ENVELOPE_TTL_S,
            )
            env_out = self.provenance_full_dir / f"{snapshot_id}.envelope.json"
            with open(env_out, "w", encoding="utf-8") as f:
                json.dump(asdict(envelope), f, indent=2, default=str, ensure_ascii=False)
            result["envelope_path"] = str(env_out)
            result["payload_hash"] = envelope.payload_hash
            chain_hash_for_anchor = envelope.payload_hash
        except Exception as e:
            logger.warning(f"K12 envelope build failed: {e}")
            return result

        try:
            rfc_anchor = rfc3161_timestamp(chain_hash_for_anchor, provider="freetsa")
            anchor_file = self.anchors_dir / "rfc3161-anchors.jsonl"
            with open(anchor_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(rfc_anchor)) + "\n")
            result["anchor_path"] = str(anchor_file)
        except Exception as e:
            logger.warning(f"K13 RFC3161 anchor failed (non-fatal): {e}")

        return result
