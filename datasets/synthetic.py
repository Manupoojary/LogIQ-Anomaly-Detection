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
