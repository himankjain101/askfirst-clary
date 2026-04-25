from datetime import datetime


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def build_scaffold(user: dict) -> list[dict]:
    """
    Returns a per-session timeline entry with absolute and relative time anchors.
    This is the deterministic foundation the LLM reasons on top of.
    """
    convs = sorted(user["conversations"], key=lambda c: _parse(c["timestamp"]))
    if not convs:
        return []

    t0 = _parse(convs[0]["timestamp"])
    scaffold = []
    for i, c in enumerate(convs):
        ts = _parse(c["timestamp"])
        days_since_start = (ts - t0).days
        prev_ts = _parse(convs[i - 1]["timestamp"]) if i > 0 else None
        days_since_prev = (ts - prev_ts).days if prev_ts else 0
        scaffold.append({
            "session_id": c["session_id"],
            "index": i + 1,
            "timestamp": c["timestamp"],
            "date": ts.strftime("%Y-%m-%d"),
            "time_of_day": ts.strftime("%H:%M"),
            "week_offset": days_since_start // 7,
            "days_since_start": days_since_start,
            "days_since_prev": days_since_prev,
            "tags": c.get("tags", []),
            "severity": c.get("severity", "unknown"),
        })
    return scaffold


def format_scaffold_for_prompt(scaffold: list[dict]) -> str:
    lines = ["Session timeline (deterministic, pre-computed):"]
    for s in scaffold:
        lines.append(
            f"  {s['session_id']} | idx={s['index']} | {s['date']} {s['time_of_day']} "
            f"| week={s['week_offset']} | +{s['days_since_prev']}d since prev "
            f"| severity={s['severity']} | tags={s['tags']}"
        )
    return "\n".join(lines)


def format_sessions_for_prompt(user: dict, scaffold: list[dict]) -> str:
    """
    Pairs each session's raw messages with its scaffold entry so the LLM sees
    both the temporal anchor and the actual content together.
    """
    convs_by_id = {c["session_id"]: c for c in user["conversations"]}
    chunks = []
    for s in scaffold:
        c = convs_by_id[s["session_id"]]
        chunk = [
            f"--- {s['session_id']} (index {s['index']}, {s['date']}, week {s['week_offset']}) ---",
            f"USER: {c['user_message']}",
        ]
        if c.get("clary_questions"):
            chunk.append(f"CLARY ASKED: {' | '.join(c['clary_questions'])}")
        if c.get("user_followup"):
            chunk.append(f"USER FOLLOWUP: {c['user_followup']}")
        if c.get("clary_response"):
            chunk.append(f"CLARY RESPONSE: {c['clary_response']}")
        chunks.append("\n".join(chunk))
    return "\n\n".join(chunks)
