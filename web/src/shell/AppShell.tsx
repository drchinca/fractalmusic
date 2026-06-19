import { type JSX, useEffect, useState } from "react";

import { ChatPanel } from "../chat/ChatPanel";
import { GatopleApp } from "../gatople/GatopleApp";

type View = "gatople" | "chat";

const HASH_TO_VIEW: Record<string, View> = {
  "#gatople": "gatople",
  "#chat": "chat",
};

function readView(): View {
  return HASH_TO_VIEW[window.location.hash] ?? "gatople";
}

export function AppShell(): JSX.Element {
  const [view, setView] = useState<View>(readView());

  useEffect(() => {
    function onHashChange(): void {
      setView(readView());
    }
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  function go(next: View): void {
    window.location.hash = next === "gatople" ? "#gatople" : "#chat";
  }

  return (
    <>
      <nav className="app-nav" aria-label="Vista principal">
        <button
          type="button"
          className={`app-nav-tab ${view === "gatople" ? "is-active" : ""}`}
          onClick={() => go("gatople")}
          aria-current={view === "gatople" ? "page" : undefined}
        >
          El Gátople
        </button>
        <button
          type="button"
          className={`app-nav-tab ${view === "chat" ? "is-active" : ""}`}
          onClick={() => go("chat")}
          aria-current={view === "chat" ? "page" : undefined}
        >
          Pregunta a los libros
        </button>
      </nav>

      {view === "gatople" ? <GatopleApp /> : <ChatPanel />}
    </>
  );
}
