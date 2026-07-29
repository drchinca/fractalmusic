import { archetypes, questions } from "./test-data.js";

export function compareScores(a, b) {
  return (
    b.normalizedScore - a.normalizedScore ||
    b.rawScore - a.rawScore ||
    b.adjustedScore - a.adjustedScore ||
    a.name.localeCompare(b.name, "es")
  );
}

export function validateAnswerSet(answers) {
  if (!answers || typeof answers !== "object") {
    throw new TypeError("Las respuestas deben ser un objeto.");
  }
  if (Object.keys(answers).length !== questions.length) {
    throw new Error(`Se requieren exactamente ${questions.length} respuestas.`);
  }
  for (const question of questions) {
    const technicalId = answers[question.id];
    if (!question.options.some((option) => option.technicalId === technicalId)) {
      throw new Error(`Respuesta inválida para ${question.id}: ${technicalId ?? "vacía"}.`);
    }
  }
}

export function scoreAnswers(answers) {
  validateAnswerSet(answers);

  const rawScores = Object.fromEntries(archetypes.map((archetype) => [archetype.name, 0]));
  for (const question of questions) {
    const selected = question.options.find((option) => option.technicalId === answers[question.id]);
    rawScores[selected.archetype] += selected.rawPoints;
  }

  const ranking = archetypes.map((archetype) => {
    const rawScore = rawScores[archetype.name];
    const normalizedScore = rawScore / archetype.opportunities;
    const adjustedScore = (rawScore + 1) / (archetype.opportunities + 2);
    return { ...archetype, rawScore, normalizedScore, adjustedScore };
  }).sort(compareScores);

  const top = ranking[0];
  const tiedAtTop = ranking.filter((item) =>
    item.normalizedScore === top.normalizedScore &&
    item.rawScore === top.rawScore &&
    item.adjustedScore === top.adjustedScore
  );

  return {
    resultType: tiedAtTop.length > 1 ? "hybrid" : "ranked",
    tiedArchetypes: tiedAtTop.map((item) => item.name),
    dominant: ranking[0],
    secondary: ranking[1],
    ranking,
    rawScores,
    normalizedScores: Object.fromEntries(ranking.map((item) => [item.name, item.normalizedScore])),
    method: "normalized_raw_adjusted_hybrid"
  };
}
