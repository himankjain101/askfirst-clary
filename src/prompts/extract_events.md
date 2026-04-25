You are analyzing a single health conversation session for structured events.

Given the session below, extract atoms into strict JSON. Do not infer causes, do not link across sessions — only record what this session explicitly reveals.

Return ONLY this JSON shape (no prose, no code fences):

{
  "session_id": "...",
  "symptoms": [
    {"name": "...", "onset_hint": "...", "severity_hint": "..."}
  ],
  "lifestyle_events": [
    {"name": "...", "direction": "started|stopped|increased|decreased|continued", "detail": "..."}
  ],
  "triggers_user_mentioned": ["..."],
  "timeframes_mentioned": ["..."],
  "notes": "one-line summary"
}

Rules:
- Extract only what the user or clary actually said. No outside knowledge.
- If a field has no content, return an empty array.
- "timeframes_mentioned" captures phrases like "since last night", "this week", "2 weeks ago", "after I started X".
