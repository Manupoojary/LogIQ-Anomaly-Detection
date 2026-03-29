# ============================================================
# NASAPreprocessor — Parses and extracts features from
# NASA HTTP log format:
# "host - - [date] "METHOD /path HTTP/1.0" status bytes"
# ============================================================

import re
import numpy as np
from preprocessing.base import BasePreprocessor
from datetime import datetime 

LOG_PATTERN = re.compile(
    r'(\S+) - - \[(.+?)\] "(\S+) (\S+)[^"]*" (\d+) (\S+)'
)

METHOD_MAP = {"GET": 0, "POST": 1, "HEAD": 2, "PUT": 3, "DELETE": 4}


class NASAPreprocessor(BasePreprocessor):

    def parse(self, raw_log: str) -> dict:
        """
        Parses NASA HTTP log line into structured dict.
        Returns None if format does not match.
        """
        match = LOG_PATTERN.match(raw_log.strip())
        if not match:
            return None

        status_code = int(match.group(5))
        bytes_sent  = match.group(6)

        parsed = {
            "timestamp":   match.group(2),
            "host":        match.group(1),
            "method":      match.group(3),
            "endpoint":    match.group(4),
            "status_code": status_code,
            "bytes_sent":  int(bytes_sent) if bytes_sent.isdigit() else 0,
            "level":       _status_to_level(status_code),
            "service":     _endpoint_to_service(match.group(4)),
            "message":     f"{match.group(3)} {match.group(4)} {status_code}"
        }


        parsed["timestamp"] = datetime.now().isoformat()

        return parsed

    def extract_features(self, parsed_log: dict) -> np.ndarray:
        """
        Extracts 6 meaningful features from NASA parsed log.
        """
        status     = parsed_log.get("status_code", 200)
        method     = parsed_log.get("method", "GET")
        endpoint   = parsed_log.get("endpoint", "/")
        bytes_sent = parsed_log.get("bytes_sent", 0)

        is_error_status  = float(status >= 500)
        is_warn_status   = float(400 <= status < 500)
        method_numeric   = float(METHOD_MAP.get(method, 0))
        endpoint_depth   = float(endpoint.count("/"))
        bytes_normalized = float(min(bytes_sent, 100000) / 100000)
        status_numeric   = float(status / 1000)

        return np.array([
            is_error_status,
            is_warn_status,
            method_numeric,
            endpoint_depth,
            bytes_normalized,
            status_numeric
        ], dtype=float)

    def feature_names(self) -> list:
        return [
            "is_error_status",
            "is_warn_status",
            "method_numeric",
            "endpoint_depth",
            "bytes_normalized",
            "status_numeric"
        ]


def _status_to_level(status_code: int) -> str:
    if status_code >= 500: return "ERROR"
    if status_code >= 400: return "WARN"
    return "INFO"


def _endpoint_to_service(endpoint: str) -> str:
    if "shuttle"  in endpoint: return "ShuttleService"
    if "images"   in endpoint: return "ImageService"
    if "history"  in endpoint: return "HistoryService"
    if "apollo"   in endpoint: return "ApolloService"
    return "GeneralService"
