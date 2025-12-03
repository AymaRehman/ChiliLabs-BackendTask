import os
import sys
import tempfile
import shutil

# --- Add project root to path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# --- Use a temporary DB for testing ---
temp_db_file = os.path.join(tempfile.gettempdir(), "BackendDeveloper_test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{temp_db_file}"

from fastapi.testclient import TestClient
from BackendDeveloper.main import app

client = TestClient(app)

# --- Use a temporary avatars folder ---
avatar_dir = os.path.join(tempfile.gettempdir(), "test_avatars")
if os.path.exists(avatar_dir):
    shutil.rmtree(avatar_dir)
os.makedirs(avatar_dir, exist_ok=True)
os.environ["AVATAR_DIR"] = avatar_dir


# --- Test workflow ---
def test_full_flow():
    # 1. Register
    resp = client.post("/register", json={"identifier": "tester", "password": "secret"})
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    print("Register OK, token:", token)

    # 2. Login
    resp = client.post("/login", json={"identifier": "tester", "password": "secret"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    print("Login OK")

    # 3. Upload avatar
    test_avatar_path = os.path.join(tempfile.gettempdir(), "test_avatar.png")
    with open(test_avatar_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")  # dummy PNG header

    with open(test_avatar_path, "rb") as f:
        resp = client.post(
            "/avatar",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test_avatar.png", f, "image/png")},
        )
    assert resp.status_code == 200
    print("Avatar upload OK:", resp.json()["data"]["avatar_url"])

    # 4. Delete user
    resp = client.delete("/user", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    print("User deletion OK:", resp.json()["data"]["message"])
