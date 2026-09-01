import { mailchimpContract, questions } from "./test-data.js";
import { scoreAnswers } from "./scoring-engine.js";
import { saveLead, sendEvent } from "./api-client.js";

const STORAGE_KEY = "fmw.dissonanceTest.v2";
const LEADS_KEY = "fmw.testLeads.v2";

const state = {
  current: 0,
  answers: {},
  result: null
};

const $ = (selector) => document.querySelector(selector);
const testView = $("#test-view");
const resultView = $("#result-view");
const progress = $("#test-progress");
const progressText = $("#progress-text");
const questionNumber = $("#question-number");
const questionText = $("#question-text");
const options = $("#options");
const previousButton = $("#previous-question");

function emit(name, detail = {}) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event: name, ...detail });
  window.dispatchEvent(new CustomEvent(`fmw:${name}`, { detail }));
  void sendEvent(name, detail);
}

function renderQuestion() {
  const question = questions[state.current];
  const completed = Object.keys(state.answers).length;
  progress.value = completed;
  progress.max = questions.length;
  progressText.textContent = `${completed} de ${questions.length} respondidas`;
  questionNumber.textContent = `Pregunta ${state.current + 1} de ${questions.length}`;
  questionText.textContent = question.text;
  previousButton.disabled = state.current === 0;

  options.replaceChildren(...question.options.map((option) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "test-option";
    button.dataset.selected = state.answers[question.id] === option.technicalId ? "true" : "false";
    button.innerHTML = `<span class="option-key">${option.id}</span><span>${option.label}</span>`;
    button.addEventListener("click", () => selectOption(question.id, option.technicalId));
    return button;
  }));
}

function selectOption(questionId, technicalId) {
  state.answers[questionId] = technicalId;
  persistDraft();
  emit("test_answer", { question_id: questionId, answer_id: technicalId });

  if (state.current < questions.length - 1) {
    state.current += 1;
    renderQuestion();
    window.scrollTo({ top: testView.offsetTop - 90, behavior: "smooth" });
    return;
  }

  calculateResult();
}

function calculateResult() {
  if (Object.keys(state.answers).length !== questions.length) return;

  let scored;
  try {
    scored = scoreAnswers(state.answers);
  } catch (error) {
    console.error(error);
    return;
  }

  state.result = {
    id: crypto.randomUUID(),
    completedAt: new Date().toISOString(),
    ...scored,
    answers: { ...state.answers }
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...state, current: questions.length - 1 }));
  emit("test_completed");
  emit("scores_calculated");
  emit("result_generated", {
    primary_archetype: state.result.dominant.name,
    secondary_archetype: state.result.secondary.name,
    result_type: state.result.resultType
  });
  renderResult();
}

function pct(value) {
  return `${Math.round(value * 100)}%`;
}

function renderResult() {
  if (!state.result) return;
  const { dominant, secondary, resultType, tiedArchetypes } = state.result;

  $("#result-type").textContent = resultType === "hybrid"
    ? `Perfil híbrido: ${tiedArchetypes.join(" + ")}`
    : "Perfil relacional actual";

  $("#dominant-name").textContent = dominant.name;
  $("#dominant-family").textContent = `Arquetipo ${dominant.group} · ${pct(dominant.normalizedScore)}`;
  $("#dominant-description").textContent = dominant.diagnosis;
  $("#secondary-name").textContent = `${secondary.name} · ${pct(secondary.normalizedScore)}`;
  $("#zone-text").textContent = dominant.zone;
  $("#blind-spot-text").textContent = dominant.blindSpot;
  $("#identity-phrase").textContent = `“${dominant.identityPhrase}”`;
  $("#route-text").textContent = dominant.sampleRecommendation;
  $("#result-cta").textContent = dominant.cta;

  testView.hidden = true;
  resultView.hidden = false;
  resultView.scrollIntoView({ behavior: "smooth", block: "start" });
  emit("result_viewed", { primary_archetype: dominant.name });
}

function persistDraft() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function restore() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    emit("test_started");
    return;
  }

  try {
    const saved = JSON.parse(raw);
    const validCurrent = Number.isInteger(saved?.current) && saved.current >= 0 && saved.current < questions.length;
    const validAnswers = saved?.answers && typeof saved.answers === "object" && Object.entries(saved.answers).every(([questionId, technicalId]) => {
      const question = questions.find((item) => item.id === questionId);
      return question?.options.some((option) => option.technicalId === technicalId);
    });
    if (!validCurrent || !validAnswers) throw new Error("Borrador inválido");
    Object.assign(state, saved);
    if (state.result) renderResult();
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    emit("test_started");
  }
}

previousButton.addEventListener("click", () => {
  if (state.current > 0) {
    state.current -= 1;
    renderQuestion();
  }
});

$("#restart-test").addEventListener("click", () => {
  localStorage.removeItem(STORAGE_KEY);
  state.current = 0;
  state.answers = {};
  state.result = null;
  resultView.hidden = true;
  testView.hidden = false;
  renderQuestion();
  emit("test_started");
});

$("#lead-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.result) return;

  const formElement = event.currentTarget;
  const submitButton = formElement.querySelector('button[type="submit"]');
  const form = new FormData(formElement);
  const name = String(form.get("name") || "").trim();
  const email = String(form.get("email") || "").trim();
  const consentTimestamp = new Date().toISOString();

  const lead = {
    FNAME: name,
    EMAIL: email,
    ARQUETIPO: state.result.dominant.name,
    ARQSEC: state.result.secondary.name,
    SCORE1: pct(state.result.dominant.normalizedScore),
    SCORE2: pct(state.result.secondary.normalizedScore),
    MUESTRA: `${location.origin}/muestra.html?arquetipo=${encodeURIComponent(state.result.dominant.id)}`,
    TESTDATE: state.result.completedAt,
    COMPRA: "NO",
    PRODUCTO: "",
    FUENTE: mailchimpContract.source,
    CONSENT: consentTimestamp,
    tags: [
      "TEST_COMPLETADO",
      "SECUENCIA_DISONANTE",
      `ARQ_${state.result.dominant.id.replaceAll("-", "_").toUpperCase()}`
    ],
    answers: state.result.answers,
    raw_scores: state.result.rawScores,
    normalized_scores: state.result.normalizedScores,
    result_type: state.result.resultType,
    result_id: state.result.id
  };

  submitButton.disabled = true;
  $("#save-status").textContent = "Guardando resultado…";
  try {
    const saved = await saveLead(lead);
    localStorage.setItem("fmw.resultAccess.v1", JSON.stringify({ email: lead.EMAIL, token: saved.accessToken, assessmentId: saved.assessmentId }));
    $("#save-status").textContent = "Resultado guardado. Tu informe y memoria evolutiva están disponibles.";
    const reportLink = $("#open-report");
    reportLink.hidden = false;
    reportLink.href = "resultado.html";
    formElement.reset();
    emit("lead_captured", {
      primary_archetype: lead.ARQUETIPO,
      secondary_archetype: lead.ARQSEC
    });
  } catch (error) {
    $("#save-status").textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

$("#export-result").addEventListener("click", () => {
  if (!state.result) return;
  const blob = new Blob([JSON.stringify(state.result, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `fmw-resultado-${state.result.dominant.id}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
});

restore();
if (!state.result) renderQuestion();
