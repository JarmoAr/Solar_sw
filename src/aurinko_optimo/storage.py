import json
import sqlite3
from pathlib import Path

from aurinko_optimo.models import ControlDecision, PowerFlow


class Storage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    production_w REAL,
                    consumption_w REAL,
                    grid_w REAL,
                    battery_w REAL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    export_limit_w INTEGER,
                    reason TEXT NOT NULL,
                    price_eur_mwh REAL,
                    grid_w REAL,
                    payload_json TEXT NOT NULL
                )
                """
            )

    def save_measurement(self, measurement: PowerFlow) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO measurements (
                    timestamp, production_w, consumption_w, grid_w, battery_w
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    measurement.timestamp.isoformat(),
                    measurement.production_w,
                    measurement.consumption_w,
                    measurement.grid_w,
                    measurement.battery_w,
                ),
            )

    def save_decision(self, decision: ControlDecision) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO decisions (
                    timestamp, action, export_limit_w, reason, price_eur_mwh, grid_w, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.timestamp.isoformat(),
                    decision.action.value,
                    decision.export_limit_w,
                    decision.reason,
                    decision.price_eur_mwh,
                    decision.grid_w,
                    json.dumps(decision.model_dump(mode="json")),
                ),
            )

    def latest_measurement(self) -> dict | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT timestamp, production_w, consumption_w, grid_w, battery_w
                FROM measurements
                ORDER BY timestamp DESC
                LIMIT 1
                """
            ).fetchone()
        return dict(row) if row else None

    def latest_decision(self) -> dict | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT timestamp, action, export_limit_w, reason, price_eur_mwh, grid_w
                FROM decisions
                ORDER BY timestamp DESC
                LIMIT 1
                """
            ).fetchone()
        return dict(row) if row else None
