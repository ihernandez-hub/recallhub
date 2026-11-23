"""Seed RecallHub with a demo workspace: 4 subjects, notes, ideas, a deck, a quiz.

Run: cd /app/backend && python seed.py
Idempotent: skips if subjects already exist (pass --force to reseed).
"""

import asyncio
import sys

from datetime import datetime, timezone

from lib.db import db, ensure_indexes
from models.app_models import Deck, Flashcard, Idea, Note, Quiz, QuizQuestion, Subject

NOW = datetime.now(timezone.utc)


def uuidish(p: str) -> str:
    import uuid

    return f"{p}-{uuid.uuid4().hex[:8]}"


SUBJECTS = [
    ("Cell Biology & Genetics", "#059669"),
    ("Data Structures & Algorithms", "#3B4CCA"),
    ("Cognitive Psychology", "#7C3AED"),
    ("World History 1900–1945", "#D9532F"),
]

NOTES = {
    "Cell Biology & Genetics": [
        (
            "Photosynthesis: Light & Dark Reactions",
            "Photosynthesis converts light energy into chemical energy stored in glucose.\n\n"
            "LIGHT REACTIONS (thylakoid membrane)\n- Chlorophyll absorbs photons; water is split "
            "(photolysis), releasing O2.\n- Electrons travel the electron transport chain, pumping "
            "H+ into the thylakoid lumen; ATP synthase makes ATP (photophosphorylation).\n- NADP+ "
            "is reduced to NADPH.\n\nDARK REACTIONS / CALVIN CYCLE (stroma)\n- RuBisCO fixes CO2 "
            "onto RuBP (carbon fixation).\n- ATP and NADPH from the light reactions reduce 3-PGA "
            "to G3P.\n- Some G3P regenerates RuBP; the rest builds glucose.\n\nKEY TERMS: "
            "photolysis, photophosphorylation, carbon fixation, stroma, thylakoid, RuBisCO",
            ["photosynthesis", "calvin-cycle", "exam2"],
        ),
        (
            "Mendelian Inheritance",
            "Mendel's laws from pea-plant crosses.\n\nLAW OF SEGREGATION: each organism carries two "
            "alleles per trait; they separate in gametes so each gamete carries one.\nLAW OF "
            "INDEPENDENT ASSORTMENT: allele pairs for different traits segregate independently "
            "(true only for unlinked genes).\n\nDominant allele masks recessive in heterozygotes. "
            "A 3:1 phenotypic ratio in F2 signals a monohybrid cross; 9:3:3:1 signals a dihybrid "
            "cross with independent assortment.\nTest cross: unknown dominant crossed with "
            "homozygous recessive reveals genotype.\n\nKEY TERMS: allele, genotype, phenotype, "
            "homozygous, heterozygous, test cross, F2 ratio",
            ["genetics", "mendel", "key-terms"],
        ),
    ],
    "Data Structures & Algorithms": [
        (
            "Big-O & Complexity Analysis",
            "Asymptotic analysis describes how runtime grows with input size n.\n\nO(1): hash map "
            "lookup, array index. O(log n): binary search, balanced BST operations. O(n): linear "
            "scan. O(n log n): merge sort, heap sort — the practical lower bound for comparison "
            "sorting. O(n^2): bubble/insertion sort, naive pair loops. O(2^n): naive recursive "
            "Fibonacci, subset enumeration.\n\nRules: drop constants (O(2n) → O(n)), keep the "
            "dominant term (O(n^2 + n) → O(n^2)). Amortized analysis: dynamic array push is O(1) "
            "amortized despite occasional O(n) resizes.\n\nKEY TERMS: asymptotic, amortized, "
            "dominant term, worst case, big-O",
            ["complexity", "big-o", "formulas"],
        ),
        (
            "Hash Tables & Collision Handling",
            "A hash table maps keys to buckets via a hash function for average O(1) insert, "
            "lookup, delete.\n\nCOLLISIONS: two keys hashing to the same bucket.\n- Chaining: "
            "each bucket holds a linked list of entries; load factor α = n/buckets, resize when "
            "α exceeds ~0.75.\n- Open addressing: probe for the next open slot — linear probing "
            "(clustering risk), quadratic probing, double hashing.\n\nA good hash function is "
            "deterministic, uniform, and fast. Python dicts and Java HashMaps use open addressing "
            "variants; chaining is common in interview answers.\n\nKEY TERMS: load factor, "
            "chaining, open addressing, clustering, resize",
            ["hashing", "interview", "key-terms"],
        ),
    ],
    "Cognitive Psychology": [
        (
            "Memory: Encoding, Storage, Retrieval",
            "Memory is classically split into three stages.\n\nSENSORY MEMORY: raw input, <1s "
            "(iconic) to ~3s (echoic).\nSHORT-TERM / WORKING MEMORY: ~15–30s, capacity 7±2 items "
            "(Miller) or ~4 chunks (Cowan); Baddeley's working-memory model adds a phonological "
            "loop, visuospatial sketchpad, and central executive.\nLONG-TERM MEMORY: effectively "
            "unlimited — explicit (episodic + semantic) vs implicit (procedural, priming).\n\n"
            "The serial position effect (primacy + recency) supports distinct short- and "
            "long-term stores. The spacing effect: distributed practice beats cramming.\n\n"
            "KEY TERMS: chunking, phonological loop, episodic, primacy effect, spacing effect",
            ["memory", "exam2", "diagrams"],
        ),
        (
            "Operant & Classical Conditioning",
            "CLASSICAL (Pavolov): a neutral stimulus paired with an unconditioned stimulus comes "
            "to elicit the response — learning by association. Key processes: acquisition, "
            "extinction, spontaneous recovery, generalization, discrimination.\n\nOPERANT "
            "(Skinner): behavior shaped by consequences.\n- Positive reinforcement: add something "
            "good → behavior up.\n- Negative reinforcement: remove something bad → behavior up.\n"
            "- Punishment (positive or negative) → behavior down.\nVariable-ratio reinforcement "
            "schedules produce the most persistent behavior.\n\nKEY TERMS: UCS, extinction, "
            "reinforcement schedule, shaping",
            ["conditioning", "key-terms"],
        ),
    ],
    "World History 1900–1945": [
        (
            "Causes of World War I",
            "The long-term causes are usually grouped as MAIN: Militarism (arms races, especially "
            "the Anglo-German naval race), Alliances (Triple Entente vs Triple Alliance), "
            "Imperialism (colonial rivalry), Nationalism (Slavic nationalism in the Balkans).\n\n"
            "The spark: the assassination of Archduke Franz Ferdinand in Sarajevo, June 1914, by "
            "Gavrilo Princip. The July Crisis and the alliance system turned a regional killing "
            "into a continental war within weeks — the Schlieffen Plan pulled Britain in via "
            "Belgium.\n\nWar of attrition on the Western Front: trench warfare, machine guns, "
            "stalemate. US entry in 1917 after unrestricted submarine warfare and the Zimmermann "
            "Telegram.\n\nKEY TERMS: MAIN, July Crisis, Schlieffen Plan, Zimmermann Telegram, "
            "attrition",
            ["wwi", "causes", "exam2"],
        ),
        (
            "The Treaty of Versailles & Aftermath",
            "Signed June 1919; the big three — Wilson (US), Clemenceau (France), Lloyd George "
            "(UK) — had conflicting goals: peace, security, and empire.\n\nWAR GUILT: Article 231 "
            "assigned responsibility to Germany. REPARATIONS: set at 132 billion gold marks in "
            "1921. TERRITORY: Alsace-Lorraine returned to France, the Polish Corridor created, "
            "all colonies became League mandates. MILITARY: German army capped at 100,000, no "
            "air force, Rhineland demilitarized.\n\nThe League of Nations was created but the US "
            "never joined. Keynes predicted the reparations would wreck the European economy; "
            "German resentment of the 'Diktat' fed later extremism.\n\nKEY TERMS: Article 231, "
            "reparations, mandate, League of Nations, Diktat",
            ["versailles", "wwi", "key-terms"],
        ),
    ],
}

IDEAS = {
    "Cell Biology & Genetics": [
        ("Compare C3 vs C4 photosynthesis efficiency in hot climates", "#059669"),
        ("Why is RuBisCO the most abundant protein on Earth?", "#4F46E5"),
        ("Link Mendel's laws to meiosis I chromosome segregation", "#7C3AED"),
        ("Punnett squares as a probability model — teach it with dice", "#D97706"),
    ],
    "Data Structures & Algorithms": [
        ("Prove why comparison sorting cannot beat O(n log n)", "#3B4CCA"),
        ("When would O(n^2) insertion sort actually win in practice?", "#D97706"),
        ("Design a hash map from scratch in a mock interview", "#059669"),
        ("Map amortized analysis to real latency spikes in services", "#7C3AED"),
    ],
    "Cognitive Psychology": [
        ("Turn the spacing effect into a study-schedule app feature", "#7C3AED"),
        ("Does chunking explain why phone numbers group digits?", "#D97706"),
        ("Classic vs operant conditioning in app notification design", "#059669"),
        ("Miller's 7±2 vs Cowan's 4 — reconcile the evidence", "#3B4CCA"),
    ],
    "World History 1900–1945": [
        ("Was WWI inevitable without the alliance system?", "#D9532F"),
        ("Compare war guilt in WWI treaties vs WWII settlement", "#D97706"),
        ("How did Article 231 shape Weimar politics?", "#4F46E5"),
        ("League of Nations vs UN: structural lessons learned", "#059669"),
    ],
}

DECK_CARDS = [
    ("Photosynthesis: Light & Dark Reactions", [
        ("Where do the light reactions of photosynthesis take place?",
         "In the thylakoid membranes of the chloroplast.",
         "The dark reactions (Calvin cycle) run in the stroma — a classic exam distinction."),
        ("What molecule does RuBisCO fix CO2 onto in the Calvin cycle?",
         "Ribulose-1,5-bisphosphate (RuBP).",
         "This carbon-fixation step is why RuBisCO is called the gateway enzyme of photosynthesis."),
        ("What are the two energy-carrying products of the light reactions?",
         "ATP and NADPH.",
         "Both feed the Calvin cycle's reduction of 3-PGA to G3P."),
        ("What gas is released when water is split during photolysis?",
         "Oxygen (O2).",
         "Photolysis of water also donates the electrons that enter the transport chain."),
        ("Which pigment absorbs the light energy driving photosynthesis?",
         "Chlorophyll.",
         "It absorbs mostly red and blue wavelengths, reflecting green."),
    ]),
    ("Causes of World War I", [
        ("What does the acronym MAIN stand for as WWI long-term causes?",
         "Militarism, Alliances, Imperialism, Nationalism.",
         "Use MAIN to structure any causes essay."),
        ("What event sparked World War I in June 1914?",
         "The assassination of Archduke Franz Ferdinand in Sarajevo by Gavrilo Princip.",
         "The July Crisis then escalated a regional killing into continental war."),
        ("Which German plan pulled Britain into the war?",
         "The Schlieffen Plan — its invasion of neutral Belgium triggered Britain's entry.",
         "The 1839 Treaty of London guaranteed Belgian neutrality."),
        ("What two factors pushed the US to enter WWI in 1917?",
         "Unrestricted submarine warfare and the Zimmermann Telegram.",
         "Both shifted US public opinion decisively toward the Allies."),
    ]),
]

QUIZ_QUESTIONS = [
    ("Big-O & Complexity Analysis", [
        ("What is the average-case time complexity of a lookup in a well-sized hash table?",
         ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 0,
         "Hash tables give average O(1) insert, lookup and delete; worst case degrades to O(n) with bad collisions."),
        ("Why is merge sort O(n log n)?",
         ["It halves the list log n times and merges each level in O(n)",
          "It compares every pair of elements exactly once",
          "It uses a heap of size log n",
          "It sorts log n sublists of size n in parallel"], 0,
         "Recursion depth is log n and each level does O(n) merge work, giving n × log n."),
        ("Which growth rate is allowed by dropping constants in O(2n + 5)?",
         ["O(n)", "O(2n)", "O(n + 5)", "O(5n)"], 0,
         "Big-O ignores constant factors and additive constants: O(2n + 5) simplifies to O(n)."),
        ("Dynamic array push is O(1) amortized because…",
         ["Occasional O(n) resizes are spread across many O(1) pushes",
          "Every push is exactly O(1)",
          "Memory is pre-allocated infinitely",
          "The array is stored as a linked list"], 0,
         "Doubling capacity means total resize work across n pushes is O(n) — O(1) per push on average."),
    ]),
]


async def seed(force: bool = False) -> None:
    existing = await db.subjects.count_documents({})
    if existing and not force:
        print(f"Seed skipped — {existing} subjects already exist (use --force to reseed).")
        return
    if force:
        for coll in ("subjects", "notes", "ideas", "decks", "flashcards", "quizzes"):
            await db[coll].delete_many({})

    subjects: dict[str, Subject] = {}
    for name, color in SUBJECTS:
        s = Subject(name=name, color=color)
        await db.subjects.insert_one(s.model_dump())
        subjects[name] = s

    notes_by_subject: dict[str, list[Note]] = {}
    for name, items in NOTES.items():
        notes_by_subject[name] = []
        for title, content, tags in items:
            n = Note(subject_id=subjects[name].id, title=title, content=content, tags=tags)
            await db.notes.insert_one(n.model_dump())
            notes_by_subject[name].append(n)

    for name, items in IDEAS.items():
        for text, color in items:
            idea = Idea(text=text, subject_id=subjects[name].id, color=color)
            await db.ideas.insert_one(idea.model_dump())

    for title, cards in DECK_CARDS:
        note = next((n for items in notes_by_subject.values() for n in items if n.title == title), None)
        subject_name = next((k for k, v in notes_by_subject.items() if any(n.title == title for n in v)), None)
        deck = Deck(title=title, note_id=note.id if note else None,
                    subject_id=subjects[subject_name].id if subject_name else None)
        await db.decks.insert_one(deck.model_dump())
        await db.flashcards.insert_many([
            Flashcard(deck_id=deck.id, front=f, back=b, explanation=e).model_dump()
            for f, b, e in cards
        ])

    for title, questions in QUIZ_QUESTIONS:
        note = next((n for items in notes_by_subject.values() for n in items if n.title == title), None)
        subject_name = next((k for k, v in notes_by_subject.items() if any(n.title == title for n in v)), None)
        quiz = Quiz(
            title=title,
            note_id=note.id if note else None,
            subject_id=subjects[subject_name].id if subject_name else None,
            questions=[
                QuizQuestion(question=q, options=o, correct_index=i, explanation=e).model_dump()
                for q, o, i, e in questions
            ],
        )
        await db.quizzes.insert_one(quiz.model_dump())

    await ensure_indexes()
    print(f"Seeded {len(SUBJECTS)} subjects, {sum(len(v) for v in NOTES.values())} notes, "
          f"{sum(len(v) for v in IDEAS.values())} ideas, "
          f"{len(DECK_CARDS)} decks, {len(QUIZ_QUESTIONS)} quiz(zes).")


if __name__ == "__main__":
    force = "--force" in sys.argv
    asyncio.run(seed(force))
