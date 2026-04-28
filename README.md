# Clary — Ask First reasoning layer

Cross-conversation health pattern detection with temporal reasoning.
Submission for the Ask First AI Intern Assignment.

## What it does

Given a user's full chat history, Clary identifies cross-session health patterns with causal + temporal justification, a streaming JSON output with confidence scores, and an explicit null-hypothesis check to guard against coincidence. A second tab runs conversational Q&A over the same history so you can ask temporal questions like "what happened 6 weeks before my hair fall?".

## Run locally

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Fill in GEMINI_API_KEY (and optionally GROQ_API_KEY) in secrets.toml
streamlit run app.py
```

## Stack and model choice

- **Streamlit** for the UI — fast to build, streams natively, deploys free.
- **Gemini 2.0 Flash** as the primary LLM. Free tier, 1M-token context, strong streaming, good temporal grounding. The full history for one user (~15k tokens) fits in a single prompt with room to spare, which is what lets us skip retrieval entirely.
- **Groq Llama 3.3 70B** as the fallback for live demos (rate-limit insurance).
- **No LangChain, no FAISS, no embeddings.** 27 total sessions across 3 users — retrieval adds latency and hides the temporal relationships the model needs to see.

## Reasoning pipeline

1. **Deterministic temporal scaffold.** Before any LLM call, we build a per-user timeline with `week_offset`, `days_since_start`, and `days_since_prev` for each session. This is injected into every prompt as the time anchor — the model never has to guess dates or count weeks.
2. **Pass 1: per-session event extraction.** For each session, the LLM returns structured JSON (symptoms, lifestyle events, user-mentioned timeframes). Small, cheap, cached.
3. **Pass 2: causal linking (streaming).** One call per user. Sees the scaffold + Pass-1 atoms + full raw conversations. Outputs one pattern JSON object at a time. Required fields: `sessions_involved`, `temporal_window`, `causal_mechanism`, `reasoning_trace`, `null_hypothesis_check`, `confidence`, `confidence_justification`.
4. **Chat mode.** Same scaffold + full history + rolling last 6 turns. Cites session IDs.

## Chunking and context management

- **Scope boundary: per-user.** No cross-user reasoning. Pre-empts hallucinated crossovers.
- **Pass 1:** one session in, atoms out. ~500 tokens/call, parallelizable.
- **Pass 2:** scaffold (~1k) + Pass-1 atoms (~2k) + raw messages (~10k) = well under Gemini Flash's context. We deliberately do NOT retrieve — the pattern in the spec rewards temporal reasoning, which requires the full timeline in-view.
- **Chat:** scaffold always + full history + rolling 6-turn window. The scaffold re-injection is what keeps temporal questions grounded across long sessions.

## Streaming

All LLM output streams. Pass-2 patterns materialize card by card via an incremental JSON brace-matcher (see `src/pattern_detector.stream_patterns`). Chat uses `st.chat_message` with a live-updating placeholder.

## Reasoning trace

Every Pass-2 pattern carries a `reasoning_trace` array (what was observed, what was ruled out, why the remaining explanation is strongest). The Patterns tab shows these in an expander on each card, plus the full raw Pass-2 response and Pass-1 events in collapsible panels. The Chat tab includes a right-rail panel that shows the exact prompt injected for the last turn.

## Deploy (free)

1. Push to a public GitHub repo.
2. On share.streamlit.io, "New app" → point to `app.py`.
3. Paste `GEMINI_API_KEY` and `GROQ_API_KEY` into the Secrets UI.

## Folder layout

```
app.py                       # Streamlit entry, 3 tabs
src/
  data_loader.py             # loads JSON, strips hidden_patterns_reference
  temporal_scaffold.py       # week offsets, days-since-prev
  llm_client.py              # Gemini + Groq streaming
  pattern_detector.py        # two-pass reasoning + streaming JSON parse
  chat_engine.py             # temporal chat
  prompts/
    extract_events.md
    link_patterns.md
    chat_system.md
data/askfirst_synthetic_dataset.json
outputs/                     # cached per-user patterns

```
