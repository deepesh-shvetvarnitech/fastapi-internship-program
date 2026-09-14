from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import verify_api_key

client = TestClient(app)


def test_list_assets():
    response = client.get("/api/v1/assets")

    assert response.status_code == 200


def test_pagination():
    response = client.get(
        "/api/v1/assets?page=1&page_size=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["assets"]) == 2


def test_invalid_pagination():
    response = client.get(
        "/api/v1/assets?page=0"
    )

    assert response.status_code == 422


def test_filter():
    response = client.get(
        "/api/v1/assets?status=assigned"
    )

    assert response.status_code == 200

    data = response.json()

    assert all(
        asset["status"] == "assigned"
        for asset in data["assets"]
    )


def test_get_existing_asset():
    response = client.get(
        "/api/v1/assets/101"
    )

    assert response.status_code == 200

    assert response.json()["id"] == 101


def test_get_nonexistent_asset():
    response = client.get(
        "/api/v1/assets/9999"
    )

    assert response.status_code == 404


def test_protected_without_api_key():
    response = client.post(
        "/api/v1/assets",
        json={
            "asset_tag": "TEST-001",
            "asset_type": "laptop",
            "brand": "Dell",
            "model": "Test Model",
            "employee_name": None,
            "department": None,
        },
    )

    assert response.status_code == 403


def test_protected_wrong_api_key():
    response = client.post(
        "/api/v1/assets",
        headers={
            "X-API-Key": "wrong-key",
        },
        json={
            "asset_tag": "TEST-002",
            "asset_type": "laptop",
            "brand": "Dell",
            "model": "Test Model",
            "employee_name": None,
            "department": None,
        },
    )

    assert response.status_code == 403


def test_protected_with_correct_api_key():
    response = client.post(
        "/api/v1/assets",
        headers={
            "X-API-Key": "development-secret-key",
        },
        json={
            "asset_tag": "TEST-003",
            "asset_type": "laptop",
            "brand": "Apple",
            "model": "MacBook Pro",
            "employee_name": None,
            "department": None,
        },
    )

    assert response.status_code == 201


def test_dependency_override():
    def fake_api_key():
        return "test-key"

    app.dependency_overrides[verify_api_key] = fake_api_key

    response = client.post(
        "/api/v1/assets",
        json={
            "asset_tag": "TEST-OVERRIDE",
            "asset_type": "monitor",
            "brand": "LG",
            "model": "Test Monitor",
            "employee_name": None,
            "department": None,
        },
    )

    assert response.status_code == 201

    app.dependency_overrides.clear()