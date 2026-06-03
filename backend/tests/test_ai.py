from fastapi.testclient import TestClient


def _login(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    assert response.status_code == 200


def test_ai_chat_applies_board_update(
    client: TestClient, monkeypatch
) -> None:
    _login(client)

    from app import ai

    async def fake_openrouter_call(messages: list[dict[str, str]]) -> str:
        del messages
        return """
{
  "message": "Updated as requested.",
  "board_update": {
    "columns": [
      {"id": "col-backlog", "title": "Inbox", "cardIds": ["card-1", "card-2"]},
      {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
      {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
      {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
      {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]}
    ],
    "cards": {
      "card-1": {"id": "card-1", "title": "Align roadmap themes", "details": "Draft quarterly themes with impact statements and metrics."},
      "card-2": {"id": "card-2", "title": "Gather customer signals", "details": "Review support tags, sales notes, and churn feedback."},
      "card-3": {"id": "card-3", "title": "Prototype analytics view", "details": "Sketch initial dashboard layout and key drill-downs."},
      "card-4": {"id": "card-4", "title": "Refine status language", "details": "Standardize column labels and tone across the board."},
      "card-5": {"id": "card-5", "title": "Design card layout", "details": "Add hierarchy and spacing for scanning dense lists."},
      "card-6": {"id": "card-6", "title": "QA micro-interactions", "details": "Verify hover, focus, and loading states."},
      "card-7": {"id": "card-7", "title": "Ship marketing page", "details": "Final copy approved and asset pack delivered."},
      "card-8": {"id": "card-8", "title": "Close onboarding sprint", "details": "Document release notes and share internally."}
    }
  }
}
"""

    monkeypatch.setattr(ai, "_call_openrouter", fake_openrouter_call)

    board = client.get("/api/board").json()
    response = client.post(
        "/api/ai/chat",
        json={
            "message": "Rename backlog to inbox",
            "history": [],
            "board": board,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Updated as requested."
    assert payload["board"]["columns"][0]["title"] == "Inbox"

    persisted = client.get("/api/board").json()
    assert persisted["columns"][0]["title"] == "Inbox"


def test_ai_chat_rejects_malformed_output_without_corrupting_board(
    client: TestClient, monkeypatch
) -> None:
    _login(client)

    from app import ai

    async def fake_openrouter_call(messages: list[dict[str, str]]) -> str:
        del messages
        return "this is not json"

    monkeypatch.setattr(ai, "_call_openrouter", fake_openrouter_call)

    board_before = client.get("/api/board").json()
    response = client.post(
        "/api/ai/chat",
        json={
            "message": "Do something",
            "history": [],
            "board": board_before,
        },
    )
    assert response.status_code == 502
    assert "AI returned non-JSON output" in response.json()["detail"]

    board_after = client.get("/api/board").json()
    assert board_after == board_before
