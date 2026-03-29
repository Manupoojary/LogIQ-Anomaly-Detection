# ============================================================
# SQLiteStorage — Lightweight storage using SQLite
# No Docker needed. 
# ============================================================

import sqlite3
import os
from storage.base import BaseStorage
from config.settings import SQLITE_PATH


class SQLiteStorage(BaseStorage):

    def __init__(self):
        os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
        self._path = SQLITE_PATH
        self._init_db()


    def clear(self):
        
        conn = sqlite3.connect(SQLITE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs")
        conn.commit()
        conn.close()

    def _connect(self):
        return sqlite3.connect(self._path)

    def _init_db(self):
        """Creates logs table if it does not exist."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    level     TEXT,
                    service   TEXT,
                    message   TEXT,
                    anomaly   INTEGER,
                    created   DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save(self, parsed_log: dict, anomaly: bool):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO logs (timestamp, level, service, message, anomaly) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    str(parsed_log.get("timestamp", "")),
                    parsed_log.get("level", "INFO"),
                    parsed_log.get("service", "Unknown"),
                    parsed_log.get("message", ""),
                    int(anomaly)
                )
            )
            conn.commit()

    def get_logs(self, limit: int = 50) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT timestamp, level, service, message, anomaly "
                "FROM logs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [
            {"timestamp": r[0], "level": r[1], "service": r[2],
             "message": r[3], "anomaly": bool(r[4])}
            for r in rows
        ]

    def get_total_count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]

    def get_anomaly_count(self) -> int:
        with self._connect() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM logs WHERE anomaly=1"
            ).fetchone()[0]

    def get_service_stats(self) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT service, COUNT(*) as total, "
                "SUM(anomaly) as anomalies FROM logs GROUP BY service"
            ).fetchall()
        return [
            {"service": r[0], "total": r[1], "anomalies": r[2] or 0}
            for r in rows
        ]

    def get_timeline(self, bucket_seconds: int = 10) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT "
                f"strftime('%Y-%m-%d %H:%M:', timestamp) || "
                f"printf('%02d', (strftime('%S', timestamp) / {bucket_seconds}) * {bucket_seconds}) as bucket, "
                f"COUNT(*) as total, SUM(anomaly) as anomalies "
                f"FROM logs GROUP BY bucket ORDER BY bucket DESC LIMIT 500"
            ).fetchall()
        return list(reversed([
            {"time": r[0], "total": r[1], "anomalies": r[2] or 0}
            for r in rows
        ]))
    