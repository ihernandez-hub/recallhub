"""Study routes: flashcard decks, card grading, quizzes and attempts."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from lib.db import db
from models.app_models import Deck, Flashcard, GradeIn, Quiz

router = APIRouter(tags=["study"])


@router.get("/decks", response_model=list[dict])
async def list_decks():
    docs = await db.decks.find().sort("created_at", -1).to_list(200)
    cards = await db.flashcards.find().to_list(5000)
    counts: dict[str, dict] = {}
    for c in cards:
        agg = counts.setdefault(c["deck_id"], {"count": 0, "solid": 0})
        agg["count"] += 1
        if c.get("mastery") == "solid":
            agg["solid"] += 1
    return [
        {
            **{k: v for k, v in d.items() if k != "_id"},
            "card_count": counts.get(d["id"], {}).get("count", 0),
            "solid_count": counts.get(d["id"], {}).get("solid", 0),
        }
        for d in docs
    ]


async def _get_deck(deck_id: str) -> dict:
    doc = await db.decks.find_one({"id": deck_id})
    if not doc:
        raise HTTPException(status_code=404, detail="deck not found")
    return doc


@router.get("/decks/{deck_id}", response_model=dict)
async def get_deck(deck_id: str):
    deck = await _get_deck(deck_id)
    cards = await db.flashcards.find({"deck_id": deck_id}).to_list(500)
    cards.sort(key=lambda c: (c.get("updated_at") or datetime.min.replace(tzinfo=timezone.utc)).replace(tzinfo=timezone.utc))
    return {
        "deck": Deck(**deck).model_dump(),
        "cards": [Flashcard(**c).model_dump() for c in cards],
    }


@router.delete("/decks/{deck_id}")
async def delete_deck(deck_id: str):
    res = await db.decks.delete_one({"id": deck_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="deck not found")
    await db.flashcards.delete_many({"deck_id": deck_id})
    return {"deleted": True}


_GRADE_MAP = {
    "again": ("new", 0),
    "hard": ("learning", 0),
    "good": ("learning", 1),
    "easy": ("solid", 1),
}


@router.patch("/flashcards/{card_id}/grade", response_model=Flashcard)
async def grade_flashcard(card_id: str, input: GradeIn):
    doc = await db.flashcards.find_one({"id": card_id})
    if not doc:
        raise HTTPException(status_code=404, detail="card not found")
    mastery, correct = _GRADE_MAP[input.grade]
    changes = {
        "mastery": mastery,
        "seen_count": doc.get("seen_count", 0) + 1,
        "correct_count": doc.get("correct_count", 0) + correct,
        "updated_at": datetime.now(timezone.utc),
    }
    await db.flashcards.update_one({"id": card_id}, {"$set": changes})
    return Flashcard(**{**doc, **changes})


@router.get("/quizzes", response_model=list[Quiz])
async def list_quizzes():
    docs = await db.quizzes.find().sort("created_at", -1).to_list(200)
    return [Quiz(**d) for d in docs]


@router.get("/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: str):
    doc = await db.quizzes.find_one({"id": quiz_id})
    if not doc:
        raise HTTPException(status_code=404, detail="quiz not found")
    return Quiz(**doc)


@router.post("/quizzes/{quiz_id}/attempt", response_model=Quiz)
async def record_attempt(quiz_id: str, input: dict):
    doc = await db.quizzes.find_one({"id": quiz_id})
    if not doc:
        raise HTTPException(status_code=404, detail="quiz not found")
    score = input.get("score")
    if not isinstance(score, int):
        raise HTTPException(status_code=422, detail="score must be an integer")
    changes = {"last_score": score, "attempts": doc.get("attempts", 0) + 1}
    await db.quizzes.update_one({"id": quiz_id}, {"$set": changes})
    return Quiz(**{**doc, **changes})


@router.delete("/quizzes/{quiz_id}")
async def delete_quiz(quiz_id: str):
    res = await db.quizzes.delete_one({"id": quiz_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="quiz not found")
    return {"deleted": True}
