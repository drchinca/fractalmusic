import { type JSX, useState } from "react";

import { AuditError, fetchAuditTrail } from "./auditApi";
import type { AuditEntry } from "./auditApi";

// Real values from cemaf.audit.models.AuditEntryType (verified against a
// live /api/audit/{run_id} response) — dotted lowercase, not the Python enum
// member spelling.
const EVAL_RESULT = "eval.result";

const SOURCE_LABELS: Readonly<Record<string, string>> = {
  corpus: "Corpus (patrón guardado)",
  expert: "Experto (recién compuesto)",
  research_loop: "Bucle de investigación",
};

function sourceLabel(source: string): string {
  return SOURCE_LABELS[source] ?? source;
}

function errorMessage(err: unknown): string {
  if (err instanceof AuditError) return err.message;
  return err instanceof Error ? err.message : String(err);
}

function CandidateRow({ entry }: { readonly entry: AuditEntry }): JSX.Element {
  const won = entry.payload.won === true;
  const pattern = typeof entry.payload.pattern_name === "string" ? entry.payload.pattern_name : "?";
  const score = typeof entry.payload.score === "number" ? entry.payload.score.toFixed(2) : "?";
  return (
    <li className={`audit-trail-entry ${won ? "is-winner" : ""}`}>
      <span className="audit-trail-badge">{won ? "Ganador" : "Descartado"}</span>
      <span className="audit-trail-source">{sourceLabel(entry.source)}</span>
      <span className="audit-trail-pattern">{pattern}</span>
      <span className="audit-trail-score">puntaje {score}</span>
    </li>
  );
}

function SummaryRow({ entry }: { readonly entry: AuditEntry }): JSX.Element {
  const winnerSource = typeof entry.payload.winner_source === "string" ? entry.payload.winner_source : "?";
  const candidateCount = typeof entry.payload.candidate_count === "number" ? entry.payload.candidate_count : "?";
  return (
    <li className="audit-trail-entry audit-trail-summary">
      Ganó: {sourceLabel(winnerSource)} · {candidateCount} candidatos evaluados
    </li>
  );
}

interface AuditTrailProps {
  readonly runId: string;
}

export function AuditTrail({ runId }: AuditTrailProps): JSX.Element {
  const [open, setOpen] = useState(false);
  const [entries, setEntries] = useState<readonly AuditEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleToggle(): Promise<void> {
    const next = !open;
    setOpen(next);
    if (!next || entries !== null || loading) return;
    setLoading(true);
    setError(null);
    try {
      const timeline = await fetchAuditTrail(runId);
      setEntries(timeline.entries);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="audit-trail">
      <button
        type="button"
        className="audit-trail-toggle"
        onClick={() => void handleToggle()}
        aria-expanded={open}
      >
        {open ? "Ocultar auditoría CEMAF" : "Ver auditoría CEMAF"}
      </button>
      {open && (
        <div className="audit-trail-body">
          {loading && <p className="audit-trail-meta">Cargando…</p>}
          {error !== null && <p className="audit-trail-error">No pudimos cargar la auditoría: {error}</p>}
          {entries !== null && (
            <ul className="audit-trail-list">
              {entries.map((entry) =>
                entry.type === EVAL_RESULT ? (
                  <CandidateRow key={entry.id} entry={entry} />
                ) : (
                  <SummaryRow key={entry.id} entry={entry} />
                ),
              )}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
