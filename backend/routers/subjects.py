"""Subject (workspace folder) routes."""

from fastapi import APIRouter, HTTPException

from lib.db import db
from models.app_models import Subject, SubjectCreate

router = APIRouter(tags=["subjects"])


@router.get("/subjects", response_model=list[Subject])
async def list_subjects():
    docs = await db.subjects.find().sort("created_at", 1).to_list(200)
    return [Subject(**d) for d in docs]


@router.post("/subjects", response_model=Subject)
async def create_subject(input: SubjectCreate):
    subject = Subject(name=input.name.strip(), color=input.color)
    await db.subjects.insert_one(subject.model_dump())
    return subject


@router.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: str):
    res = await db.subjects.delete_one({"id": subject_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="subject not found")
    # cascade: this subject's notes and ideas go with it
    await db.notes.delete_many({"subject_id": subject_id})
    await db.ideas.delete_many({"subject_id": subject_id})
    return {"deleted": True}
