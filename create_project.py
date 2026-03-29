"""
LogIQ v2 — Project Structure Creator
Run this script to create the entire project structure with all files.
Usage: python create_project.py
"""

import os

# ── Base path ─────────────────────────────────────────────────
BASE = r"D:\Project\Anomaly_detection"

# ── File contents ─────────────────────────────────────────────

FILES = {

    # ── config ────────────────────────────────────────────────
    "config/__init__.py": "",

    "config/settings.py": '''
# ============================================================
# LogIQ v2 — Central Configuration
# All settings in one place. Change here, affects everywhere.
# ============================================================

# ── Dataset options ──────────────────────────────────────────
AVAILABLE_DATASETS = ["synthetic", "nasa"]
DEFAULT_DATASET    = "synthetic"

# ── Model options ────────────────────────────────────────────
AVAILABLE_MODELS = ["isolation_forest", "lstm"]
DEFAULT_MODEL    = "isolation_forest"

# ── Storage options ──────────────────────────────────────────
AVAILABLE_STORAGES = ["sqlite", "elasticsearch"]
DEFAULT_STORAGE    = "sqlite"

# ── Pipeline options ─────────────────────────────────────────
AVAILABLE_PIPELINES = ["file", "kafka"]
DEFAULT_PIPELINE    = "file"

# ── Kafka ────────────────────────────────────────────────────
KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC     = "logs-logiq"

# ── Elasticsearch ────────────────────────────────────────────
ES_HOST  = "http://localhost:9200"
ES_INDEX = "logs-logiq"

# ── SQLite ───────────────────────────────────────────────────
SQLITE_PATH = "storage/db/logs.db"

# ── Isolation Forest ─────────────────────────────────────────
IF_N_ESTIMATORS  = 100
IF_CONTAMINATION = 0.05
IF_RANDOM_STATE  = 42
IF_TRAIN_SIZE    = 50

# ── LSTM ─────────────────────────────────────────────────────
LSTM_SEQ_LEN  = 10
LSTM_EPOCHS   = 5
LSTM_UNITS    = 64

# ── Log generation ───────────────────────────────────────────
LOG_INTERVAL_SEC = 1

# ── Synthetic dataset ────────────────────────────────────────
SYNTHETIC_SERVICES    = ["AuthService", "PaymentService", "OrderService"]
SYNTHETIC_ERROR_RATE  = 0.05
SYNTHETIC_WARN_RATE   = 0.10

SYNTHETIC_NORMAL_MSGS = [
    "Request processed successfully",
    "User authenticated",
    "Order created",
    "Payment completed",
    "Cache hit",
    "Session started",
    "Health check passed"
]

SYNTHETIC_ERROR_MSGS = [
    "Invalid token",
    "Database connection failed",
    "Timeout occurred",
    "Null pointer exception",
    "Memory overflow",
    "Service unavailable"
]

SYNTHETIC_WARN_MSGS = [
    "Slow response detected",
    "Retry attempt",
    "High memory usage",
    "Connection pool exhausted",
    "Rate limit approaching"
]

# ── NASA dataset ─────────────────────────────────────────────
NASA_LOG_PATH = "datasets/raw/nasa_access.log"

# ── Raw data paths ───────────────────────────────────────────
RAW_DATA_DIR  = "datasets/raw"
LIVE_DATA_DIR = "datasets/live"
LIVE_LOG_PATH = "datasets/live/live_logs.log"

# ── Backend ──────────────────────────────────────────────────
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 5000
BACKEND_DEBUG = True
''',

    # ── datasets ──────────────────────────────────────────────
    "datasets/__init__.py": "",
    "datasets/raw/.gitkeep": "",
    "datasets/live/.gitkeep": "",

    "datasets/base.py": '''
# ============================================================
# BaseDataset — Every dataset must inherit from this
# To add a new dataset:
#   1. Create a new file in datasets/
#   2. Inherit from BaseDataset
#   3. Implement get_log()
#   4. Register in datasets/utils.py
# ============================================================

class BaseDataset:

    def get_log(self):
        """
        Returns one raw log line as a string.
        Called repeatedly by the pipeline.
        """
        raise NotImplementedError

    def name(self):
        """
        Returns dataset name e.g. "synthetic"
        Must match the key in datasets/utils.py
        """
        raise NotImplementedError

    def description(self):
        """
        Human readable description of this dataset.
        """
        raise NotImplementedError
''',

    "datasets/synthetic.py": '''
# ============================================================
# SyntheticDataset — Generates realistic fake logs forever
# No file needed — generates logs in memory
# ============================================================

import random
from datetime import datetime
from datasets.base import BaseDataset
from config.settings import (
    SYNTHETIC_SERVICES,
    SYNTHETIC_ERROR_RATE,
    SYNTHETIC_WARN_RATE,
    SYNTHETIC_NORMAL_MSGS,
    SYNTHETIC_ERROR_MSGS,
    SYNTHETIC_WARN_MSGS
)


class SyntheticDataset(BaseDataset):

    def name(self):
        return "synthetic"

    def description(self):
        return "Generates realistic synthetic application logs in real time"

    def get_log(self):
        """
        Generates one synthetic log line with current timestamp.
        Format: YYYY-MM-DD HH:MM:SS LEVEL SERVICE MESSAGE user_id=N
        """
        rand = random.random()

        if rand < SYNTHETIC_ERROR_RATE:
            level = "ERROR"
            msg   = random.choice(SYNTHETIC_ERROR_MSGS)
        elif rand < SYNTHETIC_ERROR_RATE + SYNTHETIC_WARN_RATE:
            level = "WARN"
            msg   = random.choice(SYNTHETIC_WARN_MSGS)
        else:
            level = "INFO"
            msg   = random.choice(SYNTHETIC_NORMAL_MSGS)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        service   = random.choice(SYNTHETIC_SERVICES)
        user_id   = random.randint(1, 500)

        return f"{timestamp} {level} {service} {msg} user_id={user_id}"
''',

    "datasets/nasa.py": '''
# ============================================================
# NASADataset — Reads real NASA HTTP access logs
# Download from: ftp://ita.ee.lbl.gov/traces/NASA_access_log_Jul95.gz
# Place extracted file at: datasets/raw/nasa_access.log
# ============================================================

import os
from datasets.base import BaseDataset
from config.settings import NASA_LOG_PATH


class NASADataset(BaseDataset):

    def __init__(self):
        self._file = None
        self._open_file()

    def _open_file(self):
        if not os.path.exists(NASA_LOG_PATH):
            raise FileNotFoundError(
                f"NASA log file not found at {NASA_LOG_PATH}. "
                f"Download from ftp://ita.ee.lbl.gov/traces/NASA_access_log_Jul95.gz"
            )
        self._file = open(NASA_LOG_PATH, "r", errors="ignore")

    def name(self):
        return "nasa"

    def description(self):
        return "Real NASA HTTP access logs from July 1995 — 1.8M requests"

    def get_log(self):
        """
        Reads one line from NASA log file.
        Loops back to start when file ends.
        """
        line = self._file.readline()
        if not line:
            self._file.seek(0)
            line = self._file.readline()
        return line.strip()
''',

    "datasets/utils.py": '''
# ============================================================
# Dataset Registry — Add new datasets here
# Usage: dataset = get_dataset("synthetic")
# ============================================================

from datasets.synthetic import SyntheticDataset
from datasets.nasa      import NASADataset

DATASET_REGISTRY = {
    "synthetic": SyntheticDataset,
    "nasa":      NASADataset,
}


def get_dataset(name: str):
    """
    Returns an instance of the requested dataset.
    Raises ValueError if dataset not found.
    """
    if name not in DATASET_REGISTRY:
        raise ValueError(
            f"Unknown dataset: '{name}'. "
            f"Available: {list(DATASET_REGISTRY.keys())}"
        )
    return DATASET_REGISTRY[name]()


def list_datasets():
    """Returns list of available dataset names."""
    return list(DATASET_REGISTRY.keys())
''',

    # ── preprocessing ─────────────────────────────────────────
    "preprocessing/__init__.py": "",

    "preprocessing/base.py": '''
# ============================================================
# BasePreprocessor — Every preprocessor must inherit from this
# To add a new preprocessor:
#   1. Create a new file in preprocessing/
#   2. Inherit from BasePreprocessor
#   3. Implement parse() and extract_features()
#   4. Register in preprocessing/utils.py
# ============================================================

import numpy as np


class BasePreprocessor:

    def parse(self, raw_log: str) -> dict:
        """
        Converts raw log string into a structured dictionary.
        Returns None if log cannot be parsed.

        Example output for synthetic:
        {
            "timestamp": "2026-03-21 18:00:00",
            "level":     "ERROR",
            "service":   "AuthService",
            "message":   "Invalid token",
            "user_id":   101
        }
        """
        raise NotImplementedError

    def extract_features(self, parsed_log: dict) -> np.ndarray:
        """
        Converts parsed log dict into a numerical feature vector.
        This is what the ML model receives.
        Must always return the same length array.
        """
        raise NotImplementedError

    def feature_names(self) -> list:
        """
        Returns list of feature names for explainability.
        Must match the order of extract_features() output.
        """
        raise NotImplementedError
''',

    "preprocessing/synthetic.py": '''
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
''',

    "preprocessing/nasa.py": '''
# ============================================================
# NASAPreprocessor — Parses and extracts features from
# NASA HTTP log format:
# "host - - [date] "METHOD /path HTTP/1.0" status bytes"
# ============================================================

import re
import numpy as np
from preprocessing.base import BasePreprocessor

LOG_PATTERN = re.compile(
    r\'(\\S+) - - \\[(.+?)\\] "(\\S+) (\\S+)[^"]*" (\\d+) (\\S+)\'
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

        return {
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
''',

    "preprocessing/utils.py": '''
# ============================================================
# Preprocessor Registry — Add new preprocessors here
# Usage: preprocessor = get_preprocessor("synthetic")
# ============================================================

from preprocessing.synthetic import SyntheticPreprocessor
from preprocessing.nasa      import NASAPreprocessor

PREPROCESSOR_REGISTRY = {
    "synthetic": SyntheticPreprocessor,
    "nasa":      NASAPreprocessor,
}


def get_preprocessor(dataset_name: str):
    """
    Returns preprocessor matching the dataset name.
    Each dataset has exactly one preprocessor.
    """
    if dataset_name not in PREPROCESSOR_REGISTRY:
        raise ValueError(
            f"No preprocessor for dataset: \'{dataset_name}\'. "
            f"Available: {list(PREPROCESSOR_REGISTRY.keys())}"
        )
    return PREPROCESSOR_REGISTRY[dataset_name]()


def list_preprocessors():
    """Returns list of available preprocessor names."""
    return list(PREPROCESSOR_REGISTRY.keys())
''',

    # ── models ────────────────────────────────────────────────
    "models/__init__.py": "",

    "models/base.py": '''
# ============================================================
# BaseModel — Every model must inherit from this
# To add a new model:
#   1. Create a new file in models/
#   2. Inherit from BaseModel
#   3. Implement train(), predict(), is_ready()
#   4. Register in models/utils.py
# ============================================================

import numpy as np


class BaseModel:

    def train(self, X: list):
        """
        Trains the model on a list of feature vectors.
        Called once enough logs are collected.
        """
        raise NotImplementedError

    def predict(self, features: np.ndarray) -> bool:
        """
        Returns True if log is anomalous, False if normal.
        Called for every incoming log.
        """
        raise NotImplementedError

    def is_ready(self) -> bool:
        """
        Returns True if model is trained and ready to predict.
        """
        raise NotImplementedError

    def name(self) -> str:
        """
        Returns model name e.g. "isolation_forest"
        """
        raise NotImplementedError

    def description(self) -> str:
        """
        Human readable description of this model.
        """
        raise NotImplementedError
''',

    "models/isolation_forest.py": '''
# ============================================================
# IsolationForestModel — Unsupervised anomaly detection
# Trains on first N logs, then flags outliers
# ============================================================

import numpy as np
from sklearn.ensemble import IsolationForest
from models.base import BaseModel
from config.settings import (
    IF_N_ESTIMATORS,
    IF_CONTAMINATION,
    IF_RANDOM_STATE,
    IF_TRAIN_SIZE
)


class IsolationForestModel(BaseModel):

    def __init__(self):
        self._model = IsolationForest(
            n_estimators  = IF_N_ESTIMATORS,
            contamination = IF_CONTAMINATION,
            random_state  = IF_RANDOM_STATE
        )
        self._trained      = False
        self._train_buffer = []
        self._train_size   = IF_TRAIN_SIZE

    def train(self, X: list):
        """Trains on provided feature vectors."""
        X = np.array(X, dtype=float)
        self._model.fit(X)
        self._trained = True
        print(f"[IsolationForest] Trained on {len(X)} samples")

    def predict(self, features: np.ndarray) -> bool:
        """
        Buffers features until train_size reached,
        then trains and predicts.
        Returns True = anomaly, False = normal.
        """
        self._train_buffer.append(features)

        if not self._trained and len(self._train_buffer) >= self._train_size:
            self.train(self._train_buffer)

        if not self._trained:
            return False

        features = np.array(features, dtype=float).reshape(1, -1)
        prediction = self._model.predict(features)[0]
        return prediction == -1

    def is_ready(self) -> bool:
        return self._trained

    def name(self) -> str:
        return "isolation_forest"

    def description(self) -> str:
        return (
            "Unsupervised anomaly detection using Isolation Forest. "
            f"Trains on first {self._train_size} logs. "
            "No labelled data required."
        )
''',

    "models/lstm.py": '''
# ============================================================
# LSTMModel — Sequence-based anomaly detection
# Learns normal log sequences, flags deviations
# ============================================================

import numpy as np
import collections
from models.base import BaseModel
from config.settings import LSTM_SEQ_LEN


class LSTMModel(BaseModel):

    def __init__(self):
        self._window   = collections.deque(maxlen=LSTM_SEQ_LEN)
        self._baseline = {}
        self._trained  = False
        self._count    = 0
        self._warmup   = LSTM_SEQ_LEN * 3

    def train(self, X: list):
        """Builds baseline statistics from feature window."""
        X = np.array(X, dtype=float)
        self._baseline = {
            "mean": np.mean(X, axis=0),
            "std":  np.std(X, axis=0) + 1e-6
        }
        self._trained = True

    def predict(self, features: np.ndarray) -> bool:
        """
        Detects anomaly by measuring deviation from learned baseline.
        Returns True = anomaly, False = normal.
        """
        self._window.append(features)
        self._count += 1

        if not self._trained and self._count >= self._warmup:
            self.train(list(self._window))

        if not self._trained:
            return False

        deviation = np.abs(features - self._baseline["mean"]) / self._baseline["std"]
        anomaly_score = np.mean(deviation)
        return float(anomaly_score) > 2.5

    def is_ready(self) -> bool:
        return self._trained

    def name(self) -> str:
        return "lstm"

    def description(self) -> str:
        return (
            "Sequence-based anomaly detection using statistical baseline. "
            f"Warms up on first {self._warmup} logs. "
            "Detects temporal pattern deviations."
        )
''',

    "models/utils.py": '''
# ============================================================
# Model Registry — Add new models here
# Usage: model = get_model("isolation_forest")
# ============================================================

from models.isolation_forest import IsolationForestModel
from models.lstm             import LSTMModel

MODEL_REGISTRY = {
    "isolation_forest": IsolationForestModel,
    "lstm":             LSTMModel,
}


def get_model(name: str):
    """
    Returns a fresh instance of the requested model.
    Raises ValueError if model not found.
    """
    if name not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model: \'{name}\'. "
            f"Available: {list(MODEL_REGISTRY.keys())}"
        )
    return MODEL_REGISTRY[name]()


def list_models():
    """Returns list of available model names."""
    return list(MODEL_REGISTRY.keys())
''',

    # ── storage ───────────────────────────────────────────────
    "storage/__init__.py": "",
    "storage/db/.gitkeep": "",

    "storage/base.py": '''
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
''',

    "storage/sqlite.py": '''
# ============================================================
# SQLiteStorage — Lightweight storage using SQLite
# No Docker needed. Perfect for development and demo.
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
                f"FROM logs GROUP BY bucket ORDER BY bucket DESC LIMIT 100"
            ).fetchall()
        return list(reversed([
            {"time": r[0], "total": r[1], "anomalies": r[2] or 0}
            for r in rows
        ]))
''',

    "storage/elasticsearch.py": '''
# ============================================================
# ElasticsearchStorage — Production storage using ES
# Requires Docker: docker compose up -d
# ============================================================

from elasticsearch import Elasticsearch
from storage.base import BaseStorage
from config.settings import ES_HOST, ES_INDEX


class ElasticsearchStorage(BaseStorage):

    def __init__(self):
        self._es    = Elasticsearch(ES_HOST, verify_certs=False,
                                    ssl_show_warn=False, request_timeout=30)
        self._index = ES_INDEX

    def save(self, parsed_log: dict, anomaly: bool):
        doc = {
            "timestamp": str(parsed_log.get("timestamp", "")),
            "level":     parsed_log.get("level", "INFO"),
            "service":   parsed_log.get("service", "Unknown"),
            "message":   parsed_log.get("message", ""),
            "anomaly":   bool(anomaly)
        }
        self._es.index(index=self._index, document=doc)

    def get_logs(self, limit: int = 50) -> list:
        result = self._es.search(
            index=self._index,
            size=limit,
            sort=[{"timestamp": {"order": "desc"}}],
            query={"match_all": {}}
        )
        return [h["_source"] for h in result["hits"]["hits"]]

    def get_total_count(self) -> int:
        return self._es.count(index=self._index)["count"]

    def get_anomaly_count(self) -> int:
        return self._es.count(
            index=self._index,
            query={"term": {"anomaly": True}}
        )["count"]

    def get_service_stats(self) -> list:
        result = self._es.search(
            index=self._index, size=0,
            aggs={"by_service": {
                "terms": {"field": "service.keyword"},
                "aggs":  {"anomalies": {"filter": {"term": {"anomaly": True}}}}
            }}
        )
        return [
            {"service":   b["key"],
             "total":     b["doc_count"],
             "anomalies": b["anomalies"]["doc_count"]}
            for b in result["aggregations"]["by_service"]["buckets"]
        ]

    def get_timeline(self, bucket_seconds: int = 10) -> list:
        result = self._es.search(
            index=self._index, size=0,
            aggs={"over_time": {
                "date_histogram": {
                    "field": "timestamp",
                    "fixed_interval": f"{bucket_seconds}s",
                    "order": {"_key": "desc"}
                },
                "aggs": {"anomalies": {"filter": {"term": {"anomaly": True}}}}
            }}
        )
        buckets = result["aggregations"]["over_time"]["buckets"][:100]
        return list(reversed([
            {"time":      b["key_as_string"],
             "total":     b["doc_count"],
             "anomalies": b["anomalies"]["doc_count"]}
            for b in buckets
        ]))
''',

    "storage/utils.py": '''
# ============================================================
# Storage Registry — Add new storage backends here
# Usage: storage = get_storage("sqlite")
# ============================================================

from storage.sqlite        import SQLiteStorage
from storage.elasticsearch import ElasticsearchStorage

STORAGE_REGISTRY = {
    "sqlite":        SQLiteStorage,
    "elasticsearch": ElasticsearchStorage,
}


def get_storage(name: str):
    """
    Returns an instance of the requested storage.
    Raises ValueError if storage not found.
    """
    if name not in STORAGE_REGISTRY:
        raise ValueError(
            f"Unknown storage: \'{name}\'. "
            f"Available: {list(STORAGE_REGISTRY.keys())}"
        )
    return STORAGE_REGISTRY[name]()


def list_storages():
    """Returns list of available storage names."""
    return list(STORAGE_REGISTRY.keys())
''',

    # ── pipeline ──────────────────────────────────────────────
    "pipeline/__init__.py": "",

    "pipeline/base.py": '''
# ============================================================
# BasePipeline — Every pipeline must inherit from this
# To add a new pipeline:
#   1. Create a new file in pipeline/
#   2. Inherit from BasePipeline
#   3. Implement run() and stop()
#   4. Register in pipeline/utils.py
# ============================================================


class BasePipeline:

    def run(self, dataset, preprocessor, model, storage):
        """
        Main pipeline loop.
        Connects dataset → preprocessor → model → storage.
        Runs until stop() is called.
        """
        raise NotImplementedError

    def stop(self):
        """Stops the pipeline gracefully."""
        raise NotImplementedError

    def name(self) -> str:
        raise NotImplementedError

    def description(self) -> str:
        raise NotImplementedError
''',

    "pipeline/file.py": '''
# ============================================================
# FilePipeline — Lightweight pipeline using file/memory
# No Kafka needed. Perfect for development and demo.
# ============================================================

import time
from pipeline.base import BasePipeline
from config.settings import LOG_INTERVAL_SEC


class FilePipeline(BasePipeline):

    def __init__(self):
        self._running = False

    def run(self, dataset, preprocessor, model, storage):
        """
        Pulls logs from dataset, processes, stores.
        Runs every LOG_INTERVAL_SEC seconds.
        """
        self._running = True
        print(f"[FilePipeline] Started with dataset={dataset.name()}")

        while self._running:
            try:
                raw_log = dataset.get_log()
                if not raw_log:
                    continue

                parsed = preprocessor.parse(raw_log)
                if not parsed:
                    continue

                features = preprocessor.extract_features(parsed)
                anomaly  = model.predict(features)
                storage.save(parsed, anomaly)

                print(
                    f"[Pipeline] {parsed['level']:5} | "
                    f"{parsed['service']:15} | "
                    f"{parsed['message'][:40]:40} | "
                    f"{'ANOMALY' if anomaly else 'normal'}"
                )

                time.sleep(LOG_INTERVAL_SEC)

            except Exception as e:
                print(f"[FilePipeline] Error: {e}")
                time.sleep(1)

    def stop(self):
        self._running = False
        print("[FilePipeline] Stopped")

    def name(self) -> str:
        return "file"

    def description(self) -> str:
        return "Lightweight pipeline — no Kafka needed"
''',

    "pipeline/kafka.py": '''
# ============================================================
# KafkaPipeline — Production pipeline using Apache Kafka
# Requires Docker: docker compose up -d
# ============================================================

import json
import time
from pipeline.base import BasePipeline
from config.settings import KAFKA_BOOTSTRAP, KAFKA_TOPIC, LOG_INTERVAL_SEC


class KafkaPipeline(BasePipeline):

    def __init__(self):
        self._running  = False
        self._producer = None
        self._consumer = None

    def _get_producer(self):
        from kafka import KafkaProducer
        return KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    def _get_consumer(self):
        from kafka import KafkaConsumer
        return KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            auto_offset_reset="latest",
            value_deserializer=lambda x: json.loads(x.decode())
        )

    def run(self, dataset, preprocessor, model, storage):
        """
        Produces logs to Kafka, consumes and processes them.
        """
        self._running  = True
        self._producer = self._get_producer()
        self._consumer = self._get_consumer()

        print(f"[KafkaPipeline] Started — topic={KAFKA_TOPIC}")

        import threading
        producer_thread = threading.Thread(
            target=self._produce, args=(dataset,), daemon=True
        )
        producer_thread.start()

        for msg in self._consumer:
            if not self._running:
                break
            try:
                raw_log  = msg.value.get("log", "")
                parsed   = preprocessor.parse(raw_log)
                if not parsed:
                    continue
                features = preprocessor.extract_features(parsed)
                anomaly  = model.predict(features)
                storage.save(parsed, anomaly)
                print(
                    f"[Pipeline] {parsed['level']:5} | "
                    f"{parsed['service']:15} | "
                    f"{'ANOMALY' if anomaly else 'normal'}"
                )
            except Exception as e:
                print(f"[KafkaPipeline] Error: {e}")

    def _produce(self, dataset):
        """Continuously produces logs to Kafka topic."""
        while self._running:
            try:
                log = dataset.get_log()
                self._producer.send(KAFKA_TOPIC, {"log": log})
                time.sleep(LOG_INTERVAL_SEC)
            except Exception as e:
                print(f"[KafkaProducer] Error: {e}")
                time.sleep(1)

    def stop(self):
        self._running = False
        if self._consumer:
            self._consumer.close()
        print("[KafkaPipeline] Stopped")

    def name(self) -> str:
        return "kafka"

    def description(self) -> str:
        return "Production pipeline using Apache Kafka"
''',

    "pipeline/utils.py": '''
# ============================================================
# Pipeline Registry — Add new pipelines here
# Usage: pipeline = get_pipeline("file")
# ============================================================

from pipeline.file  import FilePipeline
from pipeline.kafka import KafkaPipeline

PIPELINE_REGISTRY = {
    "file":  FilePipeline,
    "kafka": KafkaPipeline,
}


def get_pipeline(name: str):
    """
    Returns an instance of the requested pipeline.
    Raises ValueError if pipeline not found.
    """
    if name not in PIPELINE_REGISTRY:
        raise ValueError(
            f"Unknown pipeline: \'{name}\'. "
            f"Available: {list(PIPELINE_REGISTRY.keys())}"
        )
    return PIPELINE_REGISTRY[name]()


def list_pipelines():
    """Returns list of available pipeline names."""
    return list(PIPELINE_REGISTRY.keys())
''',

    # ── backend ───────────────────────────────────────────────
    "backend/__init__.py": "",

    "backend/app.py": '''
# ============================================================
# Flask Backend — REST API for the dashboard
# Reads from storage and exposes data to frontend
# ============================================================

import threading
from flask import Flask, jsonify, request
from flask_cors import CORS

from config.settings  import BACKEND_HOST, BACKEND_PORT, BACKEND_DEBUG
from storage.utils    import get_storage
from models.utils     import list_models
from datasets.utils   import list_datasets
from pipeline.utils   import list_pipelines

app     = Flask(__name__)
CORS(app)

storage         = None
pipeline_obj    = None
pipeline_thread = None


def init_storage(storage_name: str):
    global storage
    storage = get_storage(storage_name)


# ── Info routes ───────────────────────────────────────────────

@app.route("/info", methods=["GET"])
def info():
    return jsonify({
        "models":    list_models(),
        "datasets":  list_datasets(),
        "pipelines": list_pipelines(),
    })


# ── Pipeline control routes ───────────────────────────────────

@app.route("/start", methods=["POST"])
def start():
    global pipeline_obj, pipeline_thread

    if pipeline_obj and pipeline_thread and pipeline_thread.is_alive():
        return jsonify({"message": "Pipeline already running"}), 400

    data          = request.json or {}
    model_name    = data.get("model",    "isolation_forest")
    dataset_name  = data.get("dataset",  "synthetic")
    pipeline_name = data.get("pipeline", "file")

    from datasets.utils      import get_dataset
    from preprocessing.utils import get_preprocessor
    from models.utils        import get_model
    from pipeline.utils      import get_pipeline

    dataset      = get_dataset(dataset_name)
    preprocessor = get_preprocessor(dataset_name)
    model        = get_model(model_name)
    pipeline_obj = get_pipeline(pipeline_name)

    pipeline_thread = threading.Thread(
        target=pipeline_obj.run,
        args=(dataset, preprocessor, model, storage),
        daemon=True
    )
    pipeline_thread.start()

    return jsonify({
        "message":  f"Pipeline started",
        "model":    model_name,
        "dataset":  dataset_name,
        "pipeline": pipeline_name
    })


@app.route("/stop", methods=["POST"])
def stop():
    global pipeline_obj
    if not pipeline_obj:
        return jsonify({"message": "No pipeline running"}), 400
    pipeline_obj.stop()
    pipeline_obj = None
    return jsonify({"message": "Pipeline stopped"})


@app.route("/status", methods=["GET"])
def status():
    running = (
        pipeline_thread is not None and
        pipeline_thread.is_alive()
    )
    return jsonify({"running": running})


# ── Data routes ───────────────────────────────────────────────

@app.route("/metrics", methods=["GET"])
def metrics():
    try:
        total    = storage.get_total_count()
        anomalies = storage.get_anomaly_count()
        return jsonify({
            "total":     total,
            "anomalies": anomalies,
            "normal":    total - anomalies,
            "rate":      round(anomalies / total * 100, 2) if total > 0 else 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logs", methods=["GET"])
def logs():
    try:
        limit = int(request.args.get("limit", 50))
        return jsonify(storage.get_logs(limit))
    except Exception as e:
        return jsonify([]), 500


@app.route("/services", methods=["GET"])
def services():
    try:
        return jsonify(storage.get_service_stats())
    except Exception as e:
        return jsonify([]), 500


@app.route("/timeline", methods=["GET"])
def timeline():
    try:
        bucket = int(request.args.get("bucket", 10))
        return jsonify(storage.get_timeline(bucket))
    except Exception as e:
        return jsonify([]), 500


# ── Run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    storage_name = sys.argv[1] if len(sys.argv) > 1 else "sqlite"
    init_storage(storage_name)
    print(f"[Backend] Starting with storage={storage_name}")
    app.run(host=BACKEND_HOST, port=BACKEND_PORT, debug=BACKEND_DEBUG)
''',

    # ── frontend ──────────────────────────────────────────────
    "frontend/index.html": "<!-- Frontend coming soon -->",
    "frontend/style.css":  "/* Styles coming soon */",
    "frontend/script.js":  "// Scripts coming soon",

    # ── streamlit ─────────────────────────────────────────────
    "streamlit_app/__init__.py": "",
    "streamlit_app/app.py": "# Streamlit app coming soon",

    # ── run.py ────────────────────────────────────────────────
    "run.py": '''
# ============================================================
# LogIQ v2 — Single Entry Point
# Usage examples:
#
#   python run.py
#   python run.py --model lstm --storage sqlite --pipeline file
#   python run.py --model isolation_forest --storage elasticsearch --pipeline kafka
#   python run.py --backend --storage sqlite
# ============================================================

import argparse
from config.settings import (
    DEFAULT_MODEL, DEFAULT_DATASET,
    DEFAULT_STORAGE, DEFAULT_PIPELINE
)


def run_pipeline(args):
    from datasets.utils      import get_dataset
    from preprocessing.utils import get_preprocessor
    from models.utils        import get_model
    from storage.utils       import get_storage
    from pipeline.utils      import get_pipeline

    print("=" * 60)
    print("LogIQ v2 — AIOps Log Anomaly Detection")
    print("=" * 60)
    print(f"  Dataset  : {args.dataset}")
    print(f"  Model    : {args.model}")
    print(f"  Storage  : {args.storage}")
    print(f"  Pipeline : {args.pipeline}")
    print("=" * 60)

    dataset      = get_dataset(args.dataset)
    preprocessor = get_preprocessor(args.dataset)
    model        = get_model(args.model)
    storage      = get_storage(args.storage)
    pipeline     = get_pipeline(args.pipeline)

    pipeline.run(dataset, preprocessor, model, storage)


def run_backend(args):
    from storage.utils import get_storage
    import backend.app as app_module

    app_module.init_storage(args.storage)
    print(f"[Backend] Starting with storage={args.storage}")
    app_module.app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LogIQ v2")

    parser.add_argument("--model",    default=DEFAULT_MODEL,
                        help="Model to use")
    parser.add_argument("--dataset",  default=DEFAULT_DATASET,
                        help="Dataset to use")
    parser.add_argument("--storage",  default=DEFAULT_STORAGE,
                        help="Storage backend")
    parser.add_argument("--pipeline", default=DEFAULT_PIPELINE,
                        help="Pipeline type")
    parser.add_argument("--backend",  action="store_true",
                        help="Run Flask backend only")

    args = parser.parse_args()

    if args.backend:
        run_backend(args)
    else:
        run_pipeline(args)
''',

    # ── docker-compose ────────────────────────────────────────
    "docker-compose.yml": '''
services:

  zookeeper:
    image: confluentinc/cp-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - xpack.security.http.ssl.enabled=false
    ports:
      - "9200:9200"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
''',

    # ── requirements ──────────────────────────────────────────
    "requirements.txt": '''flask
flask-cors
scikit-learn
numpy
pandas
kafka-python
elasticsearch
streamlit
plotly
tensorflow
''',

    # ── README ────────────────────────────────────────────────
    "README.md": '''# LogIQ v2 — AIOps Log Anomaly Detection

## Quick Start

### Lightweight (no Docker):
```bash
python run.py
```

### Production (Docker):
```bash
docker compose up -d
python run.py --storage elasticsearch --pipeline kafka
```

### Backend only:
```bash
python run.py --backend --storage sqlite
```

## Options
| Flag | Options | Default |
|------|---------|---------|
| --model | isolation_forest, lstm | isolation_forest |
| --dataset | synthetic, nasa | synthetic |
| --storage | sqlite, elasticsearch | sqlite |
| --pipeline | file, kafka | file |

## Add new dataset
1. Create `datasets/your_dataset.py`
2. Inherit from `BaseDataset`
3. Create `preprocessing/your_dataset.py`
4. Inherit from `BasePreprocessor`
5. Register in `datasets/utils.py` and `preprocessing/utils.py`

## Add new model
1. Create `models/your_model.py`
2. Inherit from `BaseModel`
3. Register in `models/utils.py`
''',
}


# ── Create all files ──────────────────────────────────────────

def create_project():
    print(f"Creating LogIQ v2 at: {BASE}")
    print("=" * 60)

    created_dirs  = 0
    created_files = 0

    for relative_path, content in FILES.items():
        full_path = os.path.join(BASE, relative_path.replace("/", os.sep))
        dir_path  = os.path.dirname(full_path)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"  [DIR]  {dir_path}")
            created_dirs += 1

        if not os.path.exists(full_path):
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content.lstrip("\n"))
            print(f"  [FILE] {relative_path}")
            created_files += 1
        else:
            print(f"  [SKIP] {relative_path} (already exists)")

    print("=" * 60)
    print(f"Done! Created {created_dirs} dirs, {created_files} files")
    print(f"\nNext steps:")
    print(f"  cd {BASE}")
    print(f"  pip install -r requirements.txt")
    print(f"  python run.py")


if __name__ == "__main__":
    create_project()