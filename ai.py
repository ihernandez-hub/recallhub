"""AI generation helpers — quiz, flashcards, related brainstorm ideas.

Uses the Emergent universal LLM key from backend/.env via emergentintegrations.
These are structured (JSON) extractions, so we use the non-streaming call.
"""

import json
import logging
import os
import re
import uuid
from typing import Any

from fastapi import HTTPException
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-5.4"


def _chat(session_id: str, system: str) -> LlmChat:
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        raise HTTPException(status_code=502, detail="AI is not configured (missing EMERGENT_LLM_KEY).")
    return (
        LlmChat(api_key=key, session_id=session_id, system_message=system)
        .with_model(MODEL_PROVIDER, MODEL_NAME)
    )


def _extract_json(text: str) -> Any:
    """Pull the first JSON array/object out of a model reply, tolerating code fences."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    start = min((i for i in (text.find("["), text.find("{")) if i != -1), default=-1)
    if start == -1:
        raise ValueError("no JSON found in model reply")
    opener = text[start]
    closer = "]" if opener == "[" else "}"
    end = text.rfind(closer)
    return json.loads(text[start : end + 1])


async def _ask_json(session_id: str, system: str, prompt: str) -> Any:
    try:
        reply = await _chat(session_id, system).send_message(UserMessage(text=prompt))
        return _extract_json(reply or "")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("AI generation failed: %s", exc)
        raise HTTPException(status_code=502, detail="AI generation failed — please try again.")


SYSTEM = (
    "You are RecallHub's study assistant. You reply with STRICT JSON only — no prose, "
    "no markdown fences, no commentary."
)


async def generate_quiz(note_title: str, note_content: str, count: int = 5) -> list[dict]:
    prompt = (
        f"From the study note below, write {count} multiple-choice quiz questions that test "
        "real understanding (not trivia). Each question has exactly 4 plausible options with "
        "one correct answer and a one-to-two sentence explanation of why the answer is right.\n"
        'Reply with a JSON array like: [{"question": "...", "options": ["A","B","C","D"], '
        '"correct_index": 0, "explanation": "..."}]\n\n'
        f"NOTE TITLE: {note_title}\nNOTE CONTENT:\n{note_content[:6000]}"
    )
    data = await _ask_json(f"quiz-{uuid.uuid4()}", SYSTEM, prompt)
    if not isinstance(data, list) or not data:
        raise HTTPException(status_code=502, detail="AI returned no questions — please try again.")
    out = []
    for item in data[:count]:
        options = [str(o) for o in item.get("options", [])][:4]
        if len(options) < 2:
            continue
        idx = item.get("correct_index", 0)
        out.append(
            {
                "id": str(uuid.uuid4()),
                "question": str(item.get("question", ""))[:500],
                "options": options,
                "correct_index": idx if isinstance(idx, int) and 0 <= idx < len(options) else 0,
                "explanation": str(item.get("explanation", ""))[:800],
            }
        )
    if not out:
        raise HTTPException(status_code=502, detail="AI returned unusable questions — please try again.")
    return out


async def generate_flashcards(note_title: str, note_content: str, count: int = 8) -> list[dict]:
    prompt = (
        f"From the study note below, extract {count} flashcards. Front = a question, term, or "
        "prompt; back = the concise answer; explanation = one sentence of context or why it "
        "matters.\n"
        'Reply with a JSON array like: [{"front": "...", "back": "...", "explanation": "..."}]\n\n'
        f"NOTE TITLE: {note_title}\nNOTE CONTENT:\n{note_content[:6000]}"
    )
    data = await _ask_json(f"cards-{uuid.uuid4()}", SYSTEM, prompt)
    if not isinstance(data, list) or not data:
        raise HTTPException(status_code=502, detail="AI returned no flashcards — please try again.")
    out = []
    for item in data[:count]:
        front = str(item.get("front", "")).strip()
        back = str(item.get("back", "")).strip()
        if not front or not back:
            continue
        out.append(
            {
                "id": str(uuid.uuid4()),
                "front": front[:300],
                "back": back[:600],
                "explanation": str(item.get("explanation", ""))[:500],
            }
        )
    if not out:
        raise HTTPException(status_code=502, detail="AI returned unusable flashcards — please try again.")
    return out


async def related_ideas(seed_text: str, existing: list[str], count: int = 3) -> list[str]:
    context = "\n".join(f"- {t}" for t in existing[:12]) or "(none yet)"
    prompt = (
        "Brainstorming on a study idea board. Given the seed idea and the ideas already on the "
        f"board, propose {count} NEW related concepts that genuinely extend the thinking — short "
        "phrases, each under 90 characters, no duplicates of existing ideas.\n"
        'Reply with a JSON array of strings like: ["idea one", "idea two", "idea three"]\n\n'
        f"SEED IDEA: {seed_text}\nEXISTING IDEAS:\n{context}"
    )
    data = await _ask_json(f"ideas-{uuid.uuid4()}", SYSTEM, prompt)
    if not isinstance(data, list) or not data:
        raise HTTPException(status_code=502, detail="AI returned no ideas — please try again.")
    return [str(t).strip()[:120] for t in data[:count] if str(t).strip()]
