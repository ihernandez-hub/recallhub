import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  BookOpen,
  FlaskConical,
  Layers,
  Lightbulb,
  ListChecks,
  Search,
  FolderTree,
} from "lucide-react";
import { apiGet } from "@/lib/api";
import type { SearchResults } from "@/lib/types";
import { SIMS } from "@/lib/sims";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

function Row({
  icon: Icon,
  title,
  meta,
  onClick,
  testid,
}: {
  icon: typeof BookOpen;
  title: string;
  meta?: string;
  onClick: () => void;
  testid: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      data-testid={testid}
      className="flex w-full items-center gap-2.5 px-3 py-2 text-left text-sm transition-colors hover:bg-accent/60"
    >
      <Icon className="h-4 w-4 shrink-0 text-muted-foreground" />
      <span className="flex-1 truncate">{title}</span>
      {meta && <span className="shrink-0 font-mono text-[10px] text-muted-foreground">{meta}</span>}
    </button>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="py-1.5">
      <p className="px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
        {label}
      </p>
      {children}
    </div>
  );
}

export default function QuickSearch() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [debounced, setDebounced] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(q.trim()), 250);
    return () => clearTimeout(t);
  }, [q]);

  const searchQuery = useQuery({
    queryKey: ["search", debounced],
    queryFn: () => apiGet<SearchResults>(`/search?q=${encodeURIComponent(debounced)}`),
    enabled: open && debounced.length >= 2,
  });
  const r = searchQuery.data;
  const ql = debounced.toLowerCase();
  const simHits =
    debounced.length >= 2
      ? SIMS.filter((s) => (s.title + " " + s.subject).toLowerCase().includes(ql))
      : [];
  const hasResults =
    !!r &&
    (simHits.length > 0 ||
      r.subjects.length > 0 ||
      r.notes.length > 0 ||
      r.decks.length > 0 ||
      r.quizzes.length > 0 ||
      r.ideas.length > 0);

  function go(route: string) {
    setOpen(false);
    setQ("");
    setDebounced("");
    navigate(route);
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        render={
          <Button
            variant="outline"
            size="sm"
            className="gap-2 font-normal text-muted-foreground"
            data-testid="global-search-trigger"
          >
            <Search className="h-4 w-4" />
            <span className="hidden md:inline">Search…</span>
            <kbd className="hidden rounded border bg-muted px-1.5 font-mono text-[10px] md:inline-flex">
              ⌘K
            </kbd>
          </Button>
        }
      />
      <PopoverContent align="start" className="w-[380px] p-0" data-testid="global-search-panel">
        <div className="border-b p-2">
          <Input
            ref={inputRef}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search subjects, notes, quizzes, flashcards, sims…"
            className="border-0 shadow-none focus-visible:ring-0"
            data-testid="global-search-input"
          />
        </div>
        <div className="max-h-80 overflow-y-auto py-1" data-testid="global-search-results">
          {debounced.length < 2 && (
            <p className="px-3 py-6 text-center text-sm text-muted-foreground">
              Type at least 2 characters — try "biology" or "sorting".
            </p>
          )}
          {debounced.length >= 2 && searchQuery.isFetching && !hasResults && (
            <p className="px-3 py-6 text-center text-sm text-muted-foreground">Searching…</p>
          )}
          {debounced.length >= 2 && !searchQuery.isFetching && !hasResults && (
            <p className="px-3 py-6 text-center text-sm text-muted-foreground">
              No matches for "{debounced}".
            </p>
          )}
          {simHits.length > 0 && (
            <Section label="Practice sims">
              {simHits.map((s) => (
                <Row
                  key={s.id}
                  icon={FlaskConical}
                  title={s.title}
                  meta={s.subject}
                  onClick={() => go(s.route)}
                  testid={`search-sim-${s.id}`}
                />
              ))}
            </Section>
          )}
          {r && r.subjects.length > 0 && (
            <Section label="Subjects">
              {r.subjects.map((s) => (
                <Row
                  key={s.id}
                  icon={FolderTree}
                  title={s.name}
                  onClick={() => go(`/notes?subject=${s.id}`)}
                  testid={`search-subject-${s.id}`}
                />
              ))}
            </Section>
          )}
          {r && r.notes.length > 0 && (
            <Section label="Notes">
              {r.notes.map((n) => (
                <Row
                  key={n.id}
                  icon={BookOpen}
                  title={n.title}
                  onClick={() => go(`/notes?note=${n.id}`)}
                  testid={`search-note-${n.id}`}
                />
              ))}
            </Section>
          )}
          {r && r.decks.length > 0 && (
            <Section label="Flashcard decks">
              {r.decks.map((d) => (
                <Row
                  key={d.id}
                  icon={Layers}
                  title={d.title}
                  meta={`${d.card_count} cards`}
                  onClick={() => go(`/flashcards?deck=${d.id}`)}
                  testid={`search-deck-${d.id}`}
                />
              ))}
            </Section>
          )}
          {r && r.quizzes.length > 0 && (
            <Section label="Quizzes">
              {r.quizzes.map((qz) => (
                <Row
                  key={qz.id}
                  icon={ListChecks}
                  title={qz.title}
                  meta={`${qz.question_count} questions`}
                  onClick={() => go(`/quizzes?quiz=${qz.id}`)}
                  testid={`search-quiz-${qz.id}`}
                />
              ))}
            </Section>
          )}
          {r && r.ideas.length > 0 && (
            <Section label="Ideas">
              {r.ideas.map((i) => (
                <Row
                  key={i.id}
                  icon={Lightbulb}
                  title={i.text}
                  onClick={() => go("/brainstorm")}
                  testid={`search-idea-${i.id}`}
                />
              ))}
            </Section>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
