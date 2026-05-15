import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_start_game():
    response = client.post("/api/game/start", json={"difficulty": "medium"})
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert data["turn"] == "white"
    assert data["game_over"] == False

def test_invalid_move():
    response = client.post("/api/game/start", json={"difficulty": "medium"})
    assert response.status_code == 200
    data = response.json()
    game_id = data["game_id"]

    response = client.post("/api/game/move", json={"game_id": game_id, "from_pos": "e2", "to_pos": "e5"})
    assert response.status_code == 200
    data = response.json()
    assert data["legal"] == False

def test_valid_move():
    response = client.post("/api/game/start", json={"difficulty": "simple"})
    assert response.status_code == 200
    data = response.json()
    game_id = data["game_id"]

    response = client.post("/api/game/move", json={"game_id": game_id, "from_pos": "e2", "to_pos": "e4"})
    assert response.status_code == 200
    data = response.json()
    assert data["legal"] == True

def test_get_game_state():
    response = client.post("/api/game/start", json={"difficulty": "medium"})
    data = response.json()
    game_id = data["game_id"]

    response = client.get(f"/api/game/state/{game_id}")
    assert response.status_code == 200
    data = response.json()
    assert "board" in data
    assert "turn" in data