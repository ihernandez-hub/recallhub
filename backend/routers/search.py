"""Global search across subjects, notes, decks, quizzes and ideas."""

import re

from fastapi import APIRouter

from lib.db import db
from models.app_models import (
    IdeaHit,
    DeckHit,
    NoteHit,
    QuizHit,
    SearchResults,
    Subject,
)

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResults)
async def search(q: str = ""):
    q = q.strip()
    if len(q) < 2:
        return SearchResults(subjects=[], notes=[], decks=[], quizzes=[], ideas=[])
    pat = {"$regex": re.escape(q), "$options": "i"}

    subjects = await db.subjects.find({"name": pat}).sort("created_at", 1).to_list(5)
    notes = await db.notes.find({"$or": [{"title": pat}, {"content": pat}]}).to_list(5)
    decks = await db.decks.find({"title": pat}).to_list(5)
    quizzes = await db.quizzes.find({"title": pat}).to_list(5)
    ideas = await db.ideas.find({"text": pat}).sort("created_at", -1).to_list(5)

    deck_hits = []
    for d in decks:
        card_count = await db.flashcards.count_documents({"deck_id": d["id"]})
        deck_hits.append(
            DeckHit(
                id=d["id"],
                title=d["title"],
                subject_id=d.get("subject_id"),
                card_count=card_count,
            )
        )

    return SearchResults(
        subjects=[Subject(**s) for s in subjects],
        notes=[
            NoteHit(
                id=n["id"],
                title=n["title"],
                subject_id=n.get("subject_id"),
                snippet=(n.get("content") or "")[:120],
            )
            for n in notes
        ],
        decks=deck_hits,
        quizzes=[
            QuizHit(
                id=qz["id"],
                title=qz["title"],
                question_count=len(qz.get("questions", [])),
                attempts=qz.get("attempts", 0),
                last_score=qz.get("last_score"),
            )
            for qz in quizzes
        ],
        ideas=[IdeaHit(id=i["id"], text=i["text"]) for i in ideas],
    )
