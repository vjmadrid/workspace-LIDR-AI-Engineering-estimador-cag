from fastapi.testclient import TestClient

from app.constants import manager_constants

HEALTH_ENDPOINT = f"{manager_constants.ROOT_ENDPOINT}{manager_constants.HEALTH_ENDPOINT}"

def test_health_returns_200(client: TestClient) -> None:
    response = client.get(HEALTH_ENDPOINT)
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "healthy"
