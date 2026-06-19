import { type JSX, useEffect, useState } from "react";

import { ChatPanel } from "../chat/ChatPanel";
import { ComposerPanel } from "../composer/ComposerPanel";
import { GatopleApp } from "../gatople/GatopleApp";
import { StrudelPanel } from "../strudel/StrudelPanel";

type View = "gatople" | "chat" | "composer" | "strudel";

const HASH_TO_VIEW: Record<string, View> = {
  "#gatople": "gatople",
  "#chat": "chat",
  "#composer": "composer",
  "#strudel": "strudel",
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
    window.location.hash = `#${next}`;
  }

  let body;
  if (view === "gatople") {
    body = <GatopleApp />;
  } else if (view === "chat") {
    body = <ChatPanel />;
  } else if (view === "strudel") {
    body = <StrudelPanel />;
  } else {
    body = <ComposerPanel />;
  }

  return (
    <>
      <a href="#content" className="app-skip-link">Saltar al contenido</a>
      <nav className="app-nav" aria-label="Vista principal">
        <button
          type="button"
          className={`app-nav-tab ${view === "gatople" ? "is-active" : ""}`}
          onClick={() => go("gatople")}
          aria-current={view === "gatople" ? "page" : undefined}
        >
          La Rueda
        </button>
        <button
          type="button"
          className={`app-nav-tab ${view === "composer" ? "is-active" : ""}`}
          onClick={() => go("composer")}
          aria-current={view === "composer" ? "page" : undefined}
        >
          Componer
        </button>
        <button
          type="button"
          className={`app-nav-tab ${view === "strudel" ? "is-active" : ""}`}
          onClick={() => go("strudel")}
          aria-current={view === "strudel" ? "page" : undefined}
        >
          Patrón en vivo
        </button>
        <button
          type="button"
          className={`app-nav-tab ${view === "chat" ? "is-active" : ""}`}
          onClick={() => go("chat")}
          aria-current={view === "chat" ? "page" : undefined}
        >
          Preguntar a los libros
        </button>
      </nav>

      <div id="content" className="app-content">{body}</div>
    </>
  );
}
