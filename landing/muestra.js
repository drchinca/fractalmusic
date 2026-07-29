import { samples } from "./samples.js";
import { sendEvent } from "./api-client.js";

const params = new URLSearchParams(location.search);
const slug = params.get("arquetipo") || "";
const sample = samples[slug];

if (!sample) {
  document.querySelector("#sample-title").textContent = "Muestra no encontrada";
  document.querySelector("#sample-sheet").classList.add("error-card");
} else {
  document.title = `${sample.title} | Fractal Music World`;
  document.querySelector("#sample-group").textContent = `Arquetipo ${sample.group} · ${sample.zone}`;
  document.querySelector("#sample-title").textContent = sample.title;
  document.querySelector("#sample-archetype").textContent = sample.archetype;
  document.querySelector("#sample-identity").textContent = `“${sample.identityPhrase}”`;
  document.querySelector("#sample-opening").textContent = sample.opening;
  document.querySelector("#sample-diagnosis").textContent = sample.diagnosis;
  document.querySelector("#sample-practice").textContent = sample.practice;
  document.querySelector("#sample-question").textContent = sample.question;
  document.querySelector("#sample-blind").textContent = sample.blindSpot;
  document.querySelector("#sample-affinity").textContent = `Tu contraste fértil puede aparecer al dialogar con ${sample.affinity}.`;
  void sendEvent("sample_downloaded", { archetype: sample.archetype, sample_slug: slug, mode: "view" });
}

document.querySelector("#download-sample").addEventListener("click", () => {
  if (!sample) return;
  const text = [
    "FRACTAL MUSIC WORLD — MUESTRA PERSONALIZADA",
    sample.archetype,
    sample.title,
    "",
    sample.identityPhrase,
    "",
    "TU PUERTA DE ENTRADA",
    sample.opening,
    "",
    "LECTURA RELACIONAL",
    sample.diagnosis,
    "",
    "EJERCICIO DE ACTIVACIÓN",
    sample.practice,
    "",
    "PREGUNTA DE TRANSFORMACIÓN",
    sample.question,
    "",
    "PUNTO CIEGO",
    sample.blindSpot,
    "",
    `AFINIDAD SUGERIDA: ${sample.affinity}`
  ].join("\n");
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `FMW_Muestra_${sample.slug}.txt`;
  anchor.click();
  URL.revokeObjectURL(url);
  void sendEvent("sample_downloaded", { archetype: sample.archetype, sample_slug: slug, mode: "download" });
});
