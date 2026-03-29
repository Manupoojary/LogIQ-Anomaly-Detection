# ============================================================
# Flask Backend — REST API for the dashboard
# Reads from storage and exposes data to frontend
# ============================================================

import threading
from flask import Flask, jsonify, request
from flask_cors import CORS

from config.settings  import BACKEND_HOST, BACKEND_PORT, BACKEND_DEBUG, ALLOW_KAFKA
from storage.utils    import get_storage
from models.utils     import list_models
from datasets.utils   import list_datasets
from pipeline.utils   import list_pipelines

app     = Flask(__name__)
CORS(app)

storage         = None
pipeline_obj    = None
pipeline_thread = None
current_model    = None
current_dataset  = None
current_pipeline = None

def init_storage(storage_name: str):
    global storage
    storage = get_storage(storage_name)


# ── Info routes ───────────────────────────────────────────────

@app.route("/info", methods=["GET"])
def info():
    from config.settings import ALLOW_KAFKA

    pipelines = list_pipelines()

    # 🚫 Remove kafka if disabled
    if not ALLOW_KAFKA:
        pipelines = [p for p in pipelines if p != "kafka"]

    return jsonify({
        "models":    list_models(),
        "datasets":  list_datasets(),
        "pipelines": pipelines,
})


# ── Pipeline control routes ───────────────────────────────────

@app.route("/start", methods=["POST"])
def start():
    global pipeline_obj, pipeline_thread, current_model, current_dataset, current_pipeline

    data             = request.json or {}
    model_name       = data.get("model",    "isolation_forest")
    dataset_name     = data.get("dataset",  "synthetic")
    pipeline_name    = data.get("pipeline", "file")

    # 🚫 Block Kafka in production
    if pipeline_name == "kafka" and not ALLOW_KAFKA:
        return jsonify({"error": "Kafka pipeline disabled in this environment"}), 400

    current_model    = model_name
    current_dataset  = dataset_name
    current_pipeline = pipeline_name

    # ✅ STEP 1: STOP OLD PIPELINE
    if pipeline_obj:
        try:
            pipeline_obj.stop()
        except Exception:
            pass

    # ✅ STEP 2: WAIT FOR THREAD TO STOP
    if pipeline_thread:
        pipeline_thread.join(timeout=2)

    # ✅ STEP 3: RESET GLOBAL STATE (VERY IMPORTANT)
    pipeline_obj = None
    pipeline_thread = None

    # ✅ STEP 4: CLEAR STORAGE
    storage.clear()

    # ✅ STEP 5: LOAD COMPONENTS
    from datasets.utils      import get_dataset
    from preprocessing.utils import get_preprocessor
    from models.utils        import get_model
    from pipeline.utils      import get_pipeline

    dataset      = get_dataset(dataset_name)
    preprocessor = get_preprocessor(dataset_name)
    model        = get_model(model_name)
    pipeline_obj = get_pipeline(pipeline_name)

    # ✅ STEP 6: RESET MODEL (if exists)
    if hasattr(model, "reset"):
        model.reset()

    # ✅ STEP 7: START NEW PIPELINE
    pipeline_thread = threading.Thread(
        target=pipeline_obj.run,
        args=(dataset, preprocessor, model, storage),
        daemon=True
    )
    pipeline_thread.start()

    return jsonify({
        "message":  "Pipeline started",
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
    running = pipeline_obj is not None   
    return jsonify({
        "running": running,
        "pipeline": pipeline_obj.name() if pipeline_obj else None,
        "model":    current_model,
        "dataset":  current_dataset
    })


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
    

@app.route("/reset", methods=["POST"])  
def reset():
    try:
        storage.reset()
        return jsonify({"message": "reset"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    storage_name = sys.argv[1] if len(sys.argv) > 1 else "sqlite"
    init_storage(storage_name)
    print(f"[Backend] Starting with storage={storage_name}")
    app.run(host=BACKEND_HOST, port=BACKEND_PORT, debug=BACKEND_DEBUG)
