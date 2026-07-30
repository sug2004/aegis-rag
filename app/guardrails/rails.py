import logfire
from langchain_groq import ChatGroq
from nemoguardrails import LLMRails, RailsConfig

from app.config import settings
from app.guardrails.colang_rules import COLANG_CONTENT, YAML_CONTENT

_rails: LLMRails | None = None

# These must exactly match the "define user ..." names in colang_rules.py.
# This is what we now use to decide "fired", NOT the generated text.
BLOCKING_INTENTS = ["ask off topic", "attempt jailbreak"]
CONVERSATIONAL_INTENTS = ["express greeting", "ask capabilities", "express farewell"]


def initialize_rails() -> None:
    """
    Build the NeMo LLMRails singleton at app startup.
    Uses Groq llama-3.1-8b-instant for fast intent classification at the gate.
    """
    global _rails
    try:
        guard_llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0,
        )
        config = RailsConfig.from_content(colang_content=COLANG_CONTENT, yaml_content=YAML_CONTENT)
        _rails = LLMRails(config, llm=guard_llm)
        logfire.info("🛡️ NeMo Guardrails initialised (llama-3.1-8b-instant).")
    except Exception as e:
        # Loud failure instead of silently leaving _rails as None.
        logfire.exception(f"❌ Guardrails failed to initialise: {e}")
        _rails = None


def _extract_content(result) -> str:
    """
    Normalise whatever NeMo returns into a plain string.
    Handles: plain dict {'role', 'content'}, list of message dicts,
    or an object exposing .content.
    """
    if isinstance(result, dict):
        return str(result.get("content", ""))
    if isinstance(result, list) and result:
        last = result[-1]
        if isinstance(last, dict):
            return str(last.get("content", ""))
        return str(getattr(last, "content", last))
    return str(getattr(result, "content", result))


def guard(message: str) -> tuple[bool, str | None]:
    """
    Run a user message through the NeMo rails gate.

    Detection is based on which Colang user-intent actually matched
    (read from rails.explain().colang_history), NOT on substring-matching
    the generated response text — the latter is unreliable because a
    real, on-topic answer can coincidentally contain fragments that
    overlap with your canned refusal phrases or system instructions.

    Returns:
        (True,  rail_response) — a rail fired; return this response immediately,
                                skip the RAG pipeline entirely.
        (False, None)          — message is clean; proceed to LangGraph.
    """
    if _rails is None:
        logfire.warning("⚠️ Guardrails not initialised — skipping gate.")
        return False, None

    with logfire.span("🛡️ Guardrails Check"):
        result = _rails.generate(messages=[{"role": "user", "content": message}])
        content = _extract_content(result)

        info = _rails.explain()
        history = info.colang_history or ""
        logfire.info(f"Colang trace:\n{history}")

        fired_intent = next(
            (name for name in (BLOCKING_INTENTS + CONVERSATIONAL_INTENTS) if name in history),
            None,
        )

        if fired_intent:
            logfire.info(f"🛡️ Guardrails fired | intent='{fired_intent}' | query='{message[:80]}'")
            return True, content

        logfire.info("✅ Guardrails passed — routing to RAG pipeline.")
        return False, None