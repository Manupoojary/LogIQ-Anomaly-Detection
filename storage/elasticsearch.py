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
