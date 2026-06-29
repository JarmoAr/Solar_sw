import json
import sqlite3
from pathlib import Path

from aurinko_optimo.models import ControlDecision, ControlSettings, PowerFlow


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
            self._initialize_control_settings(conn)

    def _initialize_control_settings(self, conn: sqlite3.Connection) -> None:
        existing_columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(control_settings)").fetchall()
        }
        if existing_columns and "sales_margin_cents_kwh" not in existing_columns:
            row = conn.execute(
                """
                SELECT sales_margin_eur_mwh, limit_when_net_price_below_eur_mwh,
                       limited_export_percent, max_export_w
                FROM control_settings
                WHERE id = 1
                """
            ).fetchone()
            conn.execute("DROP TABLE control_settings")
            self._create_control_settings_table(conn)
            if row:
                conn.execute(
                    """
                    INSERT INTO control_settings (
                        id, sales_margin_cents_kwh, limit_when_net_price_below_cents_kwh,
                        limited_export_percent, max_export_w
                    ) VALUES (1, ?, ?, ?, ?)
                    """,
                    (row[0] / 10, row[1] / 10, row[2], row[3]),
                )
            return

        self._create_control_settings_table(conn)

    def _create_control_settings_table(self, conn: sqlite3.Connection) -> None:
        conn.execute(
                """
                CREATE TABLE IF NOT EXISTS control_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    sales_margin_cents_kwh REAL NOT NULL,
                    limit_when_net_price_below_cents_kwh REAL NOT NULL,
                    limited_export_percent REAL NOT NULL,
                    max_export_w INTEGER NOT NULL
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

    def get_control_settings(self, defaults: ControlSettings) -> ControlSettings:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT sales_margin_cents_kwh, limit_when_net_price_below_cents_kwh,
                       limited_export_percent, max_export_w
                FROM control_settings
                WHERE id = 1
                """
            ).fetchone()
        return ControlSettings(**dict(row)) if row else defaults

    def save_control_settings(self, control_settings: ControlSettings) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO control_settings (
                    id, sales_margin_cents_kwh, limit_when_net_price_below_cents_kwh,
                    limited_export_percent, max_export_w
                ) VALUES (1, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    sales_margin_cents_kwh = excluded.sales_margin_cents_kwh,
                    limit_when_net_price_below_cents_kwh = excluded.limit_when_net_price_below_cents_kwh,
                    limited_export_percent = excluded.limited_export_percent,
                    max_export_w = excluded.max_export_w
                """,
                (
                    control_settings.sales_margin_cents_kwh,
                    control_settings.limit_when_net_price_below_cents_kwh,
                    control_settings.limited_export_percent,
                    control_settings.max_export_w,
                ),
            )
