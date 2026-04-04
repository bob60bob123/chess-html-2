import json
import os
import uuid
from typing import List, Dict, Optional
from datetime import datetime

class ReplayStorage:
    """Storage for chess game replays"""
    def __init__(self, storage_dir: str = "replays"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save(self, replay_data: Dict) -> str:
        """Save replay data, returns ID"""
        if "id" not in replay_data:
            replay_data["id"] = str(uuid.uuid4())[:8]
        if "created_at" not in replay_data:
            replay_data["created_at"] = datetime.now().isoformat()

        filepath = os.path.join(self.storage_dir, f"{replay_data['id']}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(replay_data, f, ensure_ascii=False, indent=2)
        return replay_data["id"]

    def load(self, replay_id: str) -> Optional[Dict]:
        """Load replay by ID"""
        filepath = os.path.join(self.storage_dir, f"{replay_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_replays(self) -> List[Dict]:
        """List all replays sorted by creation date (newest first)"""
        replays = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        replays.append(json.load(f))
                except (FileNotFoundError, json.JSONDecodeError):
                    continue
        return sorted(replays, key=lambda x: x.get('created_at', ''), reverse=True)

    def delete(self, replay_id: str) -> bool:
        """Delete replay by ID, returns True if deleted"""
        filepath = os.path.join(self.storage_dir, f"{replay_id}.json")
        try:
            os.remove(filepath)
            return True
        except FileNotFoundError:
            return False