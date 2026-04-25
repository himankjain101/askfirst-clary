import os
from typing import Iterator, Optional

try:
    import streamlit as st
except Exception:
    st = None


def _get_secret(key: str) -> Optional[str]:
    if st is not None:
        try:
            return st.secrets.get(key)
        except Exception:
            pass
    return os.environ.get(key)


class LLMClient:
    """
    Thin streaming wrapper over Gemini (primary) with Groq fallback.
    All calls yield text chunks.
    """

    def __init__(self, model: str = "gemini"):
        self.model = model
        self._gemini = None
        self._groq = None

    def _init_gemini(self):
        if self._gemini is not None:
            return
        import google.generativeai as genai
        key = _get_secret("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY not set")
        genai.configure(api_key=key)
        self._gemini = genai.GenerativeModel("gemini-1.5-flash-latest")

    def _init_groq(self):
        if self._groq is not None:
            return
        from groq import Groq
        key = _get_secret("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY not set")
        self._groq = Groq(api_key=key)

    def stream(self, prompt: str, system: Optional[str] = None, temperature: float = 0.2) -> Iterator[str]:
        if self.model == "gemini":
            yield from self._stream_gemini(prompt, system, temperature)
        elif self.model == "groq":
            yield from self._stream_groq(prompt, system, temperature)
        else:
            raise ValueError(f"unknown model: {self.model}")

    def _stream_gemini(self, prompt: str, system: Optional[str], temperature: float) -> Iterator[str]:
        self._init_gemini()
        full = (system + "\n\n" + prompt) if system else prompt
        resp = self._gemini.generate_content(
            full,
            generation_config={"temperature": temperature},
            stream=True,
        )
        for chunk in resp:
            if chunk.text:
                yield chunk.text

    def _stream_groq(self, prompt: str, system: Optional[str], temperature: float) -> Iterator[str]:
        self._init_groq()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        stream = self._groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def complete(self, prompt: str, system: Optional[str] = None, temperature: float = 0.2) -> str:
        return "".join(self.stream(prompt, system, temperature))
