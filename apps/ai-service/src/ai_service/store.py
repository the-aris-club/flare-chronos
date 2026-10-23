"""Run ownership and the append-only sign-off audit record (ADR-0011).

A Sign-off Request is bound to the principal that started the run, and every
Sign-off Decision is written here before the run resumes. The audit table
refuses UPDATE and DELETE at the database, so a restart or a bug cannot quietly
rewrite who approved what.
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    thread_id TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    principal TEXT NOT NULL,
    approved INTEGER NOT NULL,
    reason TEXT NOT NULL,
    decided_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit
BEGIN SELECT RAISE(ABORT, 'the sign-off audit record is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit
BEGIN SELECT RAISE(ABORT, 'the sign-off audit record is append-only'); END;
"""


class RunStore:
    """SQLite-backed ownership and audit, safe to share across request threads."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._db.executescript(_SCHEMA)

    def claim(self, thread_id: str, owner: str) -> bool:
        """Bind a new thread to ``owner``; True if the caller owns it afterwards."""
        with self._lock, self._db:
            self._db.execute(
                "INSERT OR IGNORE INTO runs (thread_id, owner) VALUES (?, ?)",
                (thread_id, owner),
            )
        return self.owner_of(thread_id) == owner

    def owner_of(self, thread_id: str) -> str | None:
        with self._lock:
            row = self._db.execute(
                "SELECT owner FROM runs WHERE thread_id = ?", (thread_id,)
            ).fetchone()
        return None if row is None else str(row["owner"])

    def record_decision(
        self, thread_id: str, principal: str, approved: bool, reason: str
    ) -> None:
        with self._lock, self._db:
            self._db.execute(
                "INSERT INTO audit (thread_id, principal, approved, reason) VALUES (?, ?, ?, ?)",
                (thread_id, principal, int(approved), reason),
            )

    def decisions(self, thread_id: str) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._db.execute(
                "SELECT * FROM audit WHERE thread_id = ? ORDER BY id", (thread_id,)
            ).fetchall()
        return [dict(r) for r in rows]
