import { useState } from "react";
import { RotateCcw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const EVENTS = [
  { year: 1914, label: "Franz Ferdinand assassinated in Sarajevo" },
  { year: 1917, label: "United States enters World War I" },
  { year: 1919, label: "Treaty of Versailles is signed" },
  { year: 1929, label: "Wall Street Crash begins the Great Depression" },
  { year: 1933, label: "Hitler becomes Chancellor of Germany" },
  { year: 1939, label: "Germany invades Poland — WWII begins" },
  { year: 1945, label: "VE Day ends the war in Europe" },
];

function shuffle<T>(items: T[]): T[] {
  const a = [...items];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export default function TimelineSim() {
  const [shuffled, setShuffled] = useState(() => shuffle(EVENTS));
  const [picked, setPicked] = useState<number[]>([]);
  const [mistakes, setMistakes] = useState(0);
  const done = picked.length === EVENTS.length;

  function pick(idx: number) {
    if (done || picked.includes(idx)) return;
    const ev = shuffled[idx];
    const expected = [...EVENTS].sort((a, b) => a.year - b.year)[picked.length];
    if (ev.year === expected.year) {
      setPicked([...picked, idx]);
    } else {
      setMistakes((m) => m + 1);
    }
  }

  function reset() {
    setShuffled(shuffle(EVENTS));
    setPicked([]);
    setMistakes(0);
  }

  return (
    <div className="space-y-5" data-testid="sim-timeline">
      <div className="flex items-center gap-2">
        <Badge variant="outline" className="font-mono text-[10px]">
          mistakes: {mistakes}
        </Badge>
        {done && (
          <Badge variant="secondary" className="font-mono text-[10px]">
            complete — {EVENTS.length} events in order!
          </Badge>
        )}
        <Button variant="outline" size="sm" onClick={reset} className="ml-auto" data-testid="timeline-reset-btn">
          <RotateCcw className="h-3.5 w-3.5" /> New round
        </Button>
      </div>

      {done && (
        <div className="rounded-lg border bg-muted/40 p-4 text-sm" data-testid="timeline-placed">
          <p className="font-medium">The full timeline:</p>
          <ol className="mt-1 list-inside list-decimal text-muted-foreground">
            {[...EVENTS].sort((a, b) => a.year - b.year).map((e) => (
              <li key={e.year}>
                <span className="font-mono">{e.year}</span> — {e.label}
              </li>
            ))}
          </ol>
        </div>
      )}

      <div className="grid gap-2">
        {shuffled.map((ev, idx) => {
          const isPicked = picked.includes(idx);
          return (
            <button
              key={`${ev.year}-${idx}`}
              type="button"
              onClick={() => pick(idx)}
              disabled={isPicked || done}
              className={`flex items-center gap-3 rounded-lg border p-3 text-left text-sm transition-colors ${
                isPicked
                  ? "border-emerald-600/50 bg-emerald-50 dark:bg-emerald-950/40"
                  : "hover:border-primary/50 hover:bg-accent/40"
              }`}
              data-testid={`timeline-event-${idx}`}
            >
              <span className="font-mono text-xs font-semibold text-muted-foreground">
                {isPicked ? ev.year : "••••"}
              </span>
              <span className={isPicked ? "" : "flex-1"}>{ev.label}</span>
              {isPicked && (
                <Badge variant="secondary" className="ml-auto font-mono text-[10px]">
                  #{picked.indexOf(idx) + 1}
                </Badge>
              )}
            </button>
          );
        })}
      </div>
      <p className="text-sm text-muted-foreground">
        Click the events in chronological order — earliest first. A wrong pick costs a mistake; the
        year stays hidden until the event is correctly placed.
      </p>
    </div>
  );
}
