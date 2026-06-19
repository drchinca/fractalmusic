import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { GatopleApp } from "./gatople/GatopleApp";
import "./gatople/gatople.css";

const container = document.getElementById("root");
if (container === null) {
  throw new Error("Root element #root not found");
}

createRoot(container).render(
  <StrictMode>
    <GatopleApp />
  </StrictMode>,
);
