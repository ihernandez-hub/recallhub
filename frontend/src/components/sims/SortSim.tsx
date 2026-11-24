import { useCallback, useEffect, useRef, useState } from "react";
import { Pause, Play, Shuffle, StepForward } from "lucide-react";
import { Button } from "@/components/ui/button";

const SIZE = 16;

function randomArr(): number[] {
  return Array.from({ length: SIZE }, () => 10 + Math.floor(Math.random() * 90));
}

export default function SortSim() {
  const work = useRef<number[]>(randomArr());
  const pos = useRef({ i: 0, j: 0 });
  const [arr, setArr] = useState<number[]>(() => [...work.current]);
  const [active, setActive] = useState<[number, number] | null>(null);
  const [stats, setStats] = useState({ comparisons: 0, swaps: 0 });
  const [playing, setPlaying] = useState(false);
  const [done, setDone] = useState(false);

  const tick = useCallback((): boolean => {
    const n = work.current.length;
    const { i, j } = pos.current;
    if (i >= n - 1) {
      setPlaying(false);
      setActive(null);
      setDone(true);
      return true;
    }
    setActive([j, j + 1]);
    setStats((s) => ({ ...s, comparisons: s.comparisons + 1 }));
    if (work.current[j] > work.current[j + 1]) {
      [work.current[j], work.current[j + 1]] = [work.current[j + 1], work.current[j]];
      setStats((s) => ({ ...s, swaps: s.swaps + 1 }));
    }
    setArr([...work.current]);
    const nj = j + 1;
    if (nj >= n - 1 - i) {
      if (i + 1 >= n - 1) {
        setDone(true);
        setPlaying(false);
        setActive(null);
        return true;
      }
      pos.current = { i: i + 1, j: 0 };
    } else {
      pos.current = { i, j: nj };
    }
    return false;
  }, []);

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => {
      if (tick()) clearInterval(id);
    }, 110);
    return () => clearInterval(id);
  }, [playing, tick]);

  function scramble() {
    work.current = randomArr();
    pos.current = { i: 0, j: 0 };
    setArr([...work.current]);
    setStats({ comparisons: 0, swaps: 0 });
    setDone(false);
    setPlaying(false);
    setActive(null);
  }

  return (
    <div className="space-y-5" data-testid="sim-sort">
      <div className="flex h-48 items-end gap-1 rounded-lg border bg-card p-3" data-testid="sort-bars">
        {arr.map((v, i) => {
          const isActive = active?.includes(i);
          return (
            <div
              key={i}
              className={`flex-1 rounded-t transition-[height,background-color] duration-100 ${
                isActive ? "bg-amber-500" : done ? "bg-emerald-500" : "bg-primary"
              }`}
              style={{ height: `${v}%` }}
            />
          );
        })}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Button
          onClick={() => setPlaying((p) => !p)}
          disabled={done}
          data-testid="sort-play-btn"
        >
          {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          {playing ? "Pause" : "Play"}
        </Button>
        <Button variant="outline" onClick={tick} disabled={done || playing} data-testid="sort-step-btn">
          <StepForward className="h-4 w-4" /> Step
        </Button>
        <Button variant="outline" onClick={scramble} data-testid="sort-scramble-btn">
          <Shuffle className="h-4 w-4" /> Scramble
        </Button>
        <p className="ml-auto font-mono text-xs text-muted-foreground" data-testid="sort-stats">
          comparisons: {stats.comparisons} · swaps: {stats.swaps}
        </p>
      </div>
      <p className="text-sm text-muted-foreground">
        Bubble sort repeatedly compares neighbors and swaps out-of-order pairs — O(n²) comparisons in
        the worst case. Watch how large values "bubble" to the right first.
      </p>
    </div>
  );
}
