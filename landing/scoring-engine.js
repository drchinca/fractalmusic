import { archetypes, questions } from "./test-data.js";

export function compareScores(a, b) {
  return (
    b.calibratedScore - a.calibratedScore ||
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
  const weightedScores = Object.fromEntries(archetypes.map((archetype) => [archetype.name, 0]));
  const weightedOpportunities = Object.fromEntries(archetypes.map((archetype) => [archetype.name, 0]));
  const squaredOpportunityWeights = Object.fromEntries(archetypes.map((archetype) => [archetype.name, 0]));
  questions.forEach((question, questionIndex) => {
    const weight = 1 + questionIndex / 100;
    for (const option of question.options) {
      weightedOpportunities[option.archetype] += weight;
      squaredOpportunityWeights[option.archetype] += weight ** 2;
    }
    const selected = question.options.find((option) => option.technicalId === answers[question.id]);
    rawScores[selected.archetype] += selected.rawPoints;
    weightedScores[selected.archetype] += selected.rawPoints * weight;
  });

  const ranking = archetypes.map((archetype) => {
    const rawScore = rawScores[archetype.name];
    const normalizedScore = rawScore / archetype.opportunities;
    const adjustedScore = (rawScore + 1) / (archetype.opportunities + 2);
    const expectedScore = weightedOpportunities[archetype.name] / 4;
    const standardDeviation = Math.sqrt((3 / 16) * squaredOpportunityWeights[archetype.name]);
    const calibratedScore = (weightedScores[archetype.name] - expectedScore) / standardDeviation;
    return { ...archetype, rawScore, normalizedScore, adjustedScore, calibratedScore };
  }).sort(compareScores);

  const top = ranking[0];
  const tiedAtTop = ranking.filter((item) =>
    Math.abs(item.calibratedScore - top.calibratedScore) < Number.EPSILON &&
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
    method: "calibrated_zscore_normalized_raw_adjusted_hybrid"
  };
}
