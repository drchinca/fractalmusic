import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./chat/chat.css";
import "./composer/composer.css";
import "./gatople/gatople.css";
import "./shell/shell.css";
import "./strudel/strudel.css";
import { AppShell } from "./shell/AppShell";

const container = document.getElementById("root");
if (container === null) {
  throw new Error("Root element #root not found");
}

createRoot(container).render(
  <StrictMode>
    <AppShell />
  </StrictMode>,
);
