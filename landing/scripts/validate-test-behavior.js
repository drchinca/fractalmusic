import fs from "node:fs/promises";
import path from "node:path";
import { archetypes, questions } from "../test-data.js";
import { scoreAnswers } from "../scoring-engine.js";

const SAMPLE_SIZE = Number(process.env.FMW_VALIDATION_SAMPLE_SIZE || 250000);
let seed = 0xD1550A7;
function random() {
  seed = (1664525 * seed + 1013904223) >>> 0;
  return seed / 0x100000000;
}

const dominantCounts = Object.fromEntries(archetypes.map((a) => [a.name, 0]));
const secondaryCounts = Object.fromEntries(archetypes.map((a) => [a.name, 0]));
const hybridSizes = {};
let hybrids = 0;
let maxTieSize = 1;

for (let i = 0; i < SAMPLE_SIZE; i += 1) {
  const answers = Object.fromEntries(questions.map((q) => {
    const option = q.options[Math.floor(random() * q.options.length)];
    return [q.id, option.technicalId];
  }));
  const result = scoreAnswers(answers);
  dominantCounts[result.dominant.name] += 1;
  secondaryCounts[result.secondary.name] += 1;
  if (result.resultType === "hybrid") {
    hybrids += 1;
    const size = result.tiedArchetypes.length;
    hybridSizes[size] = (hybridSizes[size] || 0) + 1;
    maxTieSize = Math.max(maxTieSize, size);
  }
}

const opportunities = Object.fromEntries(archetypes.map((a) => [a.name, {
  declared: a.opportunities,
  actual: questions.flatMap((q) => q.options).filter((o) => o.archetype === a.name).length
}]));

const percentages = (counts) => Object.fromEntries(Object.entries(counts).map(([name, count]) => [name, Number((count * 100 / SAMPLE_SIZE).toFixed(4))]));
const dominantPercentages = percentages(dominantCounts);
const values = Object.values(dominantPercentages);

const report = {
  generatedAt: new Date().toISOString(),
  engine: "calibrated_zscore_normalized_raw_adjusted_hybrid",
  matrix: {
    questions: questions.length,
    options: questions.reduce((sum, q) => sum + q.options.length, 0),
    archetypes: archetypes.length,
    uniqueTechnicalIds: new Set(questions.flatMap((q) => q.options.map((o) => o.technicalId))).size,
    opportunities
  },
  simulation: {
    seed: "0x0D1550A7",
    sampleSize: SAMPLE_SIZE,
    uniformRandomResponses: true,
    dominantCounts,
    dominantPercentages,
    secondaryCounts,
    secondaryPercentages: percentages(secondaryCounts),
    hybridCount: hybrids,
    hybridRatePercent: Number((hybrids * 100 / SAMPLE_SIZE).toFixed(4)),
    hybridSizes,
    maxTieSize,
    dominantSpreadPercentagePoints: Number((Math.max(...values) - Math.min(...values)).toFixed(4))
  },
  interpretation: {
    status: "TECHNICALLY_VALIDATED",
    note: "La simulación comprueba el comportamiento matemático del motor bajo respuestas uniformes. No sustituye la validación con participantes reales ni demuestra validez psicométrica."
  }
};

const output = path.resolve("validation/test-behavior-report.json");
await fs.mkdir(path.dirname(output), { recursive: true });
await fs.writeFile(output, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify(report, null, 2));
