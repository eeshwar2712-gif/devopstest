import os

import redis
from flask import Flask, jsonify
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, generate_latest, multiprocess

app = Flask(__name__)

REQUESTS = Counter("app_requests_total", "Total requests", ["endpoint"])

cache = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    socket_connect_timeout=1,
)


@app.route("/")
def index():
    REQUESTS.labels("/").inc()
    try:
        hits = cache.incr("hits")
    except redis.exceptions.RedisError:
        hits = None  # app still works without redis
    return jsonify(message="Hello DevOps", version=os.getenv("APP_VERSION", "dev"), hits=hits)


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/metrics")
def metrics():
    if os.getenv("PROMETHEUS_MULTIPROC_DIR"):
        # gunicorn runs several worker processes; aggregate counters across all of them
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        data = generate_latest(registry)
    else:
        data = generate_latest()
    return data, 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
