from fastapi.testclient import TestClient


def _login(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    assert response.status_code == 200


def test_board_read_and_update(client: TestClient) -> None:
    _login(client)

    board_response = client.get("/api/board")
    assert board_response.status_code == 200
    board = board_response.json()
    assert len(board["columns"]) == 5
    assert "card-1" in board["cards"]

    board["columns"][0]["title"] = "Inbox"
    update_response = client.put("/api/board", json=board)
    assert update_response.status_code == 200
    assert update_response.json()["columns"][0]["title"] == "Inbox"

    refreshed = client.get("/api/board")
    assert refreshed.status_code == 200
    assert refreshed.json()["columns"][0]["title"] == "Inbox"
