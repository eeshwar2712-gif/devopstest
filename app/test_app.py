from app import app


def test_health():
    res = app.test_client().get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_index_works_without_redis():
    res = app.test_client().get("/")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Hello DevOps"


def test_metrics_exposed():
    res = app.test_client().get("/metrics")
    assert res.status_code == 200
    assert b"app_requests_total" in res.data
