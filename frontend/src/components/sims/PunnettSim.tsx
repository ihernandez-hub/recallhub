import { useMemo, useState } from "react";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const GENOTYPES = ["AA", "Aa", "aa"] as const;
type Geno = (typeof GENOTYPES)[number];

// 'A' < 'a' in ASCII, so sorting the pair puts the capital allele first.
function square(p1: Geno, p2: Geno): string[][] {
  return [0, 1].map((r) =>
    [0, 1].map((c) => {
      const a = p1[r];
      const b = p2[c];
      return a === b ? a + a : a < b ? a + b : b + a;
    }),
  );
}

export default function PunnettSim() {
  const [p1, setP1] = useState<Geno>("Aa");
  const [p2, setP2] = useState<Geno>("Aa");
  const grid = useMemo(() => square(p1, p2), [p1, p2]);
  const flat = grid.flat();
  const genoCounts = flat.reduce<Record<string, number>>((acc, g) => {
    acc[g] = (acc[g] ?? 0) + 1;
    return acc;
  }, {});
  const dominant = flat.filter((g) => g !== "aa").length;
  const dominantPct = Math.round((dominant / flat.length) * 100);

  return (
    <div className="grid gap-6 md:grid-cols-[1fr_1fr]" data-testid="sim-punnett">
      <div className="space-y-4">
        <div className="space-y-1.5">
          <Label>Parent 1 genotype</Label>
          <Select value={p1} onValueChange={(v: string) => setP1(v as Geno)}>
            <SelectTrigger data-testid="punnett-parent1-select">
              <SelectValue>{(v: string) => v}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {GENOTYPES.map((g) => (
                <SelectItem key={g} value={g}>
                  {g}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-1.5">
          <Label>Parent 2 genotype</Label>
          <Select value={p2} onValueChange={(v: string) => setP2(v as Geno)}>
            <SelectTrigger data-testid="punnett-parent2-select">
              <SelectValue>{(v: string) => v}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {GENOTYPES.map((g) => (
                <SelectItem key={g} value={g}>
                  {g}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="rounded-lg border bg-muted/40 p-4 text-sm" data-testid="punnett-stats">
          <p className="font-medium">Phenotype prediction</p>
          <p className="mt-1 text-muted-foreground">
            {dominantPct}% show the dominant trait (A), {100 - dominantPct}% show the recessive trait (a).
          </p>
          <ul className="mt-2 space-y-0.5 font-mono text-xs text-muted-foreground">
            {Object.entries(genoCounts).map(([g, c]) => (
              <li key={g}>
                {g}: {c * 25}%
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          Offspring Punnett square
        </p>
        <div className="grid grid-cols-[2rem_repeat(2,1fr)] gap-1" data-testid="punnett-grid">
          <div />
          {[0, 1].map((c) => (
            <div key={c} className="flex items-center justify-center font-mono text-sm text-muted-foreground">
              {p2[c]}
            </div>
          ))}
          {[0, 1].map((r) => (
            <div key={`row-${r}`} className="contents">
              <div className="flex items-center justify-center font-mono text-sm text-muted-foreground">
                {p1[r]}
              </div>
              {[0, 1].map((c) => (
                <div
                  key={`cell-${r}-${c}`}
                  className="flex aspect-square items-center justify-center rounded-lg border bg-card font-mono text-lg font-semibold"
                >
                  {grid[r][c]}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
