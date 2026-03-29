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

                # # Fix for nasa data 
                # from datetime import datetime
                # parsed["timestamp"] = datetime.now().isoformat()


                features = preprocessor.extract_features(parsed)
                anomaly  = model.predict(features)
                storage.save(parsed, anomaly)
                print(
                        f"[Pipeline] {parsed['level']:5} | "
                        f"{parsed['service']:15} | "
                        f"{parsed['message']:40} | "
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
