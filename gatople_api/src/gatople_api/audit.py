"""Real audit trail for music generation, via CEMAF's audit subsystem.

Every /api/generate* request writes one CandidateTrace-derived AuditEntry
per candidate research_loop weighed, plus one summary entry — "what
created what and how", queryable by the same content-addressed key the
audio cache already uses (see routes/generate.py's `_cache_key`), so no
new identifier needs threading through the response.

Deliberately does NOT go through CEMAF's DAG/EventBus machinery —
research_loop is a plain function, not a DAG node, and wiring the full
EventBus/DAGExecutor stack around it would be a large, invasive rewrite
for no benefit this call site needs. EventBusAuditLog.append() and
InMemoryAuditTrail work standalone against a manually-built AuditEntry;
that's the whole integration surface used here.
"""

from __future__ import annotations

from cemaf.audit.models import Actor, AuditEntry, AuditEntryType
from cemaf.audit.protocols import AuditLog, AuditTrail
from cemaf.audit.subscriber import EventBusAuditLog
from cemaf.audit.trail import InMemoryAuditTrail
from fractalmusic.generate import GenerationRequest, GenerationTrace


def build_audit_system() -> tuple[AuditLog, AuditTrail]:
    """One process-lifetime in-memory audit log + trail. No EventBus
    subscription — entries are appended directly by record_generation()."""
    log = EventBusAuditLog()
    trail = InMemoryAuditTrail(audit_log=log)
    return log, trail


async def record_generation(
    *,
    audit_log: AuditLog,
    run_id: str,
    request: GenerationRequest,
    trace: GenerationTrace,
) -> None:
    """Write one AuditEntry per candidate research_loop weighed, plus a
    summary entry recording the winner and its source.

    Candidate entries use EVAL_RESULT with a "score" payload key — not
    just a label of convenience, this is the exact type + key CEMAF's own
    InMemoryAuditTrail.get_quality_trend()/get_anomalies() read, so this
    generation history is usable by that analysis, not merely shaped
    like an audit log.
    """
    system = Actor.system()
    for candidate in trace.candidates:
        await audit_log.append(
            AuditEntry.create(
                type=AuditEntryType.EVAL_RESULT,
                run_id=run_id,
                source=candidate.source,
                actor=system,
                payload={
                    "score": candidate.score_total,
                    "pattern_name": candidate.pattern_name,
                    "won": candidate.won,
                    "tonic": request.tonic,
                    "mode": request.mode,
                    "flavor": request.flavor,
                    "length_events": request.length_events,
                },
            )
        )
    await audit_log.append(
        AuditEntry.create(
            type=AuditEntryType.DAG_COMPLETED,
            run_id=run_id,
            source="research_loop",
            actor=system,
            payload={
                "winner_source": trace.winner_source,
                "candidate_count": len(trace.candidates),
                "tonic": request.tonic,
                "mode": request.mode,
                "flavor": request.flavor,
            },
        )
    )
