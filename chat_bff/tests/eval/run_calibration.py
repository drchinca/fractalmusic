"""Calibrate the fidelity threshold (Spec I-3).

Reads ``calibration_pairs.json``, scores every pair through the same
similarity function the BFF uses in production (cosine over nomic-embed),
sweeps thresholds in 0.01 steps, picks the one that maximizes F1, and
writes the results to ``calibration_results.md``.

Run::

    cd chat_bff
    uv run python tests/eval/run_calibration.py

Requires Ollama with ``nomic-embed-text`` pulled. Idempotent.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

from chat_bff.bootstrap import make_similarity
from meridian_library.embedders.ollama import OllamaEmbedder

EVAL_DIR = Path(__file__).resolve().parent
PAIRS_PATH = EVAL_DIR / "calibration_pairs.json"
RESULTS_PATH = EVAL_DIR / "calibration_results.md"


@dataclass(frozen=True, slots=True)
class ScoredPair:
    claim: str
    snippet: str
    supports: bool
    score: float


@dataclass(frozen=True, slots=True)
class ThresholdMetrics:
    threshold: float
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def accuracy(self) -> float:
        n = self.tp + self.fp + self.tn + self.fn
        return (self.tp + self.tn) / n if n else 0.0


def metrics_at(*, threshold: float, scored: list[ScoredPair]) -> ThresholdMetrics:
    tp = fp = tn = fn = 0
    for p in scored:
        predicted = p.score >= threshold
        if p.supports and predicted:
            tp += 1
        elif p.supports and not predicted:
            fn += 1
        elif not p.supports and predicted:
            fp += 1
        else:
            tn += 1
    return ThresholdMetrics(threshold=threshold, tp=tp, fp=fp, tn=tn, fn=fn)


async def score_pairs() -> list[ScoredPair]:
    pairs_data = json.loads(PAIRS_PATH.read_text(encoding="utf-8"))
    embedder = OllamaEmbedder(base_url="http://localhost:11434", model="nomic-embed-text")
    similarity = make_similarity(embedder)

    out: list[ScoredPair] = []
    for entry in pairs_data["pairs"]:
        score = await similarity(entry["claim"], entry["snippet"])
        out.append(
            ScoredPair(
                claim=entry["claim"],
                snippet=entry["snippet"],
                supports=entry["supports"],
                score=score,
            )
        )
    return out


def sweep(scored: list[ScoredPair]) -> list[ThresholdMetrics]:
    return [metrics_at(threshold=round(t * 0.01, 2), scored=scored) for t in range(30, 91)]


def best(metrics: list[ThresholdMetrics]) -> ThresholdMetrics:
    return max(metrics, key=lambda m: (m.f1, -abs(m.threshold - 0.55)))


def render_results(*, scored: list[ScoredPair], sweep_metrics: list[ThresholdMetrics], chosen: ThresholdMetrics) -> str:
    pos_scores = sorted([s.score for s in scored if s.supports])
    neg_scores = sorted([s.score for s in scored if not s.supports])
    lines: list[str] = []
    lines.append("# Fidelity Threshold Calibration")
    lines.append("")
    lines.append(f"- Pairs: {len(scored)} ({sum(1 for s in scored if s.supports)} supporting, {sum(1 for s in scored if not s.supports)} non-supporting)")
    lines.append(f"- Embedder: Ollama nomic-embed-text, cosine similarity")
    lines.append("")
    lines.append("## Score distribution")
    lines.append("")
    lines.append(f"- Supporting pairs:    min={min(pos_scores):.3f}  median={pos_scores[len(pos_scores)//2]:.3f}  max={max(pos_scores):.3f}")
    lines.append(f"- Non-supporting:      min={min(neg_scores):.3f}  median={neg_scores[len(neg_scores)//2]:.3f}  max={max(neg_scores):.3f}")
    lines.append("")
    lines.append("## Sweep")
    lines.append("")
    lines.append("| threshold | TP | FP | TN | FN | precision | recall | F1 | accuracy |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for m in sweep_metrics[::5]:  # every 0.05 for readability
        lines.append(f"| {m.threshold:.2f} | {m.tp} | {m.fp} | {m.tn} | {m.fn} | {m.precision:.3f} | {m.recall:.3f} | {m.f1:.3f} | {m.accuracy:.3f} |")
    lines.append("")
    lines.append(f"## Chosen threshold: **{chosen.threshold:.2f}**")
    lines.append("")
    lines.append(f"- F1: {chosen.f1:.3f}  (P={chosen.precision:.3f}, R={chosen.recall:.3f})")
    lines.append(f"- TP={chosen.tp}, FP={chosen.fp}, TN={chosen.tn}, FN={chosen.fn}")
    lines.append("")
    lines.append("## All pairs, sorted by score")
    lines.append("")
    lines.append("| score | supports | claim |")
    lines.append("|---|---|---|")
    for p in sorted(scored, key=lambda s: s.score):
        marker = "✓" if p.supports else "✗"
        claim_short = p.claim if len(p.claim) <= 80 else p.claim[:77] + "..."
        lines.append(f"| {p.score:.3f} | {marker} | {claim_short} |")
    lines.append("")
    return "\n".join(lines)


async def main() -> None:
    print("Scoring 40 pairs through nomic-embed cosine...")
    scored = await score_pairs()
    sweep_metrics = sweep(scored)
    chosen = best(sweep_metrics)
    output = render_results(scored=scored, sweep_metrics=sweep_metrics, chosen=chosen)
    RESULTS_PATH.write_text(output, encoding="utf-8")
    print(f"\nChosen threshold: {chosen.threshold:.2f}  (F1={chosen.f1:.3f}, "
          f"P={chosen.precision:.3f}, R={chosen.recall:.3f})")
    print(f"Written to {RESULTS_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
