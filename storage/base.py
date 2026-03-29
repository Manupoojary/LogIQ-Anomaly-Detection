# ============================================================
# BaseStorage — Every storage must inherit from this
# To add a new storage:
#   1. Create a new file in storage/
#   2. Inherit from BaseStorage
#   3. Implement all methods below
#   4. Register in storage/utils.py
# ============================================================


class BaseStorage:

    def save(self, parsed_log: dict, anomaly: bool):
        """Saves one parsed log with its anomaly flag."""
        raise NotImplementedError

    def get_logs(self, limit: int = 50) -> list:
        """Returns latest N logs ordered by newest first."""
        raise NotImplementedError

    def get_total_count(self) -> int:
        """Returns total number of logs stored."""
        raise NotImplementedError

    def get_anomaly_count(self) -> int:
        """Returns number of anomalous logs."""
        raise NotImplementedError

    def get_service_stats(self) -> list:
        """
        Returns per-service stats.
        Format: [{"service": "AuthService", "total": 100, "anomalies": 5}]
        """
        raise NotImplementedError

    def get_timeline(self, bucket_seconds: int = 10) -> list:
        """
        Returns time-bucketed log counts.
        Format: [{"time": "2026-03-21 18:00:00", "total": 10, "anomalies": 1}]
        """
        raise NotImplementedError
