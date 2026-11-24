import { type ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { ThemeProvider, useTheme } from "next-themes";
import { BookOpen, FlaskConical, Lightbulb, Layers, ListChecks, Moon, Sun } from "lucide-react";
import QuickSearch from "@/components/QuickSearch";
import { Toaster } from "@/components/ui/sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const NAV = [
  { to: "/notes", label: "Notes", icon: BookOpen },
  { to: "/brainstorm", label: "Brainstorm", icon: Lightbulb },
  { to: "/flashcards", label: "Flashcards", icon: Layers },
  { to: "/quizzes", label: "Quizzes", icon: ListChecks },
  { to: "/sims", label: "Sims", icon: FlaskConical },
];

function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label="Toggle theme"
      data-testid="theme-toggle-btn"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="h-4 w-4 dark:hidden" />
      <Moon className="hidden h-4 w-4 dark:block" />
    </Button>
  );
}

export default function AppShell({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
      <div className="min-h-svh">
        <header className="sticky top-0 z-40 border-b bg-white/85 backdrop-blur-xl dark:border-[#1E2631] dark:bg-[#161B22]/85">
          <div className="mx-auto flex h-14 max-w-7xl items-center gap-4 px-4 sm:px-6">
            <NavLink to="/notes" className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary font-heading text-sm font-bold text-primary-foreground">
                R
              </span>
              <span className="font-heading text-lg font-semibold tracking-tight">RecallHub</span>
              <Badge variant="secondary" className="hidden font-mono text-[10px] uppercase tracking-wider sm:inline-flex">
                Study Workspace
              </Badge>
            </NavLink>
            <QuickSearch />
            <nav className="ml-auto flex items-center gap-1" aria-label="Main">
              {NAV.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground sm:px-3 ${
                      isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground"
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{label}</span>
                </NavLink>
              ))}
              <ThemeToggle />
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">{children}</main>
        <Toaster />
      </div>
    </ThemeProvider>
  );
}
