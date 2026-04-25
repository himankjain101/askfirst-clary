import json
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "askfirst_synthetic_dataset.json"


def load_dataset(path: Path = DATASET_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # Strip the answer key so it can never leak into any prompt.
    raw.pop("hidden_patterns_reference", None)
    return raw


def get_user(dataset: dict, user_id: str) -> dict:
    for u in dataset["users"]:
        if u["user_id"] == user_id:
            return u
    raise KeyError(f"User {user_id} not found")


def list_users(dataset: dict) -> list[dict]:
    return [
        {
            "user_id": u["user_id"],
            "name": u["name"],
            "age": u["age"],
            "gender": u["gender"],
            "session_count": len(u["conversations"]),
        }
        for u in dataset["users"]
    ]
