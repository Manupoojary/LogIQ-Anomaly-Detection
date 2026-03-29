# ============================================================
# NASADataset — Reads real NASA HTTP access logs
# ============================================================

import os
from datasets.base import BaseDataset
from config.settings import NASA_LOG_PATH
import urllib.request
import gzip
import shutil


def _download_dataset():
    url = "ftp://ita.ee.lbl.gov/traces/NASA_access_log_Jul95.gz"

    os.makedirs("datasets/raw", exist_ok=True)

    gz_path  = "datasets/raw/nasa_access.log.gz"
    log_path = "datasets/raw/nasa_access.log"

    if not os.path.exists(log_path):
        print("[NASA] Downloading dataset...")
        urllib.request.urlretrieve(url, gz_path)

        print("[NASA] Extracting dataset...")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(log_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        print("[NASA] Dataset ready!")


class NASADataset(BaseDataset):

    def __init__(self):
        self._file = None
        self._iterator = None   
        self._open_file()

    def _open_file(self):
        if not os.path.exists(NASA_LOG_PATH):
            _download_dataset()
        
        self._file = open(NASA_LOG_PATH, "r", errors="ignore")
        self._iterator = iter(self._file)   # 

    def name(self):
        return "nasa"

    def description(self):
        return "Real NASA HTTP access logs from July 1995 — 1.8M requests"

    def get_log(self) -> str:
        try:
            line = next(self._iterator)   
            return line.strip()
        except StopIteration:
            # Loop back to start when file ends
            self._file.seek(0)
            self._iterator = iter(self._file)   
            return next(self._iterator).strip()