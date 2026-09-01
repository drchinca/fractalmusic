import assert from "node:assert/strict";
import test from "node:test";
import { archetypes, questions } from "../test-data.js";
import { scoreAnswers, validateAnswerSet } from "../scoring-engine.js";

function answersByOption(optionId) {
  return Object.fromEntries(questions.map((q) => [q.id, q.options.find((o) => o.id === optionId).technicalId]));
}

function findDominant(targetName, attempts = 200000) {
  let seed = 0x51f15e;
  const random = () => {
    seed = (1664525 * seed + 1013904223) >>> 0;
    return seed / 0x100000000;
  };
  for (let i = 0; i < attempts; i += 1) {
    const answers = Object.fromEntries(questions.map((q) => {
      const preferred = q.options.find((o) => o.archetype === targetName);
      const option = preferred && random() < 0.9 ? preferred : q.options[Math.floor(random() * q.options.length)];
      return [q.id, option.technicalId];
    }));
    const result = scoreAnswers(answers);
    if (result.dominant.name === targetName || result.tiedArchetypes.includes(targetName)) return result;
  }
  return null;
}

test("la matriz oficial contiene 12 preguntas y 48 IDs técnicos únicos", () => {
  assert.equal(questions.length, 12);
  const ids = questions.flatMap((q) => q.options.map((o) => o.technicalId));
  assert.equal(ids.length, 48);
  assert.equal(new Set(ids).size, 48);
  questions.forEach((q, qi) => q.options.forEach((o) => {
    assert.equal(o.technicalId, `Q${qi + 1}_${o.id}`);
  }));
});

test("las oportunidades declaradas coinciden exactamente con la matriz", () => {
  const actual = Object.fromEntries(archetypes.map((a) => [a.name, 0]));
  questions.forEach((q) => q.options.forEach((o) => { actual[o.archetype] += 1; }));
  archetypes.forEach((a) => assert.equal(actual[a.name], a.opportunities, a.name));
});

test("el motor rechaza respuestas incompletas o técnicamente inválidas", () => {
  assert.throws(() => validateAnswerSet({}), /exactamente 12/);
  const answers = answersByOption("A");
  answers.Q4 = "Q4_Z";
  assert.throws(() => scoreAnswers(answers), /Respuesta inválida/);
});

test("el resultado es determinista para las mismas 12 respuestas", () => {
  for (const optionId of ["A", "B", "C", "D"]) {
    const answers = answersByOption(optionId);
    const first = scoreAnswers(answers);
    const second = scoreAnswers({ ...answers });
    assert.deepEqual(first.rawScores, second.rawScores);
    assert.equal(first.dominant.name, second.dominant.name);
    assert.equal(first.secondary.name, second.secondary.name);
    assert.deepEqual(first.tiedArchetypes, second.tiedArchetypes);
  }
});

test("todos los arquetipos son alcanzables como dominantes o codominantes", () => {
  for (const archetype of archetypes) {
    assert.ok(findDominant(archetype.name), `No se encontró ruta para ${archetype.name}`);
  }
});

test("dominante y secundario siempre son distintos y pertenecen al catálogo", () => {
  for (const optionId of ["A", "B", "C", "D"]) {
    const result = scoreAnswers(answersByOption(optionId));
    assert.notEqual(result.dominant.name, result.secondary.name);
    assert.ok(archetypes.some((a) => a.name === result.dominant.name));
    assert.ok(archetypes.some((a) => a.name === result.secondary.name));
  }
});

test("la calibración reduce empates y mantiene equilibrada la distribución aleatoria", () => {
  const counts = Object.fromEntries(archetypes.map((archetype) => [archetype.name, 0]));
  let hybrids = 0;
  let seed = 0x260826;
  const random = () => ((seed = (1664525 * seed + 1013904223) >>> 0) / 0x100000000);
  const sampleSize = 50_000;
  for (let i = 0; i < sampleSize; i += 1) {
    const answers = Object.fromEntries(questions.map((question) => {
      const option = question.options[Math.floor(random() * question.options.length)];
      return [question.id, option.technicalId];
    }));
    const result = scoreAnswers(answers);
    counts[result.dominant.name] += 1;
    if (result.resultType === "hybrid") hybrids += 1;
  }
  const percentages = Object.values(counts).map((count) => count * 100 / sampleSize);
  assert.ok(Math.max(...percentages) - Math.min(...percentages) < 2.5);
  assert.ok(hybrids / sampleSize < 0.001);
});
