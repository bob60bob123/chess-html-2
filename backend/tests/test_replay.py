import pytest
import os
import tempfile
from backend.storage.replay import ReplayStorage

def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = ReplayStorage(tmpdir)
        replay_data = {
            "id": "test-123",
            "moves": [{"from": "e2", "to": "e4"}],
            "result": "white_win"
        }
        storage.save(replay_data)
        loaded = storage.load("test-123")
        assert loaded["id"] == "test-123"
        assert len(loaded["moves"]) == 1
        assert loaded["moves"][0]["from"] == "e2"
        assert loaded["moves"][0]["to"] == "e4"

def test_list_replays():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = ReplayStorage(tmpdir)
        storage.save({"id": "game-1", "moves": []})
        storage.save({"id": "game-2", "moves": []})
        replays = storage.list()
        assert len(replays) == 2

def test_load_nonexistent():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = ReplayStorage(tmpdir)
        loaded = storage.load("nonexistent")
        assert loaded is None

def test_delete_replay():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = ReplayStorage(tmpdir)
        storage.save({"id": "delete-me", "moves": []})
        assert storage.load("delete-me") is not None
        result = storage.delete("delete-me")
        assert result == True
        assert storage.load("delete-me") is None

def test_auto_id_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = ReplayStorage(tmpdir)
        replay_data = {
            "moves": [{"from": "e2", "to": "e4"}]
        }
        replay_id = storage.save(replay_data)
        assert replay_id is not None
        loaded = storage.load(replay_id)
        assert loaded is not None
        assert "created_at" in loaded