import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
def test_server_running():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Gamified Trading System"}
