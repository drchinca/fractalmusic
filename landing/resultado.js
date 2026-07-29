import { archetypes } from "./test-data.js";
import { getHistory, sendEvent } from "./api-client.js";

const ACCESS_KEY = "fmw.resultAccess.v1";
const access = JSON.parse(localStorage.getItem(ACCESS_KEY) || "null");
const current = JSON.parse(localStorage.getItem("fmw.dissonanceTest.v2") || "null")?.result;
const byName = Object.fromEntries(archetypes.map((item) => [item.name, item]));

function pct(value) { return typeof value === "number" ? `${Math.round(value * 100)}%` : String(value || ""); }
function showCurrent(result) {
  if (!result) return;
  document.querySelector("#delivery-dominant").textContent = result.dominant.name;
  document.querySelector("#delivery-secondary").textContent = result.secondary.name;
  document.querySelector("#delivery-score1").textContent = pct(result.dominant.normalizedScore);
  document.querySelector("#delivery-score2").textContent = pct(result.secondary.normalizedScore);
  document.querySelector("#delivery-date").textContent = new Intl.DateTimeFormat("es-CR", { dateStyle: "long", timeStyle: "short" }).format(new Date(result.completedAt));
  document.querySelector("#delivery-diagnosis").textContent = result.dominant.diagnosis;
  document.querySelector("#sample-link").href = `muestra.html?arquetipo=${encodeURIComponent(result.dominant.id)}`;
}

function renderHistory(payload) {
  const list = document.querySelector("#history-list");
  const history = payload.assessments || [];
  document.querySelector("#history-summary").textContent = payload.evolution?.summary || "Este es tu primer registro cognitivo.";
  list.replaceChildren(...history.map((item, index) => {
    const card = document.createElement("article");
    card.className = "history-entry";
    const dominant = byName[item.ARQUETIPO];
    card.innerHTML = `<span class="history-index">${String(history.length - index).padStart(2, "0")}</span><div><h3>${item.ARQUETIPO}</h3><p>${item.ARQSEC} · ${item.SCORE1} / ${item.SCORE2}</p><small>${new Intl.DateTimeFormat("es-CR", { dateStyle: "medium", timeStyle: "short" }).format(new Date(item.TESTDATE))}</small></div><a href="muestra.html?arquetipo=${dominant?.id || ""}">Muestra</a>`;
    return card;
  }));
}

showCurrent(current);
if (!access?.email || !access?.token) {
  document.querySelector("#history-summary").textContent = "Guarda tu resultado desde el formulario del test para activar la memoria evolutiva.";
} else {
  try {
    const payload = await getHistory(access.email, access.token);
    renderHistory(payload);
    void sendEvent("history_viewed", { assessments: payload.assessments.length });
  } catch (error) {
    document.querySelector("#history-summary").textContent = error.message;
  }
}
