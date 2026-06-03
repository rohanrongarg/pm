from fastapi.testclient import TestClient


def test_board_requires_auth(client: TestClient) -> None:
    response = client.get("/api/board")
    assert response.status_code == 401


def test_login_and_logout_flow(client: TestClient) -> None:
    bad_login = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "wrong"},
    )
    assert bad_login.status_code == 401

    login = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    assert login.status_code == 200
    assert login.json()["authenticated"] is True

    session = client.get("/api/auth/session")
    assert session.status_code == 200
    assert session.json() == {"authenticated": True, "username": "user"}

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"success": True}

    session_after = client.get("/api/auth/session")
    assert session_after.status_code == 200
    assert session_after.json() == {"authenticated": False, "username": None}
