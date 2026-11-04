"""API tests. TestClient calls the app in-process: no real server or network needed."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_returns_404() -> None:
    response = client.get("/does-not-exist")
    assert response.status_code == 404


def test_cors_allows_frontend_origin() -> None:
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_blocks_other_origins() -> None:
    response = client.get("/health", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in response.headers


def test_schema_lists_tables_with_columns_and_foreign_keys() -> None:
    response = client.get("/schema")
    assert response.status_code == 200
    tables = {table["name"]: table for table in response.json()}
    assert len(tables) == 11

    invoice = tables["Invoice"]
    column_names = [column["name"] for column in invoice["columns"]]
    assert "InvoiceId" in column_names and "Total" in column_names
    assert {"column": "CustomerId", "ref_table": "Customer", "ref_column": "CustomerId"} in invoice[
        "foreign_keys"
    ]
