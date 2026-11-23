"""Pydantic v2 models for RecallHub — shared workspace (no auth).

Every response model here has a hand-written TS interface mirror in
frontend/src/lib/types.ts — keep the two in sync in the same edit.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------- Subjects ----------

class Subject(BaseModel):
    id: str = Field(default_factory=_uuid)
    name: str
    color: str = "#3B4CCA"
    created_at: datetime = Field(default_factory=_now)


class SubjectCreate(BaseModel):
    name: str
    color: str = "#3B4CCA"


# ---------- Notes ----------

class Note(BaseModel):
    id: str = Field(default_factory=_uuid)
    subject_id: Optional[str] = None
    title: str
    content: str = ""
    tags: List[str] = []
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class NoteCreate(BaseModel):
    title: str
    content: str = ""
    subject_id: Optional[str] = None
    tags: List[str] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    subject_id: Optional[str] = None
    tags: Optional[List[str]] = None


# ---------- Brainstorm ideas ----------

class Idea(BaseModel):
    id: str = Field(default_factory=_uuid)
    subject_id: Optional[str] = None
    text: str
    color: str = "#D97706"
    source: Literal["user", "ai"] = "user"
    created_at: datetime = Field(default_factory=_now)


class IdeaCreate(BaseModel):
    text: str
    subject_id: Optional[str] = None
    color: str = "#D97706"


# ---------- Flashcards ----------

class Deck(BaseModel):
    id: str = Field(default_factory=_uuid)
    title: str
    note_id: Optional[str] = None
    subject_id: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class Flashcard(BaseModel):
    id: str = Field(default_factory=_uuid)
    deck_id: str
    front: str
    back: str
    explanation: str = ""
    mastery: Literal["new", "learning", "solid"] = "new"
    seen_count: int = 0
    correct_count: int = 0
    updated_at: datetime = Field(default_factory=_now)


class GradeIn(BaseModel):
    grade: Literal["again", "hard", "good", "easy"]


# ---------- Quizzes ----------

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=_uuid)
    question: str
    options: List[str] = Field(min_length=2, max_length=6)
    correct_index: int = 0
    explanation: str = ""


class Quiz(BaseModel):
    id: str = Field(default_factory=_uuid)
    title: str
    note_id: Optional[str] = None
    subject_id: Optional[str] = None
    questions: List[QuizQuestion] = []
    last_score: Optional[int] = None
    attempts: int = 0
    created_at: datetime = Field(default_factory=_now)


class AttemptIn(BaseModel):
    score: int


# ---------- Global search ----------

class NoteHit(BaseModel):
    id: str
    title: str
    subject_id: Optional[str] = None
    snippet: str = ""


class DeckHit(BaseModel):
    id: str
    title: str
    subject_id: Optional[str] = None
    card_count: int = 0


class QuizHit(BaseModel):
    id: str
    title: str
    question_count: int = 0
    attempts: int = 0
    last_score: Optional[int] = None


class IdeaHit(BaseModel):
    id: str
    text: str


class SearchResults(BaseModel):
    subjects: List[Subject] = []
    notes: List[NoteHit] = []
    decks: List[DeckHit] = []
    quizzes: List[QuizHit] = []
    ideas: List[IdeaHit] = []
