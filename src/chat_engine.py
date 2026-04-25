from pathlib import Path
from typing import Iterator

from .llm_client import LLMClient
from .temporal_scaffold import (
    build_scaffold,
    format_scaffold_for_prompt,
    format_sessions_for_prompt,
)

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def build_chat_context(user: dict) -> str:
    scaffold = build_scaffold(user)
    return (
        f"User: {user['name']} ({user['user_id']}), age {user['age']}, {user['gender']}, {user['location']}.\n"
        f"Onboarding notes: {user.get('onboarding_notes','')}\n\n"
        f"{format_scaffold_for_prompt(scaffold)}\n\n"
        "Full conversation history:\n"
        f"{format_sessions_for_prompt(user, scaffold)}"
    )


def stream_chat(
    client: LLMClient,
    user: dict,
    history: list[dict],
    user_message: str,
) -> Iterator[str]:
    system = _load_prompt("chat_system.md")
    context = build_chat_context(user)

    # Keep the last 6 turns verbatim (rolling window).
    recent = history[-6:]
    convo_lines = []
    for turn in recent:
        role = "USER" if turn["role"] == "user" else "CLARY"
        convo_lines.append(f"{role}: {turn['content']}")
    convo_lines.append(f"USER: {user_message}")

    prompt = (
        f"{context}\n\n"
        f"--- current conversation (last {len(recent)} turns + new message) ---\n"
        + "\n".join(convo_lines)
        + "\n\nCLARY:"
    )
    yield from client.stream(prompt, system=system, temperature=0.3)


def build_debug_prompt(user: dict, history: list[dict], user_message: str) -> str:
    """Returns the exact prompt shown to the model — used by the 'reasoning trace' drawer."""
    context = build_chat_context(user)
    recent = history[-6:]
    convo_lines = []
    for turn in recent:
        role = "USER" if turn["role"] == "user" else "CLARY"
        convo_lines.append(f"{role}: {turn['content']}")
    convo_lines.append(f"USER: {user_message}")
    return (
        f"{context}\n\n"
        f"--- current conversation (last {len(recent)} turns + new message) ---\n"
        + "\n".join(convo_lines)
        + "\n\nCLARY:"
    )
