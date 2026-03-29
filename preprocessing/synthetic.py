# ============================================================
# SyntheticPreprocessor — Parses and extracts features from
# synthetic log format:
# "YYYY-MM-DD HH:MM:SS LEVEL SERVICE MESSAGE user_id=N"
# ============================================================

import re
import numpy as np
from preprocessing.base import BasePreprocessor

LOG_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"(INFO|WARN|ERROR) "
    r"(\w+) "
    r"(.+?) "
    r"user_id=(\d+)"
)

LEVEL_MAP = {"INFO": 0, "WARN": 1, "ERROR": 2}

ERROR_KEYWORDS = [
    "failed", "failure", "error", "exception",
    "timeout", "refused", "unavailable", "overflow",
    "invalid", "null", "crash", "critical"
]

WARN_KEYWORDS = [
    "slow", "retry", "high", "exhausted",
    "approaching", "warning", "degraded"
]


class SyntheticPreprocessor(BasePreprocessor):

    def parse(self, raw_log: str) -> dict:
        """
        Parses synthetic log line into structured dict.
        Returns None if format does not match.
        """
        if isinstance(raw_log, dict):
            raw_log = raw_log.get("log", "")

        match = LOG_PATTERN.match(raw_log.strip())
        if not match:
            return None

        return {
            "timestamp": match.group(1),
            "level":     match.group(2),
            "service":   match.group(3),
            "message":   match.group(4),
            "user_id":   int(match.group(5))
        }

    def extract_features(self, parsed_log: dict) -> np.ndarray:
        """
        Extracts 7 meaningful features from synthetic parsed log.
        No random fields like user_id — only signal-rich features.
        """
        msg   = parsed_log.get("message", "").lower()
        level = parsed_log.get("level", "INFO")

        level_numeric     = float(LEVEL_MAP.get(level, 0))
        message_length    = float(len(msg))
        word_count        = float(len(msg.split()))
        has_error_keyword = float(any(k in msg for k in ERROR_KEYWORDS))
        has_warn_keyword  = float(any(k in msg for k in WARN_KEYWORDS))
        is_error          = float(level == "ERROR")
        is_warn           = float(level == "WARN")

        return np.array([
            level_numeric,
            message_length,
            word_count,
            has_error_keyword,
            has_warn_keyword,
            is_error,
            is_warn
        ], dtype=float)

    def feature_names(self) -> list:
        return [
            "level_numeric",
            "message_length",
            "word_count",
            "has_error_keyword",
            "has_warn_keyword",
            "is_error",
            "is_warn"
        ]
