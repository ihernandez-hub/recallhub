"""Note routes + AI generation (quiz & flashcards) from a note."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from lib.ai import generate_flashcards, generate_quiz
from lib.db import db
from models.app_models import Deck, Flashcard, Note, NoteCreate, NoteUpdate, Quiz

router = APIRouter(tags=["notes"])


def _sort_key(d: dict) -> str:
    return str(d.get("updated_at") or d.get("created_at") or "")


@router.get("/notes", response_model=list[Note])
async def list_notes(subject_id: str | None = None):
    query = {"subject_id": subject_id} if subject_id else {}
    docs = await db.notes.find(query).to_list(1000)
    docs.sort(key=_sort_key, reverse=True)
    return [Note(**d) for d in docs]


@router.post("/notes", response_model=Note)
async def create_note(input: NoteCreate):
    note = Note(**input.model_dump())
    await db.notes.insert_one(note.model_dump())
    return note


@router.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: str):
    doc = await db.notes.find_one({"id": note_id})
    if not doc:
        raise HTTPException(status_code=404, detail="note not found")
    return Note(**doc)


@router.patch("/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, input: NoteUpdate):
    changes = {k: v for k, v in input.model_dump().items() if v is not None}
    if not changes:
        raise HTTPException(status_code=422, detail="nothing to update")
    changes["updated_at"] = datetime.now(timezone.utc)
    doc = await db.notes.find_one_and_update({"id": note_id}, {"$set": changes})
    if not doc:
        raise HTTPException(status_code=404, detail="note not found")
    merged = {**doc, **changes}
    return Note(**merged)


@router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    res = await db.notes.delete_one({"id": note_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="note not found")
    return {"deleted": True}


@router.post("/notes/{note_id}/generate-quiz", response_model=Quiz)
async def ai_generate_quiz(note_id: str):
    doc = await db.notes.find_one({"id": note_id})
    if not doc:
        raise HTTPException(status_code=404, detail="note not found")
    if not (doc.get("content") or "").strip():
        raise HTTPException(status_code=422, detail="write some note content before generating a quiz")
    questions = await generate_quiz(doc["title"], doc["content"])
    quiz = Quiz(
        title=doc["title"],
        note_id=note_id,
        subject_id=doc.get("subject_id"),
        questions=questions,
    )
    await db.quizzes.insert_one(quiz.model_dump())
    return quiz


@router.post("/notes/{note_id}/generate-deck", response_model=Deck)
async def ai_generate_deck(note_id: str):
    doc = await db.notes.find_one({"id": note_id})
    if not doc:
        raise HTTPException(status_code=404, detail="note not found")
    if not (doc.get("content") or "").strip():
        raise HTTPException(status_code=422, detail="write some note content before generating flashcards")
    cards = await generate_flashcards(doc["title"], doc["content"])
    deck = Deck(title=doc["title"], note_id=note_id, subject_id=doc.get("subject_id"))
    flashcards = [
        Flashcard(deck_id=deck.id, **{k: v for k, v in c.items() if k in ("front", "back", "explanation")})
        for c in cards
    ]
    await db.decks.insert_one(deck.model_dump())
    if flashcards:
        await db.flashcards.insert_many([c.model_dump() for c in flashcards])
    return deck
