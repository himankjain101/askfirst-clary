import json

import streamlit as st

from src.chat_engine import build_debug_prompt, stream_chat
from src.data_loader import get_user, list_users, load_dataset
from src.llm_client import LLMClient
from src.pattern_detector import (
    cache_path,
    load_cached,
    run_pass_one,
    save_patterns,
    stream_patterns,
)
from src.temporal_scaffold import build_scaffold

st.set_page_config(page_title="Clary · Ask First", layout="wide", initial_sidebar_state="expanded")

# ---------- askfirst design language ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, p, span, label, div, button, input, textarea {
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
h1, h2, h3, h4, h5, h6 {
  font-family: 'DM Sans', sans-serif !important;
  color: #0F1729;
  letter-spacing: -0.02em;
  font-weight: 700 !important;
}
h1 { font-weight: 700 !important; letter-spacing: -0.035em; }
code, pre, [data-testid="stCodeBlock"] code {
  font-family: 'JetBrains Mono', ui-monospace, monospace !important;
  font-size: 0.82rem !important;
}

.stApp { background: #FFFFFF; }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
.block-container { padding-top: 2.5rem; max-width: 1280px; }

/* sidebar — askfirst's light nav rail */
[data-testid="stSidebar"] {
  background: #FFFFFF;
  border-right: 1px solid #E5E7EB;
}
[data-testid="stSidebar"] h2 {
  font-family: 'DM Sans', sans-serif !important;
  color: #1A6CFF !important;
  font-weight: 700 !important;
  letter-spacing: -0.03em;
  font-size: 1.75rem !important;
  font-style: italic;
}

/* metric cards */
[data-testid="stMetric"] {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  padding: 1rem 1.25rem;
  border-radius: 14px;
  box-shadow: 0 1px 2px rgba(15,23,41,0.04);
}
[data-testid="stMetricLabel"] {
  color: #6B7280 !important;
  font-size: 0.72rem !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 700 !important;
  color: #0F1729 !important;
  font-size: 1.9rem !important;
  letter-spacing: -0.02em;
}

/* pattern cards */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
  border-radius: 16px !important;
  padding: 1.5rem 1.75rem !important;
  box-shadow: 0 1px 3px rgba(15,23,41,0.04);
  margin-bottom: 0.75rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: #C7D2FE;
  box-shadow: 0 4px 12px rgba(26,108,255,0.08);
}

/* buttons — fully rounded pills */
.stButton > button {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  color: #0F1729;
  border-radius: 999px;
  font-weight: 500;
  transition: all 0.15s ease;
  padding: 0.55rem 1.25rem;
}
.stButton > button:hover {
  background: #F7F8FA;
  border-color: #1A6CFF;
  color: #1A6CFF;
}
.stButton > button[kind="primary"] {
  background: #0A0A0A;
  border: 1px solid #0A0A0A;
  color: #FFFFFF;
  font-weight: 600;
  border-radius: 999px;
  padding: 0.6rem 1.4rem;
}
.stButton > button[kind="primary"]:hover {
  background: #1A6CFF;
  border-color: #1A6CFF;
  color: #FFFFFF;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] {
  border-bottom: 1px solid #E5E7EB;
  gap: 1.75rem;
  background: transparent;
}
.stTabs [data-baseweb="tab"] {
  color: #6B7280;
  font-weight: 500;
  padding: 0.6rem 0;
  font-family: 'DM Sans', sans-serif;
}
.stTabs [aria-selected="true"] {
  color: #1A6CFF !important;
  font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
  background: #1A6CFF !important;
}

/* chat */
[data-testid="stChatMessage"] {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 16px;
  padding: 0.9rem 1.2rem;
  margin-bottom: 0.5rem;
  box-shadow: 0 1px 2px rgba(15,23,41,0.03);
}
[data-testid="stChatInput"] {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 999px;
}
[data-testid="stChatInput"]:focus-within {
  border-color: #1A6CFF;
  box-shadow: 0 0 0 3px rgba(26,108,255,0.12);
}

/* expanders */
[data-testid="stExpander"] {
  border: 1px solid #E5E7EB !important;
  border-radius: 12px !important;
  background: #F7F8FA !important;
}
[data-testid="stExpander"] summary {
  color: #1A6CFF;
  font-weight: 500;
}

/* alerts — lavender hint for info, like askfirst's "Not sure what to ask" card */
[data-testid="stAlert"] {
  border-radius: 14px;
  border: 1px solid #E5E7EB;
  background: #FFFFFF;
}
[data-testid="stAlert"][data-baseweb="notification"] div[kind="info"] {
  background: #EEF2FF !important;
}

/* status */
[data-testid="stStatus"] {
  border-radius: 14px;
  border: 1px solid #E5E7EB;
  background: #FFFFFF;
}

/* code blocks */
[data-testid="stCodeBlock"] {
  background: #F7F8FA !important;
  border: 1px solid #E5E7EB !important;
  border-radius: 12px;
}

/* dataframe */
[data-testid="stDataFrame"] {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid #E5E7EB;
}

/* selectbox + radio */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  border-radius: 999px !important;
  border: 1px solid #E5E7EB !important;
  background: #FFFFFF !important;
}
[data-testid="stRadio"] label {
  color: #0F1729;
}

/* text_area */
[data-testid="stTextArea"] textarea {
  border-radius: 12px !important;
  border: 1px solid #E5E7EB !important;
  background: #F7F8FA !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.78rem !important;
  color: #374151 !important;
}

/* hr */
hr { border-color: #E5E7EB; }

/* caption */
.stCaption, [data-testid="stCaptionContainer"], .stMarkdown small {
  color: #6B7280 !important;
}

/* main h1 */
.stApp > .block-container h1:first-of-type {
  color: #0F1729;
  font-weight: 700;
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #E5E7EB;
}

/* links in blue like askfirst */
a, a:visited { color: #1A6CFF; text-decoration: none; }
a:hover { text-decoration: underline; }

/* session id chips in pattern cards — inline code styling */
.stMarkdown code {
  background: #EEF2FF !important;
  color: #1A6CFF !important;
  padding: 0.15rem 0.5rem !important;
  border-radius: 999px !important;
  font-size: 0.75rem !important;
  font-weight: 500;
  border: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------- renderer (defined first so tabs below can call it) ----------
def _render_pattern_card(container, p: dict, i: int):
    with container.container(border=True):
        top = st.columns([6, 1])
        top[0].markdown(f"#### {i}. {p.get('pattern_title', '(untitled)')}")
        conf = (p.get("confidence") or "").lower()
        color = {"high": "#059669", "medium": "#D97706", "low": "#DC2626"}.get(conf, "#6B7280")
        bg = {"high": "#D1FAE5", "medium": "#FEF3C7", "low": "#FEE2E2"}.get(conf, "#F3F4F6")
        top[1].markdown(
            f"<div style='text-align:right;'><span style='background:{bg};color:{color};"
            f"padding:0.25rem 0.7rem;border-radius:999px;font-size:0.75rem;font-weight:600;"
            f"text-transform:uppercase;letter-spacing:0.06em;'>{conf or 'n/a'}</span></div>",
            unsafe_allow_html=True,
        )

        sessions = p.get("sessions_involved", [])
        if sessions:
            st.markdown("Sessions: " + " ".join(f"`{s}`" for s in sessions))

        if p.get("temporal_window"):
            st.markdown(f"**Temporal window.** {p['temporal_window']}")
        if p.get("causal_mechanism"):
            st.markdown(f"**Mechanism.** {p['causal_mechanism']}")
        if p.get("confidence_justification"):
            st.markdown(f"**Why not coincidence.** _{p['confidence_justification']}_")
        if p.get("null_hypothesis_check"):
            st.markdown(f"**Null-hypothesis check.** {p['null_hypothesis_check']}")

        trace = p.get("reasoning_trace", [])
        if trace:
            with st.expander("Reasoning trace"):
                for j, step in enumerate(trace, 1):
                    st.markdown(f"{j}. {step}")

        with st.expander("Raw JSON"):
            st.code(json.dumps(p, indent=2), language="json")


# ---------- sidebar ----------
with st.sidebar:
    st.markdown("## Clary")
    st.caption("Cross-conversation health pattern reasoner.")

    dataset = load_dataset()
    users = list_users(dataset)
    labels = [f"{u['name']} · {u['user_id']} ({u['session_count']} sessions)" for u in users]
    idx = st.selectbox("User", range(len(users)), format_func=lambda i: labels[i], index=0)
    user = get_user(dataset, users[idx]["user_id"])

    model = st.radio("Model", ["groq", "gemini"], horizontal=True, index=0, help="Groq Llama 3.3 70B (free, default) or Gemini 1.5 Flash.")

    cached = load_cached(user["user_id"])
    if cached:
        st.success(f"Cached: {len(cached.get('patterns', []))} patterns")
    else:
        st.info("No cached run for this user.")

    run_button = st.button("Run pattern analysis", type="primary", use_container_width=True)

    with st.expander("Context strategy"):
        st.markdown(
            """
**Per-user scope.** All reasoning stays within one user. No cross-user leakage.

**Two-pass pipeline.**
1. Deterministic temporal scaffold (week offsets, days-since-prev).
2. LLM event extraction per session (~500 tokens each).
3. LLM causal linking with the whole user history + scaffold in context (~8k tokens).

**No retrieval.** 27 sessions fit comfortably — retrieval would hide temporal relationships
the model needs to see. Full timeline in-prompt beats RAG for this size.

**Chat.** Scaffold + full history + rolling last 6 turns. Always cites session IDs.
            """
        )

# ---------- main ----------
st.title(f"{user['name']} · {user['user_id']}")
scaffold = build_scaffold(user)
if scaffold:
    span = f"{scaffold[0]['date']} → {scaffold[-1]['date']}"
else:
    span = "—"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Sessions", len(scaffold))
c2.metric("Date range", span)
c3.metric("Weeks covered", scaffold[-1]["week_offset"] if scaffold else 0)
c4.metric("Patterns", len(cached.get("patterns", [])) if cached else 0)

tab_patterns, tab_chat, tab_timeline = st.tabs(["Patterns", "Chat", "Timeline"])


# ---------- patterns tab ----------
with tab_patterns:
    if run_button:
        client = LLMClient(model=model)
        with st.status("Pass 1 — extracting structured events per session...", expanded=False) as status:
            try:
                events = run_pass_one(client, user)
                status.update(label=f"Pass 1 complete — {len(events)} sessions processed", state="complete")
            except Exception as e:
                status.update(label=f"Pass 1 failed: {e}", state="error")
                st.stop()

        st.markdown("### Patterns (streaming)")
        patterns: list[dict] = []
        raw_response = ""
        container = st.container()
        for item in stream_patterns(client, user, events):
            if "_raw_response" in item:
                raw_response = item["_raw_response"]
                st.session_state["_last_system_prompt"] = item["_system_prompt"]
                st.session_state["_last_user_prompt"] = item["_user_prompt"]
                continue
            patterns.append(item)
            _render_pattern_card(container, item, len(patterns))

        save_patterns(user["user_id"], patterns, events, raw_response)
        st.success(f"Saved {len(patterns)} patterns to {cache_path(user['user_id'])}")
        cached = load_cached(user["user_id"])

    if cached and cached.get("patterns"):
        st.markdown("### Patterns")
        for i, p in enumerate(cached["patterns"], start=1):
            _render_pattern_card(st, p, i)

        with st.expander("Raw Pass-2 response"):
            st.code(cached.get("raw_response", ""), language="json")
        with st.expander("Pass-1 extracted events"):
            st.code(json.dumps(cached.get("pass_one_events", []), indent=2), language="json")

    elif not run_button:
        st.info("No patterns yet. Click **Run pattern analysis** in the sidebar.")


# ---------- chat tab ----------
with tab_chat:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    history = st.session_state.chat_history.setdefault(user["user_id"], [])

    col_chat, col_trace = st.columns([2, 1])

    with col_chat:
        st.markdown("#### Ask about this user's history")
        st.caption("The model sees the full timeline + scaffold. It will cite session IDs.")

        for turn in history:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])

        st.markdown("**Quick prompts**")
        qp_cols = st.columns(3)
        quick_prompts = [
            "What's the clearest pattern in my history?",
            "What happened 6 weeks before my hair fall?" if user["user_id"] == "USR002" else "Is there a trigger for my stomach pain?" if user["user_id"] == "USR001" else "Does my sleep affect my period?",
            "Are there symptoms I should watch for next month?",
        ]
        queue_key = f"queued_prompt_{user['user_id']}"
        for i, qp in enumerate(quick_prompts):
            if qp_cols[i].button(qp, key=f"qp_{user['user_id']}_{i}", use_container_width=True):
                st.session_state[queue_key] = qp
                st.rerun()

        typed = st.chat_input("Ask a temporal question...")
        queued = st.session_state.pop(queue_key, None)
        prompt_text = typed or queued

        if prompt_text:
            history.append({"role": "user", "content": prompt_text})
            with st.chat_message("user"):
                st.markdown(prompt_text)

            client = LLMClient(model=model)
            st.session_state["_last_chat_prompt"] = build_debug_prompt(user, history[:-1], prompt_text)
            with st.chat_message("assistant"):
                placeholder = st.empty()
                acc = ""
                try:
                    for chunk in stream_chat(client, user, history[:-1], prompt_text):
                        acc += chunk
                        placeholder.markdown(acc + "▌")
                    placeholder.markdown(acc)
                except Exception as e:
                    placeholder.error(f"Error: {e}")
                    acc = f"[error: {e}]"
            history.append({"role": "assistant", "content": acc})

    with col_trace:
        st.markdown("#### Reasoning trace")
        st.caption("The exact prompt and context injected for the last turn.")
        last_prompt = st.session_state.get("_last_chat_prompt", "(no chat yet)")
        st.text_area("prompt", value=last_prompt, height=600, label_visibility="collapsed")


# ---------- timeline tab ----------
with tab_timeline:
    st.markdown("### Deterministic temporal scaffold")
    st.caption("Pre-computed before any LLM call. Injected into every prompt.")
    st.dataframe(scaffold, use_container_width=True, hide_index=True)
