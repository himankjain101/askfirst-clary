import json
from pathlib import Path
from typing import Iterator, Optional

from .llm_client import LLMClient
from .temporal_scaffold import (
    build_scaffold,
    format_scaffold_for_prompt,
    format_sessions_for_prompt,
)

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def extract_events_for_session(client: LLMClient, session: dict) -> dict:
    """Pass 1: per-session structured extraction. Non-streaming."""
    system = _load_prompt("extract_events.md")
    payload = {
        "session_id": session["session_id"],
        "user_message": session.get("user_message", ""),
        "clary_questions": session.get("clary_questions", []),
        "user_followup": session.get("user_followup", ""),
        "clary_response": session.get("clary_response", ""),
    }
    prompt = f"Session:\n{json.dumps(payload, indent=2)}"
    raw = client.complete(prompt, system=system, temperature=0.1)
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {"session_id": session["session_id"], "_parse_error": True, "_raw": raw}


def run_pass_one(client: LLMClient, user: dict) -> list[dict]:
    return [extract_events_for_session(client, c) for c in user["conversations"]]


def build_pass_two_prompt(user: dict, scaffold: list[dict], events: list[dict]) -> tuple[str, str]:
    system = _load_prompt("link_patterns.md")
    parts = [
        f"User: {user['name']} ({user['user_id']}), age {user['age']}, {user['gender']}, {user['location']}.",
        f"Onboarding notes: {user.get('onboarding_notes','')}",
        "",
        format_scaffold_for_prompt(scaffold),
        "",
        "Structured events per session (Pass 1 output):",
        json.dumps(events, indent=2),
        "",
        "Raw session content:",
        format_sessions_for_prompt(user, scaffold),
        "",
        "Now identify every genuine cross-session pattern per the rules. Stream one JSON object per pattern, newline-separated.",
    ]
    return system, "\n".join(parts)


def stream_patterns(client: LLMClient, user: dict, events: list[dict]) -> Iterator[dict]:
    """
    Pass 2: streaming. Yields parsed pattern dicts as they complete, plus a final
    {'_raw': ...} record with the full response for the trace panel.
    """
    scaffold = build_scaffold(user)
    system, prompt = build_pass_two_prompt(user, scaffold, events)

    buffer = ""
    full_response = ""
    scan_pos = 0
    depth = 0
    in_string = False
    escape = False
    start_idx = None

    for chunk in client.stream(prompt, system=system, temperature=0.2):
        full_response += chunk
        buffer += chunk
        while scan_pos < len(buffer):
            ch = buffer[scan_pos]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == "{":
                    if depth == 0:
                        start_idx = scan_pos
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0 and start_idx is not None:
                        candidate = buffer[start_idx : scan_pos + 1]
                        try:
                            obj = json.loads(candidate)
                            yield obj
                        except json.JSONDecodeError:
                            pass
                        buffer = buffer[scan_pos + 1 :]
                        start_idx = None
                        scan_pos = -1  # becomes 0 after += 1
            scan_pos += 1

    yield {"_raw_response": full_response, "_system_prompt": system, "_user_prompt": prompt}


def cache_path(user_id: str) -> Path:
    return OUTPUT_DIR / f"patterns_{user_id}.json"


def save_patterns(user_id: str, patterns: list[dict], events: list[dict], raw: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(cache_path(user_id), "w", encoding="utf-8") as f:
        json.dump(
            {"user_id": user_id, "patterns": patterns, "pass_one_events": events, "raw_response": raw},
            f,
            indent=2,
        )


def load_cached(user_id: str) -> Optional[dict]:
    p = cache_path(user_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
