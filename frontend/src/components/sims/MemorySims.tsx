import { useEffect, useRef, useState } from "react";
import { Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Phase = "idle" | "showing" | "recall" | "right" | "over";

export default function MemorySim() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [level, setLevel] = useState(3);
  const [digits, setDigits] = useState("");
  const [input, setInput] = useState("");
  const [best, setBest] = useState(0);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, []);

  function startRound(len: number) {
    const d = Array.from({ length: len }, () => Math.floor(Math.random() * 10)).join("");
    setDigits(d);
    setInput("");
    setPhase("showing");
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setPhase("recall"), 1200 + len * 350);
  }

  function begin() {
    setLevel(3);
    setPhase("showing");
    startRound(3);
  }

  function submit() {
    if (input === digits) {
      setBest((b) => Math.max(b, level));
      setPhase("right");
      timer.current = setTimeout(() => {
        setLevel(level + 1);
        startRound(level + 1);
      }, 900);
    } else {
      setPhase("over");
    }
  }

  return (
    <div className="space-y-5" data-testid="sim-memory">
      <div className="flex min-h-40 flex-col items-center justify-center gap-3 rounded-lg border bg-card p-6 text-center">
        {phase === "idle" && (
          <>
            <p className="max-w-sm text-sm text-muted-foreground">
              A digit sequence will flash on screen. Memorize it, then type it back. Each round adds
              one digit — Miller said 7±2, Cowan said 4. Where do you land?
            </p>
            <Button onClick={begin} data-testid="memory-start-btn">
              <Play className="h-4 w-4" /> Start at 3 digits
            </Button>
          </>
        )}
        {phase === "showing" && (
          <>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Memorize — {level} digits
            </p>
            <p className="font-mono text-4xl font-bold tracking-[0.3em]" data-testid="memory-digit-display">
              {digits}
            </p>
          </>
        )}
        {phase === "recall" && (
          <>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Now type the {level} digits from memory
            </p>
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value.replace(/\D/g, ""))}
                onKeyDown={(e) => e.key === "Enter" && input && submit()}
                className="w-48 text-center font-mono text-xl tracking-[0.2em]"
                autoFocus
                data-testid="memory-input"
              />
              <Button onClick={submit} disabled={!input} data-testid="memory-submit-btn">
                Check
              </Button>
            </div>
          </>
        )}
        {phase === "right" && (
          <p className="font-heading text-xl font-semibold text-emerald-600" data-testid="memory-feedback">
            Correct! Level {level} cleared…
          </p>
        )}
        {phase === "over" && (
          <>
            <p className="font-heading text-xl font-semibold" data-testid="memory-feedback">
              Round over — your span was {Math.max(best, level - 1)} digits
            </p>
            <p className="text-sm text-muted-foreground">
              Expected: {digits} · You typed: {input || "—"}
            </p>
            <Button onClick={begin} data-testid="memory-restart-btn">
              Try again
            </Button>
          </>
        )}
      </div>
      <p className="font-mono text-xs text-muted-foreground">Best span this session: {best} digits</p>
    </div>
  );
}
