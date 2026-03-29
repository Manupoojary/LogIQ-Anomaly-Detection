# ============================================================
# LogIQ v2 — Central Configuration
# All settings in one place. Change here, affects everywhere.
# ============================================================

import os


# Controls whether Kafka pipeline is allowed
ALLOW_KAFKA = os.getenv("ALLOW_KAFKA", "true").lower() == "true"


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
