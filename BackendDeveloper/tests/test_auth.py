import os
import sys
import tempfile

# --- Add project root to path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# --- Use a temporary DB for testing ---
temp_db_file = os.path.join(tempfile.gettempdir(), "BackendDeveloper_auth_test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{temp_db_file}"

from fastapi.testclient import TestClient
from BackendDeveloper.main import app

client = TestClient(app)


def test_register_and_login():
    # 1. Register
    response = client.post(
        "/register", json={"identifier": "tester_auth", "password": "secret"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    token = response.json()["data"]["access_token"]
    print("Register OK, token:", token)

    # 2. Login
    response = client.post(
        "/login", json={"identifier": "tester_auth", "password": "secret"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "access_token" in response.json()["data"]
    print("Login OK")
