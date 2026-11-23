"""Brainstorm idea board routes + AI related-idea suggestions."""

from fastapi import APIRouter, HTTPException

from lib.ai import related_ideas
from lib.db import db
from models.app_models import Idea, IdeaCreate

router = APIRouter(tags=["ideas"])

AI_COLORS = ["#4F46E5", "#7C3AED", "#059669", "#D97706", "#3B4CCA"]


@router.get("/ideas", response_model=list[Idea])
async def list_ideas(subject_id: str | None = None):
    query = {"subject_id": subject_id} if subject_id else {}
    docs = await db.ideas.find(query).sort("created_at", 1).to_list(1000)
    return [Idea(**d) for d in docs]


@router.post("/ideas", response_model=Idea)
async def create_idea(input: IdeaCreate):
    idea = Idea(text=input.text.strip(), subject_id=input.subject_id, color=input.color)
    await db.ideas.insert_one(idea.model_dump())
    return idea


@router.post("/ideas/{idea_id}/related", response_model=list[Idea])
async def suggest_related(idea_id: str):
    doc = await db.ideas.find_one({"id": idea_id})
    if not doc:
        raise HTTPException(status_code=404, detail="idea not found")
    siblings = await db.ideas.find({"subject_id": doc.get("subject_id")}).to_list(100)
    texts = [s["text"] for s in siblings if s.get("id") != idea_id]
    suggestions = await related_ideas(doc["text"], texts)
    ideas = []
    for i, text in enumerate(suggestions):
        idea = Idea(
            text=text,
            subject_id=doc.get("subject_id"),
            color=AI_COLORS[i % len(AI_COLORS)],
            source="ai",
        )
        await db.ideas.insert_one(idea.model_dump())
        ideas.append(idea)
    return ideas


@router.delete("/ideas/{idea_id}")
async def delete_idea(idea_id: str):
    res = await db.ideas.delete_one({"id": idea_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="idea not found")
    return {"deleted": True}
