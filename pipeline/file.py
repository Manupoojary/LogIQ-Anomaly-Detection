# ============================================================
# FilePipeline — Lightweight pipeline using file/memory
# ============================================================

import time
from pipeline.base import BasePipeline
from config.settings import LOG_INTERVAL_SEC


class FilePipeline(BasePipeline):

    def __init__(self):
        self._running = False

    def run(self, dataset, preprocessor, model, storage):
        self._running = True

        dataset_display = {"synthetic": "Log Simulator", "nasa": "NASA HTTP"}

        # ✅ DEBUG (temporary, helps verify correct dataset)
        print("DEBUG DATASET TYPE:", type(dataset))

        print(f"[SimpleIngest] Started with dataset={dataset_display.get(dataset.name(), dataset.name())}")

        while self._running:
            try:
                raw_log = dataset.get_log()
                if not raw_log:
                    continue

                parsed = preprocessor.parse(raw_log)
                if not parsed:
                    continue

                # from datetime import datetime
                # parsed["timestamp"] = datetime.now().isoformat()

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
                print(f"[SimpleIngest] Error: {e}")
                time.sleep(1)

    def stop(self):
        self._running = False
        print("[SimpleIngest] Stopped")

    def name(self) -> str:
        return "file"

    def description(self) -> str:
        return "Lightweight pipeline — no Kafka needed"